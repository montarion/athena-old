import os, json, redis, inspect, datetime, sys, configobj
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
        self.config = configobj.ConfigObj("settings.ini")
        #print(self.config["PASSWORD"]["reddit"])

        if not os.path.isfile("settings.ini"):
            self.logger("Settings file not found!\nPlease go to http://[IP of this machine]/settings to set it up.")
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
        credlist = []
        passdict = self.config["PASSWORD"]
        try:
            results = passdict[type]
            for result in results:
                credlist.append(results[result])
            creds = credlist
        except KeyError:
            return "credentials for \"{}\" not found!".format(type)

        return creds # list with creds

    def setcreds(self, creddict):

        self.logger("Got request to save {} credentials".format(type))
        passdict = json.loads(f.read())

        passdict.update(creddict)
        self.logger("Added new credentials.")
        with open("trackfiles/token.txt", "w") as f:
            f.write(json.dumps(passdict))

        self.logger("Saved credentials")


