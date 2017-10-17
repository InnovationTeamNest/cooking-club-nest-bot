import argparse
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

APPLICATION_NAME = 'Google Calendar API Python Quickstart'
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
# Try to add other scopes
CREDENTIAL_FILE = "calendar-python-quickstart.json"


def get_credentials():
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CREDENTIAL_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        credentials = tools.run_flow(flow, store, flags)
        print("Storing credentials to " + credential_path)

    return credentials


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + "Z"  # Z indicates UTC time
    print("Getting the upcoming 10 events...")

    eventsResult = service.events().list(calendarId='primary', timeMin=now,
                                         maxResults=10, singleEvents=True,
                                         orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()
