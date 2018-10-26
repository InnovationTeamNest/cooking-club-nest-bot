# -*- coding: utf-8 -*-
import datetime
import logging as log

from telegram import ReplyKeyboardRemove, ChatAction

from ccn_bot import fetch_turn_calendar
from common import MAX_GROUPS, MAX_ATTEMPTS, day_to_string
from secrets import groups
from telegramcalendar import create_calendar, process_calendar_selection


# Metodi di gestione dei turni

def turn(bot, day, chat_id):
    assigned_group = fetch_turn_calendar(day, MAX_ATTEMPTS)
    try:
        if assigned_group:
            people = groups[assigned_group]
            if int(assigned_group) <= MAX_GROUPS:
                message = f"{day_to_string(day, True)} il turno del gruppo {assigned_group} composto da " \
                          f"{', '.join(people)}."
            else:
                message = f"{day_to_string(day, True)} il turno di {', '.join(people)}" \
                          f", che dovranno scontare il loro richiamo. "
        else:
            message = f"Nessun turno previsto per {day_to_string(day, False)}"
    except Exception as ex:
        log.info("An exception occurred!\n")
        log.info(ex)
        message = "Errore nel server. Riprova tra qualche minuto."

    bot.send_message(chat_id=chat_id, text=message)


def turn_keyboard(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Scegli una data:",
                         reply_markup=create_calendar())
    except Exception as ex:
        log.info(ex)


def inline_handler(bot, update):
    selected, date = process_calendar_selection(bot, update)
    if selected:
        temp_message = bot.send_message(chat_id=update.callback_query.from_user.id,
                                        text="Caricamento...",
                                        reply_markup=ReplyKeyboardRemove())
        bot.send_chat_action(chat_id=update.callback_query.from_user.id, action=ChatAction.TYPING)
        temp_message.delete()
        turn(bot, date, update.callback_query.from_user.id)


def today_turn(bot, update):
    turn(bot, datetime.date.today(), update.message.chat_id)


def tomorrow_turn(bot, update):
    turn(bot, datetime.date.today() + datetime.timedelta(days=1), update.message.chat_id)
