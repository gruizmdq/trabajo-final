import cv2
from datetime import datetime, timedelta

class Person(object):
    
    id_count = 0
    
    #def __init__(self, confidence, name, face, recognized):  
    def __init__(self, centroid, face):  
        self.id = Person.id_count
        Person.id_count += 1 
        self.centroid = centroid
        self.face = face
        self.name = "name"
        self.confidence = 0
        #if "unknown" not in name: # Used to include unknown-N from Database
        #    self.name = name
        #else:
        #    self.name = "unknown"
        #self.name = name
        #self.recognized = recognized
        #self.confidence = confidence
        #ret, jpeg = cv2.imencode('.jpg', face)
        #self.thumb = jpeg.tostring()
        cv2.imwrite('static/'+str(self.id)+".jpg", face[0])
        self.set_time()

    def set_thumb(self, face):
        ret, jpeg = cv2.imencode('.jpg', face)
        self.thumb = jpeg.tostring()
        cv2.imwrite('static/'+str(self.id)+".jpg", face)
    
    def set_time(self):
        now = datetime.now() + timedelta(hours=2)
        self.time = now.strftime("%A %d %B %Y %I:%M:%S%p")
        

