# -*- coding: utf-8 -*-

import google.appengine.ext.ndb as ndb
import logging as log
import time
import telegram

from google_calendar import get_today_assigned_people
from secrets import ccn_bot_token, group_chat_id, groups


MAX_ATTEMPTS = 5


def check_turn(counter=0):
    today = time.strftime("%d/%m/%Y")

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

    log.info("Checking turn for day " + today + " at " +
             str(time.strftime("%c")))

    try:
        assigned_group = get_today_assigned_people()
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")
        if counter < MAX_ATTEMPTS:
            time.sleep(2**counter)
            check_turn(counter + 1)
        log.error(ex.message)
        return
    try:
        log.info("Today's turn: " + assigned_group)
        send_notification(today, assigned_group)
    except Exception as ex:
        log.error("Unable to fetch data from Google Calendar... "
                  "No notification for today... What a pity!")


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
            ccn_bot = telegram.Bot(ccn_bot_token)
            # TODO Improve and add Easter egg...

            message = "Salve! Oggi il turno di pulizie è di " + \
                      ", ".join(people) + ".\n\nBuona fortuna!"
            ccn_bot.sendMessage(group_chat_id, message)
        # the date can be considered processed in any case
        CheckedDay(id=date, day=date, people=assigned_group).put()
    except Exception as ex:
        log.error("Unable to send Telegram notification. No notification for "
                  "today... What a pity!")
        log.error(ex.message)
        if counter < MAX_ATTEMPTS:
            time.sleep(2**counter)
            send_notification(date, assigned_group, counter + 1)

def main():
    pass


if __name__ == '__main__':
    main()
