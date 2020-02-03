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

    def anime(self):
        # send notification to mobile device and update website
        result = {}
        msgdata = json.loads(self.r.get("lastshow").decode())
        title = msgdata["title"]
        episode = msgdata["episode"]
        imagelink = msgdata["imagelink"]
        notititle = title + " aired"
        notitext = "You can watch episode {} now!".format(episode)
        notimsg = self.buildnotification(notititle, notitext)
        anime = {"title":title, "episode":episode, "image":imagelink}
        interpretation = {"title":"title", "subtext":"episode", "main":{"image":"image"}}
        resultdict = {"data":anime, "metadata":interpretation}
        result["anime"] = resultdict
        self.send("notification", notimsg)
        self.send("card", result)
        self.logger("Done with anime!", "debug", "blue")

    def buildnotification(self, notititle, notitext):
        category = "notification"
        message = {"notititle": notititle, "notitext": notitext}
        return message

    def send(self, category, message):
        self.logger(message, "debug", "yellow")
        data = json.dumps({category:message})
        self.socketio.emit("message", data)
        self.logger("sent message: "+str(message))



