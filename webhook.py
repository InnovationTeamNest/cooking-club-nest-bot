import logging as log
import time

import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from secrets import url, ccn_bot_token

bot = telegram.Bot(ccn_bot_token)

MAX_ATTEMPTS = 5


# Ogni comando necessita di un CommandHandler appropriato,
# che prende in ingresso un metodo con due parametri, bot e update
def dispatcher_setup():
    import actions
    import turn_actions

    global dispatcher
    dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)

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


def process(update, counter=0):
    try:
        dispatcher.process_update(update)
    except NameError as ex:
        dispatcher_setup()
        bot.setWebhook(url + ccn_bot_token)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            process(update, counter + 1)
        else:
            log.critical("Failed to initialize Webhook instance")
            log.critical(ex)
    except Exception as ex:
        log.critical("An error has occurred while handling the update")
        log.critical(ex)
