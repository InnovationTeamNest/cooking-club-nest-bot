# -*- coding: utf-8 -*-

import datetime
import sys
import time

import telegram
from google.cloud import datastore

from google_calendar import get_assigned_people
from secrets import ccn_bot_token, group_chat_id, groups

ccn_bot = telegram.Bot(ccn_bot_token)

MAX_ATTEMPTS = 5
MAX_MESSAGES = 20
MAX_GROUPS = 22


def check_turn(counter=0):
    today = time.strftime(str("%d/%m/%Y"))

    try:
        res = day_already_checked(today)
        print("Already checked? " + repr(res), file=sys.stderr)
        if res:
            return 200
    except Exception as ex:
        print("Unable to fetch data from Datastore... No notification "
              "for today... What a pity!", file=sys.stderr)
        print(ex, file=sys.stderr)
        return 424

    print("Checking turn for day " + today + " at " + str(time.strftime(str("%c"))), file=sys.stderr)
    assigned_group = fetch_turn_calendar(datetime.date.today(), counter)

    try:
        print("Today's turn: " + assigned_group, file=sys.stderr)
        send_notification(today, assigned_group)
    except Exception as ex:
        print("Unable to fetch data from Google Calendar... "
              "No notification for today... What a pity!", file=sys.stderr)
        print(ex, file=sys.stderr)
        return 424

    return 200


def fetch_turn_calendar(date, counter):
    try:
        offset = date.day - datetime.date.today().day
        assigned_group = get_assigned_people(offset)
    except Exception as ex:
        print("Unable to fetch data from Google Calendar... "
              "No notification for today... What a pity!", file=sys.stderr)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            fetch_turn_calendar(date, counter + 1)
        print(ex, file=sys.stderr)
        return
    return assigned_group


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


def send_notification(date, assigned_group, counter=0):
    try:
        # there could be days with no turn. It is useless to send a message to
        # the group in this case.
        if assigned_group:
            people = groups[assigned_group]
            # TODO Improve and add Easter egg...

            if int(assigned_group) < 100:
                message = "Salve! Oggi il turno di pulizie è del gruppo " \
                          + assigned_group + ", composto da " + \
                          ", ".join(people) + ".\n\nBuona fortuna!"
            else:
                message = "Salve! Oggi dovranno scontare il proprio richiamo " + \
                          ", ".join(people) + ".\n\nBuona fortuna!"
            sent_message = ccn_bot.sendMessage(group_chat_id, message)
            ccn_bot.pinChatMessage(group_chat_id, sent_message.message_id)
        # the date can be considered processed in any case
        push_data(date, assigned_group)
    except Exception as ex:
        print("Unable to send Telegram notification. No notification for "
              "today... What a pity!", file=sys.stderr)
        print(ex, file=sys.stderr)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            send_notification(date, assigned_group, counter + 1)


def weekly_notification(date):
    try:
        message = "Salve! Questa settimana toccherà ai seguenti gruppi: "
        date = date + datetime.timedelta(days=-1)
        for i in range(0, 7):
            date = date + datetime.timedelta(days=1)
            assigned_group = fetch_turn_calendar(date, 0)
            try:
                if assigned_group is None:
                    message_temp = "\n" + \
                                   translate_date(date) + " - Nessuno"
                else:
                    people = groups[assigned_group]
                    message_temp = "\n" + translate_date(date) + \
                                   " - Gruppo " + str(assigned_group) + ": " + \
                                   ", ".join(people)
                message = str(message) + str(message_temp)
            except Exception as ex:
                print("Unable to fetch data from Google Calendar... "
                      "No notification for today... What a pity!", file=sys.stderr)
                print(ex, file=sys.stderr)
        sent_message = ccn_bot.send_message(group_chat_id, message)
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
    except Exception as ex:
        print("Unable to send Telegram notification. No notification for "
              "today... What a pity!", file=sys.stderr)
        print(ex, file=sys.stderr)


def translate_date(date):
    if date.strftime("%A") == "Monday":
        res = "Lunedi"
    elif date.strftime("%A") == "Tuesday":
        res = "Martedi"
    elif date.strftime("%A") == "Wednesday":
        res = "Mercoledi"
    elif date.strftime("%A") == "Thursday":
        res = "Giovedi"
    elif date.strftime("%A") == "Friday":
        res = "Venerdi"
    elif date.strftime("%A") == "Saturday":
        res = "Sabato"
    elif date.strftime("%A") == "Sunday":
        res = "Domenica"
    else:
        res = ""

    res = res + " " + date.strftime("%d").lstrip("0") + "/" + date.strftime("%m").lstrip("0")

    return res
