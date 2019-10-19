import feedparser, json, re, redis, os, configobj
from sortedcontainers import SortedDict
from components.logger import logger as mainlogger
class anime:
    def __init__(self):
        self.tag = "anime"
        self.config = configobj.ConfigObj("settings.ini")
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.p = self.r.pubsub()
        self.curdir = os.getcwd()
        self.publishchoice = ["[HorribleSubs]"]

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def search(self, check=True):
        feed = feedparser.parse("https://nyaa.si/?page=rss&c=1_2&f=2")
        followlist = []
        fakelist = self.config["Anime"]["shows"].split(",")
        for show in fakelist:
            if show[0] == " ":
                show = show[1:]
            followlist.append(show)
        try:
            entry = feed.entries[0]
        except IndexError:
            return "failure!"
        thing = dict(entry)
        keylist = list(thing.keys())
        title = thing["title"]
        self.title = title
        # ([publisher]) (episode name) - (episode number) ([quality])(extension)
        search = r"(\[.*\]) (.*) - (.*) (\[.*\])(.*)"
        try:
            sstring = re.search(search, title)
            quality = sstring.group(4)
            epname  = sstring.group(2)
            publisher = sstring.group(1)
            if quality == "[1080p]" and epname in followlist and publisher in self.publishchoice:
                epname  = sstring.group(2)
                epnum = sstring.group(3)
                airingshow = epname
                extension = sstring.group(5)
                fullname = "{} - {}{}".format(epname, epnum, extension)
                folder = epname
                link = thing["link"]
                size = thing["nyaa_size"]
                if check == False:
                    msg = {"category": "anime", "message":airingshow}
                    self.r.set("lastshow", airingshow)
                    self.r.publish("SENDMESSAGE", str(msg))
                    return airingshow
                check = self.r.get("lastshow")
                if check != airingshow:
                    anime = []
                    self.logger("New show aired!", "info")
                    self.r.set("lastshow", airingshow)
                    msg = {"category": "anime", "message":airingshow}
                    self.r.publish("SENDMESSAGE", str(msg))
                    # download the show
                    self.download(folder, fullname, link)
                    # save current last show
                    self.r.set("lastshow", airingshow)
                    self.logger("Wrote {} to database.".format(airingshow), "info")
                else:
                    self.logger("Already downloaded {}.".format(airingshow), "info")
                    return "empty"
            else:
                self.logger("Nothing new.")
                return "empty"
        except Exception as e:
            if e != AttributeError:
                self.logger(e, "debug", "red")
            return "empty"

    def download(self, folder, fullname, link):

        #check if folder exists:
        root =  "/media/raspidisk/files/anime/"
        truepath = os.path.join(root, "\ ".join(folder.split()))

        check = os.path.isdir(truepath)
        if not check:
            self.logger("creating folder for {}".format(folder), "debug")
            precommand = "sudo -H -u pi bash -c \""
            command = "mkdir {}".format(truepath)
            postcommand = "\""
            os.system(precommand + command + postcommand)
        else:
            self.logger("folder {} already existed".format(folder), "debug")

        precommand = "sudo -H -u pi bash -c \""
        command = (precommand + r"deluge-console 'add -p {} {}'".format(truepath, link) + "\"")
        testcommand = ("deluge-console " + "info \"{}\"".format(self.title)).split()
        os.system(command)
