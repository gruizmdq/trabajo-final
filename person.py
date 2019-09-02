import os
import cv2
from datetime import datetime, timedelta
import constants as CONSTANTS
import json

class Person(object):
    
    id_count = 0
    
    #def __init__(self, confidence, name, face, recognized):  
    def __init__(self, camera_id, centroid, face, filename, time_detection):  
        self.id = Person.id_count
        Person.id_count += 1 
        self.centroid = centroid
        self.face = face
        self.name = "name"
        self.confidence = 0
        self.camera = camera_id
        self.recognized = 2
        self.thumb = ""
        self.set_thumb(face)
        self.set_time()
        self.filename = filename
        self.time_detection_video = time_detection

    def set_thumb(self, face):
        if self.thumb == "":
            files = list(os.listdir(CONSTANTS.FACES_PATH))
            filename = '1'
            if files:
                filenames = []
                for f in files:
                    filenames.append(int(f.strip('.')[0]))
                filenames = sorted(filenames)
                filename = filenames[-1] + 1
            self.thumb = str(filename)+".jpg"
        cv2.imwrite(CONSTANTS.FACES_PATH+self.thumb, face)
        
    
    def set_time(self):
        now = datetime.now() + timedelta(hours=2)
        self.time = now.strftime("%A %d %B %Y %I:%M:%S%p")
        
    def set_recognized(self, confidence):
        if confidence > CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
            self.recognition = 0
        else: 
            if confidence > CONSTANTS.CONFIDENCE_TO_UNKNOWN_FACES:
                self.recognition = 1
            else:
                 self.recognition = 2

    def toJSON(self):
        return {"name": self.name, "confidence": self.confidence, "recognized": self.recognized, "camera": self.camera, "thumb": self.thumb, "date": self.time, "filename": self.filename, "time_video": self.time_detection_video}
