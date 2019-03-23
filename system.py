# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import pickle
import time
import cv2
import os
from recognize_video import FaceRecognizer
from detector import FaceDetector
from camera import Camera
import constants as CONSTANTS

class System(object):
    """
    System: main class. 
    Everything is going across this object.
    """
    def __init__(self):
        self.recognizer = FaceRecognizer()
        self.detector = FaceDetector(self)
        self.cameras = []
        self.cameras.append(Camera())
        self.start()

    def start(self):
        for camera in self.cameras:
            
            camera.init()
            # start the FPS throughput estimator
            fps = FPS().start()
            while True:
                frame = camera.get_frame()

                #Detection
                face, frame, startX, startY, endX, endY = self.detector.detect(frame)
                #Recognition
                self.recognizer.make_prediction(face, frame, startX, startY, endX, endY)

                cv2.imshow("Frame", frame)

                # update the FPS counter
                fps.update()

                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break
            # stop the timer and display FPS information
            fps.stop()
            # do a bit of cleanup
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            cv2.destroyAllWindows()
            camera.stop()
        
System()
        