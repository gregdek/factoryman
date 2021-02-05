from flask import Flask

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/greet')
def say_hello():
  return 'Hello from Server'
