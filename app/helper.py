# Helper functions for Factoryman
# Assumes that you've already imported Flask, is this true?

import sys
import redis
redis_host = "localhost"
redis_port = 6379
redis_password = ""
r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

def workerat(gameid,x,y):
    # Returns "no" if none, otherwise returns the workerid
    workeratxy="no"
    w = 0
    while w < int(r.get(gameid+":w:count")):
      wx = int(r.get(gameid+":w:"+str(w)+":x"))
      wy = int(r.get(gameid+":w:"+str(w)+":y"))
      wactive = r.get(gameid+":w:"+str(w)+":active")
      if (wactive == "yes") and int(x)==int(wx) and int(y)==int(wy):
        workeratxy=str(w)
      w += 1
    return workeratxy

def machineat(gameid,x,y):
    machineatxy="no"
    m = 0
    while m < int(r.get(gameid+":m:count")):
      mx = int(r.get(gameid+":m:"+str(w)+":x"))
      my = int(r.get(gameid+":m:"+str(w)+":y"))
      mactive = r.get(gameid+":m:"+str(w)+":active")
      if (mactive == "yes") and int(x)==int(mx) and int(y)==int(my):
        machineatxy="yes"
      m += 1
    return machineatxy

def cartat(gameid,x,y):
    cartatxy="no"
    c = 0
    while c < int(r.get(gameid+":c:count")):
      cx = int(r.get(gameid+":c:"+str(w)+":x"))
      cy = int(r.get(gameid+":c:"+str(w)+":y"))
      cactive = r.get(gameid+":c:"+str(w)+":active")
      if (cactive == "yes") and int(x)==int(cx) and int(y)==int(cy):
        cartatxy="yes"
      c += 1
    return cartatxy

def addworker(gameid,x,y):
    wcount = int(r.get(gameid+":w:count"))
    r.set(gameid+":w:"+str(wcount)+":x", str(x))
    r.set(gameid+":w:"+str(wcount)+":y", str(y))
    r.set(gameid+":w:"+str(wcount)+":dx", str(x))
    r.set(gameid+":w:"+str(wcount)+":dy", str(y))
    r.set(gameid+":w:"+str(wcount)+":active", "yes")
    wcount += 1
    #errlog("WARN: wcount is "+str(wcount))
    r.set(gameid+":w:count",str(wcount))
    return

def gamestatestr(gameid):
    # Return a formatted set of values representing gamestate.
    # For now, default to HTML.
    # Return worker count and list of workers x/y/active/cid/mid.
    w = 0
    rstr = gameid+":cash --> " + r.get(gameid+":cash") + "<br/>"
    rstr += gameid+":lastcmd --> " + r.get(gameid+":lastcmd") + "<br/>"
    rstr += gameid+":w:count --> " + r.get(gameid+":w:count") + "<br/>"
    while w < int(r.get(gameid+":w:count")):
       basestr = str(gameid+":w:"+str(w)+":")
       rstr += basestr+"x --> " + r.get(basestr+"x") + "<br/>"
       #rstr += basestr+"x --> " + r.get(gameid+":w:0:x") + "<br/>"
       rstr += basestr+"y --> " + r.get(basestr+"y") + "<br/>"
       rstr += basestr+"dx --> " + r.get(basestr+"dx") + "<br/>"
       rstr += basestr+"dy --> " + r.get(basestr+"dy") + "<br/>"
       rstr += basestr+"active --> " + r.get(basestr+"active") + "<br/>"
       w += 1
        
    # FIXME: Return machine count (if any) and list of machines x/y/active
    # FIXME: Return cart count (if any) and list of carts x/y/active.
    return rstr

def gamemapstr(gameid):
    # Return a formatted map representing items on the map.
    # For now, default to HTML.
    returnstr = '<pre>'                                                         
    for gmx in range(0,10):
      for gmy in range(0,10):
        # Default: empty
        mapstr="____"
        # If there's a worker, place the worker
        wid=workerat(gameid,gmx,gmy)
        if wid != "no":
          mapstr="w" + str(wid) + "__"
        # FIXME: if there's a cart or machine, add it too
        returnstr += mapstr + " "
      returnstr+="<br/>"
    returnstr+="<br/>"
    returnstr+="</pre>"
    return returnstr

def errlog(errstr):
    print(errstr,file=sys.stderr)
    return
