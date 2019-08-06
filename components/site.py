import eventlet
eventlet.monkey_patch(socket=True)
# Be sure to only patch the socket library!
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from components.anime import anime
from components.motd import motd
from ast import literal_eval as eval
import datetime, os, logging, threading, traceback, redis, json, configobj


class Site:
    def __init__(self):
        self.config = configobj.ConfigObj("settings.ini")
        self.categories = list(self.config["ENABLED MODULES"].keys())
        self.settingdict = {"appID": "password-location", "appCode": "password-location", "anime": "anime",
                            "redditUsername": "password-reddit", "redditClientId":"password-reddit",
                            "redditPassword": "password-reddit", "gatekeeper":"gatekeeper"}
        self.updatesettinglist = ["anime", "appID", "appCode", "gatekeeper", "redditUsername", "redditClientId",
                                  "redditPassword"]
        self.app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.disabled = False
        self.app.logger.disabled = False
        self.socketio = SocketIO(self.app, message_queue='redis://localhost',async_mode="eventlet")
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        # colours
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'

    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] WEBSITE".format(str(date))
        if type == 'debug':
            msg = "{} DEBUG: {}".format(tag, msg)
        elif type == 'alert':
            msg = "{} ALERT: \### {} \###".format(tag, msg)
        elif type == 'msg':
            msg = "{} Received message: {}".format(tag, msg)
        elif type == 'info':
            msg = "{} INFORMATION: {}".format(tag, msg)
        with open("output.txt", "a") as f:
            f.write(msg + "\n")
        if colour == "none":
            print(msg)
        elif colour == "green":
            print(self.GREEN + msg + self.ENDC)
        elif colour == "blue":
            print(self.BLUE + msg + self.ENDC)
        elif colour == "yellow":
            print(self.YELLOW + msg + self.ENDC)
        elif colour == "red":
            print(self.RED + msg + self.ENDC)

    def update(self, typelist):
            for category in typelist:
                if category == "anime":
                    self.logger("Getting anime from database", "info", "yellow")
                    animelist = self.r.get("lastshow")
                    animelist = animelist.decode()
                    self.socketio.emit("anime", animelist)
                if category == "motd":
                    self.logger("Getting motd from database", "info", "yellow")
                    imagelink = self.r.get("image")
                    self.logger("Getting image", "debug", "yellow")
                    imagelink = imagelink.decode()
                    self.socketio.emit("image", imagelink)

                    self.logger("Getting news", "debug", "yellow")
                    news = self.r.get("news")
                    news = news.decode()
                    self.logger(news, "alert", "yellow")
                    self.logger(type(news), "alert", "yellow")
                    news = eval(news)
                    self.logger(news, "alert", "yellow")
                    self.logger(type(news), "alert", "yellow")
                    #news = json.dumps(news)
                    self.socketio.emit("news", news)

                    self.logger("Getting song", "debug", "yellow")
                    songdict = self.r.get("song")
                    songdict = songdict.decode()
                    self.socketio.emit("song", songdict)

                    self.logger("Getting temperature", "debug", "yellow")
                    #temperature = self.r.get("weather")
                    #temperature = temperature.decode()
                    #self.socketio.emit("weather", temperature)

                    self.logger("running motd", "debug", "red")
                if category == "settings":
                    # get settings with values in a dict
                    self.config = configobj.ConfigObj("settings.ini")
                    settingdict = {}
                    for setting in self.updatesettinglist:

                        if setting == "appCode" or setting == "appID":
                            settingdict.update({setting: self.config["PASSWORD"]["location"][setting]})
                        elif "reddit" in setting:
                            settingdict.update({setting: self.config["PASSWORD"]["reddit"][setting]})
                        else:
                            settingdict.update({setting: self.config[setting].values()[0]})

                    msg = {"values":settingdict}
                    self.socketio.emit("settings", msg)
                #if category == "event":
                    #self.socketio.emit("event
            #motdlst = motd().createmotd(weather="no")

    def runsite(self):
        self.logger("Started site", "info", "yellow")
        @self.app.route('/')
        def index():
            #threading.Thread(target=anime().search, args=(False,)).start()
            #threading.Thread(target=motd().createmotd, kwargs={"weather":"no"}).start()
            return render_template('index.html')

        @self.app.route('/settings')
        def settings():
            return render_template('settings.html')

        @self.socketio.on("update")
        def update(data):
            data = eval(data)
            threading.Thread(target=self.update, args=(data,)).start()


        @self.socketio.on("settingupdate")
        def settingupdate(msg):
            for setting in msg:
                value = msg[setting]
                category = self.settingdict[setting]
                if "password-" in category:
                    category = category.split("-")[1] 
                    if len(self.config["PASSWORD"].values()) == 0:
                        self.config["PASSWORD"] = {}

                    if category not in self.config["PASSWORD"]:
                        self.config["PASSWORD"][category] = {}

                    self.config["PASSWORD"][category][setting] = value
                else:
                    if len(self.config[category].values()) == 0:
                        self.config[category] = {}
                    self.config[category][setting] = value
            self.config.filename = "settings.ini"
            self.config.write()
            self.logger("settings have been updated.", "info", "green")
            threading.Thread(target=self.update, args=(["settings"],)).start()

        self.socketio.run(self.app, host='0.0.0.0', port=8000)
