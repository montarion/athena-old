import feedparser, json, re, redis, os, configobj, requests
from sortedcontainers import SortedDict
from components.logger import logger as mainlogger
from components.settings import Settings
from time import sleep
class anime:
    def __init__(self):
        self.tag = "anime"
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.p = self.r.pubsub()
        self.curdir = os.getcwd()
        self.publishchoice = "HorribleSubs"
        self.fulllist = json.loads(self.r.get("siteshows").decode())
        self.loop = False
    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def search(self, check=True, numtocheck=0):
        base = f"https://nyaa.si/?page=rss&q={self.publishchoice}+%2B+[1080p]&c=1_2&f=2"
        #numtocheck += 1
        #feed = feedparser.parse("https://nyaa.si/?page=rss&c=1_2&f=2")
        feed = feedparser.parse(base)
        if numtocheck != 0 and type(numtocheck) == int:
            #feed.entries.reverse()
            numtocheck -= 1
            self.loop = True
            self.logger(f"GOING TO LOOP {numtocheck} TIMES!", "alert", "red")
        followlist = []
        fakelist = Settings().getsettings("Anime", "shows").split(", ")
        for show in fakelist:
            if show[0] == " ":
                show = show[1:]
            followlist.append(show)
        if numtocheck == "all":
            numtocheck = len(feed.entries)
        endvalue = ""
        index = len(feed.entries)
        mincutoff = index - numtocheck
        for entry in feed.entries:
            if index < mincutoff:
                
                msg = {"siteshows":self.fulllist}
                self.r.set("siteshows", json.dumps(self.fulllist))
                return endvalue, self.fulllist
            if mincutoff <= index >= 0:
                thing = dict(entry)
                keylist = list(thing.keys())
                title = thing["title"]
                #self.logger(f"working on {title}", "debug", "red")
                #self.title = title
                # ([publisher]) (episode name) - (episode number) ([quality])(extension)
                search = r"(\[.*\]) (.*) - (.*) (\[.*\])(.*)"
                try:
                    sstring = re.search(search, title)
                    quality = sstring.group(4)
                    epname  = sstring.group(2)
                    publisher = sstring.group(1)
                    if quality == "[1080p]" and epname in followlist:
                        epname  = sstring.group(2)
                        epnum = sstring.group(3)
                        if epname == "Boku no Hero Academia" and int(epnum) > 63:
                            epname = "Boku no Hero Academia S4"
                            epnum = int(epnum) - 63
                        airingshow = epname
                        extension = sstring.group(5)
                        fullname = "{} - {}{}".format(epname, epnum, extension)
                        folder = epname
                        self.recode(folder, fullname)
                        link = thing["link"]
                        size = thing["nyaa_size"]
                        imagelink = self.getimage(airingshow)
                        msg = {"title":airingshow, "episode":str(epnum), "imagelink":imagelink}
                        interpretation = {"title":"title", "subtext": "episode", "main":{"image":"imagelink"}}
                        resultdict = {"data":msg, "metadata":interpretation}
                        if len(self.fulllist) < 1:
                            self.fulllist.append(resultdict)
                        if self.fulllist[-1] != resultdict: 
                            self.fulllist.append(resultdict)
                        if self.loop:
                            #self.fulllist.append(resultdict)
                            self.logger(f"Working on index {index}")
                            index -= 1

                            continue
                        if check == False:
                            self.logger(f"saved anime: {airingshow}")
                            self.r.set("lastshow", json.dumps(msg))
                            return resultdict
                        check = json.loads(self.r.get("lastshow").decode()).get("title")
                        if check != airingshow:
                            self.logger("New show aired!", "info")
                            self.r.set("lastshow", json.dumps(msg))
                            # download the show
                            self.download(folder, fullname, link)
                            # save current last show
                            self.logger("Wrote {} to database.".format(airingshow), "info")
                            endvalue = resultdict
                        else:
                            self.logger("Already downloaded {}.".format(airingshow), "info")
                            endvalue = "empty"

                        index -= 1
                    else:
                        if not self.loop:
                            self.logger("Nothing new.")
                            endvalue = "empty"
                except Exception as e:
                    if e != AttributeError:
                        self.logger(e, "debug", "red")
                    endvalue = "empty"
        if not self.loop:
            index -= 1
        return endvalue

    def getimage(self, name):
        query = "query($title: String){Media (search: $title, type: ANIME){ coverImage{large}}}" # this is graphQL, not REST
        variables = {'title': name}
        url = 'https://graphql.anilist.co'
        response = requests.post(url, json={'query': query, 'variables': variables})
        imageurl = url = json.loads(response.text)["data"]["Media"]["coverImage"]["large"]
        return imageurl

    def download(self, folder, fullname, link):

        #check if folder exists:
        root =  "/mnt/raspidisk/files/anime/"
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
        self.logger(command, "debug", "blue")
        os.system(command)

    def recode(self, folder, fullname):
        
        root =  "/raspidisk/files/anime/"
        fullloc = root+folder+fullname
        #self.logger(fullloc, "alert", "yellow")

    def loopthrough(self, showlist):
        fulllist = []
        base = "https://nyaa.si/?page=rss&q=HorribleSubs+%2B+[1080p]+%2B+{}&c=1_2&f=2"
        for name in showlist:
            feed = feedparser.parse(base.format(name.replace(" ", "%20")))
            print("Currently working on {}".format(name))
            for show in feed.entries:
                thing = dict(show)
                title = thing["title"]
                search = r"(\[.*\]) (.*) - (.*) (\[.*\])(.*)"
                try:
                    sstring = re.search(search, title)
                    quality = sstring.group(4)
                    epname  = sstring.group(2)
                    publisher = sstring.group(1)
                    if quality == "[1080p]" and epname in followlist and publisher in self.publishchoice:
                        epname  = sstring.group(2)
                        epnum = sstring.group(3)
                        if epname == "Boku no Hero Academia" and int(epnum) > 63:
                            epname = "Boku no Hero Academia S4"
                            epnum = int(epnum) - 63
                        airingshow = epname
                        extension = sstring.group(5)
                        fullname = "{} - {}{}".format(epname, epnum, extension)
                        folder = epname
                        self.recode(folder, fullname)
                        link = thing["link"]
                        size = thing["nyaa_size"]
                        imagelink = self.getimage(airingshow)
                        msg = {"title":airingshow, "episode":str(epnum), "imagelink":imagelink}
                        interpretation = {"title":"title", "subtext": "episode", "main":{"image":"imagelink"}}
                        resultdict = {"data":msg, "metadata":interpretation}
                        fulllist.append(resultdict)
                        if check == False:
                            self.logger(f"saved anime: {airingshow}")
                            self.r.set("lastshow", json.dumps(msg))

                            return resultdict
                        check = json.loads(self.r.get("lastshow").decode())["title"]
                        if check != airingshow:
                            anime = []
                            self.logger("New show aired!", "info")
                            self.r.set("lastshow", json.dumps(msg))
                            # download the show
                            self.download(folder, fullname, link)
                            # save current last show
                            self.logger("Wrote {} to database.".format(airingshow), "info")
                            return resultdict
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

