import webapp2
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

import ccn_bot
import telegram
import json

from actions import start, today_turn, get_group, help, defaultResponse
from secrets import url, ccn_bot_token


class WebHookSetter(webapp2.RequestHandler):
    def setwebhook(self):
        dispatcherSetup()
        s = telegram.Bot(ccn_bot_token).setWebhook(url + '/' + ccn_bot_token)
        if s:
            self.response.write("Webhook setted")
        else:
            self.response.write("Webhook setup failed")

class WebHookHandler(webapp2.RequestHandler):
    def webhook_handler(self):
        # Retrieve the message in JSON and then transform it to Telegram object
        body = json.loads(self.request.body)
        update = telegram.Update.de_json(body)
        webhook(update)

def webhook(update):
    global dispatcher
    dispatcher.process_update(update)


def dispatcherSetup():
    dispatcher = Dispatcher(bot=telegram.Bot(ccn_bot_token), update_queue=None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('oggi', today_turn))
    dispatcher.add_handler(CommandHandler("gruppo", get_group, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(Filters.text, defaultResponse))
    return dispatcher