import csv, datetime, re, redis, json, traceback
from socket import *
from time import sleep
from flask import Flask
from blinker import signal
from flask_socketio import SocketIO, emit
#from components.anime import anime
from components.anime import anime
from components.motd import motd
from components.location import location
from components.whatsappbot import whatsappbot

## crontab rule made to send motd each hour. edit with "crontab -e"
STOP = "ø"
conndict = {}
functiondict = {}
targetid = []
class server:
    def __init__(self):
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        # redis has to be filled with set connected "{\"greylynx\", "\whatevs\"}"
        try:
            self.connecteddict = eval(self.r.get("connected").decode("utf-8"))
        except:
            self.r.set("connected", "{\"greylynx\":\"empty\"}")
            self.connecteddict = {"greylynx":"empty"}


    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] SERVER".format(str(date))
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
        elif colour == "blue":
            print(self.BLUE + msg + self.ENDC)
        elif colour == "yellow":
            print(self.YELLOW + msg + self.ENDC)
        elif colour == "red":
            print(self.RED + msg + self.ENDC)

    def send(self, id, message, conn="null"):
        if conn != "null":
            conn = conn
        else:
            try:
                conn = conndict[id]
            except KeyError:
                self.logger("Couldn't find device with id {}".format(id), "alert", "red")
                return 3
        try:
            conn.sendall(bytes(message+STOP, "utf-8"))
            if str(self.getname(id)) not in self.connecteddict and self.getname(id) != None:
               self.logger("Added id: {} to connected list".format(self.getname(id)), "info", "yellow")
               self.connecteddict.append(str(self.getname(id)))
               self.r.set("connected", json.dumps(self.connecteddict, sort_keys=True))
               return 1
        except Exception:
            if self.getname(id) in self.connecteddict:
               self.logger("Removed id: {} from connected list".format(self.getname(id)), "info", "yellow")
               self.connecteddict.remove(str(self.getname(id)))
               self.r.set("connected", json.dumps(self.connecteddict, sort_keys=True))
               return 2



    def listen(self):
        host = "0.0.0.0"
        port = 5555
        buf = 2048
        addr = ((host, port))
        TCPSock = socket(AF_INET, SOCK_STREAM)
        TCPSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        TCPSock.bind(addr)
        TCPSock.listen(50)
        while True:
            self.logger("Listening...", colour="yellow")
            (conn, ipaddr) = TCPSock.accept()
            data = str(conn.recv(buf))[10:-1]
            print(data)
            if len(data) > 1:
                if data[2] == "!":
                   data = data[2:]
                if data[1] == "!":
                   data = data[1:]
                if data[0] == "!":
                    self.logger(data, "msg", "yellow")
                    if data == "!noid":
                        id = self.assign(ipaddr, conn)
                        self.send("000", "!id-{}".format(id), conn)
                        self.logger("assigned ID {} to {}".format(id, ipaddr))
                        #conn.close()
                        #break
                    if data[:5] == "!ack":
                        self.logger("last message was received.", "debug", "green")
                    if data[:7] == "!marco-":
                        self.updateconn(data[7:10], conn, ipaddr[0])
                        sleep(0.3)
                        self.send("000", "!polo", conn)
                        id = data[7:10]
                        self.logger("Connected with {}, running standard functions.".format(self.getname(id)))
                        modules().one_offs(id)
                        functiondict[id] = [] # to make sure there is a list you can append functions to
                    if data[:5] == "!gps-":
                        self.logger("Got gps coordinates", "info", "blue")
                        #self.updateconn(data[5:8], conn, ipaddr[0])
                        modules().gpshandler(data[8:])
                    if data[:7] == "!motdr-":
                        self.logger("Got request for motd", "info", "blue")
                        id = data[7:10]
                        targetid = [id]
                        modules().getdaily(update="no")
                    if data[:5] == "!bat-":
                        id = data[5:8]
                        batpct = data[8:] #battery percentage
                        if int(batpct[:-1]) < 20:
                            self.logger("{} has low battery! Battery at {}".format(self.getname(id), batpct), "alert", "red")
                            modules().getgps()
                        elif int(batpct[:-1]) >= 20:
                            self.logger("{}'s battery is fine. Battery at {}".format(self.getname(id), batpct), "info", "blue")
                    if data[:6] == "!batc-":
                        id = data[6:9]
                        batpct = data[9:]
                        self.logger("{}'s battery is charging. Battery at {}".format(self.getname(id), batpct), "info", "blue")
                    if data[:6] == "!whap-":
                        self.logger("I'm here!", colour="blue")
                        msg = data[9:]
                        if r"\xe2\x80\xaa" in msg:
                            self.logger("it's type 1")
                            msg = msg.replace(r"\xe2\x80\xaa", "\"")
                            msg = msg.replace(r"\xe2\x80\xac", "\"")
                            firstcm = msg.find(",")  # first comma
                            secondcm = msg.find(",", firstcm + 2)  # second comma
                            msg = msg[:firstcm - 1] + "\"" + msg[firstcm:]
                            msg = msg[:secondcm + 2] + "\"" + msg[secondcm + 2:]
                        else:
                            self.logger("it's type 2")
                            msg = msg.replace(r"\xe2\x81\xa9", "")
                            msg = msg.replace(r"\xe2\x80\xac", "\"")
                            firstcm = msg.find(",")  # first comma
                            secondcm = msg.find(",", firstcm + 2)  # second comma
                            msg = msg[:firstcm] + "\"" + msg[firstcm:]
                            msg = msg[:firstcm + 3] + "\"" + msg[firstcm + 3:] #front of name
                            msg = msg[:secondcm + 4] + "\"" + msg[secondcm + 4:] # front of command

                        msg = msg[:1] + "\"" + msg[1:]
                        msg = msg[:-1] + "\"" + msg[-1:]
                        self.logger(msg,colour="red")
                        msg = eval(msg)
                        tmplist = []
                        for value in msg:
                            self.logger(value, colour="red")
                            if value == "":
                                tmplist.append(" empty")
                            elif value == " ":
                                tmplist.append("empty")
                            elif value[0] == " ":
                                tmplist.append(value[1:])
                            elif value[-1] == " ":
                                tmplist.append(value[:-1])
                            else:
                                tmplist.append(value)
                        msg = tmplist
                        self.logger("whatsapp message! {}".format(str(msg)), "debug", "yellow")
                        whatsappbot().buildmsg(msg)

    def assign(self, ipaddr, connection, name='unknown', type='generic', sub='none'):
        linelen = 0
        ipaddr = ipaddr[0]
        with open('database.csv', 'r') as f:
             reader = csv.reader(f, delimiter=',')
             linelen = sum(1 for row in reader)
        with open('database.csv', 'a', newline='') as f:
            id = "00"+str(linelen)
            writer = csv.writer(f)
            writer.writerow((ipaddr, name.lower(), type.lower(), sub.lower(),id))
        return id

    def updateconn(self, id, conn, newip):
        self.logger("Updating connection for id {}...".format(id), "debug", "yellow")
        oldlist = []
        newlist = []
        conndict[id] = conn
        idfound = 0
        with open("database.csv") as f:
            reader = csv.reader(f)
            oldlist = list(reader)
        with open("database.csv") as f:
            reader = csv.reader(f)
            rowcount = 0
            for row in reader:
                for value in row:
                    if id in value:
                        self.logger("found id {} on row number {}".format(id, rowcount), "debug", "green")
                        index = rowcount
                        idfound = 1
                        break
                rowcount += 1
        if idfound == 1:
            with open("database.csv", "w") as f:
                writer = csv.writer(f)
                oldlist[index][0] = newip
                for line in oldlist:
                    writer.writerow(line)
            self.logger("changed connection info for {}".format(self.getname(id)), "debug", "green")
        else:
            self.logger("Couldn't find id {}!".format(id), "alert", "red")
            self.send("000", "!idfailure", conn)

    def getid(self, name):
        with open('database.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                for value in row:
                    if name in value:
                        return row[-1]


    def getname(self, id):
        with open('database.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                for value in row:
                    if id in value:
                        return row[1]

    def error(self, id, function):
        self.logger("couldn't reach {}.".format(self.getname(id)), "alert", "red") 
        try:
            functiondict[id].append(function)
        except:
            pass

class modules:
    def __init__(self):
        self.targetid = targetid
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.oldconlen = 0
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.connecteddict = self.r.get("connected").decode("utf-8")

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
        elif colour == "blue":
            print(self.BLUE + msg + self.ENDC)
        elif colour == "green":
            print(self.GREEN + msg + self.ENDC)
        elif colour == "yellow":
            print(self.YELLOW + msg + self.ENDC)
        elif colour == "red":
            print(self.RED + msg + self.ENDC)

    def update(self, targetchoice): #targetchoice being a subscription
        self.targetid.clear()
        with open('database.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                for value in row:
                    if targetchoice in value:
                        self.targetid.append(row[-1]) #id

    def standard(self):
        self.logger("IN STANDARD" "alert", "yellow")
        sleep(3)
        while True:
            self.anime()
            #anime2().search(True)
            self.torrentchecker()

            sleep(120)

    def one_offs(self, id): # these are run on connect
        self.getdaily()
        self.resender(id) # should resend stuff, figure it out

    def anime(self, update="yes", check=True):
        if update == "yes":
            self.update("anime")
        animelst = anime().search(True) # returns string, not a list
        if animelst != "!failure" and animelst != None and animelst != "empty":
            finalmsg = "!ani-{}".format(animelst)
            for id in self.targetid:
                try:
                    result = server().send(id, finalmsg)
                    if result == 1:
                        self.logger("Sent anime to subscribers.", "info", "green")
                    else:
                        server().error(id, "anime")
                except:
                    #self.logger("Couldn't send anime to id: {}".format(id))
                    server().error(id, "anime")
        elif animelst == "empty":
            pass
        else:
            self.logger("Couldn't get anime(or no new show)!", "alert", "yellow")
    def getdaily(self, update="yes", bot="no"):
        if bot == "yes":
            motdlist = motd().createmotd(weather="no") # return list
            premsg = " ".join(motdlist)
            self.logger("Done with motd", "debug")
            return premsg
        if update == "yes":
            self.update("motd")
        city = self.locationcheck()
        motdlist = motd(city).createmotd() # return list
        premsg = "ø".join(motdlist) + "ø"
        finalmsg = "!motd-{}".format(premsg)
        for id in self.targetid:
            result = server().send(id, finalmsg)
            if result == 1:
                self.logger("Succesfully sent motd to {}".format(server().getname(id)))
            else:
                server().error(id, "motd")
                traceback.print_exc()

    def getgps(self):
        self.logger("Trying to get location..", "debug")
        #get gps coordinates
        self.update("greylynx") #just on mobile for now
        message = "!gps"
        id = self.targetid[0]
        #conn = conndict[id]
        result = server().send(id, message)
        if result == 1:
            self.logger("Asked {} for gps location.".format(server().getname(id)), "debug", "yellow")
        else:
            self.logger("Can't reach {} to ask for gps.".format(server().getname(id)))

    def locationcheck(self):
        with open("trackfiles/location.txt") as f:
            city = f.read()
        return city

    def gpshandler(self, gpscoords):
        search = "(.*?), (.*)"
        lat = re.search(search, gpscoords).group(1)
        lon = re.search(search, gpscoords).group(2)
        city = location().search(lat, lon)
        self.logger("Current location is {}".format(city), "info")
        if city != "failure":
            with open("trackfiles/location.txt", "w") as f:
                f.write(city)
        else:
            self.logger("Updated location", "debug", "green")

        self.logger("Done with gps", "debug")

    def torrentchecker(self):
        with open("trackfiles/torrentdone.txt") as f:
            show = f.read()
        if show != " ":
            show = show[6:]
            msg = {"torrent": show}
            msg1 = "!not1-{} is ready to watch!".format(show[:-2])
            msg2 = "!not2-episode {} is here!".format(show[-2:])
            self.logger("Sending torrent notification to subscribers", "info", "blue")
            self.notifier(msg1, "torrent")
            sleep(1.5)
            self.notifier(msg2, "torrent")
            with open("trackfiles/torrentdone.txt", "w") as f:
                f.write(" ")

    def notifier(self, message, subscriber="mobile"):
        self.update(subscriber)
        for id in self.targetid:
            result = server().send(id, message)
            if result == 1:
                self.logger("Succesfully sent {} to {}".format(subscriber, server().getname(id)))
            else:
                server().error(id, subscriber)
        pass

    def filewriter(self, message):
        with open("trackfiles/singleton.txt") as f:
            request = json.loads(f.read())
            request.append(message)
        with open("trackfiles/singleton.txt", "w") as f:
            f.write(json.dumps(request, sort_keys=True))


    def filereader(self):
        while True:
            with open("trackfiles/singleton.txt") as f:
                request = json.loads(f.read())
            # get function
            try:
                keylist = list(request.keys())
            except Exception as e:
                self.logger(e, "debug", "red")
            for key in keylist:
                try:
                    if key == "notification": # {"notification": "[\"greylynx\", \"file test\", \"looks like it worked!\"]"}
                        contents = list(request[key]) # evaluate value
                        name = contents[0]
                        self.logger("Got request to send notification to {}.".format(name), "info", "blue")
                        #conn = conndict[server().getid(name)]
                        id = server().getid(name)
                        title = contents[1]
                        body = contents[2]
                        msg1 = "!not1-{}".format(title)
                        msg2 = "!not2-{}".format(body) 
                        self.logger(msg1)
                        server().send(id, msg1)
                        sleep(1.5)
                        server().send(id, msg2)
                        # remove it
                        del request[key] # del because it's a dict and dicts don't have remove
                        with open("trackfiles/singleton.txt", "w") as f:
                            f.write(json.dumps(request, sort_keys=True))
                    if key == "text":
                        name = contents[0]
                        self.logger("Got request to send text to {}.".format(name), "info", "blue")
                        conn = conndict[server().getid(name)]
                        text = contents[1] 
                        # remove it
                        del remove[key]
                        with open("trackfiles/singleton.txt", "w") as f:
                            f.write(json.dumps(request, sort_keys=True))
                    if key == "motd":
                        self.logger("Sending scheduled motd to subscribers", "info", "blue")
                        self.getdaily()
                        # remove it
                        del request[key]
                        with open("trackfiles/singleton.txt", "w") as f:
                            f.write(json.dumps(request, sort_keys=True))
                except Exception:
                    # must be empty, nothing to read
                    traceback.print_exc()
            sleep(5)

    def buttonlistener(self):
        # listen to buttons, do stuff based on button.
        command = "ls /dev/ttyACM* -l | awk '{print $10}' | tail -n 1"
        device = subprocess

    def scheduler(self):
        # schedules events to fire at specific times
        pass

    def resender(self, id):
        if id in functiondict:
            functionlist = functiondict[id]
            targetid=[id] # for the functions that need id
            for function in functionlist:
                self.logger("Re-executing {} to {}".format(function, server().getname(id)), "info", "yellow")
                if function == "anime":
                    self.anime("no", check=False)
                if function == "motd":
                    self.getdaily("no")
                functiondict[id].remove(function)
