# import the necessary packages
from imutils.video import FPS
import cv2
from recognize_video import FaceRecognizer
from detector import FaceDetector
import constants as CONSTANTS
from camera import Camera
import threading
from person import Person

class System(object):
    """
    System: main class. 
    Everything go across this object.
    """
    def __init__(self):
        self.recognizer = FaceRecognizer(self)
        self.detector = FaceDetector(self)
        self.cameras = []
        self.camerasThreads = []
        self.predictions = []
        #self.start()
        #self.add_camera(Camera())

    
    def add_camera(self, camera):
        """
        Add a camera to the system and it also creates a new thread.
        """
        self.cameras.append(camera)
        t = threading.Thread(target=self.process, args=(self.cameras[-1],))
        self.camerasThreads.append(t)
        t.start()

    def remove_camera(self, id):
        """
        Remove the camera from the camera array and change the status to terminate the thread execution
        """
        camera = self.cameras.pop(id)
        camera.processing_on = False
        self.camerasThreads.pop(id)

    def process(self, camera):

        # start the FPS throughput estimator
        fps = FPS().start()

        while camera.processing_on:
            frame = camera.get_frame()

            #Detection
            frame, faces = self.detector.detect(frame)
            #Recognition

            if not (faces is None):
                for face in faces:
                    try:
                        #face, frame, startX, startY, endX, endY
                        prediction = self.recognizer.make_prediction(face[0], frame, face[1], face[2], face[3], face[4])
                        if not (prediction is None):
                            #Already have recognition from this face
                            if prediction['name'] in camera.recognized_people:
                                if prediction['confidence'] > camera.recognized_people[prediction['name']].confidence:
                                    camera.recognized_people[prediction['name']].confidence = prediction['confidence']

                                    if prediction['confidence'] > CONSTANTS.CONFIDENCE_TO_ACCEPT_RECOGNITION:
                                        camera.recognized_people[prediction['name']].name = prediction['name']
                                    
                                    camera.recognized_people[prediction['name']].set_thumb(face)
                                    camera.recognized_people[prediction['name']].set_time()
                            else:
                                camera.recognized_people[prediction["name"]] = Person(prediction['confidence'], prediction['name'], prediction['face'], prediction['recognized'])
                    
                    except Exception as e:
                        print(str(e))
            
            
            


            #frame = cv2.resize(frame,None,fx=0.5,fy=0.5)     
            # Save processed frame to stream later      
            camera.processedFrame = frame
            cv2.imshow("Frame", frame)

            # update the FPS counter
            fps.update()

            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                #break
                self.remove_camera(camera.id)

        # stop the timer and display FPS information
        fps.stop()
        # do a bit of cleanup
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        #cv2.destroyAllWindows()
        #camera.stop()

    def add_prediction(self, person):
        self.predictions.append(person)

        