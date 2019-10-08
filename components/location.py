import json, requests, sys, traceback, os, datetime
from time import sleep
from components.settings import Settings
from components.logger import logger as mainlogger

class Location:
    def __init__(self):
        self.tag = "location"
        self.i = 0
        self.string = " "
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)


    def search(self, latitude, longtitude):
        #with open ("trackfiles/lastcoordinates.txt", "w") as f:
            #f.write("{},{}".format(latitude, longtitude))
        appID = Settings().getsettings("Credentials", "hereAppID")
        appCode = Settings().getsettings("Credentials", "hereAppCode")
        url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_id={}&app_code={}&mode=retrieveAddresses&prox={},{},5".format(appID, appCode, latitude, longtitude)
        # ---needed conversion---#
        r = requests.get(url)
        rtext = str(r.text)
        prettystring = rtext.replace("\'", "\"")
        goodstring = json.loads(prettystring)

        fulladdr = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]
        state = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["State"]
        city = goodstring["Response"]["View"][0]["Result"][0]["Location"]["Address"]["City"]
        print(fulladdr)
        #print(state)
        return city
