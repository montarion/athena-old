import os, sys, redis, json, socketio

class Event:
    def __init__(self):
        mgr = socketio.RedisManager('redis://')
        self.socketio = socketio.Server(client_manager=mgr)
        self.r = redis.Redis(host="localhost", port=6379, db=0)

    def anime(self, data):
        # send notification to mobile device and update website
        print("Data is:" + str(data))
        if type(data) != dict:
            data = json.loads(self.r.get("lastshow").decode())
        self.send("anime", data)


    def send(self, category, message):
        data = json.dumps({category:message})
        print(data)
        self.socketio.emit("message", data)
        print("sent message")


