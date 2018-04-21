# -*- coding: utf-8 -*-

import logging as log

from google_calendar import getAssignedPeople
from secrets import groups, group_chat_id


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Ciao! Questo è il bot del Cooking Corner del Nest, mantenuto dal club Tech@Nest."
                          + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta verrà ignorata.")


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="/oggi - Mostra il turno di oggi" +
                                                          "\n/domani - Mostra il turno di domani" +
                                                          "\n/gruppo NUMEROGRUPPO - Mostra i membri di un certo gruppo" +
                                                          "\n/info - Ottieni informazioni sul bot")  # +
    # "\n/direttivo - Ottieni informazioni sul Direttivo del Cooking Corner")


def info(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackaton nel novembre 2017." +
                          " Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest. Al momento il bot è mantenuto da Matteo Franzil" +
                          ", se serve aiuto conttattalo su @mfranzil.")


# TODO Finire il metodo direttivo
# def direttivo(bot, update):
#    bot.send_message(chat_id=update.message.chat_id, text="")

def todayTurn(bot, update):
    assigned_group = getAssignedPeople(0)
    try:
        if assigned_group:
            people = groups[assigned_group]
            message = "Oggi il turno è del gruppo " + assigned_group + ", composto da " + \
                      ", ".join(people)
            bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)
        bot.sendMessage(update.message.chat_id, "Mi dispiace, in questo momento non riesco a ottenere i turni di oggi.")


def tomorrowTurn(bot, update):
    assigned_group = getAssignedPeople(1)
    try:
        if assigned_group:
            people = groups[assigned_group]
            message = "Domani sarà il turno del gruppo " + assigned_group + ", composto da " + \
                      ", ".join(people)
            bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)
        bot.sendMessage(update.message.chat_id,
                        "Mi dispiace, in questo momento non riesco a ottenere i turni di domani.")


def defaultResponse(bot, update):
    if (update.message.chat_id != group_chat_id):
        bot.sendMessage(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")


def getGroup(bot, update, args):
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