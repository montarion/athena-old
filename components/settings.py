import json, redis, configobj
from time import sleep
from ast import literal_eval as eval
from components.logger import logger as mainlogger

class Settings:
    def __init__(self):
        self.tag = "settings"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def getdata(self, category, data=None):
        config = configobj.ConfigObj("data/data.ini")
        try:
            if data != None:
                result = config[category][data]
            else:
                result = config[category]
            return result
        except KeyError:
            return None


    def setdata(self, msg):
        config = configobj.ConfigObj("data/data.ini")
        # msg looks like {"MACHINELEARNING":{"trainingfeatures":[{...},{...},...]}
        for data in msg:
            # make sure the category exists
            try:
                s = config[data]
            except KeyError:
                config[data] = {}
                config.write()
            if type(msg[data]) == dict:
                config[data].update(msg[data])
            else:
                config.update(msg[data])
        config.write()
        return 0

    def getsettings(self, category, setting=None):
        config = configobj.ConfigObj("data/settings.ini")
        try:
            if setting != None:
                result = config[category][setting]
            else:
                result = config[category]
            return result
        except KeyError:
            return None
    def setsettings(self, msg):
        # msg looks like {"CREDENTIALS":{"redditusername":"spez", "hereappid":"sdfdsujkh"}, "ANIME": "one punch man, one piece"}
        config = configobj.ConfigObj("data/settings.ini")
        self.logger(msg, "debug", "red")
        for setting in msg:
            self.logger("Changing setting: {} from {} to {}".format(str(setting), str(config[setting]), str(msg[setting])), "debug", "blue")
            config[setting] = msg[setting]

        config.write()
