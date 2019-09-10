# -*- coding: utf-8 -*-

from apiclient import discovery
from google.auth import app_engine


def get_google_calendar_service():
    credentials = app_engine.Credentials(scopes=['https://www.googleapis.com/auth/calendar.readonly'])
    # credentials = service_account.Credentials.from_service_account_file(
    #    'credentials.json').with_scopes(['https://www.googleapis.com/auth/calendar.readonly'])
    return discovery.build('calendar', 'v3', credentials=credentials)


def get_google_sheets_service():
    credentials = app_engine.Credentials(scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    # credentials = service_account.Credentials.from_service_account_file(
    #    'credentials.json').with_scopes(['https://www.googleapis.com/auth/spreadsheets.readonly'])
    return discovery.build('sheets', 'v4', credentials=credentials)
