import datetime
import logging as log
import time

import requests
from telegram import Bot

import common
from api import api
from secrets import group_chat_id, ccn_bot_token

from common import translate_date

ccn_bot = Bot(ccn_bot_token)


def fetch_turn_calendar(date, counter):
    log.info(f"Starting turn fetching helper at {date} {counter}")

    try:
        offset = (date - datetime.date.today()).days
        event = api.get_day_event(offset)
        if event is None:
            raise Exception
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
    message = ""
    timedelta = 1
    days = 0
    while timedelta < 8 and days < 2:
        try:
            fetched_groups = fetch_turn_calendar(datetime.date.today() + datetime.timedelta(days=timedelta),
                                                 common.MAX_ATTEMPTS)  # only a single attempt
        except TimeoutError:
            timedelta += 1
            continue

        group_array = []
        if type(fetched_groups) is tuple:
            for item in fetched_groups:
                if item >= 100:
                    group_array.append("persone richiamate")
                else:
                    group_array.append(str(item) + ", ")
            group_array += "dopo cena"
        elif type(fetched_groups) is list:
            after_lunch_groups = fetched_groups[0]
            for item in after_lunch_groups:
                if item >= 100:
                    group_array.append("persone richiamate, ")
                else:
                    group_array.append(str(item) + ", ")
            group_array += "dopo pranzo; "

            after_dinner_groups = fetched_groups[1]
            for item in after_dinner_groups:
                if item >= 100:
                    group_array.append("persone richiamate, ")
                else:
                    group_array.append(str(item) + ", ")
            group_array += "dopo cena"

        else:
            raise AttributeError("Provided data must be either a list of two tuples or a single tuple")

        message += f"{common.get_day_name(timedelta)} (tra {timedelta} giorni):" \
                   f" *{''.join(group_array)}*\n"
        timedelta += 1
        days += 1

    return message


def unpin_all_messages():
    URL = f"https://api.telegram.org/bot{ccn_bot_token}/unpinAllChatMessages"
    PARAMS = {'chat_id': group_chat_id}
    requests.get(url=URL, params=PARAMS)


def get_message_string(assigned_group):
    if type(assigned_group) is list:  # [(1, 2, 3, 4), (5, 6, 7, 8)]
        # Post-lunch turn and post-dinner turn. Must be exactly two
        people_after_lunch = common.flatten(api.get_group_by_id(assigned_group[0]))
        people_after_dinner = common.flatten(api.get_group_by_id(assigned_group[1]))
        message = f"Salve! Oggi ci saranno due turni di pulizie.\n\n"\
                  f"Il turno dopo pranzo è {'dei gruppi' if len(assigned_group[0]) != 1 else 'del gruppo'}" \
                  f" *{common.stringify(assigned_group[0])}*:" \
                  f"\n\n{', '.join(people_after_lunch)}." \
                  f"\n\nIl turno dopo cena è {'dei gruppi' if len(assigned_group[1]) != 1 else 'del gruppo'}" \
                  f" *{common.stringify(assigned_group[1])}*:" \
                  f"\n\n{', '.join(people_after_dinner)}." \
                  f"\n\nBuona fortuna! 👨🏻‍🍳"
    elif type(assigned_group) is tuple:  # (1, 2, 3, 4)
        # Single turn
        if len(assigned_group) == 1:
            # Just a group assigned
            message = get_message_string_single(assigned_group[0])  # (1,) -> 1
        else:
            people = common.flatten(api.get_group_by_id(assigned_group))
            message = f"Salve! Oggi il turno di pulizie è dei gruppi" \
                      f" *{common.stringify(assigned_group)}*, composti da:" \
                      f"\n\n{', '.join(people)}." \
                      f"\n\nBuona fortuna! 👨🏻‍🍳"
    else:
        raise AttributeError("Provided data must be either a list of two tuples or a single tuple")

    message += f"\n\nProssimi turni:\n{get_next_days_turns()}"

    log.info(f"Crafted message: {message}")
    return message


def get_message_string_single(assigned_group):
    people = api.get_group_by_id(assigned_group)

    if 0 < int(assigned_group) <= common.MAX_GROUPS:  # 10
        # The group is a standard one
        message = f"Salve! Oggi il turno di pulizie è del gruppo" \
                  f" *{assigned_group}*, composto da:" \
                  f"\n\n{', '.join(people)}." \
                  f"\n\nBuona fortuna! 👨🏻‍🍳"

    elif int(assigned_group) >= 100:  # 101
        # This is a punishment
        original_group = common.calendar_to_int_tuple(people[0])
        log.info(f"Retrieved data for original group: {original_group}")

        if 0 < int(original_group) <= common.MAX_GROUPS:
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
            raise AttributeError("Either provide a standard single group in the calendar,"
                                 " or a -1 followed by a list of people in the adjacent cell.")
    else:
        raise AttributeError("Either provide a single int group or a number > 100 for a punishment.")

    return message


def weekly_notification(date):
    try:
        message = ["Salve! Questa settimana toccherà ai seguenti gruppi: "]
        for i in range(0, 7):
            try:
                assigned_group = fetch_turn_calendar(date, 3)
            except TimeoutError as ex:
                log.error(ex)
                assigned_group = None
            log.info(f"Checking day {i} for {assigned_group}")
            try:
                if assigned_group is None:
                    message.append(f"\n\n{translate_date(date)} - Nessuno")
                elif type(assigned_group) is list:  # [(1, 2, ..), (3, 4, ..)]
                    people_after_lunch = common.flatten(api.get_group_by_id(assigned_group[0]))
                    people_after_dinner = common.flatten(api.get_group_by_id(assigned_group[1]))

                    number_after_lunch = assigned_group[0][0] if len(assigned_group[0]) == 1 \
                        else common.stringify(assigned_group[0])
                    number_after_dinner = assigned_group[1][0] if len(assigned_group[1]) == 1 \
                        else common.stringify(assigned_group[1])

                    message.append(f"\n\n{translate_date(date)} - "
                                   f"*{number_after_lunch}* dopo pranzo: {', '.join(people_after_lunch)}; "
                                   f"*{number_after_dinner}* dopo cena: {', '.join(people_after_dinner)}")
                elif type(assigned_group) is tuple:  # (1, 2, ..)
                    # Just a single turn
                    if len(assigned_group) == 1:
                        # (1,)
                        people = api.get_group_by_id(assigned_group[0])
                        if 0 < int(assigned_group[0]) <= common.MAX_GROUPS:  # 10
                            # The group is a standard one
                            message.append(f"\n\n{translate_date(date)} - *{assigned_group[0]}*: {', '.join(people)}")
                        elif int(assigned_group[0]) >= 100:
                            message.append(f"\n\n{translate_date(date)} - *Richiamo*")
                    else:
                        people = common.flatten(api.get_group_by_id(assigned_group))
                        message.append(f"\n\n{translate_date(date)} - *{common.stringify(assigned_group)}*:"
                                       f" {', '.join(people)}")
                else:
                    log.error(f"Error in formatting the data: {assigned_group}")
            except Exception as ex:
                log.error("Unable to fetch data from Google Calendar... "
                          "No notification for today... What a pity!")
                log.error(ex)
            date += datetime.timedelta(days=1)
        sent_message = ccn_bot.send_message(chat_id=group_chat_id,
                                            text="".join(message),
                                            parse_mode="Markdown")
        ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
    except Exception as ex:
        log.error("Unable to send Telegram notification. No notification for "
                  "today... What a pity!")
        log.error(ex)


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
