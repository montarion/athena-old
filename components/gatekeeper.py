import os, json, re, redis, datetime
from time import sleep

class gatekeeper:
    def __init__(self):
        self.addressbook = {}
        self.addrlist = []
        self.namelist = []
        self.statuslist = {}
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'


    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] GATEKEEPER".format(str(date))
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



    def watch(self):
        self.logger("STARTED GATEKEEPER", "info", "yellow")
        while True:
            with open("trackfiles/statuslist.txt") as f:
                self.statuslist = json.loads(f.read())
                self.oldstatuslist = dict(self.statuslist)
            #run commands
            os.system("sudo ip -s -s neigh flush all > /dev/null 2>&1") # flush arp table
            os.system("components/arp.sh > /dev/null 2>&1") # run script to ping everyone, updating arp tables
            sleep(2) # wait for script
            os.system("sudo arp | grep ether | awk '{print $3}' | tail -n +2 > trackfiles/connected.txt") # read and write arp table

            with open("trackfiles/addressbook.txt") as f:
                self.addressbook = json.loads(f.read())

            with open("trackfiles/connected.txt") as f: # read file with mac addresses
                lines = f.readlines()
                for line in lines:
                    if line[:-1] in self.addressbook:
                        name = self.addressbook[line[:-1]]
                        self.namelist.append(name)
                        self.statuslist[name] = "home"

            for key in self.statuslist:
                if key not in self.namelist:
                    self.statuslist[key] = "away"

            with open("trackfiles/statuslist.txt", "w") as f:
                f.write(json.dumps(self.statuslist, sort_keys=True))

            for name in self.statuslist:
                if self.statuslist[name] != self.oldstatuslist[name]:
                    if self.statuslist[name] == "away":
                        self.logger(name + " left!")
                        self.statuslist[name] = "left"
                    else:
                        self.logger(name + " came home!")
                        self.statuslist[name] = "came home"


            #even though I say list, it's a dict..
            self.r.set("gatekeeper",json.dumps(self.statuslist, sort_keys=True))
            #self.logger("Set gatekeeper values", "debug")
            sleep(30)
