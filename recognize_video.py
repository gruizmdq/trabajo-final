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



class FaceRecognizer():
	"""
	FaceRecognizer. This identify the faces of the frames.
	"""
	# load our serialized face embedding model from disk
	print("[INFO] loading face recognizer...")
	embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)
	# load the actual face recognition model along with the label encoder
	recognizer = pickle.loads(open(CONSTANTS.RECOGNIZER_PATH, "rb").read())
	le = pickle.loads(open(CONSTANTS.LABEL_ENCODER_PATH, "rb").read())

	def __init__(self):
		self.last_time = time.time()

	def save_frame(self, frame):
		img_item =  CONSTANTS.UNRECOGNIZED_FACES_PATH + str(len(os.listdir(CONSTANTS.UNRECOGNIZED_FACES_PATH))) + ".png"
		cv2.imwrite(img_item, frame)
		pass

	def make_prediction(self, face, frame, startX, startY, endX, endY):
		faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
		self.embedder.setInput(faceBlob)
		vec = self.embedder.forward()

		# perform classification to recognize the face
		preds = self.recognizer.predict_proba(vec)[0]
		j = np.argmax(preds)
		proba = preds[j]
		name = self.le.classes_[j]

		# draw the bounding box of the face along with the
		# associated probability
		if proba > CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
			text = "{}: {:.2f}%".format(name, proba * 100)
			color = (0, 0, 255)

		else: 
			text = "desconocido:"
			color = (255, 0, 0)
			now = time.time()
			#Timer to avoid multi saves per second
			if now - self.last_time > CONSTANTS.SECONDS_BETWEEN_CAPTURE:
				self.save_frame(frame)
				self.last_time = now
			

		
		y = startY - 10 if startY - 10 > 10 else startY + 10
		cv2.rectangle(frame, (startX, startY), (endX, endY),
				color, 2)
		cv2.putText(frame, text, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)