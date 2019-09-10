import datetime, redis, pytz
from components.google import google
class motd:
    def __init__(self):
        self.location = "Zeist"

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
        eventsummary = eventlist[times[0]]["summary"]
        event = {"time":str(times[0]), "event":eventsummary}
        return event

    def builder(self, type = ["short", "agenda", "weather"]):
        result = {}
        if "short" in type:
            shortmotd = self.timemsg()
            result["short"] = shortmotd
        if "agenda" in type:
            agenda = self.agenda()
            result["agenda"] = agenda
        if "weather" in type:
            weather = "it's warm"
            result["weather"] = weather
        return result
