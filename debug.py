import redis
from flask_socketio import SocketIO, emit

class debug():
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


    def sendevent(self, eventmsg):
        self.socketio.emit("event", dict(eventmsg))
        print("Done.")

    def menu(self):
        while True:
            choice = input("Press 1 to send an event. ")
            if choice == "1":
                eventmsg = input("what do you want to send? ")
                category = "alert"
                eventmsg = {"msg":eventmsg, "category":category}
                self.sendevent(eventmsg)

debug().menu()
