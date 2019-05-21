import os, json, redis, inspect, datetime, sys
from time import sleep

# simple function to ask all necessary credentials

class credentials:
    def __init__(self):
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        if not os.path.isfile("trackfiles/token.txt"):
            self.logger("Password file not found!\n you must have a password file in \"trackfiles\" called \"token\" "\
                        "that contains a json dictionary looking like this:\n\n"\
                        "{\"reddit\":[\"username\", \"password\"]}")
            sys.exit()
            
    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] PASSWORDSTORE".format(str(date))
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

    def checkcreds(self, type):
        self.logger("Got request for {} credentials".format(type))
        with open("trackfiles/token.txt") as f:
            passdict = json.loads(f.read())
        try:
            creds = passdict[type]
        except Keyerror:
            return "credentials for \"{}\" not found!".format(type)

        return creds # list with creds

    def setcreds(self, creddict):

        self.logger("Got request to save {} credentials".format(type))
        with open("trackfiles/token.txt") as f:
            passdict = json.loads(f.read())

        passdict.update(creddict)
        self.logger("Added new credentials.")
        with open("trackfiles/token.txt", "w") as f:
            f.write(json.dumps(passdict))

        self.logger("Saved credentials")


