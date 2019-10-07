from __future__ import print_function
import datetime, pytz
import pickle
import os.path
import traceback
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from sortedcontainers import SortedDict

# If modifying these scopes, delete the file token.pickle.
class google:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.calendars = []
        self.calendar_names = {}
        self.realevents = SortedDict({})
        self.isfree = False

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
        #newtime = "{} {} {} {}".format(days, hours, minutes, seconds)
        #datetime.datetime.strptime(newtime, 
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

    def main(self, numberofevents = 1):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('components/google/token.pickle'):
            with open('components/google/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'components/google/credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('components/google/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        #print("getting calendars")
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
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
            events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
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
