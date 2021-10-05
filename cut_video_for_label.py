import cv2
import os
import csv
import argparse
import sys

def toframe(images,n,saving = False):
    if not saving:
        print('Current frame: ', n)
    return images[n]

videofile = sys.argv[1]
videofile_basename = os.path.splitext(os.path.basename(videofile))[0]

OUTPUT_FOLDER = os.path.join('./output/', videofile_basename)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

video = cv2.VideoCapture(videofile)
total_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
print ("Total frame : {}\n\n\n".format(total_frame))

fps = int(video.get(cv2.CAP_PROP_FPS))
output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')

currentFrame = 0
print('Current frame: ', currentFrame)

images = [None] * total_frame

i = 0
while(True):
    success, image = video.read()
    if not success:
        print(i)
        break
    images[i] = image
    i = i+1

image=images[currentFrame]
cv2.namedWindow("image")


output_video_idx = 1


start = None
end = None



while(True):
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("x"):     #jump next frame
        if currentFrame < total_frame-1:
            if images[currentFrame+1] is not None:
                image=images[currentFrame+1]
                currentFrame+=1
                print('Current frame: ', currentFrame)
            else:
                print('Frame {} is broken'.format(currentFrame+1))
        else:
            print('This is the last frame')
    elif key == ord("z"):     #jump last frame
        if currentFrame == 0:
            print('\nThis is the first frame')
        else:
            currentFrame-=1
            print('Current frame: ', currentFrame)
            image=images[currentFrame]
    elif key == ord("s"):
        if start is None:
            start = currentFrame
            print("START AT {}".format(currentFrame))
        else:
            print("YOU DIDNT PRESS E AFTER last S !")
            sys.exit(1)
    elif key == ord("e"):
        end = currentFrame
        if start is None:
            print("YOU FORGET TO PRESS S !")
            sys.exit(1)
        elif start > end:
            print("THE FRAME OF START > END !")
            sys.exit(1)
        else:
            # Output start~end to video
            output_filename = '{}_{}.avi'.format(videofile_basename,output_video_idx)
            print("SAVE FRAME {} TO {} into {}".format(start,end,output_filename))

            output_video_path = os.path.join(OUTPUT_FOLDER,output_filename)
            print(output_width)
            print(output_height)
            output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width,output_height))
            for i in range(start,end+1):
                frame = images[i]
                output_video.write(frame)
            output_video.release()
            output_video_idx += 1
            start = None
            end = None
            print("SAVE DONE")
    elif key == ord("c"): #cancel
        print("Clear Start and End")
        start = None
        end = None
    elif key == ord("q"):
        if start or end:
            print("YOU FORGET TO PRESS E !")
        break
    

video.release()