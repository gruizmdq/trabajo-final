# import the necessary packages
import os
import numpy as np
import imutils
import cv2
import constants as CONSTANTS

class FaceDetector():
    """
    Face Detector. This detect faces from a frames.
    """
    protoPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PROTOTXT])
    modelPath = os.path.sep.join([CONSTANTS.MODEL_PATH, CONSTANTS.MODEL_PRE_TRAINED])
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
    embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)

    def __init__(self):
        # load our serialized face detector from disk
        print("[INFO] loading face detector...")

    def detect(self, frame):
        # resize the frame to have a width of 600 pixels (while
        # maintaining the aspect ratio), and then grab the image
        # dimensions
        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]

        # construct a blob from the image
        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (224, 224)), 1.0, (224, 224),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

        # apply OpenCV's deep learning-based face detector to localize
        # faces in the input image
        arr_faces = []

        try:
            self.detector.setInput(imageBlob)   
            detections = self.detector.forward()
            #array with all faces detected
            end_loop = False
            i = 0
            #to avoid processing to many poor detections
            if len(detections) > 0:
                while not end_loop:
                #for i in range(0, detections.shape[2]):
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
                        arr_faces.append([face, startX, startY, endX, endY])

                        i += 1
                        if (i >= detections.shape[2]):
                            end_loop = True
                    else:
                        end_loop = True
        except Exception as e:
            print("********************************* EXCEP " +str(e))
        # show the output frame
        return frame, arr_faces

