import os
from flask import Flask, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from pymongo import MongoClient

from PIL import Image, ExifTags

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient()
db = client.fitnessDB
userCollection = db.users
attachmentCollection = db.attachments
workoutCollection = db.workouts

UPLOAD_FOLDER = '/home/zack/jhu/agile/fitness-progress/static/pictures'
PICTURE_FOLDER = '/static/pictures'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#Login and logout routes
@app.route('/')
def basePage():
  if ('username' in session):
    return render_template('home.html', user=session['username'])
  else:
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    if (loginUser(request.form['username'], request.form['password'])):
      session['username'] = request.form['username']
      return redirect('/')
    else:
      return render_template('login.html', message="Unsuccesful login. Please Try Again")
  else:
    return render_template('login.html')

@app.route('/logout')
def logout():
  session.pop('username', None)
  return render_template('login.html')

@app.route('/pictures', methods=['GET', 'POST'])
def pictures():
  if request.method == 'POST':
    if 'file' not in request.files:
      return render_template('pictures.html', message="No File Found. Please Try Again", success=0)
    file = request.files['file']
    if file.filename == '':
      return render_template('pictures.html', message="No File Found. Please Try Again", success=0)
    if file and allowed_file(file.filename):
      filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
      file.save(filepath)
      rotateImage(filepath)
      location = os.path.join(PICTURE_FOLDER, secure_filename(file.filename))
      attachmentCollection.insert_one(
        {
          "name": file.filename,
          "location": location,
          "date": request.form['date'],
          "angle": request.form['angle'],
          "weight": request.form['weight'],
          "notes": request.form['notes'],
          "user": session['username']
        }
      )
      picList = list(attachmentCollection.find({"user": session['username']}).sort("date", 1))
      return render_template('pictures.html', message="Upload Succesful", success=1, picDict=makePictureDict(picList))
  else:
    picList = list(attachmentCollection.find({"user": session['username']}).sort("date", 1))
    return render_template('pictures.html', picDict=makePictureDict(picList))

@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
  if request.method == 'POST':
    if request.form['type'] == 'other':
      workoutType =  request.form['otherType']
    else:
      workoutType = request.form['type']
    workoutCollection.insert_one(
      {
        "type": workoutType,
        "date": request.form['date'],
        "notes": request.form['notes'],
        "user": session['username']
      }
    )
    workoutList = list(workoutCollection.find({"user": session['username']}).sort("date", 1))
    return render_template('workouts.html', message="Succesful", success=1, workoutList=workoutList)
  else:
    workoutList = list(workoutCollection.find({"user": session['username']}).sort("date", 1))
    return render_template('workouts.html', workoutList=workoutList)

#Helper functions. TODO move to utils
def loginUser(username, password):
  user = userCollection.find_one({"username": username})
  if (user == None):
    return False

  return (user['password'] == password)

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def makePictureDict(picList):
  picDict = {}
  for pic in picList:
    if pic['date'] in picDict:
      picDict[pic['date']][pic['angle']] = pic
    else:
      picDict[pic['date']] = {}
      picDict[pic['date']]['front'] = {}
      picDict[pic['date']]['back'] = {}
      picDict[pic['date']]['side'] = {}
      picDict[pic['date']][pic['angle']] = pic

  return picDict

def rotateImage(filepath):
  try:
    image=Image.open(filepath)
    for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation]=='Orientation':
        break
    exif=dict(image._getexif().items())

    if exif[orientation] == 3:
      image=image.rotate(180, expand=True)
    elif exif[orientation] == 6:
      image=image.rotate(270, expand=True)
    elif exif[orientation] == 8:
      image=image.rotate(90, expand=True)
    image.save(filepath)
    image.close()

  except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexi
    print("HERE");
    pass
