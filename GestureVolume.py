import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import numpy as np
from math import *
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput import keyboard

set = True
def on_press_key(key):
    global set
    if key == keyboard.Key.esc:
        set = False
        print(set)
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable
        set = True
        print('Key pressed: ' + k)
        # return False  # stop listener; remove this if want more keys
    return True
def main():
    pTime = 0
    cTime = 0
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    cap = cv2.VideoCapture(0)
    # cap.set(3, 1280)
    # cap.set(4, 720)
    detector = htm.handDetector(maxHands=1)
    vol = 0
    volBar = 400
    volPer = 0
    while cap.isOpened():
        success, img = cap.read()
        img = detector.findHands(img)
        img = cv2.flip(img, 1)
        lmList = detector.findPos(img, draw=False)
        h, w, c = img.shape
        vol_Range = volume.GetVolumeRange()
        minVol = vol_Range[0]
        maxVol = vol_Range[1]
        if len(lmList) != 0:
            x1, y1 = w - lmList[4][1], lmList[4][2]
            x2, y2 = w - lmList[8][1], lmList[8][2]
            m1, m2 = (x1 + x2) // 2, (y1 + y2) // 2
            length = int(sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
            #volume
            max_length = 300
            min_length = 40

            # print(length, vol)
            listener = keyboard.Listener(on_press=on_press_key)
            listener.start()
            if set:
                # if true, it draws a line
                vol = np.interp(length, [min_length, max_length], [minVol, maxVol])
                volBar = np.interp(length, [min_length, max_length], [400, 150])
                volPer = np.interp(length, [min_length, max_length], [0, 100])

                cv2.circle(img, (x1, y1), 10, (194, 113, 25), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (194, 113, 25), cv2.FILLED)
                cv2.circle(img, (m1, m2), 10, (194, 113, 25), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (194, 113, 25), 2)
                volume.SetMasterVolumeLevel(vol, None)
            else:
                print("Do nothing")

        #calculate fps
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        #add fps
        cv2.putText(img, "FPS: " + str(int(fps)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (47, 158, 68), 3)
        cv2.putText(img, f'Volume: {int(volPer)}%', (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (194, 113, 25), 3)
        cv2.rectangle(img, (50, 150), (85, 400), (194, 113, 25), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (194, 113, 25), cv2.FILLED)
        # BGR -> RGB
        #render video
        cv2.imshow('Hand Tracking', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
