import os
import time
from flask import Flask, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient()
db = client.fitnessDB
userCollection = db.users
attachmentCollection = db.attachments

UPLOAD_FOLDER = '/home/zack/jhu/agile/fitness-progress/static/pictures'
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
      filepath = os.path.join(UPLOAD_FOLDER,secure_filename(file.filename))
      file.save(filepath)
      attachmentCollection.insert_one(
        {"name": file.filename, "location": filepath, "date": time.time(), "angle": request.form['angle'], "weight": request.form['weight'], "notes": request.form['notes'], "user": session['username']}
      )
      return render_template('pictures.html', message="Upload Succesful", success=1)
  else:
    return render_template('pictures.html')

#Helper functions. TODO move to utils
def loginUser(username, password):
  user = userCollection.find_one({"username": username})
  if (user == None):
    return False

  return (user['password'] == password)

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
