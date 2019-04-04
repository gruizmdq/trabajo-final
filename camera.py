# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import pickle
import time
import cv2
import os
import threading

class Camera:
    """
    Camera: this object will capture frames from a camera/
    
    """
    def __init__(self, id):
        self.tempFrame = 0
        self.processedFrame = 0
        self.id = id
        self.processing_on = True
        self.vs = VideoStream(src=0).start()
        self.recognized_people = {}
        self.readingThread = threading.Thread(name='reading_thread',target=self.start_read)
        self.readingThread.daemon = True
        self.readingThread.start()

    def start_read(self):
        while True:
            self.current_frame = self.vs.read()
            self.current_frame = cv2.flip(self.current_frame,1) 

    def get_frame(self):  
        #frame = self.vs.read()
        #frame = cv2.flip(frame,1)
        return self.current_frame

    def get_jpg_to_stream(self):
        frame = self.current_frame 	
        #frame = ImageUtils.resize_mjpeg(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tostring()

    def get_jpg_to_stream_proccessed(self):
        frame = self.processedFrame 	
        #frame = ImageUtils.resize_mjpeg(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tostring()
        
    def stop(self):
        self.vs.stop()

