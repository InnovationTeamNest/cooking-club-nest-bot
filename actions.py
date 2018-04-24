# -*- coding: utf-8 -*-

import logging as log

from google_calendar import getAssignedPeople
from secrets import groups, group_chat_id, direttivoid


class ReplyStatus:
    direttivoresponse = False


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Ciao! Questo è il bot del Cooking Corner del Nest, mantenuto dal club Tech@Nest."
                          + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta verrà ignorata.")


def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="/info - Ottieni informazioni sul e sul Direttivo del Cooking Corner" +
                         "\n/oggi - Mostra il turno di oggi" +
                         "\n/domani - Mostra il turno di domani" +
                         "\n/gruppo <#> - Mostra i membri di un certo gruppo" +
                         "\n/direttivo - Conttatta il Direttivo del Cooking Corner")


def info(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackaton nel novembre 2017." +
                          " Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest. Al momento il bot è mantenuto da Matteo Franzil" +
                          ", se serve aiuto conttattalo su @mfranzil.")
    bot.send_message(chat_id=update.message.chat_id,
                     text="Membri del Direttivo:\n\nSofia Caruso, Matteo Franzil, Matteo Marra, " +
                          "Alice Massa, Francesco Misiano, Nicola Pozza, Giovanni Rachello. ")


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
        bot.sendMessage(update.message.chat_id, "Nessun turno è in programma per oggi!")


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
                        "Nessun turno previsto per domani!")


def getGroup(bot, update, args):
    args = args[0]
    try:
        people = groups[str(args)]
        message = "Il gruppo " + str(args) + " è formato da " + \
                  ", ".join(people) + "."
        bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        bot.sendMessage(update.message.chat_id,
                        "Scrivi /gruppo seguito da un numero da 1 a 40 per ottenere informazioni sul gruppo.")
        log.error(ex.message)


def direttivo(bot, update):
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id=chat_id,
                    force_reply=True,
                    text="Rispondi a questo messaggio per recapitare un messaggio " + \
                         "al Direttivo. Segnalazioni, suggerimenti sono ben accetti. Eventuali abusi saranno puniti con un richiamo.")
    ReplyStatus.direttivoresponse = True


def risposteDirettivo(bot, update):
    try:  # TODO Add datastore to failed message
        if ReplyStatus.direttivoresponse:
            if update.message.from_user.last_name == None:
                bot.sendMessage(chat_id=direttivoid, text=str(update.message.from_user.first_name) + " scrive:\n\n" + \
                                                          update.message.text)
            else:
                bot.sendMessage(chat_id=direttivoid, text=str(update.message.from_user.first_name) + " " + \
                                                          str(update.message.from_user.last_name) + " scrive:\n\n" + \
                                                          update.message.text)
            bot.sendMessage(chat_id=update.message.chat_id, text="Messaggio inviato con successo.")
    except Exception as ex:
        log.error(ex.message)
    ReplyStatus.direttivoresponse = False


def default(bot, update):
    if not (update.message.chat_id == group_chat_id):
        bot.sendMessage(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")
