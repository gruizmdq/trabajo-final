# import the necessary packages
import os
import pickle
import time
import numpy as np
import cv2
import constants as CONSTANTS
from person import Person

class FaceRecognizer():
	"""
	FaceRecognizer. This identify the faces from a frame.
	"""
	# load our serialized face embedding model from disk
	print("[INFO] loading face recognizer...")
	embedder = cv2.dnn.readNetFromTorch(CONSTANTS.EMBEDDING_MODEL_PATH)
	# load the actual face recognition model along with the label encoder
	recognizer = pickle.loads(open(CONSTANTS.RECOGNIZER_PATH, "rb").read())
	le = pickle.loads(open(CONSTANTS.LABEL_ENCODER_PATH, "rb").read())

	def __init__(self, system):
		self.last_time = time.time()
		self.system = system

	def make_prediction(self, face):
		faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
		self.embedder.setInput(faceBlob)
		vec = self.embedder.forward()
		# perform classification to recognize the face
		preds = self.recognizer.predict_proba(vec)
		preds = preds[0]
		j = np.argmax(preds)
		proba = preds[j]
		name = self.le.classes_[j]

		# draw the bounding box of the face along with the
		# associated probability
		
		if proba > CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
			text = name
			recognized = True
		else: 
			text = "unknown"
			recognized = False
			if proba > CONSTANTS.CONFIDENCE_TO_UNKNOWN_FACES:
				text = text + "-" + name

		return {"name": text, "face": face, "confidence": proba, "recognized": recognized}
		