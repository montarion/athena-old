import datetime, redis, threading, eventlet, logging
from time import sleep
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from blinker import signal
class site:
    def __init__(self):
        self.app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.disabled = True
        self.app.logger.disabled = True
        self.socketio=SocketIO(self.app, async_mode="eventlet")
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.olddata = {"anime": " ", "sysinfo":" ", "gatekeeper": " ", "background": " ", "connected":" "}


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

    def runsite(self):
        self.logger("STARTED SITE", "info", "yellow")
        @self.app.route('/')
        def normal():
            t0 = threading.Thread(target=mainloop)
            t0.start()
            return render_template('index.html')

        def ontestevent(sender):
            self.logger("Running ontestevent!", "alert", "yellow")
            with self.app.test_request_context():
                for id in self.idlist:
                    self.socketio.emit("test", {"data":"it worked!"}, namespace="/", broadcast=True)

        @self.socketio.on('connect')
        def test_connect():
            self.logger("Connected!", colour="blue")
            #self.logger(request.sid, colour="blue")
            #emit('connected', {'data': 'Connected'})
            for name in self.olddata:
                function = name
                data = self.olddata[function]
                #self.logger("Emitting data for {}!".format(function), colour="blue")
                emit(function, {"data":str(data)}, namespace="/", broadcast=True)

        def updater(function):
            data = self.r.get(function).decode("utf-8")
            if data != self.olddata[function]:
                self.logger("new data!", colour="blue")
                self.olddata[function] = data
                with self.app.test_request_context('/'):
                    emit(function, {"data":str(data)}, namespace="/", broadcast=True)
                self.logger("sent msg: {}".format(str(data)), colour="yellow")

        def mainloop():
            self.logger("Started loop", colour="blue")
            olddata = "null"
            while True:
                updater("anime")
                updater("gatekeeper")
                updater("background")
                updater("connected")
                sleep(30)
        self.socketio.run(self.app, host='0.0.0.0', port=8080)
