import json, requests, sys, traceback, os, datetime
from time import sleep
from components.credentials import credentials

class location:
    def __init__(self):
        self.i = 0
        self.string = " "
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'

    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] MODULES".format(str(date))
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
        elif colour == "yellow":
            print(self.YELLOW + msg + self.ENDC)
        elif colour == "red":
            print(self.RED + msg + self.ENDC)



    def search(self, latitude, longtitude):
        with open ("trackfiles/lastcoordinates.txt", "w") as f:
            f.write("{},{}".format(latitude, longtitude))
        appID, appCode = credentials().checkcreds("geolocation")
        url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_id={}&app_code={}&mode=retrieveAddresses&prox={},{},5".format(appID, appCode, latitude, longtitude)
        # ---needed conversion---#
        r = requests.get(url)
        rtext = str(r.text)
        prettystring = rtext.replace("\'", "\"")
        goodstring = json.loads(prettystring)

        fulladdr = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]
        state = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["State"]
        city = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["City"]
        #print(fulladdr)
        #print(state)
        return city
