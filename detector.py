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

class FaceDetector():
    """
    Face Detector. This detect faces from a frames.
    """
    protoPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PROTOTXT])
    modelPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PRE_TRAINEED])
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
    embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)

    def __init__(self, controller):
        # load our serialized face detector from disk
        print("[INFO] loading face detector...")
        #self.vs = VideoStream(src=0).start()
        #time.sleep(2.0)
        self.controller = controller
        # load our serialized face embedding model from disk
        #print("[INFO] loading face recognizer...")
        #embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)
        #self.detect()

    def detect(self, frame):
        # start the FPS throughput estimator
        #fps = FPS().start()

        # Save last time that non recognized face was captured. time.time() - last_time > SECONDS_INTERVAL
        #last_time = time.time()

        # loop over frames from the video file stream
        #while True:
            # grab the frame from the threaded video stream
         #   frame = self.vs.read()
            
            # resize the frame to have a width of 600 pixels (while
            # maintaining the aspect ratio), and then grab the image
            # dimensions
            frame = imutils.resize(frame, width=600)
            (h, w) = frame.shape[:2]

            # construct a blob from the image
            imageBlob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False)

            # apply OpenCV's deep learning-based face detector to localize
            # faces in the input image
            self.detector.setInput(imageBlob)
            detections = self.detector.forward()

            # loop over the detections
            tiempo = time.time()

            #print("Detections format: {}".format(detections))
            for i in range(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections
                if confidence > CONSTANTS.CONFIDENCE_TO_ACCEPT_DETECTION:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the face
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # extract the face ROI
                    face = frame[startY:endY, startX:endX]
                    (fH, fW) = face.shape[:2]

                    # ensure the face width and height are sufficiently large
                    if fW < 20 and fH < 20:
                        continue

                    # construct a blob for the face ROI, then pass the blob
                    # through our face embedding model to obtain the 128-d
                    # quantification of the face

                    # Adding try to fix bug.
                    try:
                       #Recognizer().make_prediction(face, frame, startX, startY, endX, endY)
                        self.controller.recognizer.make_prediction(face, frame, startX, startY, endX, endY)
                    except Exception as e:
                       print(str(e))

            tiempo = time.time()
            # update the FPS counter
            #fps.update()

            # show the output frame
            cv2.imshow("Frame", frame)
            #key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
           # if key == ord("q"):
            #    break

        # stop the timer and display FPS information
        #fps.stop()
        #print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        #print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # do a bit of cleanup
        #cv2.destroyAllWindows()
        #self.vs.stop()

    def save_frame(self, frame):
        img_item =  CONSTANTS.UNRECOGNIZED_FACES_PATH + str(len(os.listdir(CONSTANTS.UNRECOGNIZED_FACES_PATH))) + ".png"
        cv2.imwrite(img_item, frame)
        pass

    def make_prediction(self, face, frame, startX, startY, endX, endY):
        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(faceBlob)
        vec = embedder.forward()

        # perform classification to recognize the face
        preds = recognizer.predict_proba(vec)[0]
        j = np.argmax(preds)
        proba = preds[j]
        name = le.classes_[j]

        # draw the bounding box of the face along with the
        # associated probability
        if proba > CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
            text = "{}: {:.2f}%".format(name, proba * 100)
            color = (0, 0, 255)

        else: 
            text = "desconocido:"
            color = (255, 0, 0)
            

        #copy frame	to save 
        frame_copy = frame.copy()
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
                color, 2)
        cv2.putText(frame, text, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        self.save_frame(frame_copy)
