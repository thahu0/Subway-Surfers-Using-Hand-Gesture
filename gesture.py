import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
gesture_cooldown = 1  # seconds
last_gesture_time = time.time()

def count_extended_fingers(landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if landmarks[tip_ids[id]].y < landmarks[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    frame_height, frame_width, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark

            fingers = count_extended_fingers(landmarks)
            current_time = time.time()

            if current_time - last_gesture_time > gesture_cooldown:
                total_fingers = sum(fingers)

                if total_fingers == 5:
                    pyautogui.press("up")  # Jump
                    print("Jump")
                    last_gesture_time = current_time

                elif total_fingers == 0:
                    pyautogui.press("down")  # Slide
                    print("Slide")
                    last_gesture_time = current_time

                elif fingers == [0, 1, 0, 0, 0]:  # Index only
                    pyautogui.press("right")
                    print("Right")
                    last_gesture_time = current_time

                elif fingers == [0, 1, 1, 0, 0]:  # Index + middle
                    pyautogui.press("left")
                    print("Left")
                    last_gesture_time = current_time

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
