# -*- coding: utf-8 -*-

import logging as log

from google_calendar import get_today_assigned_people
from secrets import groups, group_chat_id


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Ciao! Questo è il bot del Cooking Corner del Nest"
                                                          + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta verrà ignorata.")


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="/oggi - Mostra il turno di oggi")
    bot.send_message(chat_id=update.message.chat_id, text="/gruppo NUMEROGRUPPO - Mostra i membri di un certo gruppo")


def today_turn(bot, update):
    assigned_group = get_today_assigned_people()
    try:
        if assigned_group:
            people = groups[assigned_group]
            message = "Oggi il turno è del gruppo " + assigned_group + ", composto da " + \
                      ", ".join(people)
            bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)
        bot.sendMessage(update.message.chat_id, "Mi dispiace, in questo momento non riesco a ottenere i turni di oggi.")


def defaultResponse(bot, update):
    if (update.message.chat_id != group_chat_id):
        bot.sendMessage(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")


def get_group(bot, update, args):
    args = args[0]
    try:
        people = groups[str(args)]
        message = "Il gruppo " + str(args) + " è formato da " + \
                  ", ".join(people) + "."
        bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        bot.sendMessage(update.message.chat_id,
                        "Non ho capito bene il numero del gruppo. I gruppi possibili vanno da 1 a 40.")
        log.error(ex.message)