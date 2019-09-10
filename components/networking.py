import eventlet
eventlet.monkey_patch(socket=True)
import socketio, json, redis
from time import sleep

from components.motd import motd
from components.whatsappbot import whatsappbot

class Networking:
    def __init__(self):
        mgr = client_manager=socketio.RedisManager("redis://")
        self.socketio = socketio.Server(client_manager=mgr)
        self.app = socketio.WSGIApp(self.socketio)
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.connectionlist = json.loads(self.r.get("connectionlist").decode())
        self.sidinfo = {}

    def addconnection(self, name, sid):
        self.connectionlist = json.loads(self.r.get("connectionlist").decode())
        self.connectionlist[name] = {"sid": sid, "address":self.sidinfo[sid]}
        self.r.set("connectionlist", json.dumps(self.connectionlist))
        return 0

    def getsidbyname(self, name):
        return json.loads(self.r.get("connectionlist").decode())[name]

    def send(self, category, message):
        data = json.dumps({category:message})
        self.socketio.emit("message", data)
        print("sent message")

    def runsite(self):

        @self.socketio.on("connect")
        def connect(sid, environ):
            print("{} connected!".format(sid))
            self.sidinfo[sid] = environ["REMOTE_ADDR"]
            self.socketio.emit("connect", "empty")
            print("emitted")

        @self.socketio.on("message")
        def message(sid, data):
            print("got data")
            print(data)
            if type(data) != dict: # for notifications
                data = json.loads(data)
            for key in list(dict(data).keys()):
                #print(key)
                if key == "motd":
                    # get motd
                    print("got motd request")
                    types = data[key]
                    print(types)
                    result = motd().builder(types)
                    msg = json.dumps({"motd": result})
                    self.socketio.emit("message", msg)
                    print("Sent motd")
                if key == "test":
                    print("got test request")
                    self.socketio.emit("test", "test complete")
                    print("responded to test")
                if key == "socketACK":
                    name = data[key]
                    if name != "" and name not in self.connectionlist:
                        self.addconnection(name, sid)
                        print("connection with {} established and added to the list.".format(name))
                        self.socketio.emit("socketSUC", name) #make client respond to that and use name as check
                    #print(self.getsidbyname(name))
                    print(self.connectionlist)
                if key == "journal":
                    journaldict = dict(data[key])
                    time = journaldict["time"]
                    location = journaldict.get("location")
                    message = journaldict["message"]
                    print(location)
                if key == "notification":
                    print("got new notification!")
                    notification = (data["notification"])
                    print(notification)
                    notification = notification.replace(" ", "")
                    print(notification)
                    notification = notification.strip("[").strip("]").strip(" ").split(",")
                    print(notification)
                    whatsappbot().buildmsg(notification)
        @self.socketio.on("event")
        def event(sid, data):
            print("got data")

        #my_logger = logging.getLogger('my-logger')
        #my_logger.setLevel(logging.ERROR)
        eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 7777)), self.app) #log=my_logger)

