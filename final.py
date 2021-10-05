import cv2
import os
import csv
import queue
import numpy as np
import imutils

#計算v1到v2的順時鐘夾角 (x向右 y向下, cv2圖片座標)
def clockwise_angle(v1, v2):
    x1,y1 = v1
    x2,y2 = v2
    dot = x1*x2+y1*y2
    det = x1*y2-y1*x2
    theta = np.arctan2(det, dot)
    theta = theta if theta>0 else 2*np.pi+theta
    return theta*180/np.pi

# 特效icon圖片 (若PNG圖片有去背代表有透明度則為4channel : BGRA)
# cv2.IMREAD_UNCHANGED為讀取圖片中所有的 channels，包含透明度alpha channel
effect_img = cv2.imread('fire.png', cv2.IMREAD_UNCHANGED)

# 軌跡視覺化長度
TRAJECTORY_SIZE = 8

# 讀取CSV檔案
frames = [] # 第幾個Frame
visibility = [] # 有無辨識到球
x = [] # 球的x座標 (恆為整數)
y = [] # 球的y座標 (恆為整數)

with open('final.csv', newline='') as csvfile:
    rows = csv.DictReader(csvfile) # 將第一列當作欄位的名稱，將往後的每一列轉成Dictionary
    
    # 讀取每一列(row)
    for row in rows:
        frames.append(int(row['Frame'])) # 將欄位 Frame 的值加到 frames
        visibility.append(int(row['Visibility'])) # 將欄位 的值Visibility 加到 visibility
        x.append(int(row['X'])) # 將欄位 X 的值加到 x
        y.append(int(row['Y'])) # 將欄位 Y 的值加到 y

# 讀取範例影片
video = cv2.VideoCapture('final.mp4')

# 記錄目前處理到第幾幀(從0開始)
currentFrame = 0

# 建立一個deque (一種資料結構，支援前後新增刪除資料，可以取中間索引的值)
q = queue.deque()

# 從左側塞入長度為8的空資料
for i in range(0,TRAJECTORY_SIZE):
    q.appendleft(None)

# 影片的FPS (影片每秒有多少張相片)
fps = int(video.get(cv2.CAP_PROP_FPS))

# 影片的寬
output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))

# 影片的高
output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# cv2的影片編碼方式
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# 欲輸出之影片名稱以及相關設定
output_video = cv2.VideoWriter('final_output.mp4',fourcc, fps, (output_width,output_height))

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

    # 將先前8個Frame的羽球座標畫入圖片
    for i in range(0,TRAJECTORY_SIZE):
        if q[i] is not None:
            draw_x = q[i][0] # 欲畫之羽球中心座標x (以圖片左上角為原點向右)
            draw_y = q[i][1] # 欲畫之羽球中心座標y (以圖片左上角為原點向下)


            # 想要顯示特效圖片的寬高(寬高為=30 (OFFSET * 2))，離球越遠OFFSET越小: 16 12 8 4
            OFFSET = ((TRAJECTORY_SIZE - i + 1) // 2) * 4

            # 根據前後球的位置對圖片進行旋轉
            v1 = np.array([0,-1]) # png原本朝向方向
            if i != TRAJECTORY_SIZE-1 and q[i+1] is not None:
                v2 = np.array([draw_x-q[i+1][0],draw_y-q[i+1][1]]) # v2為png應該要朝的方向
            elif i != 0 and q[i-1] is not None:
                v2 = np.array([q[i-1][0]-draw_x,q[i-1][1]-draw_y])
            else: # 前後球沒偵測到為None，跳過
                continue
            if np.sum(v2**2) == 0: # v2為[0,0]則跳過(代表前後球偵測到的位置相同)
                continue
            angle = clockwise_angle(v1,v2) # v1到v2的順時鐘夾角
            effect_img_tmp = imutils.rotate_bound(effect_img, angle=angle) # 對圖片進行旋轉
            effect_img_tmp = cv2.resize(effect_img_tmp, (OFFSET*2, OFFSET*2)) # 圖片縮放
            # 特效小圖片的透明度channel
            alpha_effect = effect_img_tmp[:, :, 3] / 255.0

            # 我們要將特效小圖片貼在原圖上，原圖的透明度為1減去特效圖透明度
            alpha_image = 1.0 - alpha_effect




            # 特效小圖的左上角座標(x1,y1) 以及右下角座標(x2,y2)
            x1, x2 = draw_x - OFFSET, draw_x + OFFSET
            y1, y2 = draw_y - OFFSET, draw_y + OFFSET

            # 如果羽球在圖片邊緣處，特效小圖有可能超出整張相片的範圍，則不做
            if x1 < 0 or y1 < 0 or x2 > image.shape[1] or y2 > image.shape[0]: # shape[1]為相片寬度， shape[0]為相片高度
                continue
            else:
                # 對特效小圖所在的範圍的BGR三個channel根據透明度alpha進行結合 (透明度*像素 的相加)
                for c in range(0, 3):
                    # cv2 圖片的資料維度為[高度,寬度,Channel]
                    image[y1:y2, x1:x2, c] = (alpha_effect * effect_img_tmp[:, :, c] + alpha_image * image[y1:y2, x1:x2, c])

    # 輸出圖片至影片中
    output_video.write(image)

    # 將Frame Index值加一
    currentFrame = currentFrame + 1

# 釋放影片資源
video.release()
output_video.release()





