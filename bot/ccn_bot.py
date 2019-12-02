# -*- coding: utf-8 -*-

import datetime
import logging as log
import time

import telegram

from api import api
from common import MAX_ATTEMPTS, translate_date, MAX_GROUPS
from secrets import ccn_bot_token, group_chat_id

ccn_bot = telegram.Bot(ccn_bot_token)


def check_turn(counter=0):
    today = time.strftime(str("%d/%m/%Y"))

    try:
        res = api.day_already_checked(today)
        log.info(f"Already checked? {repr(res)}")
        if res:
            return 200
    except Exception as ex:
        log.info("Unable to fetch data from Datastore... No notification "
                 "for today... What a pity!")
        log.critical(ex)
        return 424

    log.info(f"Checking turn for day {today} at {str(time.strftime(str('%c')))}")
    assigned_group, assigned_description = fetch_turn_calendar(datetime.date.today(), counter)
    print(assigned_group, assigned_description)

    try:
        log.info(f"Today's turn: {assigned_group}")
        send_notification(today, assigned_group, assigned_description)
    except Exception as ex:
        log.info("Unable to fetch data from Google Calendar... "
                 "No notification for today... What a pity!")
        log.critical(ex)
        return 424

    return 200


def fetch_turn_calendar(date, counter):
    try:
        offset = (date - datetime.date.today()).days
        event = api.get_day_event(offset)
    except Exception as ex:
        log.info("Unable to fetch data from Google Calendar... "
                 "No notification for today... What a pity!")
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            return fetch_turn_calendar(date, counter + 1)
        log.critical(ex)
        return
    return int(event.get("summary")), str(event.get("description"))


def send_notification(date, assigned_group, _assigned_description, counter=0):
    try:
        # there could be days with no turn. It is useless to send a message to
        # the group in this case.
        if assigned_group:
            people = api.get_group(assigned_group)
            if int(assigned_group) < 100:
                # Gruppo "normale"

                if datetime.datetime.today().month == 11 and datetime.datetime.today().day == 19:
                    message = f"Buongiorno a tutti! Oggi dovranno pulire {', '.join(people)} " \
                        f"del gruppo *{assigned_group}*, ma cosa più " \
                        f"importante, è il mio compleanno!\n\n" \
                        f"Buona pulizia a tutti! 🎉🥳"
                else:
                    message = f"Salve! Oggi il turno di pulizie è del gruppo *{assigned_group}*," \
                        f" composto da {', '.join(people)}.\n\nBuona fortuna! 👨🏻‍🍳"
            else:
                try:
                    original_group = int(people[0])
                except Exception as ex:
                    original_group = -1

                if original_group == -1:
                    message = f"Salve! Oggi non sarà una bella giornata per {', '.join(people[1:])}" \
                              f", che {'dovranno' if len(people[1:]) > 1 else 'dovrà'}" \
                              f" scontare il proprio *richiamo*.\n\nBuona fortuna! 🔪👮🏻‍♂️"
                elif 0 < original_group <= MAX_GROUPS:
                    original_group_people = api.get_group(original_group)
                    message = f"Salve! Oggi il turno di pulizie è del gruppo {original_group}, composto da " \
                              f"{', '.join(original_group_people)}.\n\nIn aggiunta {', '.join(people[1:])}" \
                              f" {'dovranno' if len(people[1:]) > 1 else 'dovrà'} scontare il proprio *richiamo*." \
                              f"\n\nBuona fortuna! 🔪👮🏻‍♂️"
                else:
                    raise AttributeError
            sent_message = ccn_bot.send_message(chat_id=group_chat_id,
                                                text=message,
                                                parse_mode="Markdown")
            ccn_bot.pin_chat_message(group_chat_id, sent_message.message_id)
        # the date can be considered processed in any case
        api.push_data(date, assigned_group)
    except Exception as ex:
        log.info("Unable to send Telegram notification. No notification for "
                 "today... What a pity!")
        log.critical(ex)
        if counter < MAX_ATTEMPTS:
            time.sleep(2 ** counter)
            send_notification(date, assigned_group, counter + 1)


# phrases = [
#     f"Salve! Oggi il turno di pulizie è del gruppo {group} composto da {people}.\n\nBuona fortuna! 👨🏻‍🍳",
#     f"Buongiorno! La cucina dovrà essere pulita dal gruppo {group} oggi: {people}.\n\nBuona pulizia! 🧹",
#     f"Buongiorno! L'ingrato compito della pulizia toccherà a {people}, del gruppo {group}.\n\nHave fun!",
#     f"Buon weekend a tutti! Questo sabato dovranno pulire {people}, del gruppo {group}\n\nBuona fortuna! 👨🏻‍🍳",
#     f""
# ]


def weekly_notification(date):
    try:
        message = ["Salve! Questa settimana toccherà ai seguenti gruppi: "]
        for i in range(0, 7):
            assigned_group, assigned_description = fetch_turn_calendar(date, 0)
            log.info(f"Checking day {i} for {assigned_group} and {assigned_description}")
            try:
                if assigned_group is None:
                    message.append(f"\n{translate_date(date)} - Nessuno")
                else:
                    if assigned_group < 100:
                        people = api.get_group(assigned_group)
                        message.append(f"\n{translate_date(date)} - Gruppo *{assigned_group}*: {', '.join(people)}")
                    else:
                        message.append(f"\n{translate_date(date)} - *Richiamo*: {assigned_description}")
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
