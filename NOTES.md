### Design Summary

Factory Manager is a simple client/server game, with the simplest possible state representation and an easy set of API calls to run the game engine. Each call to the API moves the game one clock tick forward. 

### Endpoints
The following endpoints are available for client communication. The client renders the map and accepts commands; the endpoints evaluate moves, and communicate and store game state.
* /newgame -- returns a unique gameid and a game state (an empty factory and some cash).
* /gameid/state -- for the given gameid, returns the current game state.
* /gameid/command/[xxx] -- for the given gameid, analyzes the command [xxx], updates the game state, and returns the updated game state.

### Game State
The game state consists of a set of objects and their location on a 10x10 map. I suppose the game state is stored as a tuple of a gameid and JSON. 

### Game Objects
The game objects are Workers, Carts, and Machines. Various simple actions can be performed by the player that can change the state of those objects. 
There are also widgets, but widgets are not objects in and of themselves; they are properties of Carts, that can be changed by Workers or Machines.

* __[W]orkers__ are the lifeblood of the factory. They move the Carts around and they run the Machines. Instantiated with a "buyw" command.
    * w.id is the count of the worker.
    * w.x is the x position of the worker on the map [0..9], changed by the "move" command. Can overlap 
    * w.y is the y position of the worker on the map [0..9], changed by the "move" command.
    * w.c is the cart the worker is attached to, if any, changed by the "attach" or "detach" command. See *Cart* for details.
    * w.m is the machine the worker is attached to, if any, changed by the "attach" or "detach" command. See *Machine* for details.
    * Workers cannot share coordinates with other W.
    * Workers can share coordinates with C or M.
    
* __[C]arts__ are how widgets are moved around the plant. 
    - c.id is the count of the cart.
    - c.x is the x position of the cart on the map. Only changed if a worker is attached and the worker moves.
    - c.y is the y position of the cart on the map. Only changed if a worked is attached and the worker moves.
    - c.count is the number of widgets in a cart. 
    - c.type is the type of widget in a cart, if any. Empty carts can accept a widget of any type, which then sets c.type.
    - Carts cannot share coordinates with other C or M.
    - Carts can share coordinates with W.
    
* __[M]achines__ are how widgets are transformed into other widgets.
    - m.id is the id of the machine.
    - m.x is the x position of the machine. Only changed if a worker is attached and the worker moves.
    - m.y is the y position of the machine. Only changed if a worker is attached and the worker moves.
    - m.i is the input type widget that the machine accepts from an adjacent cart. Predetermined at instantiation time.
    - m.o is the output type widget that the machine puts into an adjacent cart. Predetermined at instantiation time.
    - Machines transform widgets in adjacent cards under the following circumstances: if an adjacent cart has a c.count/c.type that matches m.input, and another adjacent cart has c.count/c.type that matches m.output, and if a W is attached to the machine, then the machine decrements the count of the input cart and increments the count of the output cart.  
    
### Game Commands
- The player executes game commands. One command can be executed per turn:
    - The "wait" command does nothing. The state of the game can still change.
    - The "move(wxy) sets worker W on path to X,Y. 
    - The "buyw" command instantiates a new W at [0,0]. Fails if: W at [0,0]; insufficient funds.
    - The "buyc" command instantiates a new C at [0,0]. Fails if: C or M at [0,0]; insufficient funds.
    - The "buym(io)" command instantiates a new M of input i and output o at [0,0]. Fails if: C or M at [0,0]; (io) combo is invalid; insufficient funds.
    - The "buyw(tc)" command buys widget type t of count c and puts into C at [0,0]. Fails if: no C or wrong type C at [0,0]; insufficient funds.
    - The "sell" command sells whatever is at [9,9]: W, M, or contents of C. Fails if: no W, M, or C at [9,9].

### Game Loop
FIXME.