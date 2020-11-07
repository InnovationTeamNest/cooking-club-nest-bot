import logging as log
import time

from telegram.ext import Dispatcher

from common import MAX_ATTEMPTS
from cron.helpers import ccn_bot
from secrets import url, ccn_bot_token


def dispatcher_setup():
    """Ogni comando necessita di un CommandHandler appropriato,
    che prende in ingresso un metodo con due parametri, bot e update"""

    global dispatcher
    dispatcher = Dispatcher(bot=ccn_bot, workers=0, use_context=True)


def process(update, counter=0):
    try:
        dispatcher.process_update(update)
    except NameError as ex:
        dispatcher_setup()
        ccn_bot.set_webhook(url + ccn_bot_token)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            process(update, counter + 1)
        else:
            log.critical("Failed to initialize Webhook instance")
            log.critical(ex)
    except Exception as ex:
        log.critical("An error has occurred while handling the update")
        log.critical(ex)