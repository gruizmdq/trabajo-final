# import the necessary packages
from imutils.video import FPS
import cv2
from recognize_video import FaceRecognizer
from detector import FaceDetector
from camera import Camera

class System(object):
    """
    System: main class. 
    Everything go across this object.
    """
    def __init__(self):
        self.recognizer = FaceRecognizer()
        self.detector = FaceDetector(self)
        self.cameras = []
        self.cameras.append(Camera())
        self.start()

    def start(self):

        for camera in self.cameras:
            
            camera.init()
            # start the FPS throughput estimator
            fps = FPS().start()
            while True:
                frame = camera.get_frame()

                #Detection, then detector will call recognizer.
                frame, faces = self.detector.detect(frame)
                #Recognition
                if not (faces is None):
                    for face in faces:
                        try:
                            #face, frame, startX, startY, endX, endY
                            self.recognizer.make_prediction(face[0], frame, face[1], face[2], face[3], face[4])
                        except Exception as e:
                            print(str(e))
                            
                cv2.imshow("Frame", frame)

                # update the FPS counter
                fps.update()

                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break
            # stop the timer and display FPS information
            fps.stop()
            # do a bit of cleanup
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            cv2.destroyAllWindows()
            camera.stop()
        
System()
        