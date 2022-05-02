# -*- coding: utf-8 -*-
import datetime

import requests
from google.cloud import datastore

from api.google_api import get_google_calendar_service, get_google_sheets_service
from common import MAX_GROUPS
from secrets import spreadsheet_id, calendar_id


# Metodi per l'ottenimento dei gruppi

def get_group_by_id(id):
    if type(id) is tuple:
        data = []
        for subid in id:
            data.append(get_group_by_id(subid))
        return data

    elif type(id) is int and id > 0:
        range_ = f"Gruppi!A{id}:E{id}"

        service = get_google_sheets_service()
        data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()

        try:
            if data["values"][0][0] == "NONE":
                return None
            return data["values"][0]
        except KeyError as ex:
            return None

    else:
        return None


def get_groups_by_range(start, end):
    range_ = f"Gruppi!A{start}:E{end}"
    data = get_google_sheets_service().spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()

    for group_number in range(len(data["values"])):
        if data["values"][group_number][0] == "NONE":
            data["values"][group_number] = None

    try:
        return data["values"]
    except KeyError as ex:
        return None


def get_all_group_tuples():
    result = []
    people = get_groups_by_range(1, MAX_GROUPS)

    i = 1
    for group in people:
        if group is not None:
            for person in group:
                result.append((i, person))
        i = i + 1
    return result


# Metodi per la memorizzazione della data

def set_day_checked(date, assigned_group):
    client = datastore.Client()
    key = client.key('CheckedDay', date)
    entity = datastore.Entity(key=key)
    entity['day'] = date
    entity['people'] = str(assigned_group)
    client.put(entity)


def is_day_checked(date):
    client = datastore.Client()
    return client.get(client.key('CheckedDay', date))


# Metodo per l'ottenimento degli eventi da Google Calendar

def get_day_event(offset):
    calendar_service = get_google_calendar_service()
    now = datetime.datetime.utcnow() + datetime.timedelta(days=offset)
    now = now.replace(hour=3, minute=0, second=0, microsecond=0)
    endday = now + datetime.timedelta(hours=18)
    now = now.isoformat() + 'Z'
    endday = endday.isoformat() + 'Z'

    eventresult = calendar_service.events().list(
        calendarId=calendar_id, timeMax=endday, timeMin=now,
        maxResults=1, singleEvents=True, orderBy='startTime').execute()
    events = eventresult.get('items')

    if len(events) <= 0:
        return None
    else:
        return events[0]


# Metodo per ottenere i dati di affluenza dal foglio Google

def get_turnout_data(day: datetime.datetime):
    day_no = day.weekday() + 1

    range_ = f"Affluenza!A{day_no}:G{day_no}"
    data = get_google_sheets_service().spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()

    try:
        return data["values"]
    except KeyError as ex:
        return None
