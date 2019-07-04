import eventlet
eventlet.monkey_patch(socket=True)
# Be sure to only patch the socket library!
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from components.anime import anime
from components.motd import motd
from ast import literal_eval as eval
import datetime, os, logging, threading, traceback, redis, json


class Site:
    def __init__(self):
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
                self.logger("Getting anime from database", "info", "yellow")
                if category == "anime":
                    animelist = self.r.get("anime")
                    if animelist:
                        animelist = animelist.decode()
                        self.socketio.emit("anime", animelist)
                    else:
                        self.logger("running anime", "info", "yellow")
                        animelist = anime().search(False)
                if category == "motd":
                    self.logger("Getting motd from database", "info", "yellow")
                    imagelink = self.r.get("image")
                    self.logger("Getting image", "debug", "yellow")
                    if imagelink:
                        imagelink = imagelink.decode()
                        self.logger(imagelink, "debug", "green")
                        self.socketio.emit("image", imagelink)
                    self.logger("Getting news", "debug", "yellow")
                    news = self.r.get("news")
                    if news:
                        news = news.decode()
                        news = eval(news)
                        self.logger("Got news", "debug", "green")
                        self.logger(news, "debug", "green") 
                        self.logger(type(news), "debug", "green")
                        self.socketio.emit("news", news)
                    self.logger("Getting song", "debug", "yellow")
                    songdict = self.r.get("song")
                    if songdict:
                        songdict = songdict.decode()
                        self.logger("Got song", "debug", "green")
                        self.socketio.emit("song", songdict)
                    self.logger("Getting temperature", "debug", "yellow")
                    temperature = self.r.get("weather")
                    if temperature:
                        temperature = temperature.decode()
                        self.logger("Got temperature", "debug", "green")
                        self.socketio.emit("weather", temperature)
                    else:
                        self.logger("running motd", "debug", "red")
                        motdlst = motd().createmotd(weather="no")

    def runsite(self):
        self.logger("Started site", "info", "yellow")
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.socketio.on('connect')
        def test_connect():
            self.logger("GOT CONNECTION", "alert", "red")
            threading.Thread(target=self.update, args=(["anime", "motd"],)).start()


        @self.socketio.on("msg")
        def getmsg(msg):
            pass

        self.socketio.run(self.app, host='0.0.0.0', port=8000)
