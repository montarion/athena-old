import requests, json
from datetime import datetime, date, timedelta
from components.location import Location
from components.settings import Settings
from components.logger import logger as mainlogger
api_id = "sDK1UNZ7XguGtNp7PBO9"
api_key = "FtUmy8gp1vkAZVzqaQsrAQ"

class Transit:
    def __init__(self):
        self.tag = "Transit"
        self.transporttypes = {"0": "High-speed Train", "1": "Intercity Train", "2": "Train", "3": "Train", "4": "Sprinter", "5": "Bus", "7": "Subway", "20": "Walking"}

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)

    def parsetime(self, dt):
        realdate, realtime = str(dt).split("T")
        return realdate, realtime

    def parseduration(self, duration):
        durationdict = {}
        for section in ["H", "M"]:
            if section in duration:
                target = duration.find(section)
                result = duration[target - 2:target]
                if result[0] == "0":
                    result = result[1:]
                durationdict[duration[target]] = result
        if len(durationdict) > 1:
            return "{} and {} minutes".format(durationdict["H"], durationdict["M"])
        else:
            return "{} minutes".format(durationdict["M"])

    def routing(self, dep_coords="52.103029, 5.241949", arr_coords="52.359176, 4.909479", time=datetime.now(), arrival_choice=0):
        routelist = []
        # first check if preferred stop is near
        lat, lon = [float(i) for i in dep_coords.split(", ")]
        prefnear = self.checkprefstop(lat, lon)
        self.logger(prefnear, "debug", "yellow")
        if prefnear:
            # get bus coords
            lat = Settings().getsettings("Personalia", "busstop")["coordinates"]["x"]
            lon = Settings().getsettings("Personalia", "busstop")["coordinates"]["y"]
            dep_coords = "{}, {}".format(lat, lon)
            # get preferred busstop name
            name = Settings().getsettings("Personalia", "busstop")["name"]
            # get busstop walking time location
            wtstring = Settings().getsettings("Personalia", "busstop")["walking time"]
            pwt = datetime.strptime(wtstring,"%M:%S").time()
            walking_time = timedelta(minutes=pwt.minute)

        url = "https://transit.api.here.com/v3/route.json"  # this is the public transit API
        parameters = {"app_id": api_id,
                      "app_code": api_key,
                      "dep": dep_coords,
                      "arr": arr_coords,
                      "arrival": arrival_choice,
                      "time": time.isoformat(),
                      "routingMode": "realtime",
                      "max":6} # max number of results

        result = requests.get(url, params=parameters)
        if arrival_choice == 0:
            arrival_string = "departure"
        else:
            arrival_string = "arrival"
        self.logger("Going for {} at {}".format(arrival_string, time))
        result = json.loads(result.text)["Res"]
        #self.logger(result)
        connections = result["Connections"]["Connection"]
        #self.logger(connections)
        for thing in connections:
            try:
                busid = thing["Dep"].get("Stn")["id"]
            except:
                busid = None
                continue
            if busid == "215150824": # fav bus
                break

        connection = thing
        transfers = connection["transfers"]
        duration = connection["duration"]
        start_time = connection["Dep"]["time"]
        arrival_time = connection["Arr"]["time"]
        self.logger("Your journey will start at {}, end at {}, and take {}.".format(self.parsetime(start_time), self.parsetime(arrival_time), self.parseduration(duration)))
        self.logger("___________________________________________")
        for index, section in enumerate(connection["Sections"]["Sec"]):
            secmode = section["mode"]
            secdeptime = self.parsetime(section["Dep"]["time"])[1] # departure time
            if secmode == 20 and index == 0:
                secdeploc = "Current location"
            else:
                secdeploc = section["Dep"]["Stn"].get("name")  # departure station name
            sectransportname = section["Dep"]["Transport"].get("name", "\b") # transport name

            if "Stn" in section["Arr"].keys():
                secarrsloc = section["Arr"]["Stn"].get("name") # arrival station name
            else:
                try:
                    secarrsloc = section["Dep"].get("AP")["name"]
                except:
                    secarrsloc = section["Dep"]["Stn"]["name"]
            if secmode != 20:
                self.logger(self.transporttypes[str(secmode)])
                sectranscat = " using " + self.transporttypes[str(secmode)]  # transport category
                sectransportdir = section["Dep"]["Transport"]["dir"] # transport direction
            else:
                sectranscat = ". Walk"  # transport category
                # look into the future a bit
                if index + 1 < len(connection["Sections"]["Sec"]):
                    #futsecmode = connection["Sections"]["Sec"][index + 1]["mode"]
                    futsecdeploc = connection["Sections"]["Sec"][index + 1]["Dep"]["Stn"].get("name")
                    sectransportdir = futsecdeploc
                else:
                    sectransportdir = secdeploc
            secduration = self.parseduration(section["Journey"]["duration"]) # journey duration
            secdistance = section["Journey"]["distance"] # journey distance
            secarrtime = self.parsetime(section["Arr"]["time"])[1] # time of arrival
            if str(secmode) in ["0", "1", "2","3"]:
                sectransportname = "{} on platform {}".format(sectransportname, section["Arr"]["platform"]) # arrival platform, if applicable

            secstring = "You depart from {} at {}{} {} in the direction of {}. your journey will take {} and cross {} meters. You will arrive at {} at around {}.".format(secdeploc, secdeptime, sectranscat, sectransportname, sectransportdir, secduration, secdistance, secarrsloc, secarrtime)
            self.logger(secstring)
            sectionlist = [secdeploc, secdeptime, sectranscat, sectransportname, sectransportdir, secduration, secdistance, secarrsloc, secarrtime]
            routelist.append(sectionlist)
            self.logger("-----------")
        if prefnear:
            realdeparture = datetime.strptime(routelist[0][1], "%H:%M:%S") - walking_time
            self.logger("adding {} to base time of {} to get {}.".format(walking_time, time, realdeparture))
            time = realdeparture
            realdeparture = str(realdeparture).split(" ")[1].split(".")[0]

            wtlist = str(walking_time).split(":")
            walking_time = self.parseduration("PT{}M".format(wtlist[1]))
            self.logger(walking_time)
            routelist.insert(0, ["Home", realdeparture, self.transporttypes["20"], "\b", name, walking_time, "\b", name])
        self.logger("_________________________________")
        return routelist

    def busstop(self, time, dep_lat=52.102182, dep_lon=5.236826, radius="10"):
        url = "https://transit.api.here.com/v3/multiboard/by_geocoord.json"
        stationdict = {}

        parameters = {"app_id": api_id,
                      "app_code": api_key,
                      "center": str(dep_lat) + "," + str(dep_lon),
                      "radius": radius,
                      "max": "1",
                      "time": time.isoformat()}
        result = requests.get(url, params=parameters)

        result = json.loads(result.text)["Res"]
        try:
            stations = result["MultiNextDepartures"]["MultiNextDeparture"]
        except:
            self.logger("No stations found", type="info")
            return None
        for departure in stations:
            stationname = departure["Stn"]["name"]
            stationdistance = departure["Stn"]["distance"]
            stationduration = datetime.strptime(departure["Stn"]["duration"], "PT%HH%MM%SS")
            lat, lon = departure["Stn"]["y"], departure["Stn"]["x"]
            id = departure["Stn"]["id"]
            stationdict[id] = {"name": stationname, "distance":stationdistance, "walkingtime": stationduration, "id": id, "lat":lat, "lon":lon}
            stationstring = "Station \"{}\" is {}m away, and it will take {} to walk there.".format(stationname, stationdistance, stationduration)
            #print(stationstring)
            for departure in departure["NextDepartures"]["Dep"]:
                departuretime = departure["time"]
                direction = departure["Transport"]["dir"]
                line = departure["Transport"]["name"]
                category = departure["Transport"]["At"]["category"]
                ttl = str(datetime.strptime(departuretime, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(datetime.now().isoformat(),"%Y-%m-%dT%H:%M:%S.%f")).split(".")[0]

                departurestring = "At this station you will find {} {}, going in the direction of \"{}\" on {}. It departs in {}.".format(category, line, direction, departuretime, ttl)
                stationdict[id]["departuretime"] = departuretime
                stationdict[id]["direction"] = direction
                stationdict[id]["line"] = line
                #print(departurestring)
                departuredict = {"category": category, "line": line, "direction": direction, "departuretime": departuretime, "timetoleave": ttl}

            #finaldict =
        return stationdict

    def getbusstops(self, time=datetime.now()):
        address = Settings().getsettings("Location")["full"]
        self.logger("Using address: {}".format(address))
        lat, lon = Location().geocode(address)
        maindict = self.busstop(time, lat, lon, radius="500")
        return maindict

    def checkprefstop(self, lat, lon):
        # checking if preferred stop is within 500 meters of current location
        maindict = self.busstop(datetime.now(), lat, lon, radius="500")
        if maindict:
            buslat = float(Settings().getsettings("Personalia", "busstop")["coordinates"]["x"])
            buslon = float(Settings().getsettings("Personalia", "busstop")["coordinates"]["y"])
            for id in maindict:
                stoplat = maindict[id]["lat"]
                stoplon = maindict[id]["lon"]
                if buslat == stoplat and buslon == stoplon:
                    return True
        return False

    def nextbus(self, busid, numberofbusses=1):
        url = "https://transit.api.here.com/v3/multiboard/by_stn_ids.json"
        time = datetime.now()
        parameters = {"app_id": api_id,
                      "app_code": api_key,
                      "stnIds":busid,
                      "time": time.isoformat()}
        result = requests.get(url, params=parameters).json()
        for x in range(0, numberofbusses):
            departure = result["Res"]["MultiNextDepartures"]["MultiNextDeparture"][0]["NextDepartures"]["Dep"][x]
            stationname = departure["Stn"]["name"]
            departuretime = departure["time"]
            direction = departure["Transport"]["dir"]
            line = departure["Transport"]["name"]

        maindict = {"name":stationname, "departure":departuretime, "direction":direction, "line":line}
        return maindict

    def get_route(self, address="pensylvania avenue 14", time=datetime.now(), arrival_choice=0):
        # get home address
        address = Settings().getsettings("Personalia", "Address")["full"]

        # get preferred busstop coordinates
        lat = Settings().getsettings("Personalia", "busstop")["coordinates"]["x"]
        lon = Settings().getsettings("Personalia", "busstop")["coordinates"]["y"]
        dep_coords = "{}, {}".format(lat, lon)
        # get preferred busstop name
        name = Settings().getsettings("Personalia", "busstop")["name"]
        #
        realdeparture = time
        #get actual route
        routelist = self.routing(dep_coords=dep_coords, time=realdeparture, arrival_choice=arrival_choice)
        for section in routelist:
            self.logger(section)
        return routelist

    def builder(self, type):
        result = {}
        if type == "nextbus":
            busid = "215150824" # grab busid from store
            nextbus = self.nextbus(busid) # looks like {'line': '73', 'direction': 'Maarssen via Utrecht CS', 'departure': '2020-01-19T07:45:00', 'name': 'Zeist, De Dreef/Panweg'}
            interpretation = {"title": "!timeuntil:departure", "subtext": "line","main": {"text":"direction"}}
            resultdict = {"data":nextbus, "metadata":interpretation}
            result["transit"] = resultdict
            return result
