from flask import Flask, Response, render_template
from camera import Camera
from system import System
import cv2

system = System()
camera = Camera(0)
app = Flask(__name__)
system.add_camera(camera)

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/predictions")
def predictions():
  prediction_array = []
  for key, prediction in camera.recognized_people.items():
    print(prediction)
    prediction_array.append({'name': prediction.name, 'confidence': "{:.2f}".format(prediction.confidence*100), 'time': prediction.time, 'recognized': prediction.recognized})
  return render_template('predictions.html', predictions = prediction_array)

def gen(camera):
    """Start processing camera. 
        get_frame will get the frame without drawing. Less information, but speeder
    """
    while True:
      frame = camera.get_jpg_to_stream_proccessed()    # get_jpg_to_stream()  # get_jpg_to_stream_proccessed()    
      yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # Builds 'jpeg' data with header and payload

        
#@app.route('/video_streamer/<camNum>')
@app.route('/video_streamer/<id>')
def video_streamer(id):
    """
        Stream camera to client.
    """
    return Response(gen(system.cameras[int(id)]),
                    mimetype='multipart/x-mixed-replace; boundary=frame') # A stream where each part replaces the previous part the multipart/x-mixed-replace content type must be used.

  


def gen2(camera):
    """Start processing camera. 
        get_frame will get the frame without drawing. Less information, but speeder
    """
    while True:
      frame = camera.get_jpg_to_stream()    # get_jpg_to_stream()  # get_jpg_to_stream_proccessed()    
      yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # Builds 'jpeg' data with header and payload

        
#@app.route('/video_streamer2/<camNum>')
@app.route('/video_streamer2/<id>')
def video_streamer2(id):
    """
        Stream camera to client.
    """
    return Response(gen2(system.cameras[int(id)]),
                    mimetype='multipart/x-mixed-replace; boundary=frame') # A stream where each part replaces the previous part the multipart/x-mixed-replace content type must be used.

  
if __name__ == "__main__":
  app.run()