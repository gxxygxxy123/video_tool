import cv2
import os
import csv
import queue

# 欲輸出之影片名稱
filename = 'example4_output.mp4'

# cv2的影片輸出編碼方式
fourcc = cv2.VideoWriter_fourcc(*'MP4V')

# 輸出影片的FPS (影片每秒有多少張相片)
fps = 25

# 欲輸出影片的寬
output_width = 1280

# 欲輸出影片的高
output_height = 720

# 輸出影片相關設定
output_video = cv2.VideoWriter(filename, fourcc, fps, (output_width,output_height))

# 來源資料夾
directory4 = './example3/'

# 讀取來源資料夾裡的所有檔名
images = [f for f in os.listdir(directory4)]

# 將所有圖片排序(frame0001.jpg,frame0002.jpg,frame0003.jpg, ......)
images.sort()

for f in images:
    # images只是檔案名稱，需要加上路徑才算是一個完整的路徑
    fullpath = os.path.join(directory4,f)

    # 讀取該路徑的圖片檔案
    image = cv2.imread(fullpath)

    # 將image輸出到影片中
    output_video.write(image)
    print('將 {} 輸出至影片 {}'.format(fullpath, filename))

# 釋放影片資源 (關閉該VideoWriter)
output_video.release()