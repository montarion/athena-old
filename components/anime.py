import json, requests, os, datetime, urllib.request, redis


# DEPRECIATED

print("\n\n DEPRECIATED. USE ANIME2.PY\n\n")
exit(1)
class anime:
    def __init__(self):
        self.targetip = []
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.r = redis.Redis(host='localhost', port=6379, db=0)
    def logger(self, msg, type="info", colour="none"):
        msg = str(msg)
        predate = datetime.datetime.now()
        date = predate.strftime("%Y-%m-%d %H:%M")
        tag = "[{}] ANIME".format(str(date))
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

    def sitesearch(self):
            self.logger("in sitesearch", "debug")
            url = 'http://www.masterani.me/api/releases'
            #{"anime": {"black clover": ['wallpaper', 'link'], "mob 100":["wallpaper", "link"]}}
            # ---needed conversion---#
            test = requests.get(url)
            test1 = test.text
            test = str(test1)
            string = json.loads(str(test))
            finaldict = {}
            finaldict["anime"]= {}

            def getlink(link, episode):
                base = "https://www.masterani.me/anime/watch/"
                return base + link + "/" + episode

            def downloadposter(posterlink):
                fileloc = "components/static/files/anime/" + posterlink.rsplit("/",1)[1]
                urllib.request.urlretrieve(posterlink,fileloc)
                print(posterlink)
                print(fileloc)
                return fileloc

            def getposter(poster):
                base = "https://cdn.masterani.me/poster/1/"
                posterlink = base + poster
                downloadposter(posterlink)
                localbase = "static/files/anime/"
                print(localbase + poster)
                return localbase + poster #static/files/animexxxxxxx.jpg

            for _ in range(0, 5):
                title = string[_]['anime']['title']
                link = string[_]["anime"]["slug"]
                episode = string[_]["episode"]
                poster = string[_]["anime"]["poster"]

                finaldict["anime"][title]= [getlink(link, episode), getposter(poster)]

            self.r.set("anime", json.dumps(finaldict, sort_keys=True))


    def search(self, check=True):
        self.logger("In anime.", "debug")
        # ---url for releases, in JSON---#
        url = 'http://www.masterani.me/api/releases'

        # ---needed conversion---#
        try:
            test = requests.get(url)
        except:
            return "!failure"
        test1 = test.text
        test = str(test1)
        try:
            string = json.loads(str(test))
        except:
            return "!failure"
        filecheck = os.path.isfile('trackfiles/lastshow.txt')
        airingshow = string[0]['anime']["title"]
        anime = "!failure"
        if filecheck is False:
            self.logger("Creating file..", "info", "yellow")
            lastshow = string[0]['anime']["title"]
            #---writes last aired show to file---#
            with open('trackfiles/lastshow.txt', 'w') as f:
                f.write(lastshow)
        else:
            #---checks if new show has aired---#
            outfile = open('trackfiles/lastshow.txt')
            if check == False:
                return airingshow
            check = outfile.read()
            if check != airingshow:
                anime = []
                self.logger("New show aired!", "info")
                # might be useful for the webui
                for _ in range(0,5):
                    preanime = string[_]['anime']['title']
                    anime.append(preanime)
                with open('trackfiles/lastshow.txt', 'w') as f:
                    f.write(anime[0])
                self.sitesearch()
            else:
                #print(self.BLUE + "No new show" + self.ENDC)
                lastshow = string[0]['anime']["title"]
                with open('trackfiles/lastshow.txt', 'w') as f:
                    f.write(lastshow)
                anime = "!failure"
                self.logger("No new show")
            
        return anime 
