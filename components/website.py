
from gevent import monkey
monkey.patch_socket()
# Be sure to only patch the socket library!
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from components.anime import anime
from components.motd import motd
from components.settings import Settings
from components.logger import logger as mainlogger
from components.location import Location
from components.transit import Transit
from ast import literal_eval as eval
import datetime, os, logging, threading, traceback, redis, json, configobj, socket

class Website:
    def __init__(self):
        self.tag = "website"
        self.config = configobj.ConfigObj("settings.ini")
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, message_queue='redis://localhost',async_mode="gevent")
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        # colours
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def runsite(self, setup=False):
        indexpath = "/"
        if setup:
            indexpath = "/jklfhdsljkfhdsjklfhsdjlk" # random
        @self.app.route(indexpath)
        def index():
            return render_template('index.html')

        @self.app.route("/settings")
        def settings():
            return render_template("settings.html")
        setuppath = "/setup"
        if setup:
            setuppath = "/"
            # get ip
            gw = os.popen("ip -4 route show default").read().split()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((gw[2], 0))
            ipaddr = s.getsockname()[0]
            s.close()
            self.logger("running setup, please go to http://{}:8000 in a browser.".format(ipaddr), "alert", "blue")
        @self.app.route(setuppath)
        def setup():
            return render_template('setup.html')

        @self.socketio.on("connect")
        def onconnect():
            print("got connected!")
            emit("message", {"data": "test string"})
            print("msg sent")

        @self.socketio.on("echo")
        def onmessage(message):
            message = json.loads(message)
            emit("message", {"echo":message})

        @self.socketio.on("message")
        def onmessage(message):
            self.logger(f"pure message: {message}")
            message = json.loads(str(message))
            self.logger(message)

        @self.socketio.on("update")
        def onupdatemessage(message):
            self.logger(f"pure message: {message}")
            message = json.loads(str(message))
            self.logger(message)
            for key in list(message):
                if key == "anime":
                    siteshowlist = json.loads(self.r.get("siteshows").decode())
                    self.logger(siteshowlist)
                    if len(siteshowlist) < 1:
                        # run anime
                        anime().search(check=True,numtocheck=7)
                        # then get it after all
                        siteshowlist = json.loads(self.r.get("siteshows").decode())
                        self.logger("updated siteshow list")
                    siteshowlist.reverse() # get most recent first
                    for show in siteshowlist:
                        self.logger(show["data"]["title"])
                    emit("animeupdate", siteshowlist[:7])
                    siteshowlist.reverse() # make list normal again

        self.socketio.run(self.app, host='0.0.0.0', port=8000)
