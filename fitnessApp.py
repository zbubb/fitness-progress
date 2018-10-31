from flask import Flask, render_template, request, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient()
db = client.fitnessDB
userCollection = db.users

#Login and logout routes
@app.route('/')
def basePage():
  return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    if (loginUser(request.form['username'], request.form['password'])):
      session['username'] = request.form['username']
      return 'Success'
    else:
      return render_template('login.html', message="Unsuccesful login. Please Try Again")
  else:
    return render_template('login.html')

@app.route('/logout')
def logout():
  session.pop('username', None)
  return render_template('login.html')

#Helper functions. TODO move to utils
def loginUser(username, password):
  user = userCollection.find_one({"username": username})
  if (user == None):
    return False

  return (user['password'] == password)
