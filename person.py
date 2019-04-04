import cv2
from datetime import datetime, timedelta

class Person(object):
    
    id_count = 0
    
    def __init__(self, confidence, name, face, recognized):  

        if "unknown" not in name: # Used to include unknown-N from Database
            self.name = name
        else:
            self.name = "unknown"
        self.recognized = recognized
        self.id = Person.id_count
        self.confidence = confidence
        Person.id_count += 1 
        now = datetime.now() + timedelta(hours=2)
        ret, jpeg = cv2.imencode('.jpg', face)
        self.thumb = jpeg.tostring()
        self.time = now.strftime("%A %d %B %Y %I:%M:%S%p")

    def set_thumb(self, face):
        ret, jpeg = cv2.imencode('.jpg', face)
        self.thumb = jpeg.tostring()
    
    def set_time(self):
        self.time = now.strftime("%A %d %B %Y %I:%M:%S%p")
        

