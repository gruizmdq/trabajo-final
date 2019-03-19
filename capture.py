# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
import os


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()


ap.add_argument("-o", "--output", required=True,
	help="Name of the person")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

#PATHS
MODEL_PATH = 'face_detection_model/'
MODEL_PROTOTXT = 'deploy.prototxt'
MODEL_PRE_TRAINEED = 'res10_300x300_ssd_iter_140000.caffemodel'

DATA_SET_PATH = 'dataset/'
OUTPUT_PATH = DATA_SET_PATH + args["output"] + "/"


quantity_photos = 0

#If OUTPUT_PATH exists, add total number of files to i.
if os.path.isdir(OUTPUT_PATH):
    quantity_photos = len(os.listdir(OUTPUT_PATH))
else:
    os.mkdir(OUTPUT_PATH)

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(MODEL_PATH+MODEL_PROTOTXT, MODEL_PATH+MODEL_PRE_TRAINEED)

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
 
	# grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

		# loop over the detections
    for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the
		# prediction
        confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
        if confidence < args["confidence"]:
            continue

		# compute the (x, y)-coordinates of the bounding box for the
		# object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        quantity_photos += 1
        img_item =  OUTPUT_PATH + str(quantity_photos) + ".png"        
        cv2.imwrite(img_item, frame)

		# draw the bounding box of the face along with the associated
		# probability
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        font = cv2.FONT_HERSHEY_SIMPLEX
        stroke = 2
        cv2.rectangle(frame, (startX, startY), (endX, endY),
		    (0, 0, 255), 2)
        cv2.putText(frame, text, (startX, y), font, .5, (0, 0, 255), stroke, cv2.LINE_AA)

        cv2.putText(frame, str(quantity_photos)+" fotos", (25,25), font, .5, (0, 0, 255), stroke, cv2.LINE_AA)

		# show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
os.system("python3 extract_embeddings.py")
os.system("python3 train_model.py")
