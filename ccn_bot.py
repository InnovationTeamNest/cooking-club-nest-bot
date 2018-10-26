# -*- coding: utf-8 -*-

import datetime
import logging as log
import time

import telegram
from google.cloud import datastore

from google_calendar import get_assigned_people
from secrets import ccn_bot_token, group_chat_id, groups
from common import MAX_ATTEMPTS

ccn_bot = telegram.Bot(ccn_bot_token)


def check_turn(counter=0):
    today = time.strftime(str("%d/%m/%Y"))

    try:
        res = day_already_checked(today)
        log.info(f"Already checked? {repr(res)}")
        if res:
            return 200
    except Exception as ex:
        log.info("Unable to fetch data from Datastore... No notification "
                 "for today... What a pity!")
        log.info(ex)
        return 424

    log.info(f"Checking turn for day {today} at {str(time.strftime(str('%c')))}")
    assigned_group = fetch_turn_calendar(datetime.date.today(), counter)

    try:
        log.info(f"Today's turn: {assigned_group}")
        send_notification(today, assigned_group)
    except Exception as ex:
        log.info("Unable to fetch data from Google Calendar... "
                 "No notification for today... What a pity!")
        log.info(ex)
        return 424

    return 200


def fetch_turn_calendar(date, counter):
    try:
        offset = date.day - datetime.date.today().day
        assigned_group = get_assigned_people(offset)
    except Exception as ex:
        log.info("Unable to fetch data from Google Calendar... "
                 "No notification for today... What a pity!")
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            fetch_turn_calendar(date, counter + 1)
        log.info(ex)
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
                message = f"Salve! Oggi il turno di pulizie è del gruppo *{assigned_group}*," \
                          f" composto da {', '.join(people)}.\n\nBuona fortuna! 👨🏻‍🍳"
            else:
                message = f"Salve! Oggi dovranno scontare il proprio richiamo {', '.join(people)}" \
                          f".\n\nBuona fortuna!"
            sent_message = ccn_bot.send_message(chat_id=group_chat_id, text=message, parse_mode="Markdown")
            ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
        # the date can be considered processed in any case
        push_data(date, assigned_group)
    except Exception as ex:
        log.info("Unable to send Telegram notification. No notification for "
                 "today... What a pity!")
        log.info(ex)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            send_notification(date, assigned_group, counter + 1)


def weekly_notification(date):
    try:
        header = "Salve! Questa settimana toccherà ai seguenti gruppi: "
        date = date - datetime.timedelta(days=1)
        for i in range(0, 7):
            date = date + datetime.timedelta(days=1)
            assigned_group = str(fetch_turn_calendar(date, 0))
            try:
                if assigned_group is None:
                    message = f"\n{translate_date(date)} - Nessuno"
                else:
                    people = groups[assigned_group]
                    message = f"\n {translate_date(date)} - Gruppo {assigned_group}: " \
                              f"{', '.join(people)}"
            except Exception as ex:
                log.info("Unable to fetch data from Google Calendar... "
                         "No notification for today... What a pity!")
                log.info(ex)

        sent_message = ccn_bot.send_message(chat_id=group_chat_id, text=f"{header} {message}")
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
    except Exception as ex:
        log.info("Unable to send Telegram notification. No notification for "
                 "today... What a pity!")
        log.info(ex)
