# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import logging as log
import time

import google.appengine.ext.ndb as ndb
import telegram

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
        log.info("Already checked? " + repr(res))
        if res:
            return
    except Exception as ex:
        log.error("Unable to fetch data from Datastore... No notification "
                  "for today... What a pity!")
        log.error(ex.message)
        return

    log.info("Checking turn for day " + today + " at " + str(time.strftime(str("%c"))))
    assigned_group = fetch_turn_calendar(datetime.date.today(), counter)

    try:
        log.info("Today's turn: " + assigned_group)
        send_notification(today, assigned_group)
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")
        log.error(ex.message)


def fetch_turn_calendar(date, counter):
    try:
        offset = date.day - datetime.date.today().day
        assigned_group = get_assigned_people(offset)
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            fetch_turn_calendar(date, counter + 1)
        log.error(ex.message)
        return
    return assigned_group


# this Datastore class is required to keep track of processed days
class CheckedDay(ndb.Model):
    day = ndb.StringProperty(indexed=False)
    people = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


def day_already_checked(date):
    return ndb.Key('CheckedDay', date).get()


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
        CheckedDay(id=date, day=date, people=assigned_group).put()
    except Exception as ex:
        log.error("Unable to send Telegram notification. No notification for "
                  "today... What a pity!")
        log.error(ex.message)
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
                log.error("Unable to fetch data from Google Calendar... "
                          "No notification for today... What a pity!")
                log.error(ex.message)
        sent_message = ccn_bot.send_message(group_chat_id, message)
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
    except Exception as ex:
        log.error("Unable to send Telegram notification. No notification for "
                  "today... What a pity!")
        log.error(ex.message)


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


def main():
    pass


if __name__ == '__main__':
    main()
