import os

import socketio, json, redis, threading
from time import sleep


from components.anime import anime
from components.settings import Settings
from components.location import Location
from components.event import Event
from components.logger import logger as mainlogger
# run your general modules here
class Modules:
    def __init__(self):
        mgr = client_manager=socketio.RedisManager("redis://")
        self.socketio = socketio.Server(client_manager=mgr)
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.tag = "modules"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def standard(self):
        while True:
            self.logger("Running anime!")
            anime().search()
            anidict = json.loads(self.r.get("lastshow"))
            if "title" not in list(anidict.keys()):
                anime().search(numtocheck="all") # loop through the last week to fill the redis "lastshow" keypair
                Event().anime()
            else:
                Event().anime()
            sleep(60)

    def getlocation(self):
        data = json.dumps({"location":{"command":"request"}})
        self.socketio.emit("message", data)

    def revgeocode(self, message):
        self.tag = "location"
        lat, lon = message["lat"], message["lon"]
        city = Location().revgeocode(lat, lon)
        self.logger("updated location to: "+ city, colour="blue")
        self.tag = "modules"
        return city
