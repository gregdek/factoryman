## TODO

- [ ] Write buyx pseudocode 
- [ ] Write buyx code 
- [ ] Write sellx pseudocode
- [ ] Write sellx code
- [ ] Add error checking for various command inputs
- [ ] Capture full game history into DB for replay/CI ability
- [ ] Set up venv
- [ ] Introduce auto-cart K?
- [ ] Introduce robot-machine R?
- [ ] Introduce different bulk commodity prices?
- [ ] Kube: retest deploy to make sure all is well
- [ ] Kube: figure out ingress to filter out garbage requests
- [x] Set commodity prices in database in separate process
- [x] Write buyx pseudocode
- [x] Write sellx pseudeocode 
- [x] Add new cart attributes to new cart code
- [x] Add new machine attributes to new machine code (all machines are a2b1)
- [x] Write machine processing spec
- [x] Write cart type spec
- [x] Expand form with all game options
- [x] Split command parser to accept two args: "command" and "value"
- [x] Add basic commands form to game state output
- [x] Change command route to accept GET form data
- [x] Change newgame to return game state
- [x] Create main page link to start game
- [x] Add carts and machines to gamestate return
- [x] Add "buyc" and cart creation code
- [x] Add worker/cart attach/detach code to command loop
- [x] Add cart move code to game loop
- [x] Add worker/machine attach/detach code to command loop
- [x] Add machine move code to game loop
- [x] Add "buym" and machine creation code
- [x] Write map output function
- [x] Replace game loop map return with helper map return function
- [x] Bug: why does move command not immediately move player in game loop?
- [x] Replace game loop functions with helper collision functions
- [x] Write helper.gamemapstr
- [x] Write helper.errlog
- [x] Replace sadd/smember with helper.gamestatestr
- [x] Write helper functions: workerat(x,y), machineat(x,y), cartat(x,y)
- [x] Write hire command and helper.addworker
- [x] Get uppercase out of the model
- [x] Write actual code for basic game loop with user movement
- [x] Write pseudocode for full game loop
- [x] Write command: worker move
- [x] Recast output from byte to str
- [x] Send response as HTML
- [x] Finish game state data model
- [x] Finish game loop design
- [x] Install redis locally
- [x] Write basic game instantiation endpoint
- [x] Write basic state retrieval endpoint
