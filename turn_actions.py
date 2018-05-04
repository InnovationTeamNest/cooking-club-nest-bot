# -*- coding: utf-8 -*-

import datetime
import logging as log

from telegram import ReplyKeyboardRemove, ChatAction

from ccn_bot import fetch_turn_calendar, MAX_ATTEMPTS, MAX_GROUPS
from lib.telegramcalendar import telegramcalendar
from secrets import groups


# Metodi di gestione dei turni

def turn(bot, day, chat_id):
    assigned_group = fetch_turn_calendar(day, MAX_ATTEMPTS)
    try:
        if assigned_group:
            people = groups[assigned_group]
            if int(assigned_group) <= MAX_GROUPS:
                message = day_to_string(day, True) + " il turno del gruppo " + assigned_group + ", composto da " + \
                          ", ".join(people) + "."
            else:
                message = day_to_string(day, True) + " il turno di " + ", ".join(people) + \
                          ", che dovranno scontare il loro richiamo. "
            bot.send_message(chat_id=chat_id, text=message)
        else:
            bot.send_message(chat_id=chat_id,
                             text="Nessun turno previsto per " + day_to_string(day, False))
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


def turn_keyboard(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Scegli una data:",
                         reply_markup=telegramcalendar.create_calendar())
    except Exception as ex:
        log.error(ex.message)


def inline_handler(bot, update):  # TODO Expand inline functionality
    try:
        selected, date = telegramcalendar.process_calendar_selection(bot, update)
        if selected:
            temp_message = bot.send_message(chat_id=update.callback_query.from_user.id,
                                            text="Caricamento...",
                                            reply_markup=ReplyKeyboardRemove())
            bot.send_chat_action(chat_id=update.callback_query.from_user.id, action=ChatAction.TYPING)
            temp_message.delete()
            turn(bot, date, update.callback_query.from_user.id)
    except Exception as ex:
        log.error(ex.message)


def today_turn(bot, update):
    turn(bot, datetime.date.today(), update.message.chat_id)


def tomorrow_turn(bot, update):
    turn(bot, datetime.date.today() + datetime.timedelta(days=1), update.message.chat_id)


# Metodo che prende in ingresso date, in formato datetime, e phrase, un parametro per regolare la frase in uscita.
# Utilizzato per discriminare oggi, domani dagli altri giorni nelle frasi.


def day_to_string(date, phrase):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    if phrase:
        if date.day == today.day:
            message = "Oggi è"
        elif date.day == tomorrow.day:
            message = "Domani sarà"
        else:
            log.error(str(today.day) + " " + str(date.day))
            message = "Il " + date.strftime("%d/%m/%Y") + " è"
    else:
        if date.day == today.day:
            message = "oggi"
        elif date.day == tomorrow.day:
            message = "domani"
        else:
            message = "il " + date.strftime("%d/%m/%Y")
    return message
