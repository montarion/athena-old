import os

import socketio, json, redis, threading
from time import sleep


from components.anime import anime
from components.settings import Settings
from components.location import Location
from components.logger import logger as mainlogger
# run your general modules here
class Modules:
    def __init__(self):
        mgr = client_manager=socketio.RedisManager("redis://")
        self.socketio = socketio.Server(client_manager=mgr)
        self.tag = "modules"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def standard(self):
        while True:
            anime().search()

            sleep(60)

    def getlocation(self):
        data = json.dumps({"location":{"command":"request"}})
        self.socketio.emit("message", data)

    def geocode(self, message):
        self.tag = "location"
        lat, lon = message["lat"], message["lon"]
        city = Location().search(lat, lon)
        self.logger("updated location to: "+ city, colour="blue")
        self.tag = "modules"
        return city
