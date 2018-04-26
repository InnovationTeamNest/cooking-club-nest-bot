# -*- coding: utf-8 -*-

import logging as log
import time

import google.appengine.ext.ndb as ndb
import telegram

from google_calendar import getAssignedPeople
from secrets import ccn_bot_token, group_chat_id, groups

ccn_bot = telegram.Bot(ccn_bot_token)

MAX_ATTEMPTS = 5


def checkTurn(counter=0):
    today = time.strftime("%d/%m/%Y")

    try:
        res = dayAlreadyChecked(today)
        log.info("Already checked? " + repr(res))
        if res:
            return
    except Exception as ex:
        log.error("Unable to fetch data from Datastore... No notification "
                  "for today... What a pity!")
        log.error(ex.message)
        return

    log.info("Checking turn for day " + today + " at " +
             str(time.strftime("%c")))
    assigned_group = fetchTurnCalendar(0, counter)
    try:
        log.info("Today's turn: " + assigned_group)
        sendNotification(today, assigned_group)
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")
        log.error(ex.message)


def fetchTurnCalendar(offset, counter):
    try:
        assigned_group = getAssignedPeople(offset)
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            checkTurn(counter + 1)
        log.error(ex.message)
        return
    return assigned_group

# this Datastore class is required to keep track of processed days

class CheckedDay(ndb.Model):
    day = ndb.StringProperty(indexed=False)
    people = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


def dayAlreadyChecked(date):
        return ndb.Key('CheckedDay', date).get()


def sendNotification(date, assigned_group, counter=0):
    try:
        # there could be days with no turn. It is useless to send a message to
        # the group in this case.
        if assigned_group:
            people = groups[assigned_group]
            # TODO Improve and add Easter egg...

            if (int(assigned_group) < 100):
                message = "Salve! Oggi il turno di pulizie è del gruppo " + assigned_group + ", composto da " + \
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
            time.sleep(2**counter)
            sendNotification(date, assigned_group, counter + 1)


def main():
    pass


if __name__ == '__main__':
    main()
