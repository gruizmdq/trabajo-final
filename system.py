# import the necessary packages
import cv2
import time
import os
from datetime import date
from recognize_video import FaceRecognizer
from detector import FaceDetector
import constants as CONSTANTS
from camera import Camera
import threading
from person import Person
from persistence import Persistence
import requests

class System(object):
    """
    System: main class. 
    Everything go across this object.
    """
    def __init__(self):
        self.recognizer = FaceRecognizer(self)
        self.detector = FaceDetector()
        self.detection_lock = threading.Lock()
        self.prediction_lock = threading.Lock()
        self.cameras = {}
        self.camerasThreads = {}
        self.test_until_database_detections = {}
        #self.start()
        #self.add_camera(Camera())
        self.notifications = Persistence.get_notifications()
        self.get_cameras()
        

    def get_cameras(self):
        cameras = Persistence.get_cameras()
        for camera in cameras:
            new_camera = Camera(camera['url'], camera['id_camera'], camera['name'], self)
            self.append_camera(new_camera)

    #If camera_id exist, camera is already in database. So its not necessary call DB. 
    # This implementation is to can stop camera, capture new people and restart camera again.
    def add_camera(self, url, name, camera_id = None):
        if camera_id is not None: 
            camera = Camera(url, camera_id, name, self)
            self.append_camera(camera)
            return '200'

        result = Persistence.add_camera(url, name)

        if result is False:
            print(result)
        else:
            if type(result) is str:
                return result
            
            else:
                camera = Camera(url, result['id_camera'], name, self)
                self.append_camera(camera)
                return '200'
            

    def append_camera(self, camera):
        """
        Append a camera to the system and it also creates a new thread.
        """
        self.cameras.update({camera.id : camera})
        t = threading.Thread(target=self.process, args=(camera,))
        self.camerasThreads.update({camera.id: t})
        t.start()

    def remove_camera(self, id):
        """
        Remove the camera from the camera array and change the status to terminate the thread execution
        """
        camera = self.cameras.pop(id)
        camera.processing_on = False
        t = self.camerasThreads.pop(id)
        camera.stop()
        return True

    def process(self, camera):

        # start the FPS throughput estimator

        FPScount = 0 # Used to calculate frame rate at which frames are being processed
        FPSstart = time.time()

        #Check directory for recording
        path = CONSTANTS.VIDEO_RECORDING_PATH + str(camera.id) + '/'

        if os.path.isdir(path) == False:
            os.mkdir(path)

        path = path + date.today().strftime("%Y_%m_%d")
        i = 1

        if os.path.isdir(path) == False:
            os.mkdir(path)
        else: 
            i = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]) + 1

        camera.filename = path + "/" + str(i) + ".webm"
        fourcc = cv2.VideoWriter_fourcc(*'VP80')
        out = cv2.VideoWriter(camera.filename, fourcc, 15.0, (640,480), True)

        #Time to know recording time
        #crotada que agrega 1/3 de segundo para saber en que parte del video esta la deteccion
        camera.time_recording = 0

        while camera.processing_on:

            frame = camera.get_frame()
            if frame is not None:
                camera.tempFrame = frame

                out.write(frame)

                if FPScount == 5:
                    #adding 1/3s (Writer is 15FPS, so if it counted 5FPS => 1/3 s.)
                    camera.time_recording = camera.time_recording + 1/3
                    camera.fps = 5/(time.time() - FPSstart)
                    FPSstart = time.time()
                    FPScount = 0

                FPScount += 1
                cv2.putText(frame, "[INFO] FPS: {:.2f}".format(camera.fps), (25, 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                #Detection
            # with self.detection_lock:
                frame, faces = self.detector.detect(frame)
                
                people = camera.update_people(faces)
                print(str(camera.id), ' ****************' , len(faces), len(people))
                
                if not (people is None):
                    for person in people.values():
                        try:
                            face = person.face
                            text = "ID {} - {} - {}".format(person.id, person.name, person.confidence)
                            cv2.putText(frame, text, (person.centroid[0] - 10, person.centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            cv2.circle(frame, (person.centroid[0], person.centroid[1]), 4, (0, 255, 0), -1)
                        
                            #Recognition 
                            if person.confidence < CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
                                #with self.prediction_lock:
                                print('PREDICTION ****************' )

                                prediction = self.recognizer.make_prediction(face[0])
                                
                                if not (prediction is None or prediction['confidence'] < person.confidence):
                                    person.set_recognized(prediction['confidence'])
                                    person.name = prediction['name']
                                    person.confidence = prediction['confidence']
                                    person.set_thumb(face[0])
                                    self.test_until_database_detections[person.id] = person
                                    self.send_notification(person)
                        except Exception as e:
                            print(str(e))
                #cv2.imshow("Camera " + str(camera.id), frame)
                
                
                
                


                #frame = cv2.resize(frame,None,fx=0.5,fy=0.5)     
                # Save processed frame to stream later      
                camera.processedFrame = frame
                #cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    #break
                    self.remove_camera(camera.id)

        #cv2.destroyAllWindows()
        #camera.stop()

    def add_detection_database(self, person):
        if Persistence.insert_detection(person.toJSON()):
            URL = "http://0.0.0.0:5000/new_detection"
            r = requests.post(url = URL) 
            # extracting data in json format 
            #data = r.json()
            #print(data)

    def get_fps(self, camera):
        return camera.fps

    def send_notification(self, person):
        if self.notifications[person.name]:
            notification = self.notifications[person.name]
            URL = "http://0.0.0.0:5000/send_mail"
            for n in notification:
                r = requests.post(url = URL, params = n) 
            
            # extracting data in json format 
            data = r.json()

    def remove_prediction(self, camera, thumb, name, date):
        path = CONSTANTS.FACES_PATH + thumb
        if os.path.isfile(path):
            os.remove(path)
        return Persistence.remove_prediction(camera, name, date)


    def get_personas(self):
        personas = Persistence.get_personas()
        return personas
