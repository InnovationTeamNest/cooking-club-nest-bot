# -*- coding: utf-8 -*-

import google.appengine.ext.ndb as ndb
import logging as log
import time
import telegram
import json

from google_calendar import get_today_assigned_people
from secrets import ccn_bot_token, group_chat_id, groups, url
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

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
        log.error(ex.message)


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
            send_notification(date, assigned_group, counter + 1)

def dispatcherSetup():
    dispatcher = Dispatcher(bot=telegram.Bot(ccn_bot_token), update_queue=None, workers=0)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('oggi', today_turn))
    dispatcher.add_handler(CommandHandler("gruppo", get_group, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    return dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Ciao! Questo è il bot del Cooking Corner del Nest"
                     + ". Per iniziare scrivi un comando o scrivi /help per aiuto.")

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="/oggi - Mostra il turno di oggi")
    bot.send_message(chat_id=update.message.chat_id, text="/gruppo NUMEROGRUPPO - Mostra i membri di un certo gruppo")


def today_turn(bot, update):
    assigned_group = get_today_assigned_people()
    try:
        #try:
        #assigned_group = TEMP #get_today_assigned_people()
        #except Exception as ex:
        #    log.error("Fetch data error!\n" + ex.message)

        if assigned_group:
            people = groups[assigned_group]
            message = "Oggi il turno è del gruppo " + assigned_group + ", composto da " + \
                      ", ".join(people)
            bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)
        bot.sendMessage(update.message.chat_id, "Mi dispiace, in questo momento non riesco a ottenere i turni di oggi.")


def get_group(bot, update, args):
    args = args[0]
    try:
        people = groups[str(args)]
        message = "Il gruppo " + str(args) + " è formato da " + \
                  ", ".join(people) + "."
        bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        bot.sendMessage(update.message.chat_id,
                        "Non ho capito bene il numero del gruppo. I gruppi possibili vanno da 1 a 40.")
        log.error(ex.message)

def echo(bot, update):
    bot.sendMessage(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")

def setwebhook(self):
        dispatcherSetup()
        s = telegram.Bot(ccn_bot_token).setWebhook(url + '/' + ccn_bot_token)
        if s:
            self.response.write("Webhook setted")
        else:
            self.response.write("Webhook setup failed")

def webhook_handler(self):
    # Retrieve the message in JSON and then transform it to Telegram object
    body = json.loads(self.request.body)
    update = telegram.Update.de_json(body)
    webhook(update)


def webhook(update):
    global dispatcher
    dispatcher.process_update(update)


def main():
    pass


if __name__ == '__main__':
    main()
