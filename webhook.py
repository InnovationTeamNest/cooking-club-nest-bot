import json

import telegram
import webapp2
from telegram.ext import Dispatcher, CommandHandler

from actions import start, todayTurn, getGroup, help, tomorrowTurn, direttivo, info
from secrets import url, ccn_bot_token

ccn_bot = telegram.Bot(ccn_bot_token)


class WebHookHandler(webapp2.RequestHandler):
    def get(self):
        dispatcherSetup()
        res = ccn_bot.setWebhook(url + ccn_bot_token)
        if res:
            self.response.write("Webhook set up!")
        else:
            self.response.write("Webhook setup failed...")


class UpdateHandler(webapp2.RequestHandler):
    def post(self):
        webhook(telegram.Update.de_json(json.loads(self.request.body), ccn_bot))


def webhook(update):
    dispatcher.process_update(update)


def dispatcherSetup():
    global dispatcher
    dispatcher = Dispatcher(bot=ccn_bot, update_queue=None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("oggi", todayTurn))
    dispatcher.add_handler(CommandHandler("domani", tomorrowTurn))
    dispatcher.add_handler(CommandHandler("gruppo", getGroup, pass_args=True))
    dispatcher.add_handler(CommandHandler("direttivo", direttivo))
    # dispatcher.add_handler(MessageHandler(Filters.text, defaultResponse))
    return dispatcher