import datetime
import logging as log
import time

from telegram import Bot
from telegram.ext import Dispatcher

from api import api
from common import MAX_ATTEMPTS, flatten, stringify, MAX_GROUPS
from secrets import group_chat_id, ccn_bot_token, url

ccn_bot = Bot(ccn_bot_token)


def fetch_turn_calendar(date, counter):
    log.info(f"Starting turn fetching helper at {date} {counter}")

    try:
        offset = (date - datetime.date.today()).days
        event = api.get_day_event(offset)
    except Exception as ex:
        log.info("Exception during Datastore data retrieval")
        log.critical(ex)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            return fetch_turn_calendar(date, counter + 1)
        else:
            raise Exception

    groups = []
    for item in str(event.get("summary")).split(" "):
        try:
            groups.append(int(item))
        except ValueError:
            pass

    log.info(f"Retrieved data: {groups}")

    return tuple(groups)


def get_next_days_turns():
    try:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_after = datetime.date.today() + datetime.timedelta(days=2)

        return f"domani *{stringify(fetch_turn_calendar(tomorrow, 0))}*," \
               f" dopodomani *{stringify(fetch_turn_calendar(tomorrow_after, 0))}*."
    except Exception as ex:
        log.critical(ex)
        return "_da definire_"


def get_message_string(assigned_group):
    people = flatten(api.get_group_by_id(assigned_group))
    next_days_turns = get_next_days_turns()
    if type(assigned_group) is tuple:
        return f"Salve! Oggi il turno di pulizie è dei gruppi" \
               f" *{stringify(assigned_group)}*, composti da:" \
               f"\n\n{', '.join(people)}." \
               f"\n\nBuona fortuna! 👨🏻‍🍳" \
               f"\n\nTurni dei prossimi giorni: {next_days_turns}"
    elif int(assigned_group) < MAX_GROUPS:
        return f"Salve! Oggi il turno di pulizie è del gruppo" \
               f" *{assigned_group}*, composto da:" \
               f"\n\n{', '.join(people)}." \
               f"\n\nBuona fortuna! 👨🏻‍🍳" \
               f"\n\nTurni dei prossimi giorni: {next_days_turns}"
    elif int(assigned_group) > 100:
        try:
            original_group = int(people[0])
        except Exception:
            original_group = -1

        if original_group == -1:
            return f"Salve! Oggi non sarà una bella giornata per {', '.join(people[1:])}" \
                   f", che {'dovranno' if len(people[1:]) > 1 else 'dovrà'}" \
                   f" scontare il proprio *richiamo*.\n\nBuona fortuna! 🔪👮🏻‍♂️"
        elif 0 < original_group <= MAX_GROUPS:
            original_group_people = api.get_group_by_id(original_group)
            return f"Salve! Oggi il turno di pulizie è del gruppo {original_group}, composto da " \
                   f"{', '.join(original_group_people)}.\n\nIn aggiunta {', '.join(people[1:])}" \
                   f" {'dovranno' if len(people[1:]) > 1 else 'dovrà'} scontare il proprio *richiamo*." \
                   f"\n\nBuona fortuna! 🔪👮🏻‍♂️"
        else:
            raise AttributeError


def send_cron_notification(date, assigned_group, counter=0):
    log.info(f"Starting notification helper at {date}, {assigned_group}, {counter}")
    try:
        if assigned_group:
            message = get_message_string(assigned_group)
        else:
            raise AttributeError
        sent_message = ccn_bot.send_message(chat_id=group_chat_id, text=message, parse_mode="Markdown")
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
        # The date can be considered processed in any case
        api.set_day_checked(date, assigned_group)

    except Exception as ex:
        log.info("Error during notification crafting.")
        log.critical(ex)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            send_cron_notification(date, assigned_group, counter + 1)
        else:
            raise Exception


def dispatcher_setup():
    """Ogni comando necessita di un CommandHandler appropriato,
    che prende in ingresso un metodo con due parametri, bot e update"""

    global dispatcher
    dispatcher = Dispatcher(bot=ccn_bot, update_queue=None, workers=0, use_context=True)

    # dispatcher.add_handler(CommandHandler("start", actions.start))
    # dispatcher.add_handler(CommandHandler("help", actions.help))
    # dispatcher.add_handler(CommandHandler("info", actions.info))
    # dispatcher.add_handler(CommandHandler("cerca", actions.search, pass_args=True))
    # dispatcher.add_handler(CommandHandler("gruppo", actions.group, pass_args=True))
    #
    # dispatcher.add_handler(CommandHandler("oggi", turn_actions.today_turn))
    # dispatcher.add_handler(CommandHandler("domani", turn_actions.tomorrow_turn))
    # dispatcher.add_handler(CommandHandler("turno", turn_actions.turn_keyboard))
    #
    # dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, actions.text_filter))
    # dispatcher.add_handler(CallbackQueryHandler(turn_actions.inline_handler))


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
