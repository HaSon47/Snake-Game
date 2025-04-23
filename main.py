import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import math
import random

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

detector = HandDetector(detectionCon=0.8,maxHands=1)

class SnakeGameClass:
    """
    list of points
    list of distances
    current length
    total length    
    """
    def __init__(self, pathFood):
        self.points = [] # list of all points of the snake
        self.lengths = [] # distance between each point
        self.currentLength = 0 # total length of the snake
        self.allowedLength = 150 # total allowed length
        self.previousHead = (0,0) # previous head point

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        # Thêm dòng này để thay đổi kích thước (ví dụ: scale xuống 50%)
        scale_percent = 50  # Tỷ lệ phần trăm kích thước mong muốn
        width = int(self.imgFood.shape[1] * scale_percent / 1000)
        height = int(self.imgFood.shape[0] * scale_percent / 1000)
        self.imgFood = cv2.resize(self.imgFood, (width, height))


        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = (0,0)
        self.randomFoodLocation()

        self.score=0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = (random.randint(100,1000), random.randint(100,600))

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300,400], scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f"Your Score: {self.score}", [300,550], scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead
            self.points.append([cx, cy])
            distance = math.hypot(cx-px, cy-py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = (cx, cy)

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break 
            # Check if snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood//2 <cx< rx + self.wFood//2 and \
                ry - self.hFood//2 <cy<ry + self.hFood//2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score +=1
                print(self.score)


            # Draw Snake
            if self.points:
                for i,point in enumerate(self.points):
                    if i!=0:
                        cv2.line(imgMain, self.points[i-1], self.points[i], (0,0,255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (200,0,200), cv2.FILLED)



            # Draw Food
            rx, ry = self.foodPoint
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx-self.wFood//2,ry-self.hFood//2))

            cvzone.putTextRect(imgMain, f"Score: {self.score}", [50,80], scale=3, thickness=3, offset=10)
            
            # Check for Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(imgMain, [pts], False, (0,200,0),3)
            minDist = cv2.pointPolygonTest(pts,(cx,cy), True)
            if -0.5<= minDist <=0.5:
                self.gameOver = True
                self.points = [] # list of all points of the snake
                self.lengths = [] # distance between each point
                self.currentLength = 0 # total length of the snake
                self.allowedLength = 150 # total allowed length
                self.previousHead = (0,0) # previous head point
                self.randomFoodLocation()

                self.score=0
        return imgMain

game = SnakeGameClass(r"C:\Users\Lenovo\OneDrive - Hanoi University of Science and Technology\Desktop\Self_learning\Snake-Game\donut.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    hands, img = detector.findHands(img, flipType=False)
    

    if hands:
       lmList = hands[0]['lmList']
       pointIndex = lmList[8][0:2]
       img = game.update(img, pointIndex)

    cv2.imshow("Image",img)   
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('r'):
        game.gameOver=False

# Release resources
cap.release()
cv2.destroyAllWindows()