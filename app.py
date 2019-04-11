from flask import Flask, Response, render_template, request, redirect
from flask_socketio import SocketIO, send, emit
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from camera import Camera
from system import System
import json
import cv2

system = System()
camera = Camera(0)
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/security_system"
bcrypt = Bcrypt()
mongo = PyMongo(app)
system.add_camera(camera)
socketio = SocketIO(app)

@app.route("/")
def hello():
  return render_template('dashboard.html')

@app.route('/create_user', methods=['GET','POST'])
def create_user():
    if request.method == 'POST':
      print(bcrypt.generate_password_hash(request.form['password']))
      username = request.form['username']
      password = request.form['password']
      print(username)
      print(password)
      return 'true'
        #session.pop('user',None) # Drops session everytime user tries to login
        #if request.form['username'] != 'admin' or request.form['password'] != 'admin':
         #   error = 'Invalid username or password. Please try again'
        #else:
           # session['user'] = request.form['username']
         #   return redirect(url_for('home'))
    else:
      return render_template('create_user.html')

@app.route("/predictions")
def predictions():
  prediction_array = []
  for key, prediction in camera.recognized_people.items():
    print(prediction.name +" "+ str(prediction.confidence) + str(prediction.recognized))
    prediction_array.append({'name': prediction.name, 'confidence': "{:.2f}".format(prediction.confidence*100), 'time': prediction.time, 'recognized': prediction.recognized, 'id': prediction.id})
  return render_template('predictions2.html', predictions = prediction_array)

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

  

@app.route("/get_faces")
def get_faces():
  prediction_array = []
 # for key, prediction in camera.detected_people.items():
  if system.test_until_database_detections.items() is not None:
    for key, prediction in system.test_until_database_detections.items():
      prediction_array.append({'name': prediction.name, 'confidence': "{:.2f}".format(prediction.confidence*100), 'time': prediction.time, 'recognized': True, 'id': prediction.id, 'camera': camera.id})
  return json.dumps(prediction_array)

@app.route('/remove_face', methods=['POST'])
def remove_face():
  #system.remove_prediction(request.form['id'])  
  #print(request.form['id'])
  #return system.cameras[request.form['camera']].remove_face(request.form['id'])
  return camera.remove_face(request.form['name'])
  #return render_template('login.html', error = error)

@socketio.on('connect', namespace='/system') 
def connect(): 
    #print "\n\nclient connected\n\n"
    print("client connected")
    socketio.emit('test', get_faces(), namespace='/system')


if __name__ == "__main__":
  #app.run()
  socketio.run(app, host='0.0.0.0', debug=False, use_reloader=False) 