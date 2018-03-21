import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import argparse
try:
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class CalMain:
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Slack-Cal-Integration'
    CALENDAR_ID = '22opmonkdpao2o2grfgev4fvss@group.calendar.google.com'

    def __init__(self):
        self.credentials = self.get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)
        print('Initialization')

    @staticmethod
    def get_now():
        return datetime.datetime.utcnow().isoformat() + 'Z'

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'mcds-off-day-cred.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)

        return credentials

    def get_incoming_dayoffs(self):
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(
            calendarId=self.CALENDAR_ID, timeMin=self.get_now(), maxResults=100,
            singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        payload = {'items':[]}

        if not events:
            print('No upcoming events found.')
            payload['error'] = 'No upcoming events found.'

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(start, end, event['summary'])
            ret_value = {'summary': event['summary'], 'start': start, 'end': end}
            payload['items'].append(ret_value)

        return payload


    def create_dayoff_event(self, name, start, end, detail=None):
        event = {
            'summary': '{0} is off'.format(name) if detail is None else '{0} is off for {1}'.format(name, detail),
            'start': {'date': start},
            'end': {'date': end}
        }
        self.service.events().insert(calendarId=self.CALENDAR_ID, body=event).execute()


if __name__ == '__main__':
    cal = CalMain()
    # cal.create_dayoff_event('Rayer', '2018-10-3', '2018-10-4', 'Oh my god')
    cal.get_incoming_dayoffs()