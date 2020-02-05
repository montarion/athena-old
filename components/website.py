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
        #self.categories = list(self.config["ENABLED MODULES"].keys())
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
        

    def setupupdate(self, typelist):
        print(typelist)
        for category in typelist:
            base = typelist[category]
            if category == "greeting":
                fname = base["fname"]
                lname = base["lname"]
                street = base["street"]
                city = base["city"]
                addressdict = Location().getaddress(street + " " + city)
                print("{} lives in {}".format(fname, city))
                setdict = {"firstname": fname,"lastname": lname, "Address":addressdict}
                Settings().setsettings({"Personalia": setdict})
                self.logger("Wrote personalia to file!", "info", "green")
            if category == "busstops":
                self.logger("Got busstop request", "debug", "yellow")
                busdict = Transit().getbusstops()
                self.socketio.emit("bussetup", busdict)
    def update(self, typelist):
            for category in typelist:
                if category == "anime":
                    self.logger("Getting anime from database", "info", "yellow")
                    anime().search()
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
                    self.logger("Updating settings.")
                    categorylist = ["Anime", "Gatekeeper", "Credentials"]
                    settingdict = {}
                    for cat in categorylist:
                        result = Settings().getsettings(cat)
                        settingdict.update(result)
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


        @self.socketio.on("setupupdate")
        def setupupdate(data):
            threading.Thread(target=self.setupupdate, args=(data,)).start()

        @self.socketio.on("update")
        def update(data):
            data = eval(data)
            threading.Thread(target=self.update, args=(data,)).start()


        @self.socketio.on("settingupdate")
        def settingupdate(msg):
            Settings().setsettings(msg)
            self.logger("settings have been updated.", "info", "green")

        self.socketio.run(self.app, host='0.0.0.0', port=8000)
