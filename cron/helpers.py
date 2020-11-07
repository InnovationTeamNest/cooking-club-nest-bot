import datetime
import logging as log
import time
from timeit import Timer

import requests
from telegram import Bot

import common
from api import api
from secrets import group_chat_id, ccn_bot_token

ccn_bot = Bot(ccn_bot_token)


def fetch_turn_calendar(date, counter):
    log.info(f"Starting turn fetching helper at {date} {counter}")

    try:
        offset = (date - datetime.date.today()).days
        event = api.get_day_event(offset)
    except Exception as ex:
        log.info("Exception during Datastore data retrieval")
        log.critical(ex)
        if counter < common.MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            return fetch_turn_calendar(date, counter + 1)
        else:
            raise TimeoutError

    groups = common.calendar_to_int_tuple(event.get("summary"))
    log.info(f"Retrieved data: {groups}")

    return groups


def get_next_days_turns():
    try:
        groups_tomorrow = fetch_turn_calendar(datetime.date.today() + datetime.timedelta(days=1), 0)
        groups_tomorrow_after = fetch_turn_calendar(datetime.date.today() + datetime.timedelta(days=2), 0)

        groups_tomorrow_final = []
        for item in groups_tomorrow:
            if item >= 100:
                groups_tomorrow_final.append("persone richiamate")
            else:
                groups_tomorrow_final.append(item)

        groups_tomorrow_after_final = []
        for item in groups_tomorrow_after:
            if item >= 100:
                groups_tomorrow_after_final.append("persone richiamate")
            else:
                groups_tomorrow_after_final.append(item)

        return f"domani *{common.stringify(tuple(groups_tomorrow_final))}*," \
               f" dopodomani *{common.stringify(tuple(groups_tomorrow_after_final))}*."
    except Exception as ex:
        log.critical(ex)
        return "_da definire_"


def get_turnout():
    try:
        today = datetime.datetime.today()
        turnout = common.flatten(api.get_turnout_data(today))

        string = []

        for i in range(len(turnout)):
            string.append(f"{common.ranges[i]}: {turnout[i]}")

        return "\n".join(string)
    except Exception as ex:
        log.critical(ex)
        return "_Nessun dato disponibile oggi._"


def unpin_all_messages():
    URL = f"https://api.telegram.org/bot{ccn_bot_token}/unpinAllChatMessages"
    PARAMS = {'chat_id': group_chat_id}
    requests.get(url=URL, params=PARAMS)


def get_message_string(assigned_group):
    people = api.get_group_by_id(assigned_group)

    if len(assigned_group) == 1:
        assigned_group = assigned_group[0]

    if type(assigned_group) is tuple:
        # Two or more groups cleaning
        people = common.flatten(people)  # People is a list of lists
        message = f"Salve! Oggi il turno di pulizie è dei gruppi" \
                  f" *{common.stringify(assigned_group)}*, composti da:" \
                  f"\n\n{', '.join(people)}." \
                  f"\n\nBuona fortuna! 👨🏻‍🍳"

    elif 0 < int(assigned_group) <= common.MAX_GROUPS:
        # One group cleaning cleaning
        message = f"Salve! Oggi il turno di pulizie è del gruppo" \
                  f" *{assigned_group}*, composto da:" \
                  f"\n\n{', '.join(people)}." \
                  f"\n\nBuona fortuna! 👨🏻‍🍳"

    elif int(assigned_group) >= 100:
        # Punishment
        original_group = common.calendar_to_int_tuple(people[0][0])
        log.info(f"Retrieved data for original group: {original_group}")

        if len(original_group) == 1:
            original_group = original_group[0]

        if type(original_group) is tuple:
            # Two or more groups being punished
            original_group_people = common.flatten(api.get_group_by_id(original_group))
            message = f"Salve! Oggi non sarà una bella giornata per i gruppi " \
                      f"*{common.stringify(original_group)}*, composti da " \
                      f"{', '.join(original_group_people)}, " \
                      f"che dovranno scontare il proprio *richiamo*." \
                      f"\n\nBuona fortuna! 🔪👮🏻‍♂️"

        elif 0 < int(original_group) <= common.MAX_GROUPS:
            # Single group being punished
            original_group_people = api.get_group_by_id(original_group)
            message = f"Salve! Oggi non sarà una bella giornata per il gruppo " \
                      f"{original_group}, composto da " \
                      f"{', '.join(original_group_people)}, " \
                      f"che dovrà scontare il proprio *richiamo*." \
                      f"\n\nBuona fortuna! 🔪👮🏻‍♂️"

        elif int(original_group) == -1:
            # People with a punishment without a particular group
            original_group_people = common.flatten(people)[1:]
            message = f"Salve! Oggi non sarà una bella giornata per " \
                      f"{', '.join(original_group_people)}, " \
                      f"che {'dovrà' if len(original_group_people) == 1 else 'dovranno'} " \
                      f"scontare il proprio *richiamo*." \
                      f"\n\nBuona fortuna! 🔪👮🏻‍♂️"

        else:
            raise AttributeError
    else:
        raise AttributeError

    message += f"\n\nTurni dei prossimi giorni: {get_next_days_turns()}" \
               f"\n\nPrevisioni di affluenza nelle fasce orarie critiche:\n{get_turnout()}"

    log.info(f"Crafted message: {message}")

    return message


def send_cron_notification(date, assigned_group, counter=0):
    log.info(f"Starting notification helper at {date}, {assigned_group}, {counter}")
    try:
        if assigned_group:
            message = get_message_string(assigned_group)
        else:
            raise AttributeError
        sent_message = ccn_bot.send_message(chat_id=group_chat_id, text=message, parse_mode="Markdown")
        unpin_all_messages()
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
        # The date can be considered processed in any case
        api.set_day_checked(date, assigned_group)

        log.info("Notification helper successfully completed.")

    except Exception as ex:
        log.info("Error during notification crafting.")
        log.critical(ex)
        if counter < common.MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            send_cron_notification(date, assigned_group, counter + 1)
        else:
            raise Exception
