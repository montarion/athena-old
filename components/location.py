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
        self.appID = Settings().getsettings("Credentials", "hereAppID")
        self.appCode = Settings().getsettings("Credentials", "hereAppCode")


    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)


    def revgeocode(self, latitude, longtitude):
        url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json"
        parameters = {"app_id": self.appID,
              "app_code": self.appCode,
              "mode": "retrieveAddress",
              "maxresults": "1",
              "prox": "{},{}".format(latitude, longtitude)}

        # ---needed conversion---#
        r = requests.get(url, params=parameters).json()
        old = Settings().getsettings("Location")
        try:
            fulladdr = r["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]
            state = r["Response"]["View"][0]["Result"][0]["Location"]["Address"]["State"]
            city = r["Response"]["View"][0]["Result"][0]["Location"]["Address"]["City"]
            #print(fulladdr)
            #print(state)
            old["full"] = fulladdr
            old["city"] = city
            Settings().setsettings({"Location":old})
            self.logger("UPDATED LOCATION TO: {}".format(old), "alert", "red")
        except Exception as e:
            city = old["city"]
            traceback.print_exc()
        return city

    def geocode(self, address):
        url = "https://geocoder.api.here.com/6.2/geocode.json"
        parameters = {"app_id":self.appID,
                      "app_code":self.appCode,
                      "searchtext": address}
        result = requests.get(url, params=parameters).json()
        coords = result["Response"]["View"][0]["Result"][0]["Location"]["DisplayPosition"]
        lat = float(coords["Latitude"])
        lon = float(coords["Longitude"])

        return lat, lon
    # helper functions
    def getaddress(self, address):
        url = "https://geocoder.api.here.com/6.2/geocode.json"
        parameters = {"app_id":self.appID,
                      "app_code":self.appCode,
                      "searchtext": address}
        result = requests.get(url, params=parameters).json()
        addressdict = result["Response"]["View"][0]["Result"][0]["Location"]["Address"]
        addressdict["full"] = addressdict.pop("Label")
        return addressdict
