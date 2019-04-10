import feedparser, json, re, redis, os, datetime, subprocess


class anime2:
    def __init__(self):
        self.targetip = []
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.ENDC = '\033[0m'
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.curdir = os.getcwd()
        self.publishchoice = ["[HorribleSubs]"]

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

    def search(self, check=True):
        self.logger("In anime.", "debug")
        feed = feedparser.parse("https://nyaa.si/?page=rss&c=1_2&f=2")
        #[PuyaSubs!] Kemurikusa - 08 [1080p][2369253E].mkv

        followlist = ['Yakusoku no Neverland', 'Tate no Yuusha no Nariagari', 'Fairy Tail Final Season', 'Mob Psycho 100 S2', 'Tensei Shitara Slime Datta Ken', 'Yakusoku no Neverland', 'Tate no Yuusha no Nariagari', 'Fairy Tail Final Season', 'Mob Psycho 100 S2', 'Tensei Shitara Slime Datta Ken',"Sword Art Online - Alicization", "One Piece", "One Punch Man S2"]
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
                outfile = open('trackfiles/lastshow.txt')
                if check == False:
                    return airingshow
                check = outfile.read()
                outfile.close()
                if check != airingshow:
                    anime = []
                    self.logger("New show aired!", "info")
                    # might be useful for the webui
                    #for _ in range(0,5):
                        #preanime = string[_]['anime']['title']
                        #anime.append(preanime)
                    with open('trackfiles/lastshow.txt', 'w') as f:
                        f.write(epname)
                    self.download(folder, fullname, link)
                else:
                    self.logger("Already downloaded {}.".format(airingshow), "info")
                    exit()
                #print(epnum)
                #print(extension)
                #print(link)
                #test = input("Do you care?")
                #if test == "w":
                    #followlist.append(title)
            else:
                self.logger("{} aired.".format(title))
        except Exception as e:
            self.logger("Couldn't search \"{}\", probably bad format".format(title), "debug", "red")
    def download(self, folder, fullname, link):

        #check if folder exists:
        truepath = "/media/raspidisk/files/anime/{}".format(r"\ ".join(folder.split()))
        check = os.path.isdir(truepath)
        if not check:
            #folderpath = "/media/raspidisk/files/anime/{}".format(folder)
            self.logger("creating folder for {}".format(folder), "debug")
            precommand = "sudo -H -u pi bash -c \""
            command = "mkdir {}".format(truepath)
            postcommand = "\""
            os.system(precommand + command + postcommand)
        else:
            self.logger("folder {} already existed".format(folder), "debug")


        #deluge-console "command; nextcommand"
        #print("folder: " + folder)
        #print("fullname: " + fullname)
        #print("link: " + link)
        precommand = "sudo -H -u pi bash -c \""
        command = (precommand + r"deluge-console 'add -p {} {}'".format(truepath, link) + "\"")

        testcommand = ("deluge-console " + "info \"{}\"".format(self.title)).split()
        #self.logger(str(command))
        #print(str(testcommand))
        #self.logger(subprocess.check_output(command.split()).decode())
        #print(subprocess.check_output(testcommand).decode()) DOESN'T WORK
        os.system(command)
        # for auto name change, login to the deluge webui, go to settings > executor,
        # and write a script that changes the name into desired. do a simple ls -l to get newest folder, 
        # then go in and change the name.


#anime2().search(check=True)
