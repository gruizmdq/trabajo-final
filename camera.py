# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import pickle
import time
import cv2
import os
import constants as CONSTANTS

class Camera:

    def init(self):
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)

    def get_frame(self):    
       # while True:
        # grab the frame from the threaded video stream
        frame = self.vs.read()
        # show the output frame
        cv2.imshow("Frame", frame)
        return frame
           # key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
           # if key == ord("q"):
           #     break
    def stop(self):
        self.vs.stop()