import os, json, redis
from components.settings import Settings
from components.website import Website

# install redis

print("installing redis backend server..")
os.system("sudo apt install redis-server")
r = redis.Redis(host='localhost', port=6379, db=0)

# check imports

# check which modules should be enabled.

# populate redis
r.set("connectionlist", "{}")

# populate settings(start webserver and have them go to the settings page)
Website().runsite(setup=True)
