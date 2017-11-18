# -*- coding: utf-8 -*-

from oauth2client.client import GoogleCredentials
from apiclient import discovery
import datetime
import httplib2
import secrets


def get_credentials_from_token():
    return GoogleCredentials(secrets.access_token, secrets.client_id,
                             secrets.client_secret, secrets.refresh_token,
                             secrets.token_expiry, secrets.token_uri,
                             secrets.user_agent)


def get_google_calendar_service():
    credentials = get_credentials_from_token()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)


def get_today_assigned_people():
    calendar_service = get_google_calendar_service()
    now = datetime.datetime.utcnow()
    endday = now.replace(hour=21, minute=0, second=0)
    now = now.isoformat() + "+01:00"
    endday = endday.isoformat() + "+01:00"
    eventResult = calendar_service.events().list(calendarId='primary', timeMax=endday, timeMin=now,
                                                 maxResults=1, singleEvents=True,
                                                 orderBy='startTime').execute()
    events = eventResult.get('items')

    return str(events[0].get("summary"))
