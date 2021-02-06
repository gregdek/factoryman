#!/usr/local/bin/python3

from flask import Flask
from flask import render_template
from flask import Response
import pprint
import uuid
import redis
import sys

app = Flask(__name__)
app.debug = True
pp = pprint.PrettyPrinter(indent=4)

redis_host = "localhost"
redis_port = 6379
redis_password = ""
r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

@app.route('/')
def index():
  return 'This will point to a link to start a new game!'

@app.route('/newgame')
def newgame():
  gameid = str(uuid.uuid4())
  # New game. 
  # "set" starting values, and "sadd" values to Redis set for gameid.
  # TODO: put these into a newworker function.
  r.set(gameid+":cash", "5000")
  r.set(gameid+":wcount", "1")
  r.set(gameid+":active:0", "yes")
  r.set(gameid+":x:0", "0")
  r.set(gameid+":y:0", "0")
  r.set(gameid+":dx:0", "0")
  r.set(gameid+":dy:0", "0")
  r.sadd(gameid, gameid+":cash", gameid+":wcount", gameid+":active:0")
  r.sadd(gameid, gameid+":x:0", gameid+":y:0")
  r.sadd(gameid, gameid+":dx:0", gameid+":dy:0")

  # FIXME: just return the newgameid for now, but figure out how to 
  # return game state also
  return(gameid)

@app.route('/state/<gameid>')
def state(gameid):
  gamestatestr = ''
  gamestateset = r.smembers(gameid)
  for gamestateitem in gamestateset:
    gamestatestr += "<p>"
    gamestatestr += str(gamestateitem)
    gamestatestr += str(r.get(gamestateitem))
    gamestatestr += "</p>"
  #print(gamestatestr, file=sys.stderr)
  return gamestatestr, {'Content-Type': 'text/html'}

@app.route('/command')
def command():
  return('This processes a command and returns the new state of the game!')


