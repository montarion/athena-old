import json, redis, configobj
from time import sleep
from ast import literal_eval as eval
class Settings:
    def __init__(self):
        self.config = configobj.ConfigObj("settings.ini")
        self.settingdict = {"appID": "password-location", "appCode": "password-location", "anime": "anime",
                            "redditUsername": "password-reddit", "redditClientId":"password-reddit",
                            "redditPassword": "password-reddit", "gatekeeper":"gatekeeper"}

    def lostgetsettings(self, target): # target is a list of target values
        index = 0
        tmpdict = {}
        while True:
            if index == 0:
                tmpdict = self.config.get(target[index])
            else:
                tmpdict = tmpdict[target[index]]
            if type(tmpdict) == dict and index == len(target):
                index += 1
            else:
                print(tmpdict)
                break
        return tmpdict

    def getsettings(self, category, setting=None):
        if setting != None:
            result = self.config[category][setting]
        else:
            result = self.config[category]
        return result

    def setsettings(self, msg):
        # msg looks like {"CREDENTIALS":{"redditusername":"spez", "hereappid":"sdfdsujkh"}, "ANIME": "one punch man, one piece"}
        print(msg)
        print(type(msg))
        testdict = {}
        for setting in msg:
            print(self.config)
            print(self.config[setting])
            print("changing setting: {} from {} to {}".format(setting, self.config[setting], msg[setting]))
            self.config[setting] = msg[setting]
        
        print("final!")
        print(self.config.keys())
        self.config.write()
