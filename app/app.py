from flask import Flask
import uuid
import redis

app = Flask(__name__)
app.debug = True

redis_host = "localhost"
redis_port = 6379
redis_password = ""

@app.route('/')
def index():
  return 'This will point to a link to start a new game!'

@app.route('/newgame')
def newgame():
  newgameid = str(uuid.uuid4())
  r = redis.Redis()
  newgamestate = "Game state for " + newgameid
  r.set(newgameid, newgamestate)
  # FIXME: just return the newgameid for now, but figure out how to 
  # return game state also
  return(newgameid)

@app.route('/state/<gameid>')
def state(gameid):
  r = redis.Redis()
  gamestate = r.get(gameid)
  return(gamestate)

@app.route('/command')
def command():
  return('This processes a command and returns the new state of the game!')


