from __future__ import print_function
import datetime, pytz
import pickle
import os.path
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

    def main(self):
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
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                # print(start)
                # 2019-08-27T18:30:00+02:00
                # remove last : from start time
                if "+" in start:
                    start = start[::-1].replace(":", "")[::-1]
                    start = datetime.datetime.strptime(start, "%Y-%m-%dT%H%M%S%z")
                else:
                    start = datetime.datetime.strptime(start, "%Y-%m-%d")
                    start = pytz.timezone("Europe/Amsterdam").localize(start)
                #print(start)
                #print(event)
                #print("START")
                #print(start)
                self.realevents[start] = event
                #print(start, event['summary'])

        sortedlist = list(self.realevents.keys())
        for time in sortedlist:
            eventsummary = self.realevents[time]["summary"]
            #print(time, eventsummary)
            
        return sortedlist, self.realevents
