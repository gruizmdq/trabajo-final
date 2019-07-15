import time
from datetime import date, datetime
from flask import Flask, Response, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send, emit
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from flask_login import  LoginManager, UserMixin, login_required, login_user, logout_user 
from flask_bcrypt import Bcrypt
from functools import wraps
from camera import Camera
from system import System
from models import User
import constants as CONSTANTS
import json
import psutil
import cv2
import threading

################################
  #DEFINE CONSTANTS
###############################
system = System()
camera = Camera(0, system)
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

#MAIL CONFIG
app.config['MAIL_SERVER']='localhost'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = 'gruiz@localhost'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TSL'] = False
mail = Mail(app)

#DATABASE CONFIG
app.config["MONGO_URI"] = CONSTANTS.DATABASE_HOST+CONSTANTS.DATABASE_NAME
app.config["MONGO_DBNAME"] = CONSTANTS.DATABASE_NAME
mongo = PyMongo(app)

system.add_camera(camera)
socketio = SocketIO(app)

monitoringThread = threading.Thread()
monitoringThread.daemon = False


#INDEX
@app.route("/")
@login_required
def index():
  return render_template('index.html')


#PEOPLE
@app.route("/people")
@login_required
def people():
  return render_template('people.html')

#CAMERA
@app.route("/cameras")
@login_required
def camera():
  return render_template('cameras.html')


################################
  #LOGIN
###############################
#LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    users = mongo.db.users
    user = users.find_one({'email' : request.form['email']})

    if login_user:
      if bcrypt.check_password_hash(user['password'], request.form['pass']):
        new_user = User(user['email'])
        login_user(new_user)
        next = request.args.get('next')
        if next is not None:
          return redirect(next)
        else:
          return redirect('/')

    return render_template('login.html', error = "error en el login pa")
  return render_template('login.html')

#LOGOUT
@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect('/login')

#REGISTER
#CHEQUEAR ROLES.
@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'POST':
    users = mongo.db.users
    existing_user = users.find_one({'email' : request.form['email']})

    if existing_user is None:
      hashpass = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
      users.insert({'email' : request.form['email'], 'password' : hashpass, 'name': request.form['name'], 'last_name': request.form['last_name'],'house': request.form['house'], 'owner': request.form['owner']})
      session['email'] = request.form['email']
      return redirect(url_for('index'))
    
    return 'That username already exists!'

  return render_template('register.html')




################################
  #SEND MAIL ALERT
###############################
@app.route('/send_mail', methods=['POST'])
def send_mail():
  if request.method == 'POST':
    email = request.args['email']
    text = request.args['text']
    msg = Message("New Detection - " + datetime.now().strftime('%H:%M - %d/%m/%Y '),
                sender="gruiz@localhost",
                recipients=["gruiz@localhost"])
    msg.body = text
    mail.send(msg)
  return '200'



#SHOW VIDEO DETECTION
@app.route("/static/videos/<camid>/<date>/<filename>/<position>")
@login_required
def show_video(camid, date, filename, position):
  url = "/static/videos/"+camid+"/"+date+"/"+filename
  return render_template('video.html', url = url, position = position)



################################
  #STREAMING PROCESSED FRAMES
###############################
def gen(camera):
  """Start processing camera. 
      get_frame will get the frame without drawing. Less information, but speeder
  """
  while True:
    frame = camera.get_jpg_to_stream_proccessed()    # get_jpg_to_stream()  # get_jpg_to_stream_proccessed()    
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # Builds 'jpeg' data with header and payload
      
@app.route('/video_streamer/<id>')
@login_required
def video_streamer(id):
  """
      Stream camera to client.
  """
  return Response(gen(system.cameras[int(id)]),
                  mimetype='multipart/x-mixed-replace; boundary=frame') # A stream where each part replaces the previous part the multipart/x-mixed-replace content type must be used.


################################
  #STREAMING UNPROCESSED FRAMES
###############################
def gen2(camera):
  """Start processing camera. 
      get_frame will get the frame without drawing. Less information, but speeder
  """
  while True:
    frame = camera.get_jpg_to_stream()    # get_jpg_to_stream()  # get_jpg_to_stream_proccessed()    
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # Builds 'jpeg' data with header and payload

@app.route('/video_streamer2/<id>')
@login_required
def video_streamer2(id):
  """
      Stream camera to client.
  """
  return Response(gen2(system.cameras[int(id)]),
                  mimetype='multipart/x-mixed-replace; boundary=frame') # A stream where each part replaces the previous part the multipart/x-mixed-replace content type must be used.


#GET ALL DETECTIONS.
@app.route("/get_faces")
@login_required
def get_faces():
  prediction_array = []
 # for key, prediction in camera.detected_people.items():
  arr = mongo.db['detections'].find({})
  for i in arr:
    prediction_array.append({'name': i['name'], 'confidence': "{:.2f}".format(i['confidence']*100), 'time': i['date'], 'recognized': True, 'thumb': i['thumb'], 'camera': i['camera'], 'filename': i['filename'], 'time_video': i['time_video']})
  return json.dumps(prediction_array)

#REMOVE FACE FROM DETECTIONS DATABASE
@app.route('/remove_face', methods=['POST'])
@login_required
def remove_face():
  cameras = request.form['camera']
  thumb = request.form["thumb"]
  name = request.form["name"]
  date = request.form["date"]
  if system.remove_prediction(cameras, thumb, name, date):
    return '200'
  else:
    return '500'

#SEND SOCKET THERE IS NEW DETECTION
@app.route('/new_detection', methods=['POST'])
def new_detection():
  socketio.emit('get_faces', get_faces() ,namespace='/system')
  return Response('200', status=200, mimetype='application/json')



################################
  #SYSTEM STATS
###############################
def system_stats():
  while True:
    camerasFPS = []
    for camera in system.cameras:
        camerasFPS.append(camera.fps)
    systemState = {'cpu':cpu_usage(),'memory':memory_usage(), 'camerasFPS': camerasFPS}
    socketio.emit('system_monitoring', json.dumps(systemState) ,namespace='/system')
    time.sleep(5)
def cpu_usage():
  psutil.cpu_percent(interval=1, percpu=False) #ignore first call - often returns 0
  time.sleep(0.12)
  cpu_load = psutil.cpu_percent(interval=1, percpu=False)
  return cpu_load  
def memory_usage():
  mem_usage = psutil.virtual_memory().percent
  return mem_usage 


################################
  #NEW CLIENT
###############################
@socketio.on('connect', namespace='/system') 
def connect(): 
  print("***********************")
  print("*** CLIENT CONNECTED **")
  print("***********************")

  global monitoringThread
  socketio.emit('get_faces', get_faces(), namespace='/system')

  if not monitoringThread.isAlive():
    monitoringThread = threading.Thread(name='stats_process_thread_',target= system_stats, args=())
    monitoringThread.start()


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
  return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(email):
  return User(email)


################################
  #START THE APP
###############################
if __name__ == "__main__":
  app.secret_key = 'mysecret'
  socketio.run(app, host='0.0.0.0', debug=False, use_reloader=False) 

