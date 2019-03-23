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

# load our serialized face detector from disk
#print("[INFO] loading face detector...")
#protoPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PROTOTXT])
#modelPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PRE_TRAINEED])
#detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load our serialized face embedding model from disk
#print("[INFO] loading face recognizer...")
#embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)

# load the actual face recognition model along with the label encoder
#recognizer = pickle.loads(open(CONSTANTS.RECOGNIZER_PATH, "rb").read())
#le = pickle.loads(open(CONSTANTS.LABEL_ENCODER_PATH, "rb").read())

class System(object):

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
                self.detector.detect(frame)


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
        