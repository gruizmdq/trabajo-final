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
    """
    Camera: this object will capture frames from a camera/
    
    """
    def init(self):
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)
    
    def get_frame(self):    
        frame = self.vs.read()
        return frame

    def stop(self):
        self.vs.stop()