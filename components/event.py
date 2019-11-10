import os, sys, redis, json, socketio
from components.logger import logger as mainlogger
class Event:
    def __init__(self):
        mgr = socketio.RedisManager('redis://')
        self.socketio = socketio.Server(client_manager=mgr)
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.tag = "events"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def anime(self, data):
        # send notification to mobile device and update website
        self.logger("Data is:" + str(data))
        if type(data) != dict:
            data = json.loads(self.r.get("lastshow").decode())
        self.send("anime", data)


    def send(self, category, message):
        data = json.dumps({category:message})
        self.socketio.emit("message", data)
        self.logger("sent message: "+str(message))



