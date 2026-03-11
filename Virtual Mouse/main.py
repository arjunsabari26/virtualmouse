import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math

class HandDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):
        """
        Initializes the HandDetector object with MediaPipe's Hands solution.
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        
    def findHands(self, img, draw=True):
        """
        Finds hands in a given frame/image.
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
        
    def findPosition(self, img, handNo=0, draw=True):
        """
        Returns a list of landmark positions for the detected hand.
        """
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        """
        Checks which fingers are up. 
        Returns a list of 5 integers (0 for down, 1 for up).
        """
        fingers = []
        
        if len(self.lmList) == 0:
            return fingers
            
        # Thumb (Simple check assuming hand facing forward)
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 4 Fingers (Index, Middle, Ring, Pinky)
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers


def main():
    wCam, hCam = 640, 480
    frameR = 100 # Frame reduction (padding) for smoother cursor reach at edges
    smoothening = 7 # Smoothening factor to avoid cursor jitter
    
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam) # Set width
    cap.set(4, hCam) # Set height
    
    detector = HandDetector(maxHands=1)
    wScr, hScr = pyautogui.size()
    
    scroll_prev_y = None

    # Disable PyAutoGUI failsafe so cursor doesn't interrupt when pushed to edges
    pyautogui.FAILSAFE = False

    print("Starting Virtual Mouse System...")
    print("Press 'Esc' to exit.")

    while True:
        success, img = cap.read()
        if not success:
            break
            
        # Flip image horizontally for a natural mirror-like interaction
        img = cv2.flip(img, 1) 
        
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]   # Index finger tip
            x2, y2 = lmList[12][1:]  # Middle finger tip
            
            fingers = detector.fingersUp()
            
            # Draw movement boundary box
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
            
            # 1. Moving Mode: Index finger UP, Middle/Ring DOWN
            if fingers[1] == 1 and fingers[2] == 0:
                # Convert camera coordinates to screen coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                
                # Smoothen values to make tracking fluent
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                
                # Move mouse
                pyautogui.moveTo(clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                
                plocX, plocY = clocX, clocY
                scroll_prev_y = None # Reset scroll tracker when moving
                
            # 2. Clicking & Scrolling Mode: Index & Middle UP, Ring DOWN
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                # Distance between Index & Middle fingers
                length = math.hypot(x2 - x1, y2 - y1)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Left Click Action (Fingers close)
                if length < 40:
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
                    time.sleep(0.2) # Delay to prevent multiple instant clicks
                    scroll_prev_y = None
                
                # Scroll Action (Fingers slightly apart & moving vertically)
                else:
                    cv2.circle(img, (cx, cy), 15, (255, 255, 0), cv2.FILLED)
                    if scroll_prev_y is not None:
                        dy = scroll_prev_y - cy # Difference in Y position
                        if abs(dy) > 5:
                            # Scroll multiplier to adjust scrolling speed
                            scroll_amount = int(dy * 3) 
                            pyautogui.scroll(scroll_amount)
                    scroll_prev_y = cy # Store current Y to track next frame's movement
                    
            # 3. Right Click Mode: Index, Middle, Ring UP
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                # Distance between Middle and Ring fingers to confirm close gesture
                length_right = math.hypot(lmList[16][1] - lmList[12][1], lmList[16][2] - lmList[12][2])
                
                # Right Click Action
                if length_right < 40:
                    cv2.circle(img, (lmList[16][1], lmList[16][2]), 15, (0, 0, 255), cv2.FILLED)
                    pyautogui.rightClick()
                    time.sleep(0.3)
                scroll_prev_y = None
                
            else:
                scroll_prev_y = None
                
        # Calculate & Display Frame Rate (FPS)
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        # Display Window
        cv2.imshow("Virtual Mouse Tracker", img)
        if cv2.waitKey(1) & 0xFF == 27: # Press 'Esc' to terminate
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
