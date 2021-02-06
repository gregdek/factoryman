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
  return gameid, {'Content-Type': 'text/html'}

@app.route('/state/<gameid>')
def state(gameid):
  returnstr = ''
  if r.exists(gameid):
    gamestateset = r.smembers(gameid)
    for gamestateitem in gamestateset:
      returnstr += "<p>"
      returnstr += str(gamestateitem)
      returnstr += str(r.get(gamestateitem))
      returnstr += "</p>"
      #print(gamestatestr, file=sys.stderr)
  else:
    returnstr = 'Error: gameid not found'
  return returnstr, {'Content-Type': 'text/html'}

@app.route('/command/<commandid>/<gameid>')
def command(commandid, gameid):
  returnstr = ''
  # First we process the gameid. Is it valid?
  
  # First we process the command.
  # Is it a move?
  if 'wait' in commandid:
    # Do nothing, set lastcmd
    r.set(gameid+":lastcmd",commandid)
  elif 'move' in commandid:
    wid=commandid[4]
    dx=commandid[5]
    dy=commandid[6]
    # Is the player active?
    if r.get(gameid+":active:"+wid) == "yes":
      # Are x and y in bounds?
      if (0<=int(dx)<=9) and (0<=int(dy)<=9): 
        # Valid. Set destination and last command.
        r.set(gameid+":dx:"+wid, dx)
        r.set(gameid+":dy:"+wid, dy)
        r.set(gameid+":lastcmd",commandid)
      else:
        returnstr = "ERROR " + commandid + ": invalid xy"
    else:
      returnstr = "ERROR " + commandid + ": worker "+wid+" invalid/inactive" 
  else:
    returnstr = "ERROR: invalid command: " +commandid  
  if not ("ERROR" in returnstr):
    returnstr = commandid+'-->'+gameid
  return returnstr, {'Content-Type': 'text/html'} 
