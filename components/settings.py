import json, redis, configobj
from time import sleep
from ast import literal_eval as eval
from components.logger import logger as mainlogger
class Settings:
    def __init__(self):
        self.config = configobj.ConfigObj("settings.ini")
        self.tag = "settings"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def getsettings(self, category, setting=None):
        if setting != None:
            result = self.config[category][setting]
        else:
            result = self.config[category]
        return result

    def setsettings(self, msg):
        # msg looks like {"CREDENTIALS":{"redditusername":"spez", "hereappid":"sdfdsujkh"}, "ANIME": "one punch man, one piece"}
        self.logger(msg, "debug", "red")
        for setting in msg:
            self.logger("Changing setting: {} from {} to {}".format(str(setting), str(self.config[setting]), str(msg[setting])), "debug", "blue")
            self.config[setting] = msg[setting]

        self.config.write()
