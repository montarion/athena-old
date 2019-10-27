import json, redis, configobj
from time import sleep
from ast import literal_eval as eval
class Settings:
    def __init__(self):
        self.config = configobj.ConfigObj("settings.ini")

    def getsettings(self, category, setting=None):
        if setting != None:
            result = self.config[category][setting]
        else:
            result = self.config[category]
            print(result)
        return result

    def setsettings(self, msg):
        # msg looks like {"CREDENTIALS":{"redditusername":"spez", "hereappid":"sdfdsujkh"}, "ANIME": "one punch man, one piece"}
        testdict = {}
        for setting in msg:
            print("changing setting: {} from {} to {}".format(setting, self.config[setting], msg[setting]))
            self.config[setting] = msg[setting]

        self.config.write()
