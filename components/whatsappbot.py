from adb.client import Client as AdbClient
from time import sleep
from sortedcontainers import SortedDict
from components.logger import logger as mainlogger
import datetime
from ast import literal_eval as eval
#from components.server import modules
class whatsappbot:
    def __init__(self):
        # Default is "127.0.0.1" and 5037
        client = AdbClient(host="127.0.0.1", port=5037)
        self.device = client.device("ZX1D22WJC2")
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.tag = "whatsappbot"
    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def buildmsg(self, notification):
        #from components.server import modules
        commands =["debug", "help"]
        names = []
        self.logger(notification)
        
        title = notification[0]
        caller = notification[1]
        if "+" in caller:
            caller = caller[1:]
            caller = caller.replace(" ", "")
            caller = caller.replace("(", "")
            caller = caller.replace(")", "")
        names.append(caller)
        self.logger(notification[2])
        command = notification[2].split(" ")
        self.logger(command)
        if not "bot" in command:
            command.insert(0, "bot")
        self.logger(command)
        if command[1] == "debug":
            self.logger("Received debug command from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            text = r"debug output is: \"Just talk to a rubber duck\"."
            self.writemessage(title, names, text)
        elif command[1] == "motd":
            self.logger("Received motd command from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            text = modules().getdaily(bot="yes") # bot=yes removes weather/location information
            text = text.replace("\"", r"\"")
            self.logger("Motd text is {}".format(text), colour="yellow")
            self.writemessage(title, names, text)
        elif command[1] == "help":
            self.logger("Received help command from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            tmplist = []
            for value in commands:
                if value == commands[-1]:
                    tmplist.append("and " + r"\"" + value + r"\"")
                else:
                    tmplist.append(r"\"" + value + r"\"")
            listofcommands = r", ".join(tmplist)
            self.logger(listofcommands, "debug", "yellow")
            text = r"At the moment I can answer to: {}.".format(listofcommands)
            self.writemessage(title, names, text)
        elif command[1] == "empty":
            self.logger("Received empty command from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            text = r"yes?"
            self.writemessage(title, names, text)
        elif "fuck you" in command:
            self.logger("Received cussing from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            text = r"no fuck you."
            self.writemessage(title, names, text)
        else:
            self.logger("Received unknown command from \"{}\" in \"{}\"".format(caller, title), "debug", "blue")
            tmplist = []
            for value in commands:
                if value == commands[-1]:
                    tmplist.append("and " + r"\"" + value + r"\"")
                else:
                    tmplist.append(r"\"" + value + r"\"")
            listofcommands = r", ".join(tmplist)
            self.logger(listofcommands, "debug", "yellow")
            tmp2list = []
            for value in command:
                if value != command[0]:
                    if value == command[-1]:
                        tmp2list.append(value)
                    else:
                        tmp2list.append(value + " ")
            realcmd = "".join(tmp2list)
            text = r"Sorry, I don't know what \"{}\" means yet. At the moment I can answer to: {}.".format(realcmd, listofcommands)
            self.writemessage(title, names, text)

    def writemessage(self, title, names, text):
        device = self.device
        searchevent = "input keyevent 84"
        enterevent = "input keyevent 66"
        backevent = "input keyevent 4"

        # all of these numbers are hardcoded to the size of my phone's screen. unless you have a motorola moto g4+
        #   it likely won't work.
        device.shell("am start -n com.whatsapp/com.whatsapp.HomeActivity") # start whatsapp
        device.shell(searchevent) # tap search
        sleep(2)
        device.shell(backevent)
        sleep(2)
        device.shell("input text '{}'".format(title)) # look for chat
        sleep(2)
        device.shell("input tap 335 300") # tap chat
        sleep(2)
        device.shell(backevent)
        for name in names:
            device.shell("input text '@{}'".format(name)) # type name
            sleep(2)
            device.shell("input tap 300 1035") # tap name
        sleep(2)
        device.shell("input text \"{}\"".format(text)) # type text
        sleep(2)
        device.shell("input tap 650 1135") # tap send
        device.shell("am start -n com.whatsapp/com.whatsapp.HomeActivity") # back to home screen

    def tagadmin(self, title, names, text):
        admin = "31614597694"
        device = self.device
        device.shell("am start -n com.whatsapp/com.whatsapp.HomeActivity") # start whatsapp
        device.shell("input tap 889 167") # tap search
        device.shell("input text '{}'".format(title)) # look for chat
        device.shell("input tap 559 491") # tap chat
        # call admin
        device.shell("input text '@{}'".format(admin)) # type name
        device.shell("input tap 480 820") # tap name
        device.shell("input text \"Please help me out with this..\"") # request assistance from admin
        device.shell("input tap 992 945") # tap send
        for name in names:
            device.shell("input text '@{}'".format(name)) # type name
            device.shell("input tap 480 820") # tap name
        device.shell("input text \"{}\"".format(text)) # type text
        device.shell("input tap 992 945") # tap send
        device.shell("am start -n com.whatsapp/com.whatsapp.HomeActivity") # back to home screen

