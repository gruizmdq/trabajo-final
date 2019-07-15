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
		self.unknowns_count = 0
		self.system = system

	def save_frame(self, text, frame):
		path = CONSTANTS.UNRECOGNIZED_FACES_PATH + text
		os.makedirs(path, exist_ok=True)
		img_item =  path + str(len(os.listdir(path))) + ".png"
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
			recognized = True
		else: 
			text = "unknown"
			color = (255, 0, 0)
			recognized = False
			now = time.time()
			if proba > CONSTANTS.CONFIDENCE_TO_UNKNOWN_FACES:
				name = text + "-" + name
			else:
				self.unknowns_count += 1
				name = text + str(self.unknowns_count)

		y = startY - 10 if startY - 10 > 10 else startY + 10
		cv2.rectangle(frame, (startX, startY), (endX, endY),
				color, 2)
		cv2.putText(frame, text, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		return {"name": name, "face": face, "confidence": proba, "recognized": recognized}
		