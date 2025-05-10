
from imutils import face_utils
from utils import *
import numpy as np
import pyautogui as pyag
import imutils
import dlib
import cv2
import threading

# Thresholds and consecutive frame length for triggering the mouse action.
MOUTH_AR_THRESH = 0.6
MOUTH_AR_CONSECUTIVE_FRAMES = 15
EYE_AR_THRESH = 0.19
EYE_AR_CONSECUTIVE_FRAMES = 15
WINK_AR_DIFF_THRESH = 0.04
WINK_AR_CLOSE_THRESH = 0.19
WINK_CONSECUTIVE_FRAMES = 10

# Initialize the frame counters for each action as well as 
# booleans used to indicate if action is performed or not
MOUTH_COUNTER = 0
EYE_COUNTER = 0
WINK_COUNTER = 0
INPUT_MODE = False
EYE_CLICK = False
LEFT_WINK = False
RIGHT_WINK = False
SCROLL_MODE = False
ANCHOR_POINT = (0, 0)
WHITE_COLOR = (255, 255, 255)
YELLOW_COLOR = (0, 255, 255)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (255, 0, 0)
BLACK_COLOR = (0, 0, 0)

# Initialize Dlib's face detector (HOG-based) and then create
# the facial landmark predictor
shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

# Grab the indexes of the facial landmarks for the left and
# right eye, nose and mouth respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

vid = cv2.VideoCapture(0)
resolution_w = 1366
resolution_h = 768
cam_w = 640
cam_h = 480
unit_w = resolution_w / cam_w
unit_h = resolution_h / cam_h

voice_commands = {
    "click": lambda: pyag.click(),
    "left click": lambda: pyag.click(button='left'),
    "right click": lambda: pyag.click(button='right'),
    "scroll mode on": lambda: enable_scroll_mode(True),
    "scroll mode off": lambda: enable_scroll_mode(False),
    "stop": lambda: exit()
}

RUNNING = False

def enable_scroll_mode(state):
    global SCROLL_MODE
    SCROLL_MODE = state
    print(f"Scroll mode {'enabled' if state else 'disabled'}")

def voice_thread():
    while RUNNING:
        cmd = listen_command()
        if cmd:
            for trigger, action in voice_commands.items():
                if trigger in cmd:
                    action()

def run_mouse_controller():
    global RUNNING, MOUTH_COUNTER, EYE_COUNTER, WINK_COUNTER, INPUT_MODE, SCROLL_MODE, ANCHOR_POINT
    RUNNING = True
    threading.Thread(target=voice_thread, daemon=True).start()

    while RUNNING:
        ret, frame = vid.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = imutils.resize(frame, width=cam_w, height=cam_h)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)
        if len(rects) > 0:
            rect = rects[0]
        else:
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        mouth = shape[mStart:mEnd]
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        nose = shape[nStart:nEnd]

        temp = leftEye
        leftEye = rightEye
        rightEye = temp

        mar = mouth_aspect_ratio(mouth)
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        diff_ear = np.abs(leftEAR - rightEAR)
        nose_point = (nose[3, 0], nose[3, 1])

        mouthHull = cv2.convexHull(mouth)
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [mouthHull], -1, YELLOW_COLOR, 1)
        cv2.drawContours(frame, [leftEyeHull], -1, YELLOW_COLOR, 1)
        cv2.drawContours(frame, [rightEyeHull], -1, YELLOW_COLOR, 1)

        for (x, y) in np.concatenate((mouth, leftEye, rightEye), axis=0):
            cv2.circle(frame, (x, y), 2, GREEN_COLOR, -1)

        if diff_ear > WINK_AR_DIFF_THRESH:
            if leftEAR < rightEAR:
                if leftEAR < EYE_AR_THRESH:
                    WINK_COUNTER += 1
                    if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                        pyag.click(button='left')
                        WINK_COUNTER = 0
            elif leftEAR > rightEAR:
                if rightEAR < EYE_AR_THRESH:
                    WINK_COUNTER += 1
                    if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                        pyag.click(button='right')
                        WINK_COUNTER = 0
            else:
                WINK_COUNTER = 0
        else:
            if ear <= EYE_AR_THRESH:
                EYE_COUNTER += 1
                if EYE_COUNTER > EYE_AR_CONSECUTIVE_FRAMES:
                    SCROLL_MODE = not SCROLL_MODE
                    EYE_COUNTER = 0
            else:
                EYE_COUNTER = 0
                WINK_COUNTER = 0

        if mar > MOUTH_AR_THRESH:
            MOUTH_COUNTER += 1
            if MOUTH_COUNTER >= MOUTH_AR_CONSECUTIVE_FRAMES:
                INPUT_MODE = not INPUT_MODE
                MOUTH_COUNTER = 0
                ANCHOR_POINT = nose_point
        else:
            MOUTH_COUNTER = 0

        if INPUT_MODE:
            cv2.putText(frame, "READING INPUT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            x, y = ANCHOR_POINT
            nx, ny = nose_point
            w, h = 60, 35
            multiple = 1
            cv2.rectangle(frame, (x - w, y - h), (x + w, y + h), GREEN_COLOR, 2)
            cv2.line(frame, ANCHOR_POINT, nose_point, BLUE_COLOR, 2)

            dir = direction(nose_point, ANCHOR_POINT, w, h)
            cv2.putText(frame, dir.upper(), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            drag = 18
            if dir == 'right':
                pyag.moveRel(drag, 0)
            elif dir == 'left':
                pyag.moveRel(-drag, 0)
            elif dir == 'up':
                pyag.moveRel(0, -drag) if not SCROLL_MODE else pyag.scroll(40)
            elif dir == 'down':
                pyag.moveRel(0, drag) if not SCROLL_MODE else pyag.scroll(-40)

        if SCROLL_MODE:
            cv2.putText(frame, 'SCROLL MODE IS ON!', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    vid.release()
    RUNNING = False
