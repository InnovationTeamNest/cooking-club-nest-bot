import json

import telegram
import webapp2
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

from actions import start, today_turn, get_group, help, defaultResponse
from secrets import token_url, ccn_bot_token

ccn_bot = telegram.Bot(ccn_bot_token)


class WebHookHandler(webapp2.RequestHandler):
    def get(self):
        dispatcherSetup()
        s = ccn_bot.setWebhook(token_url)
        if s:
            self.response.write("Webhook setted")
        else:
            self.response.write("Webhook setup failed")


class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        # Retrieve the message in JSON and then transform it to Telegram object
        body = json.loads(self.request.body)
        update = telegram.update.Update.de_json(body, ccn_bot)
        webhook(update)

def webhook(update):
    dispatcher.process_update(update)


def dispatcherSetup():
    global dispatcher
    dispatcher = Dispatcher(bot=ccn_bot, update_queue=None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('oggi', today_turn))
    dispatcher.add_handler(CommandHandler("gruppo", get_group, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(Filters.text, defaultResponse))
    return dispatcher