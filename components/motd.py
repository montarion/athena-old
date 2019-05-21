from time import sleep
import requests, csv, praw, json, calendar, base64, urllib.request, os, re, datetime, redis
from random import *
from components.credentials import credentials

class motd:
    def __init__(self, city="Zeist"):
        self.songlink = ""
        self.headlines = []
        self.city = city
        self.weatherlist = []
        self.finallist = []
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
        tag = "[{}] MOTD".format(str(date))
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

    def createmotd(self, weather="yes"):
        rtext, ilink = self.reddit()
        stext, stitle, slink = self.song()

        if weather == "yes":
            wtext = self.weather()
            self.finallist.append(wtext)
        rtext, ilink = self.reddit()
        stext, stitle, slink = self.song()
        self.finallist.append(rtext)
        self.finallist.append(stext)
        self.finallist.append(stitle)
        self.finallist.append(slink)
        if weather == "yes":
            self.finallist.append(ilink)

        return self.finallist
    def reddit(self):
        username, clientsecret, password = credentials().checkcreds("reddit")
        client_id = "Ers-s6mSnoaCsw"
        client_secret = clientsecret
        username = username
        password = password
        user_agent = "testscript by /u/montarion"
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password, username=username, user_agent=user_agent)


        multi = reddit.multireddit('montarion', 'takemethere').top('day', limit=1)
        for thing in multi:
            imagelink = thing.url #idea: display image urls on greyhawk?
            url = imagelink
            self.logger("getting image..", "debug")
            # Not using because the hardcoded part is ugly! (using anyway)
            extsearch = "\.(.*?)\?"
            if "?" in url:
                index = url.find("?")
                results = re.search(extsearch, url[index-10:]) # go back 10 so you actually get the extension
                extension = results.group(1)
            else:
                extension = url[-3:]
            filename = "image." + extension
            self.logger("Found image link: {}".format(imagelink), "debug")

        #download image
        fileloc = "components/static/files/motd/" + imagelink.rsplit("/",1)[1]
        try:
            urllib.request.urlretrieve(imagelink,fileloc)
            tmpdict = {"background":"static/files/motd/" + imagelink.rsplit("/",1)[1]}
            self.r.set("background", json.dumps(tmpdict, sort_keys=True))
            self.logger("Downloaded background image to :" + imagelink.rsplit("/",1)[1] , "info", "blue")
        except:
            self.logger("Sorry, couldn't get {}".format(imagelink))

        multi = reddit.multireddit(username, 'news').top('day',limit=1)
        news = []
        for thing in multi:
            news.append(thing.title)
            news.append(thing.permalink)
            self.headlines.append(news)
        headline = "Today's news is that {0}.".format(self.headlines[0][0])
        self.logger("Got reddit headline", "debug")
        return headline, imagelink

    def song(self):
        vidlist = []        
        with open('scriptlets/vidlinks.csv', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            vidlink = list(reader)
        
        choice = randint(1, len(vidlink))
        songtitle = vidlink[choice][1]
        songlink = vidlink[choice][0]
        songset = ["now", "finally", "lest we forget"]
        songprep = songset[randint(0, len(songset)-1)] #now, finally, lest we forget
        songmsg = "And {0}, here is the song of the day:".format(songprep) 
        self.logger("Got song stuff", "debug")
        return songmsg, songtitle, songlink
    def weather(self):
        city = self.city.lower()
        url = "https://5dayweather.org/api.php?city="+ city
        r = requests.get(url)
        test1 = r.text
        test = str(test1)
        string = json.loads(str(test))
        temperature = (int(string["data"]["temperature"]) - 32) * 5//9
        templist = []
        with open("trackfiles/weather.txt", "a") as f:
            f.write(str(temperature)+ "\n")

        with open("trackfiles/weather.txt", "r") as f:
            for temp in f:
                templist.append(int(temp[:-1]))
        
        avgtemp = sum(templist)/len(templist)
        if temperature >= avgtemp:
            self.tempstat = "a nice"
            self.tempstat2 = ", so"
        else:
            self.tempstat = "a chilly"
            self.tempstat2 = ". Nevertheless,"
        dayset = ["stellar", "awesome", "great", "supercalifragilisticexpialidocious", "amazing"]
        dayword = dayset[randint(0,len(dayset)-1)] #stellar, awesome
        
        #1
        self.weatherlist.append(temperature) #21
        skytext = string["data"]["skytext"]
        #2
        self.weatherlist.append(skytext.lower()) #cloudy, sunny
        windspeed = string["data"]["wind"]

        #3
        now = datetime.datetime.now()
        day = now.day
        dayname = now.strftime("%A")
        month = calendar.month_name[now.month]
        date = month + " " + str(day)
        self.weatherlist.append(dayname.lower()) #monday
        datenumber = string["data"]["date"]

        #4
        self.weatherlist.append(date) #august 1

        weatherreport = "Good morning! It's {0}, {1} in {2}. We're looking at {3} skies today, and it'll be {4} {5} degrees{6} let's make it a {7} day!".format(dayname.lower(),  date, self.city, skytext.lower(), self.tempstat, \
        str(temperature), self.tempstat2, dayword)
        return weatherreport

