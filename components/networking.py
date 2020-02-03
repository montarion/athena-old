import eventlet
from eventlet import GreenPool
eventlet.monkey_patch(socket=True)
import socketio, json, redis, threading
from time import sleep

from components.motd import motd
from components.anime import anime
from components.modules import Modules
from components.event import Event
from components.logger import logger as mainlogger
from components.transit import Transit
from ast import literal_eval as eval
class Networking:
    def __init__(self):
        mgr = client_manager=socketio.RedisManager("redis://")
        self.socketio = socketio.Server(client_manager=mgr)
        self.app = socketio.WSGIApp(self.socketio)
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.connectionlist = {} #json.loads(self.r.get("connectionlist").decode())
        #fill redis
        self.r.set("connectionlist", json.dumps(self.connectionlist))
        self.r.set("image", "https://cdna.artstation.com/p/assets/images/images/023/154/550/large/nikolai-lockertsen-f0952e7c-f76f-4899-94f0-a475241af0a3.jpg")
        self.tag = "networking"
        self.sidinfo = {}
        # classes
        self.motd = motd()

        # stuff
        self.tasklist = [] # currently working on
    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def addconnection(self, name, sid):
        self.connectionlist = json.loads(self.r.get("connectionlist").decode())
        self.connectionlist[name] = {"sid": sid, "address":self.sidinfo[sid]["address"]}
        self.sidinfo[sid]["name"] = name
        self.r.set("connectionlist", json.dumps(self.connectionlist))
        return 0

    def getsidbyname(self, name):
        return json.loads(self.r.get("connectionlist").decode())[name]

    def send(self, category, message):
        data = json.dumps({category:message})
        try:
            self.socketio.emit("message", data)
            self.logger("sent message: "+str(message))
        except Exception as e:
            self.logger("couldn't send message: "+str(message), "alert", "red")

    def starttimer(self, sid, maxresponsetime = 3):
        eventlet.sleep(maxresponsetime)
        if "name" not in self.sidinfo[sid].keys():
            self.logger("{} with sid {} didn't follow protocol, removing.".format(self.sidinfo[sid]["address"], sid), "debug", "yellow")
            try:
                self.sidinfo.pop(sid, None)
                self.socketio.disconnect(sid)
            except Exception as e:
                self.logger("had an error with removing that sid.", "debug", "red")
                self.logger(e, "debug", "red")
        else:
            name = self.sidinfo[sid]["name"]
            self.logger("{} followed protocol, status OK.".format(name), "info", "green")
            self.socketio.emit("socketSUCC", name)

    def runserver(self):
        @self.socketio.on("connect")
        def connect(sid, environ):
            self.logger("{} connected!".format(sid), colour="green")
            self.sidinfo[sid] = {"address": environ["REMOTE_ADDR"]}
            self.socketio.emit("connectmsg", "empty")
            GreenPool().spawn(self.starttimer, sid)
            self.logger("finish connect")

        @self.socketio.on("message")
        def message(sid, data):
            self.logger(data, "debug", "yellow")
            if type(data) != dict: # for whatsapp(bot) notifications
                data = json.loads(data)
            for key in list(dict(data).keys()):
                self.logger(list(dict(data).keys()), "alert", "blue")
                if key == "motd":
                    self.tasklist.append(key)
                    # get motd
                    self.logger("got motd request", colour="yellow")
                    Modules().getlocation()
                    types = data[key][1:-1].split(", ")
                    for motdtype in types:
                        result = self.motd.builder([motdtype])
                        self.send("card", result)
                    self.logger("Sent motd")
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "test":
                    self.logger("got test request", colour="yellow")
                    self.socketio.emit("test", "test complete")
                    self.logger("responded to test")
                if key == "socketACK":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    name = data[key]
                    if name != "" and name != ' ': #and name not in self.connectionlist:
                        self.addconnection(name, sid)
                        #self.socketio.emit("socketSUC", name) #make client respond to that and use name as check
                    #print(self.getsidbyname(name))
                    #print(self.connectionlist)
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "socketSUCACK":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    name = data[key]
                    self.logger("connection with {} established and added to the list.".format(name), colour="green")
                    self.motd.builder()
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "journal":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    journaldict = dict(data[key])
                    time = journaldict["time"]
                    location = journaldict.get("location")
                    message = journaldict["message"]
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "gpscoords":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    data = data[key]
                    self.logger("Got current gps coordinates", colour="yellow")
                    city = Modules().revgeocode(json.loads(data))
                    self.r.set("location", str(city))
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "anime":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    anime().search(check=False)
                    self.logger("Sent anime to Event handler.", "debug", "yellow")
                    self.logger("TEMPORARILY DISABLED ANIME RESPONSE")
                    sendanime = True
                    if sendanime:
                        Event().anime()
                        sendanime=False
                    #result = Transit().builder("nextbus")
                    #self.send("card", result)
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "calendar":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    result = self.motd.builder("calendar")
                    self.send("card", result)
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "weather":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    result = self.motd.builder("weather")
                    self.send("card", result)
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "transit":
                    self.logger("started {}".format(key), "alert", "blue")
                    self.tasklist.append(key)
                    result = Transit().builder("nextbus")
                    self.send("card", result)
                    self.tasklist.remove(key)
                    self.logger("finished {}. tasklist is: {}".format(key, self.tasklist), "alert", "blue")
                if key == "contexttraining":
                    pass
        @self.socketio.on("ping")
        def ping(sid, data):
            self.logger("got ping", type="alert")

        @self.socketio.on("pong")
        def pong(sid, data):
            self.logger("got pong", type="alert")

        #my_logger = logging.getLogger('my-logger')
        #my_logger.setLevel(logging.ERROR)
        self.logger("Started server.", "alert", "blue")
        eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 7777)), self.app, log=None,log_output=False) #log=my_logger)

