#!/usr/local/bin/python3

from flask import Flask
from flask import request
from flask import render_template
from flask import Response
import pprint
import uuid
import redis
import sys
# helper functions like collisions, etc.
import helper

app = Flask(__name__)
app.debug = True
pp = pprint.PrettyPrinter(indent=4)

redis_host = "localhost"
redis_port = 6379
redis_password = ""
r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

#----------------------------------------------------------------------

@app.route('/')
def index():
  return 'To start a new game: <a href="newgame">newgame</a>'

#----------------------------------------------------------------------

@app.route('/newgame')
def newgame():
  gameid = str(uuid.uuid4())
  # New game. 
  # "set" starting values, and "sadd" values to Redis set for gameid.
  # TODO: put these into a newworker function.
  r.set(gameid+":cash", "5000")
  r.set(gameid+":lastcmd", "newgame")
  r.set(gameid+":w:count", "1")
  r.set(gameid+":m:count", "0")
  r.set(gameid+":c:count", "0")
  r.set(gameid+":w:0:active", "yes")
  r.set(gameid+":w:0:x", "0")
  r.set(gameid+":w:0:y", "0")
  r.set(gameid+":w:0:dx", "0")
  r.set(gameid+":w:0:dy", "0")

  # FIXME: just return the newgameid for now, but figure out how to 
  # return game state also
  returnstr = helper.gamemapstr(gameid)
  returnstr += helper.gamestatestr(gameid)
  return returnstr, {'Content-Type': 'text/html'}

#----------------------------------------------------------------------

@app.route('/state/<gameid>')
def state(gameid):
  if r.exists(gameid+":cash"):
    returnstr = helper.gamestatestr(gameid)
  else:
    returnstr = "Error: gameid not found: " + gameid
  return returnstr, {'Content-Type': 'text/html'}

#----------------------------------------------------------------------
@app.route('/command')
def command():
  gameid=request.args.get('g')
  commandid=request.args.get('c')
  valueid=request.args.get('v')
  returnstr = ''
  # Command triggers the game and, on accepting
  # a valid command, then triggers the game loop.

  #-------------------------------------------------------- 
  # PROCESS COMMAND
  #-------------------------------------------------------- 
  # Is it a wait? If so, do nothing but set lastcmd.
  #-------------------------------------------------------- 
  if 'wait' in commandid:
    # Do nothing, set lastcmd
    r.set(gameid+":lastcmd",commandid)
  #-------------------------------------------------------- 
  # Is it a move? Make sure it's valid, otherwise error.
  #-------------------------------------------------------- 
  elif 'move' in commandid:
    wid=valueid[0]
    dx=valueid[1]
    dy=valueid[2]
    # Is the player active?
    active=r.get(gameid+":w:"+wid+":active")
    helper.errlog("wid active? " + active)
    if active == "yes":
      # Are x and y in bounds?
      if (0<=int(dx)<=9) and (0<=int(dy)<=9): 
        # Valid. Set destination and last command.
        r.set(gameid+":w:"+wid+":dx", dx)
        r.set(gameid+":w:"+wid+":dy", dy)
        r.set(gameid+":lastcmd",commandid+valueid)
      else:
        returnstr = "ERROR " + commandid + ": invalid xy"
    else:
      returnstr = "ERROR " + commandid + ": worker "+wid+" invalid/inactive" 
  #-------------------------------------------------------- 
  # Is it a hire? Make sure money is available and no 
  # worker is on 0,0; otherwise error.
  #-------------------------------------------------------- 
  elif 'hire' in commandid:
    # Does the player have enough money?
    cash=int(r.get(gameid+":cash"))
    if cash>=1000:
      # player has enough money, is there a w on 0,0?
      if helper.workerat(gameid,"0","0")=="no":
        helper.addworker(gameid,"0","0")
        r.set(gameid+":cash", str(cash-1000))
      else:
        returnstr = "ERROR " + commandid + ": worker already present at (0,0)"
    else:
      returnstr = "ERROR " + commandid + ": not enough cash, hire costs 1000"
  #-------------------------------------------------------- 
  # Is it a buym? Make sure money is available and no 
  # machine or cart is on 0,0; otherwise error.
  #-------------------------------------------------------- 
  elif 'buym' in commandid:
    # Does the player have enough money?
    cash=int(r.get(gameid+":cash"))
    if cash>=1000:
      # player has enough money, is there an m or c on 0,0?
      if (
        (helper.machineat(gameid,"0","0")=="no") and
        (helper.cartat(gameid,"0","0")=="no")
      ):
        helper.addmachine(gameid,"0","0")
        r.set(gameid+":cash", str(cash-1000))
      else:
        returnstr = "ERROR " + commandid + ": object already present at (0,0)"
    else:
      returnstr = "ERROR " + commandid + ": not enough cash, buym costs 1000"
  #-------------------------------------------------------- 
  # Is it a buyc? Make sure money is available and no 
  # machine or cart is on 0,0; otherwise error.
  #-------------------------------------------------------- 
  elif 'buyc' in commandid:
    # Does the player have enough money?
    cash=int(r.get(gameid+":cash"))
    if cash>=1000:
      # player has enough money, is there an m or c on 0,0?
      if (
        (helper.machineat(gameid,"0","0")=="no") and
        (helper.cartat(gameid,"0","0")=="no")
      ):
        helper.addcart(gameid,"0","0")
        r.set(gameid+":cash", str(cash-1000))
      else:
        returnstr = "ERROR " + commandid + ": object already present at (0,0)"
    else:
      returnstr = "ERROR " + commandid + ": not enough cash, buyc costs 1000"
  #--------------------------------------------------------
  # Is it a buyx? Then you're buying a commodity with an
  # argument of "type" and "count". No partial transaction
  # allowed; a cart must be present; the type-bought must
  # be the same as the cart's type, or the cart's type must
  # be "none"; the count-bought plus the cart's count must
  # not exceed 99; and the cost of the transaction must not
  # exceed the player's cash. If all those things are true,
  # the cart's type is set, if necessary, and its count is
  # incremented accordingly. If any of these things are not
  # true, or if there's no cart at (0,0), the transaction 
  # fails and the turn is incremented.
  #--------------------------------------------------------
  elif 'buyx' in commandid:
    pass
  #--------------------------------------------------------
  # Is it a sellx? Then you're selling whatever commodity 
  # is in the cart at (9,9), and you're selling all of it.
  # cart type is set to "None", cart count is set to "0",
  # and cash is incremented accordingly. If there's no cart
  # at (9,9) the transaction fails and the turn is 
  # incremented.
  #--------------------------------------------------------
  elif 'buyx' in commandid:
    pass
  elif 'sellx' in commandid:
    pass
  #--------------------------------------------------------
  # Is it an att? att is a toggle. If something is
  # attached, detach it. If nothing is attached and 
  # something is present to attach, then attach, otherwise
  # silently fail.
  elif 'sellx' in commandid:
    pass
  #--------------------------------------------------------
  # Is it an att? att is a toggle. If something is
  # attached, detach it. If nothing is attached and 
  # something is present to attach, then attach, otherwise
  # silently fail.
  #-------------------------------------------------------- 
  elif 'att' in commandid:
    wid=valueid[0]
    # get w coordinates, and machineat and cartat for coordinates
    wx = r.get(gameid+":w:"+wid+":x")
    wy = r.get(gameid+":w:"+wid+":y")
    mat = helper.machineat(gameid,wx,wy)
    cat = helper.cartat(gameid,wx,wy)
    # if machine is attached, detach
    if r.exists(gameid+":w:"+wid+":mid"):
      r.delete(gameid+":w:"+wid+":mid")
    # elif cart is attached, detach
    elif r.exists(gameid+":w:"+wid+":cid"):
      r.delete(gameid+":w:"+wid+":cid")
    # elif machineat, attach machine
    elif mat != "no":
      r.set(gameid+":w:"+wid+":mid", mat)
    # elif cartat, attach cart
    elif cat != "no":
      r.set(gameid+":w:"+wid+":cid", cat)
    # else pass, maybe add an error later
    else:
      pass
  #--------------------------------------------------------
  # elif 'blah' in commandid:
  #   ...and so on.
  #-------------------------------------------------------- 
  # All valid commands exhausted. Set the returnstr and
  # skip the game loop.
  else:
    returnstr = "ERROR: invalid command: " +commandid  

  #-------------------------------------------------------- 
  # GAME LOOP
  #-------------------------------------------------------- 
  # OK, commands have been processed. If not error has
  # been found in the command, run the game loop.

  if not ("ERROR" in returnstr):

    # First, iterate through workers and try to move them.
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

        # If there is an m attached:
        if r.exists(gameid+":w:"+str(w)+":mid"):
          # set m to attached
          m = r.get(gameid+":w:"+str(w)+":mid")
          # If there is no w-at and no m-at and no c-at target:
          if (
            helper.machineat(gameid,wx,wy)=="no" and
            helper.cartat(gameid,wx,wy)=="no" and
            helper.workerat(gameid,wx,wy)=="no"
          ):
          # move w, move m.
            r.set(gameid+":w:"+str(w)+":x",wx)
            r.set(gameid+":w:"+str(w)+":y",wy)
            r.set(gameid+":m:"+str(m)+":x",wx)
            r.set(gameid+":m:"+str(m)+":y",wy)
            
        # If there is a c attached:
        if r.exists(gameid+":w:"+str(w)+":cid"):
          # set c to attached
          c = r.get(gameid+":w:"+str(w)+":cid")
          # If there is no w-at and no m-at and no c-at target:
          if (
            helper.machineat(gameid,wx,wy)=="no" and
            helper.cartat(gameid,wx,wy)=="no" and
            helper.workerat(gameid,wx,wy)=="no"
          ):
          # move w, move m.
            r.set(gameid+":w:"+str(w)+":x",wx)
            r.set(gameid+":w:"+str(w)+":y",wy)
            r.set(gameid+":c:"+str(c)+":x",wx)
            r.set(gameid+":c:"+str(c)+":y",wy)
        
        # elsif there is nothing attached: 
        #   If there is no w-at target:
        #     move w.
        elif helper.workerat(gameid,wx,wy)=="no":
            r.set(gameid+":w:"+str(w)+":x",wx)
            r.set(gameid+":w:"+str(w)+":y",wy)
      w += 1

      # FIXME: Now iterate through workers and assess attach/detach moves.
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
    
    # Now return the map and status.
    returnstr += helper.gamemapstr(gameid)
    returnstr += helper.gamestatestr(gameid)

  return returnstr, {'Content-Type': 'text/html'} 
