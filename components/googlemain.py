from __future__ import print_function
import datetime, pytz
import pickle
import os.path
import traceback
import requests
import json
import sys
import configobj

from .google.service import Service
from sortedcontainers import SortedDict
from time import sleep
from components.settings import Settings

#### DO NOT CHANGE THESE VALUES ####

client_id = Settings().getsettings("Credentials", "googleAppId")
client_secret = Settings().getsettings("Credentials", "googleAppSecret")


class google:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.calendars = []
        self.calendar_names = {}
        self.realevents = SortedDict({})
        self.isfree = False
        self.creds = {}

    def timecleaner(self, time):
        if "+" in time:
            time = time[::-1].replace(":", "")[::-1]
            time = datetime.datetime.strptime(time, "%Y-%m-%dT%H%M%S%z")
        else:
            time = datetime.datetime.strptime(time, "%Y-%m-%d")
            time = pytz.timezone("Europe/Amsterdam").localize(time)
        return time

    def timedifference(self, duration):
        print(duration)
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        timelist = []
        if days != 0:
            timelist.append(days)
        if hours != 0:
            timelist.append(hours)
        if minutes != 0:
            timelist.append(minutes)
        if seconds != 0:
            timelist.append(seconds)
            #pass
        print(timelist)
        return timelist

    def requestusercode(self, client_id):
        data = {
            'client_id': client_id,
            'scope': 'https://www.googleapis.com/auth/calendar'
            }
        url = 'https://accounts.google.com/o/oauth2/device/code'
        response = json.loads(requests.post(url, data=data).text)
        return response

    def poll(self, device_code, interval):
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': device_code,
            'grant_type': "http://oauth.net/grant_type/device/1.0"
            }
        url = 'https://oauth2.googleapis.com/token'
        while True:
            response = json.loads(requests.post(url, data=data).text)
            if "access_token" in response.keys():
                # figure out when the token expires:
                expiredate = datetime.datetime.now() + datetime.timedelta(seconds=response["expires_in"])
               # fill creds with infomration to figure out if accesstoken is expired or not
                olddict = {}
                with open("components/google/credentials.json", "w") as f:
                    olddict["access_token"] = response["access_token"]
                    olddict["refresh_token"] = response["refresh_token"]
                    olddict["expires_at"] = str(expiredate)
                    tmpdict = {"installed":olddict}
                    f.write(json.dumps(tmpdict))
                return olddict["access_token"]
            else:
                print("not yet..")
                sleep(interval)

    def refreshtoken(self, creddict):
        refresh_token = creddict["refresh_token"]
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': "refresh_token"
            }
        url = 'https://oauth2.googleapis.com/token'
        response = json.loads(requests.post(url, data=data).text)
        expiredate = datetime.datetime.now() + datetime.timedelta(seconds=response["expires_in"])
        with open("components/google/credentials.json", "w") as f:
            creddict["access_token"] = response["access_token"]
            creddict["expires_at"] = str(expiredate)
            tmpdict = {"installed":creddict}
            f.write(json.dumps(tmpdict))
        return creddict["access_token"]

    def getcreds(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = os.path.exists("components/google/credentials.json")
        #creddict = json.loads(open("components/google/credentials.json").read())["installed"]

        if creds:
            print("creds found!")
            creddict = json.loads(open("components/google/credentials.json").read())["installed"]
            now = datetime.datetime.now()
            expiredate = datetime.datetime.strptime(creddict["expires_at"],"%Y-%m-%d %H:%M:%S.%f")
            if now < expiredate:
                print("Getting from credentials.json")
                return creddict["access_token"]
            else:
                print("creds need to be refreshed!")
                creds = self.refreshtoken(creddict)
                return creds
        # If there are no (valid) credentials available, let the user log in.
        if not creds:
            print("No creds found!")
            response = self.requestusercode(client_id)
            print("Please go to {} and enter this code: {}".format(response["verification_url"], response["user_code"]))
            device_code, interval = response["device_code"], response["interval"]
            creds = self.poll(device_code, interval)
            print("Got access token, ready to rumble.")
            return creds
                #creds = flow.run_local_server(port=0)
            # Save the credentials for the next run

    def main(self, numberofevents = 1):
        creds = self.getcreds()
        service = Service(creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        #print("getting calendars")
        page_token = None
        while True:
            calendar_list = service.calendarList()
            #sys.exit()
            for calendar_list_entry in calendar_list['items']:
                id = calendar_list_entry["id"]
                name = calendar_list_entry['summary']
                #print("calendar \"{}\" has id: {}".format(name ,id))
                self.calendars.append(id)
                self.calendar_names[id] = name
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        #print('Getting the upcoming 10 events')
        
        for calendar_id in self.calendars:
            events_result = service.eventList(calendarId=calendar_id, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime')
            events = events_result.get('items', [])

            if not events:
                #print('No upcoming events found for calendar {}'.format(self.calendar_names[calendar_id]))
                pass
            for index, event in enumerate(events): #[:numberofevents + 1]):
                
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                try:
                    nextstart = events[index + 1]['start'].get('dateTime', event['start'].get('date'))
                    nextstart = self.timecleaner(nextstart)
                    event["nextstart"] = nextstart # when the next event starts
                except Exception as e:
                    pass
                start = self.timecleaner(start)
                end = self.timecleaner(end)
                event["start"] = start
                event["end"] = end
                #event["until_next"] = timelist # so you know how long it takes until the next event. not implemented on flutter yet.
                self.realevents[start] = event
                #print(start, event['summary'])

        now = pytz.timezone("Europe/Amsterdam").localize(datetime.datetime.now())
        self.isfree = not (start < now < end)
        sortedlist = list(self.realevents.keys())
        for time in sortedlist:
            eventsummary = self.realevents[time]["summary"]
            #print(time, eventsummary)
            
        return sortedlist, self.realevents
