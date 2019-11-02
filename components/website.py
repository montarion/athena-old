import eventlet
eventlet.monkey_patch(socket=True)
# Be sure to only patch the socket library!
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from components.anime import anime
from components.motd import motd
from components.settings import Settings
from components.logger import logger as mainlogger
from ast import literal_eval as eval
import datetime, os, logging, threading, traceback, redis, json, configobj, socket


class Website:
    def __init__(self):
        self.tag = "website"
        self.config = configobj.ConfigObj("settings.ini")
        self.categories = list(self.config["ENABLED MODULES"].keys())
        self.settingdict = {"appID": "password-location", "appCode": "password-location", "anime": "anime",
                            "redditUsername": "password-reddit", "redditClientId":"password-reddit",
                            "redditClientSecret":"password-reddit", "redditPassword": "password-reddit",
                            "gatekeeper":"gatekeeper"}
        self.updatesettinglist = ["anime", "appID", "appCode", "gatekeeper", "redditUsername", "redditClientId",
                                  "redditClientSecret", "redditPassword"]
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
        mainlogger().logger(self.tag, msg, type, colour)



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

                    self.logger("Getting agenda", "debug", "yellow")
                    agenda = dict(json.loads(self.r.get("motd").decode()))["agenda"]
                    self.socketio.emit("agenda", agenda)
                    self.logger("running motd", "debug", "red")
                if category == "settings":
                    # get settings with values in a dict
                    print("UPDATING SETTINGS")
                    categorylist = ["Anime", "Gatekeeper", "Credentials"]
                    settingdict = {}
                    for cat in categorylist:
                        print(cat)
                        result = Settings().getsettings(cat)
                        settingdict.update(result)
                    print(settingdict)
                    msg = {"values":settingdict}
                    self.socketio.emit("settings", msg)
                #if category == "event":
                    #self.socketio.emit("event
            #motdlst = motd().createmotd(weather="no")

    def runsite(self, setup=False):
        indexpath = "/"
        if setup:
            indexpath = "/jklfhdsljkfhdsjklfhsdjlk" # random
        @self.app.route(indexpath)
        def index():
            #threading.Thread(target=anime().search, args=(False,)).start()
            #threading.Thread(target=motd().createmotd, kwargs={"weather":"no"}).start()
            return render_template('index.html')

        settingspath = "/settings"
        if setup:
            settingspath = "/"
            # get ip
            gw = os.popen("ip -4 route show default").read().split()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((gw[2], 0))
            ipaddr = s.getsockname()[0]
            s.close()
            print("running setup, please go to http://{}:8000 in a browser.".format(ipaddr))
        @self.app.route(settingspath)
        def settings():
            return render_template('settings.html')


        @self.socketio.on("update")
        def update(data):
            data = eval(data)
            print(data)
            threading.Thread(target=self.update, args=(data,)).start()


        @self.socketio.on("settingupdate")
        def settingupdate(msg):
            Settings().setsettings(msg)
            self.logger("settings have been updated.", "info", "green")

        self.socketio.run(self.app, host='0.0.0.0', port=8000)
