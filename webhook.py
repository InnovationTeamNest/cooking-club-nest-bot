from __future__ import unicode_literals

import json
import logging as log
import time

import telegram
import webapp2
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from secrets import url, ccn_bot_token

ccn_bot = telegram.Bot(ccn_bot_token)

MAX_ATTEMPTS = 5


class WebHookHandler(webapp2.RequestHandler):
    def get(self):
        dispatcher_setup()  # Ogni volta che si carica una nuova versione, bisogna rifare il setup del bot!
        res = ccn_bot.setWebhook(url + ccn_bot_token)
        if res:
            self.response.write("Success!")
        else:
            self.response.write("Webhook setup failed...")


class UpdateHandler(webapp2.RequestHandler):
    def post(self):  # Gli update vengono forniti da telegram in Json e vanno interpretati
        webhook(telegram.Update.de_json(json.loads(self.request.body), ccn_bot), 0)


# Ogni comando necessita di un CommandHandler appropriato,
# che prende in ingresso un metodo con due parametri, bot e update
def dispatcher_setup():
    import actions
    import turn_actions

    global dispatcher
    dispatcher = Dispatcher(bot=ccn_bot, update_queue=None, workers=0)

    dispatcher.add_handler(CommandHandler("start", actions.start))
    dispatcher.add_handler(CommandHandler("help", actions.help))
    dispatcher.add_handler(CommandHandler("info", actions.info))
    dispatcher.add_handler(CommandHandler("direttivo", actions.direttivo))
    dispatcher.add_handler(CommandHandler("cerca", actions.search, pass_args=True))
    dispatcher.add_handler(CommandHandler("gruppo", actions.group, pass_args=True))

    dispatcher.add_handler(CommandHandler("oggi", turn_actions.today_turn))
    dispatcher.add_handler(CommandHandler("domani", turn_actions.tomorrow_turn))
    dispatcher.add_handler(CommandHandler("turno", turn_actions.turn_keyboard))

    dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, actions.text_filter))
    dispatcher.add_handler(CallbackQueryHandler(turn_actions.inline_handler))


def webhook(update, counter):
    try:
        dispatcher.process_update(update)
    except Exception as ex:
        dispatcher_setup()
        ccn_bot.setWebhook(url + ccn_bot_token)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            webhook(update, counter + 1)
        else:
            log.critical("Failed to initialize Webhook instance" + ex.message)
