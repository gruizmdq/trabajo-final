# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from scipy.spatial import distance as dist
from collections import OrderedDict
from person import Person
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
        #All detected people
        self.detected_people = {}
        #All recognized people
        self.recognized_people = {}
        #Unknown detections.
        self.unknown_people = {}
        #People who was detected and now it is not.\
        self.people_disappeared = {}
        self.readingThread = threading.Thread(name='reading_thread',target=self.start_read)
        self.readingThread.daemon = True
        self.readingThread.start()

        self.frames_to_delete_detection = 50

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

    def remove_face(self, name):
        self.recognized_people.pop(name)
        return 'true'

    def update_people(self, people):
        #If len = 0, no people was detected.
        if (len(people) == 0):
            #put the items in list for runtime bug. (dictionary changed size during iteration)
            for person_id in list(self.people_disappeared.keys()):
                self.people_disappeared[person_id] += 1
                
                if self.people_disappeared[person_id] > self.frames_to_delete_detection:
                    self.delete_person(person_id)

			# return early as there are no centroids or tracking info
			# to update
            return self.detected_people
        
        # initialize an array of input centroids for the current frame
        frame_centroids = np.zeros((len(people), 2), dtype="int")
        faces_coordenates = []
		# loop over the bounding box rectangles
        for (i, (face, startX, startY, endX, endY)) in enumerate(people):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            frame_centroids[i] = (cX, cY)
            faces_coordenates.append((face, startX, startY, endX, endY))
        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.detected_people) == 0:
            for i in range(0, len(frame_centroids)):
                self.add_detected_person(Person(frame_centroids[i], faces_coordenates[i]))

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            list_person_id = list(self.detected_people.keys())
            list_person = list(self.detected_people.values())
            list_person_centroid = list()
            for person in list_person:
                list_person_centroid.append(person.centroid)
            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid

            D = dist.cdist(np.array(list_person_centroid), frame_centroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so detected_people[person_id]that the row
            # with the smallest value as at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            used_rows = set()
            used_cols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in used_rows or col in used_cols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                person_id = list_person_id[row]
                self.detected_people[person_id].centroid = frame_centroids[col]
                self.detected_people[person_id].face = faces_coordenates[col]
                self.people_disappeared[person_id] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                used_rows.add(row)
                used_cols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unused_rows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    person_id = list_person_id[row]
                    self.people_disappeared[person_id] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.people_disappeared[person_id] > self.frames_to_delete_detection:
                        self.delete_person(person_id)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as aregister trackable object
            else:
                for col in unused_cols:
                    self.add_detected_person(Person(frame_centroids[col], faces_coordenates[col]))

        # return the set of trackable objects
        return self.detected_people

    def delete_person(self, person_id):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
        del self.detected_people[person_id]
        del self.people_disappeared[person_id]

    def add_detected_person(self, person):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.detected_people[person.id] = person
        self.people_disappeared[person.id] = 0