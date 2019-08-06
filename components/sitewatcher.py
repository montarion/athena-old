import eventlet
#eventlet.monkey_patch()
from flask_socketio import SocketIO, emit
from ast import literal_eval as eval
import redis, datetime
# this has to run outside of the main site script, call it sitewatcher or something
# this is how you use it

"""
p = r.pubsub()

msg = {"category": "anime", "message":"update"}
r.publish("SENDMESSAGE", str(msg))
"""

class watch():
    def __init__(self):
        self.socketio = SocketIO(message_queue='redis://')
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.p = self.r.pubsub()
        self.p.subscribe("SENDMESSAGE")
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
        tag = "[{}] PUBSUB".format(str(date))
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

    def serve(self):
        while True:
            msg = self.p.get_message()
            if msg:
                msg = msg["data"]
                if type(msg) != int:
                    msg = msg.decode()
                    msg = eval(msg)
                    category = msg["category"]
                    msg = msg["message"]
                    self.logger("category is: {}".format(category))
                    oldmsg = self.r.get(category).decode()
                    self.logger("{}| vs |{}".format(oldmsg, msg), "alert", "yellow")
                    if oldmsg != msg:
                        self.logger("type of value for category {} is: {}".format(category, type(msg)), "debug", "yellow")
                        self.socketio.emit(category, msg)
                        self.r.set(category, str(msg))
                        self.logger("updated category \"{}\" with value \"{}\"".format(category, msg), "info", "green")
                    else:
                        self.logger("Nothing changed for category: \"{}\"".format(category), "info", "red")
