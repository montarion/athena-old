import os

import socketio, json, redis, threading
from time import sleep

from components.motd import motd
from components.anime import anime
from components.settings import Settings
from components.location import Location

# run your general modules here
class Modules:
    def __init__(self):
        mgr = client_manager=socketio.RedisManager("redis://")
        self.socketio = socketio.Server(client_manager=mgr)

    def standard(self):
        while True:
            anime().search()

            sleep(120)

    def getlocation(self):
        data = json.dumps({"location":"request"})
        self.socketio.emit("message", data)

    def geocode(self, message):
        print(message)
        lat, lon = message["lat"], message["lon"]
        city = Location().search(lat, lon)
        print("updated location to: "+ city)
        return city
