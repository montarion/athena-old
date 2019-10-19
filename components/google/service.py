import requests, json
from unidecode import unidecode

class Service:
    def __init__(self, token):
        self.access_token = token


    def calendarList(self):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token)
            }
        url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
        response = json.loads(requests.get(url, headers=headers).text)
        
        return response

    def eventList(self, calendarId, **kwargs):
            maxResults = kwargs["maxResults"]
            timeMin = kwargs["timeMin"]
            orderBy = kwargs["orderBy"]
            headers = {
                "Authorization": "Bearer {}".format(self.access_token),
            }
            params = {
                "maxResults": str(maxResults),
                "singleEvents": "True",
                "timeMin": str(timeMin),
                "orderBy": str(orderBy),
                "showDeleted": "False"
                }

            url = "https://www.googleapis.com/calendar/v3/calendars/{}/events".format(calendarId)
            response = json.loads(unidecode(requests.get(url, headers=headers, params=params).text))
            return response

