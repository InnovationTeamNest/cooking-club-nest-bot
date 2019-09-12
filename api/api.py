# -*- coding: utf-8 -*-
import datetime

from google.cloud import datastore

from api.google_api import get_google_calendar_service, get_google_sheets_service
from common import MAX_GROUPS
from secrets import spreadsheet_id


# Metodi per l'ottenimento dei gruppi

def get_group(id):
    range_ = f"Gruppi!A{id}:H{id}"
    data = get_google_sheets_service().spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()

    try:
        if data["values"][0][0] == "NONE":
            return None
        return data["values"][0]
    except KeyError as ex:
        return None


def get_multiple_groups(start, end):
    range_ = f"Gruppi!A{start}:H{end}"
    data = get_google_sheets_service().spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()

    for group_number in range(len(data["values"])):
        if data["values"][group_number][0] == "NONE":
            data["values"][group_number] = None

    try:
        return data["values"]
    except KeyError as ex:
        return None


def get_number_members_tuple():
    result = []
    people = get_multiple_groups(1, MAX_GROUPS)

    i = 1
    for group in people:
        if group is not None:
            for person in group:
                result.append((i, person))
        i = i + 1
    return result


# Metodi per la memorizzazione della data

def push_data(date, assigned_group):
    client = datastore.Client()
    key = client.key('CheckedDay', date)
    entity = datastore.Entity(key=key)
    entity['day'] = date
    entity['people'] = assigned_group
    client.put(entity)


def day_already_checked(date):
    client = datastore.Client()
    return client.get(client.key('CheckedDay', date))


def get_day_event(offset):
    calendar_service = get_google_calendar_service()
    now = datetime.datetime.utcnow() + datetime.timedelta(days=offset)
    endday = now.replace(hour=21, minute=0, second=0)
    now = now.isoformat() + "+01:00"
    endday = endday.isoformat() + "+01:00"
    eventresult = calendar_service.events().list(
        calendarId='primary', timeMax=endday, timeMin=now,
        maxResults=1, singleEvents=True, orderBy='startTime').execute()
    events = eventresult.get('items')
    return events[0]
