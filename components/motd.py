import datetime, redis, pytz, json
from components.googlemain import google
class motd:
    def __init__(self):
        self.location = "Zeist"
        self.r = redis.Redis(host='localhost', port=6379, db=0)


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
        print("getting calendar data")
        times, eventlist = google().main()
        baseevent = eventlist[times[0]]
        start = baseevent["start"]
        end = baseevent["end"]
        nextstart = baseevent["nextstart"]
        now = pytz.timezone("Europe/Amsterdam").localize(datetime.datetime.now())
        ongoing = start < now < end
        eventsummary = baseevent["summary"]
        event = {"start":str(start), "event":eventsummary, "end":str(end), "ongoing": ongoing, "nextstart": str(nextstart)}
        if "location" in baseevent.keys():
            event["location"] = baseevent["location"]
        return event


    def builder(self, type = ["short", "agenda", "weather"]):
        result = {}
        if "short" in type:
            shortmotd = self.timemsg()
            result["short"] = shortmotd
        if "agenda" in type:
            #agenda = self.agenda()
            #result["agenda"] = agenda
            # google implementation is currently broken.
            pass
        if "weather" in type:
            weather = "it's warm"
            result["weather"] = weather
        self.r.set("motd", json.dumps(result))
        return result
