import cv2
import os
import csv
import queue

# 目的資料夾
directory3 = './example3/'

# 如果沒有該資料夾則建立
if not os.path.exists(directory3):
    os.makedirs(directory3)

# 特效icon圖片 (若PNG圖片有去背代表有透明度則為4channel : BGRA)
# cv2.IMREAD_UNCHANGED為讀取圖片中所有的 channels，包含透明度alpha channel
effect_img = cv2.imread('redball.png', cv2.IMREAD_UNCHANGED) 

# 想要顯示特效圖片的寬高(寬高為=30 (OFFSET * 2))
OFFSET = 6

# 將特效圖片縮小成寬高30的小圖片
effect_img = cv2.resize(effect_img, (OFFSET*2, OFFSET*2))

# 特效小圖片的透明度channel
alpha_effect = effect_img[:, :, 3] / 255.0

# 我們要將特效小圖片貼在原圖上，原圖的透明度為1減去特效圖透明度
alpha_image = 1.0 - alpha_effect

# 軌跡視覺化長度
TRAJECTORY_SIZE = 8

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

# 從左側塞入長度為8的空資料
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

    # 將先前8個Frame的羽球座標畫入圖片
    for i in range(0,TRAJECTORY_SIZE):
        if q[i] is not None:
            draw_x = q[i][0] # 欲畫之羽球中心座標x (以圖片左上角為原點向右)
            draw_y = q[i][1] # 欲畫之羽球中心座標y (以圖片左上角為原點向下)

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
                    image[y1:y2, x1:x2, c] = (alpha_effect * effect_img[:, :, c] + alpha_image * image[y1:y2, x1:x2, c])

    # 欲輸出之圖片檔案名稱 (frame0001.jpg, frame0002.jpg, frame0003.jpg ......)
    filename = os.path.join(directory3, 'frame{:0>4d}.jpg'.format(currentFrame))

    # 將相片寫入圖片檔案中
    cv2.imwrite(filename, image)

    print('將 Frame {} 輸出至檔案 {}'.format(currentFrame, filename))

    # 將Frame Index值加一
    currentFrame = currentFrame + 1

# 釋放影片資源
video.release()