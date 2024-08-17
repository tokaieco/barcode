import streamlit as st
import cv2
import time
from PIL import Image
#追加
from collections import defaultdict
from datetime import datetime
from pyzbar.pyzbar import decode
#import pyzbar
import pandas as pd
#import os
#import threading
import csv
#音
import numpy as np
import pyaudio
# サンプリングレートを定義
SAMPLE_RATE = 44100
# 指定ストリームで、指定周波数のサイン波を、指定秒数再生する関数
def play(s: pyaudio.Stream, freq: float, duration: float):
    # 指定周波数のサイン波を指定秒数分生成
    samples = np.sin(np.arange(int(duration * SAMPLE_RATE)) * freq * np.pi * 2 / SAMPLE_RATE)
    # ストリームに渡して再生
    s.write(samples.astype(np.float32).tostring())


#追加
#カラー
m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #009991;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #0fff01;
    color:#ff0000;
    }
</style>""", unsafe_allow_html=True)
#Set exit file 
recorded_barcodes = set()
#Counter
barcode_counts = defaultdict(int)
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = f'barcode82_{current_date}.csv'
csv_header = ['product_num', 'date']


st.markdown("# Camera Application")
cap = cv2.VideoCapture(0)
if not cap.isOpened:
    print("カメラが開けません")
#追加 ボタン 
#st.button("Reset", type="primary")
if st.button("Reset"):
    cap.release()
    #削除ボタン
if st.button("Delete Last Row"):
    # CSVファイルを読み込む
    file_path = csv_file_path
    df = pd.read_csv(file_path)
    # 最新の行を削除
    df = df.iloc[:-1]

    # CSVファイルに保存（上書き）
    df.to_csv(file_path, index=False)




if st.button("Barcode", type="primary"):
#if st.success('Success message'):  
    #st.write("Why hello there")
    device = user_input = st.text_input("input your video/camera device", "0")

    if device.isnumeric():
        # e.g. "0" -> 0
        device = int(device)

    cap = cv2.VideoCapture(device)
    #cap = cv2.VideoCapture(0)



    image_loc = st.empty()
    while cap.isOpened:
        ret, img = cap.read()
    #追加 上
        height, width, _ = img.shape
        img = img[:height // 3, :]
       


    #追加
        # フレームの淵を緑にする
        #img = cv2.rectangle(img, (0, 0), (width-1, height//2-1), (0, 255, 0), 1)


        #追加
        ##bar code
        for d in decode(img):
            s = d.data.decode()
                # 速度を調整
            time.sleep(0.1)  # 必要に応じて時間を調整
            if s not in recorded_barcodes:
                barcode_counts[s] += 1

                #record
                if barcode_counts[s] >= 2:
                    print(s)
                    try:
                        if '.' in s:
                            s_formatted = f"{float(s):.6f}" 
                        else:
                            s_formatted = f"{int(s)}" 
                    except ValueError:
                        s_formatted = s 

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    #write
                    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:# 追記モードa
                        writer = csv.writer(csv_file)
                        writer.writerow([s_formatted, timestamp])

                    recorded_barcodes.add(s)
                    del barcode_counts[s]  #Reset counter

        #追加
                    file_path = csv_file_path
                    df = pd.read_csv(file_path)
                    #追加       
                    for i in range(len(df)):
                        if df.iloc[i-1,1]==df.iloc[i,1]:
                            df.drop(df.index[i])
                            df.to_csv(file_path, index=False)    



            img = cv2.rectangle(img, (d.rect.left, d.rect.top),
                                (d.rect.left + d.rect.width, d.rect.top + d.rect.height), (0, 255, 0), 3)
            img = cv2.putText(img, s, (d.rect.left, d.rect.top + d.rect.height),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            #追加
            #



            # フレームの淵を変える
            img = cv2.rectangle(img, (0, 0), (width-1, height//2-1), (255, 0,0), 10)
            time.sleep(0.3)
            # PyAudio開始
            p = pyaudio.PyAudio()
            # ストリームを開く
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=SAMPLE_RATE,
                            frames_per_buffer=1024,
                            output=True)
            # ドミソドーを再生
            #play(stream, 261.626, 0.2)  # note#60 C4 ド
            #play(stream, 329.628, 0.3)  # note#64 E4 ミ
            #play(stream, 391.995, 0.1)  # note#67 G4 ソ
            play(stream, 523.251, 0.1)  # note#72 C5 ド            
            play(stream, 391.995, 0.3)  # note#67 G4 ソ
            # ストリームを閉じる
            time.sleep(0.1)
            stream.close()
            # PyAudio終了
            p.terminate()
         



        
        time.sleep(0.1)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        image_loc.image(img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    else:
        st.write("Goodbye")





