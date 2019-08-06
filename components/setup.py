import os, configobj, datetime

class setup:
    def __init__(self):
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.config = configobj.ConfigObj("settings.ini")
        self.categories = list(self.config["ENABLED MODULES"].keys())
        self.filelist = ["addressbook", "connected", "keepstate", "lastcoordinates", "lastshow", "location",
                         "singleton", "statuslist", "token", "torrentdone", "weather"]
    def logger(self, msg, type="setup", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] SETUP".format(str(date))
        if type == 'debug':
            msg = "{} DEBUG: {}".format(tag, msg)
        elif type == 'alert':
            msg = "{} ALERT: \### {} \###".format(tag, msg)
        elif type == 'msg':
            msg = "{} Received message: {}".format(tag, msg)
        elif type == 'info':
            msg = "{} INFORMATION: {}".format(tag, msg)
        elif type == "setup":
            print(msg)
            return 0
        with open("output.txt", "a") as f:
            f.write(msg + "\n")
        if colour == "silent":
            pass
        elif colour == "none":
            print(msg)
        elif colour == "green":
            print(self.GREEN + msg + self.ENDC)
        elif colour == "blue":
            print(self.BLUE + msg + self.ENDC)
        elif colour == "yellow":
            print(self.YELLOW + msg + self.ENDC)
        elif colour == "red":
            print(self.RED + msg + self.ENDC)

    def setup(self):
        self.logger("Welcome to athena. Let's run through the setup.")
        followlist = []
        fakelist = self.config["anime"]["anime"].split(",")
        for show in fakelist:
            if show[0] == " ":
                show = show[1:]
            followlist.append(show)
        self.logger(followlist)

        #self.logger(self.categories)
        templist = []
        """
        for category in self.categories:
            self.logger(self.categories)
            question = "Do you want to enable {}?\nThis will allow you to {} ".format(category,
                             self.config[category]["text"])
            while True:
                answer = input(question)

                if answer == "yes" or answer == "y":
                    self.logger("Enabling {}".format(category), "info", "silent")
                    self.config["ENABLED MODULES"][category] = "yes"
                    templist.append(category)
                    break
                elif answer == "no" or answer == "n":
                    self.logger("Disabling {}".format(category), "info", "silent")
                    self.config["ENABLED MODULES"][category] = "no"
                    
                    break
                else:
                    self.logger("Please answer with either yes or no")
            self.logger("new value of {} is: {}".format(category, self.config["ENABLED MODULES"][category]))
        """
        

        self.categories = templist
        self.logger(self.categories)
        # save the file

        #self.config.filename = "settings.ini"
        #self.config.write()
