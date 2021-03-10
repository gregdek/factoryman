# This is a separate script that sets game-independent
# variables, like commodity prices. 

import redis
r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

# Set commodity prices
r.set("buy:A", "2")
r.set("sell:A", "1")
r.set("buy:B", "10")
r.set("sell:B", "8")

