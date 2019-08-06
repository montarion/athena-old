# does anime stuff
import feedparser, re, traceback, os, configobj

catchuplist = []
config = configobj.ConfigObj("settings.ini")
print(config["anime"])
def check(followlist=[]):
    feed = feedparser.parse("https://nyaa.si/?page=rss&q=HorribleSubs+%2B+[1080p]&c=1_2&f=2")
    #[PuyaSubs!] Kemurikusa - 08 [1080p][2369253E].mkv

#    print(followlist)


    for number, entry in enumerate(feed.entries):
        
        search = r"(\[.*\]) (.*) - (.*) (\[.*\])(.*)"
        try:
            thing = dict(entry)
            keylist = list(thing.keys())
            title = thing["title"]

            sstring = re.search(search, title)
            quality = sstring.group(4)
            epname  = sstring.group(2)
            epnum = sstring.group(3)

            publisher = sstring.group(1)
            extension = sstring.group(5)
            fullname = "{} - {}{}".format(epname, epnum, extension)
            folder = epname
            link = thing["link"]
            if epname in followlist:
                catchuplist.append(number)
        except Exception as e:
            traceback.print_exc()

def findshows():
    url = "https://horriblesubs.info/current-season/"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "lxml")
    preshows = soup.find_all(class_="ind-show")
    showlist = []
    chosenlist = []
    for show in preshows:
        showlist.append(show.find("a")["title"])

    for i, show in enumerate(showlist):
        print("Show number {} is: {}".format(i + 1, show))
        interest = input("w to add {}".format(show))
        if interest == "w":
            chosenlist.append(show)
    
#flist = ['Bokutachi wa Benkyou ga Dekinai', 'Hitoribocchi no Marumaru Seikatsu', 'Bungou Stray Dogs', 'Bungou Stray Dogs', 'Kenja no Mago', 'Tate no Yuusha no Nariagari', 'One Punch Man S2', 'Isekai Quartet', 'RobiHachi', 'Fairy Gone', 'One Piece', 'Fairy Tail Final Season', 'Bokutachi wa Benkyou ga Dekinai', 'Kimetsu no Yaiba', 'Hitoribocchi no Marumaru Seikatsu', 'Tate no Yuusha no Nariagari', 'Mob Psycho 100 S2', 'One Piece', "Shingeki no Kyojin S3", "Dr. Stone"]
followlist = []
fakelist = config["anime"]["anime"].split(",")
for show in fakelist:
    if show[0] == " ":
        show = show[1:]
    followlist.append(show)
flist = followlist
check(flist)

def catchup(catchuplist):
    print("playing catchup")
    feed = feedparser.parse("https://nyaa.si/?page=rss&q=HorribleSubs+%2B+[1080p]&c=1_2&f=2")
 
    for number in catchuplist:
        entry = feed.entries[number]
        thing = dict(entry)
        keylist = list(thing.keys())
        title = thing["title"]

        search = r"(\[.*\]) (.*) - (.*) (\[.*\])(.*)"
        try:
            sstring = re.search(search, title)
            quality = sstring.group(4)
            epname  = sstring.group(2)
            entry = feed.entries[number]
            epname  = sstring.group(2)
            epnum = sstring.group(3)
            airingshow = epname
            extension = sstring.group(5)
            fullname = "{} - {}{}".format(epname, epnum, extension)
            folder = epname
            link = thing["link"]
            download(folder, fullname, link)
        except Exception as e:
            print(e)
def download(folder, fullname, link):

        #check if folder exists:
        root = "/media/raspidisk/files/anime/"
        truepath = os.path.join(root, "\ ".join(folder.split()))
        check = os.path.isdir(truepath)
        #print(truepath)
        if not check:
            #folderpath = "/media/raspidisk/files/anime/{}".format(folder)
            #print("creating folder for {}".format(folder))
            precommand = "sudo -H -u pi bash -c \""
            command = "mkdir {}".format(truepath)
            postcommand = "\""
            #print(precommand + command + postcommand)
            os.system(precommand + command + postcommand)
        else:
            #print("folder {} already existed".format(folder))
            pass

        precommand = "sudo -H -u pi bash -c \""
        command = (precommand + r"deluge-console 'add -p {} {}'".format(truepath, link) + "\"")
        print("downloading {}".format(fullname))
        os.system(command)

catchup(catchuplist)
