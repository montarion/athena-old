import datetime, redis, pytz, json, requests, traceback
from components.googlemain import google
from components.settings import Settings
from components.modules import Modules
from components.logger import logger as mainlogger
class motd:
    def __init__(self):
        self.location = "Zeist"
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.tag = "motd"

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def timemsg(self):
        day = datetime.datetime.now(pytz.timezone("Europe/Amsterdam")).strftime("%A")
        time = datetime.datetime.now(pytz.timezone("Europe/Amsterdam")).strftime("%H")
        time = int(time)
        if time < 6:
            period = "night"
            greeting = " had a good day today!"
        elif time >= 6 and time < 12:
            period = "morning"
            greeting = "'re looking forward to today!"
        elif time >= 12 and time < 18:
            period = "afternoon"
            greeting = "'re having a good day!"
        elif time >= 18:
            period = "evening"
            greeting = " had a good day!"


        message = "Good {}! I hope you{}".format(period, greeting)
        return message

    def agenda(self):
        self.logger("getting calendar data")
        times, eventlist = google().main()
        baseevent = eventlist[times[0]]
        start = baseevent["start"]
        end = baseevent["end"]
        #nextstart = baseevent["nextstart"]
        now = pytz.timezone("Europe/Amsterdam").localize(datetime.datetime.now())
        ongoing = start < now < end
        eventsummary = baseevent["summary"]
        event = {"start":str(start), "event":eventsummary, "end":str(end), "ongoing": ongoing}
        if "location" in baseevent.keys():
            event["location"] = baseevent["location"]
        return event

    def weather(self):
        logger("getting weather data")
        API_KEY = Settings().getsettings("Credentials","weatherApiKey")
        baseurl = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"
        city = self.r.get("location")
        
        finalurl = baseurl.format(city, API_KEY)
        response = json.loads(requests.get(finalurl).text)
        try:
            temperature = response["main"]["temp"]
            windspeed = response["wind"]["speed"]
            cloudpercentage = response["clouds"]["all"]
            rain = response.get("rain")
            if rain:
                rain = rain.get("1h")
            if rain == None:
                rain = "None"
            icon = response["weather"][0]["icon"]
            iconurl = "http://openweathermap.org/img/wn/{}@2x.png".format(icon)
            resultdict = {"temperature": temperature, "windspeed": windspeed, "cloudpercentage": cloudpercentage, "iconurl": iconurl, "rain":rain}
            return resultdict
        except:
            self.logger(finalurl, colour="red")
            traceback.print_exc()
            return {"Failure":"0"} # think of error codes

    def builder(self, type = ["short", "calendar", "weather"]):
        result = {}
        if "short" in type:
            shortmotd = self.timemsg()
            result["short"] = shortmotd
            # currently not implemented or requested
        if "calendar" in type:
            agenda = self.agenda()
            result["calendar"] = agenda
        if "weather" in type:
            Modules().getlocation()
            weather = self.weather()
            result["weather"] = weather
        self.r.set("motd", json.dumps(result))
        return result
