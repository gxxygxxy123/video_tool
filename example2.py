import cv2
import os
import csv
import queue

# 目的資料夾
directory2 = './example2/'

# 如果沒有該資料夾則建立
if not os.path.exists(directory2):
    os.makedirs(directory2)

# 軌跡視覺化長度
TRAJECTORY_SIZE = 2

# 讀取CSV檔案
frames = [] # 第幾個Frame
visibility = [] # 有無辨識到球
x = [] # 球的x座標 (恆為整數)
y = [] # 球的y座標 (恆為整數)
with open('example.csv', newline='') as csvfile:
    rows = csv.DictReader(csvfile) # 將第一列當作欄位的名稱，將往後的每一列轉成Dictionary
    
    # 讀取每一列(row)
    for row in rows:
        frames.append(int(row['Frame'])) # 將欄位 Frame 的值加到 frames
        visibility.append(int(row['Visibility'])) # 將欄位 的值Visibility 加到 visibility
        x.append(int(row['X'])) # 將欄位 X 的值加到 x
        y.append(int(row['Y'])) # 將欄位 Y 的值加到 y

# 讀取範例影片
video = cv2.VideoCapture('example.mp4')

# 記錄目前處理到第幾幀(從0開始)
currentFrame = 0

# 建立一個deque (一種資料結構，支援前後新增刪除資料，可以取中間索引的值)
q = queue.deque()

# 從左側塞入長度為2的空資料
for i in range(0,TRAJECTORY_SIZE):
    q.appendleft(None)

while(True):
    # 從影片讀取一張相片 (Frame)
    success, image = video.read()

    # 如果讀取不到Frame則離開 (代表影片讀取終了)
    if not success: 
        break

    if visibility[currentFrame] != 0: # 如果visibility不為0代表有抓到羽球位置，deque塞入羽球座標x y
        q.appendleft((x[currentFrame],y[currentFrame]))
        q.pop()
    else: # 如果visibility為0代表沒有抓到羽球位置，deque塞入空資料
        q.appendleft(None)
        q.pop()

    # 將先前2個Frame的羽球座標畫入圖片
    for i in range(0,TRAJECTORY_SIZE):
        if q[i] is not None:
            draw_x = q[i][0] # 欲畫之羽球中心座標x (以圖片左上角為原點向右)
            draw_y = q[i][1] # 欲畫之羽球中心座標y (以圖片左上角為原點向下)
            # 在image上(x,y)的位置畫上大小為4，顏色(B,G,R)為紅色(0,0,255)，線條寬度為-1(-1代表實心)的圓
            cv2.circle(image,(draw_x, draw_y), 4, (0,0,255), -1)

    # 欲輸出之圖片檔案名稱 (frame0001.jpg, frame0002.jpg, frame0003.jpg ......)
    filename = os.path.join(directory2, 'frame{:0>4d}.jpg'.format(currentFrame))

    # 將相片寫入圖片檔案中
    cv2.imwrite(filename, image)

    print('將 Frame {} 輸出至檔案 {}'.format(currentFrame, filename))

    # 將Frame Index值加一
    currentFrame = currentFrame + 1

# 釋放影片資源
video.release()