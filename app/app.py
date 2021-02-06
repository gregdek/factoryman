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
  r.set(gameid+":Wcount", "1")
  r.set(gameid+":W:0:active", "yes")
  r.set(gameid+":W:0:x", "0")
  r.set(gameid+":W:0:y", "0")
  r.set(gameid+":W:0:dx", "0")
  r.set(gameid+":W:0:dy", "0")
  r.sadd(gameid, gameid+":cash", gameid+":Wcount", gameid+"W:0:active")
  r.sadd(gameid, gameid+"W:0:x", gameid+":W:0:y")
  r.sadd(gameid, gameid+"W:0:dx", gameid+"W:0:dy")

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
      returnstr += "---"
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
    if r.get(gameid+"W:"+wid+":active") == "yes":
      # Are x and y in bounds?
      if (0<=int(dx)<=9) and (0<=int(dy)<=9): 
        # Valid. Set destination and last command.
        r.set(gameid+"W:"+wid+":dx", dx)
        r.set(gameid+"W:"+wid+":dy", dy)
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
