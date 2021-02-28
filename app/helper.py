# Helper functions for Factoryman

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
      mx = int(r.get(gameid+":m:"+str(m)+":x"))
      my = int(r.get(gameid+":m:"+str(m)+":y"))
      mactive = r.get(gameid+":m:"+str(m)+":active")
      if (mactive == "yes") and int(x)==int(mx) and int(y)==int(my):
        machineatxy=str(m)
      m += 1
    return machineatxy

def cartat(gameid,x,y):
    cartatxy="no"
    c = 0
    while c < int(r.get(gameid+":c:count")):
      cx = int(r.get(gameid+":c:"+str(c)+":x"))
      cy = int(r.get(gameid+":c:"+str(c)+":y"))
      cactive = r.get(gameid+":c:"+str(c)+":active")
      if (cactive == "yes") and int(x)==int(cx) and int(y)==int(cy):
        cartatxy=str(c)
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

def addmachine(gameid,x,y):
    mcount = int(r.get(gameid+":m:count"))
    r.set(gameid+":m:"+str(mcount)+":x", str(x))
    r.set(gameid+":m:"+str(mcount)+":y", str(y))
    r.set(gameid+":m:"+str(mcount)+":dx", str(x))
    r.set(gameid+":m:"+str(mcount)+":dy", str(y))
    r.set(gameid+":m:"+str(mcount)+":active", "yes")
    mcount += 1
    #errlog("WARN: wcount is "+str(wcount))
    r.set(gameid+":m:count",str(mcount))
    return

def addcart(gameid,x,y):
    ccount = int(r.get(gameid+":c:count"))
    r.set(gameid+":c:"+str(ccount)+":x", str(x))
    r.set(gameid+":c:"+str(ccount)+":y", str(y))
    r.set(gameid+":c:"+str(ccount)+":dx", str(x))
    r.set(gameid+":c:"+str(ccount)+":dy", str(y))
    r.set(gameid+":c:"+str(ccount)+":active", "yes")
    ccount += 1
    r.set(gameid+":c:count",str(ccount))
    return 

def gamestatestr(gameid):
    # Return a formatted set of values representing gamestate.
    # For now, default to HTML.
    # Return worker count and list of workers x/y/active/cid/mid.
    rstr = gameid+":cash --> " + r.get(gameid+":cash") + "<br/>"
    rstr += gameid+":lastcmd --> " + r.get(gameid+":lastcmd") + "<br/>"
    rstr += gameid+":w:count --> " + r.get(gameid+":w:count") + "<br/>"
    rstr += gameid+":m:count --> " + r.get(gameid+":m:count") + "<br/>"
    rstr += gameid+":c:count --> " + r.get(gameid+":c:count") + "<br/>"
    w = 0
    while w < int(r.get(gameid+":w:count")):
       basestr = str(gameid+":w:"+str(w)+":")
       rstr += basestr+"x --> " + r.get(basestr+"x") + "<br/>"
       rstr += basestr+"y --> " + r.get(basestr+"y") + "<br/>"
       rstr += basestr+"dx --> " + r.get(basestr+"dx") + "<br/>"
       rstr += basestr+"dy --> " + r.get(basestr+"dy") + "<br/>"
       rstr += basestr+"active --> " + r.get(basestr+"active") + "<br/>"
       w += 1
    c = 0
    while c < int(r.get(gameid+":c:count")):
       basestr = str(gameid+":c:"+str(c)+":")
       rstr += basestr+"x --> " + r.get(basestr+"x") + "<br/>"
       rstr += basestr+"y --> " + r.get(basestr+"y") + "<br/>"
       rstr += basestr+"active --> " + r.get(basestr+"active") + "<br/>"
       c += 1
    m = 0
    while m < int(r.get(gameid+":m:count")):
       basestr = str(gameid+":m:"+str(m)+":")
       rstr += basestr+"x --> " + r.get(basestr+"x") + "<br/>"
       rstr += basestr+"y --> " + r.get(basestr+"y") + "<br/>"
       rstr += basestr+"active --> " + r.get(basestr+"active") + "<br/>"
       m += 1
    rstr += '<form action="/command">'
    rstr += '<label for="commandid">Command:</label>'
    # rstr += 'c:<input type="text" id="c" name="c" /> '
    rstr += '<select name="c" id="c">'
    rstr += '<option value="wait">wait</option>'
    rstr += '<option value="move">move</option>'
    rstr += '<option value="buyc">buyc</option>'
    rstr += '<option value="buym">buym</option>'
    rstr += '<option value="att">attach/detach</option>'
    rstr += '</select>'
    rstr += 'v:<input type="text" id="v" name="v" />'
    rstr += '<input type="hidden" id="g" name="g" value="' + gameid + '"/>'
    rstr += '<input type="submit" value="Submit" />'
    rstr += '</form>'
    return rstr

def gamemapstr(gameid):
    # Return a formatted map representing items on the map.
    # For now, default to HTML.
    returnstr = '<pre>'                                                         
    for gmx in range(0,10):
      for gmy in range(0,10):

        # Default: empty
        mapstr="____"

        # Is there a worker? Render it
        wid=workerat(gameid,gmx,gmy)
        if wid != "no":
          mapstr="w" + str(wid) + "__"

        # Is there a machine? Render it
        mid=machineat(gameid,gmx,gmy)
        if mid != "no":
          if "w" in mapstr:
            # if w and m are attached, put m first
            if r.exists(gameid+":w:"+str(wid)+":mid"):
              mapstr="m" + str(mid) + "w" + str(wid)
            # else put w first
            else:
              mapstr="w" + str(wid) + "m" + str(mid)
          else:
            mapstr="m" + str(mid) + "__" 

        # Is there a cart ? Render it
        cid=cartat(gameid,gmx,gmy)
        if cid != "no":
          if "w" in mapstr:
            # if w and c are attached, put c first
            if r.exists(gameid+":w:"+str(wid)+":cid"):
              mapstr="c" + str(cid) + "w" + str(wid)
            # else put w first
            else:
              mapstr="w" + str(wid) + "c" + str(cid)
          else:
            mapstr="c" + str(cid) + "__" 

        # Add this tile to the map
        returnstr += mapstr + " "
      returnstr+="<br/>"
    returnstr+="<br/>"
    returnstr+="</pre>"
    return returnstr

def errlog(errstr):
    print(errstr,file=sys.stderr)
    return
