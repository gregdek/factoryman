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
  r.set(gameid+":w:count", "1")
  r.set(gameid+":w:0:active", "yes")
  r.set(gameid+":w:0:x", "0")
  r.set(gameid+":w:0:y", "0")
  r.set(gameid+":w:0:dx", "0")
  r.set(gameid+":w:0:dy", "0")
  r.sadd(gameid, gameid+":cash", gameid+":w:count", gameid+":w:0:active")
  r.sadd(gameid, gameid+":w:0:x", gameid+":w:0:y")
  r.sadd(gameid, gameid+":w:0:dx", gameid+":w:0:dy")

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
  # Command triggers the game and, on accepting
  # a valid command, then triggers the game loop.

  # PROCESS COMMAND
  # Is it a wait? If so, do nothing but set lastcmd.
  if 'wait' in commandid:
    # Do nothing, set lastcmd
    r.set(gameid+":lastcmd",commandid)
  # Is it a move? Make sure it's valid, otherwise error.
  elif 'move' in commandid:
    wid=commandid[4]
    dx=commandid[5]
    dy=commandid[6]
    # Is the player active?
    if r.get(gameid+":w:"+wid+":active") == "yes":
      # Are x and y in bounds?
      if (0<=int(dx)<=9) and (0<=int(dy)<=9): 
        # Valid. Set destination and last command.
        r.set(gameid+":w:"+wid+":dx", dx)
        r.set(gameid+":w:"+wid+":dy", dy)
        r.set(gameid+":lastcmd",commandid)
      else:
        returnstr = "ERROR " + commandid + ": invalid xy"
    else:
      returnstr = "ERROR " + commandid + ": worker "+wid+" invalid/inactive" 
  else:
    returnstr = "ERROR: invalid command: " +commandid  

  # GAME LOOP
  # OK, commands have been processed. If not error has
  # been found in the command, run the game loop.
  if not ("ERROR" in returnstr):
    
    # First, build map for collision detection and lists for iteration.
    w = 0
    # I'm sure there's a better way to do this, but this is comprehensible:
    gamemap=[
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
      ['__','__','__','__','__','__','__','__','__','__'],
    ]
    # We will keep the gamemap simple, because when paired with
    # the game status, client comprehension should be easy
    while w < int(r.get(gameid+":w:count")):
      wx = int(r.get(gameid+":w:"+str(w)+":x"))
      wy = int(r.get(gameid+":w:"+str(w)+":y"))
      if r.exists(gameid+":w:cid"):
        gamemap[wx][wy]="wc"
      elif r.exists(gameid+":w:mid"):
        gamemap[wx][wy]="wm"
      else:
        gamemap[wx][wy]="w_"
      w+=1 

    # Now iterate through workers and assess attach/detach moves.
    # FIXME.

    # Now iterate through workers and try to move them.
    # reset w to 0 again
    w = 0
    # For each worker:
    while w < int(r.get(gameid+":w:count")):
      wx = int(r.get(gameid+":w:"+str(w)+":x"))
      wy = int(r.get(gameid+":w:"+str(w)+":y"))
      wdx = int(r.get(gameid+":w:"+str(w)+":dx"))
      wdy = int(r.get(gameid+":w:"+str(w)+":dy"))
      wactive = r.get(gameid+":w:"+str(w)+":active")
      if wactive == 'yes' and ((wx!=wdx) or (wy!=wdy)):
        if wx < wdx: wx+=1
        if wx > wdx: wx-=1
        if wy < wdy: wy+=1
        if wy > wdy: wy-=1
        # For now, it's simple: is there a w at target?
        # If so, move. 
        if 'w' not in gamemap[wx][wy]:
          r.set(gameid+":w:"+str(w)+":x",wx)
          r.set(gameid+":w:"+str(w)+":y",wy)
      w+=1
          # FIXME: sort out future logic as below
          # Compute destination square based on DX/DY.
          #   If they are holding nothing:
          #     If "w" not in destination square:
          #       Move them in DB.
          #     Else:
          #       Do not move them.
          #       Warn: can not move w; destination blocked by w
          #   Elif they are attached, i.e. exists w:cid or w:mid:
          #     If "w" in destination square:
          #       Do not move them.
          #       Warn: can not move w; destination blocked by w
          #     Elif "M" or "C" in destination square:
          #       Do not move them.
          #       Throw warning: can not move w holding M/C; blocked by M/C
      #     Else:
      #       Move them in DB.
      #       Move attached C or M in DB.

    # Now process machines and carts.
    # FIXME. 
    
    # Finally, get formatted game state and set returnstr.
    # Return the map first.
    returnstr = '<pre>'
    for gmx in range(0,10):
      for gmy in range(0,10):
        returnstr+=gamemap[gmx][gmy]+" "
      returnstr+="<br/>"
    returnstr+="<br/>"
    returnstr+="</pre>"

    if r.exists(gameid):
      gamestateset = r.smembers(gameid)
      for gamestateitem in gamestateset:
        returnstr += "<p>"
        returnstr += str(gamestateitem)
        returnstr += "---"
        returnstr += str(r.get(gamestateitem))
        returnstr += "</p>"
        #print(gamestatestr, file=sys.stderr)

  return returnstr, {'Content-Type': 'text/html'} 
