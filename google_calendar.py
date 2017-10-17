# -*- coding: utf-8 -*-

from oauth2client.client import GoogleCredentials
from apiclient import discovery
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
    # TODO use calendar_service to perform API calls to Google Calendar

    return "Tizio e Caio"
