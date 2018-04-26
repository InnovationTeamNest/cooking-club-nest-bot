# -*- coding: utf-8 -*-

import logging as log

from ccn_bot import fetchTurnCalendar
from secrets import groups, direttivoid


class ReplyStatus:
    direttivoresponse = False
    groupresponse = False

    @staticmethod
    def allfalse():
        ReplyStatus.direttivoresponse = False
        ReplyStatus.groupresponse = False


# Metodi di base, start, help e info

def start(bot, update):
    try:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Ciao! Questo è il bot del Cooking Corner del Nest, mantenuto dal club Tech@Nest."
                             + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta verrà ignorata.")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


def help(bot, update):
    try:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="/info - Ottieni informazioni sul e sul Direttivo del Cooking Corner" +
                             "\n/oggi - Mostra il turno di oggi" +
                             "\n/domani - Mostra il turno di domani" +
                             "\n/gruppo <#> - Mostra i membri di un certo gruppo" +
                             "\n/direttivo - Conttatta il Direttivo del Cooking Corner")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)

def info(bot, update):
    try:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackaton nel novembre 2017." +
                             " Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest." +
                             "Al momento il bot è mantenuto da Matteo Franzil, se serve aiuto conttattalo su @mfranzil.")
        bot.send_message(chat_id=update.message.chat_id,
                         text="Membri del Direttivo:\n\nSofia Caruso, Matteo Franzil, Matteo Marra, " +
                              "Alice Massa, Francesco Misiano, Nicola Pozza, Giovanni Rachello. ")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


# Metodi  per fetchare i turni del giorno

def todayTurn(bot, update):
    turn(bot, update, 0)


def tomorrowTurn(bot, update):
    turn(bot, update, 1)


def turn(bot, update, day):
    assigned_group = fetchTurnCalendar(day, 5)
    try:
        if assigned_group:
            people = groups[assigned_group]

            if day == 0:
                message = "Oggi è"
            elif day == 1:
                message = "Domani sarà"
            else:
                message = ""  # message = dayToString() # TODO IMPLEMENT FUNCTION FOR ANY TYPE OF DAY

            message = message + " il turno del gruppo " + assigned_group + ", composto da " + \
                      ", ".join(people)
            bot.sendMessage(update.message.chat_id, message)
        else:
            bot.sendMessage(update.message.chat_id, "Nessun turno previsto per questa data!")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


# Metodi che supportano le risposte dirette in chat

def group(bot, update, args):
    ReplyStatus.allfalse()
    try:
        args = args[0]
        people = groups[str(args)]
        message = "Il gruppo " + str(args) + " è formato da " + \
                  ", ".join(people) + "."
        bot.sendMessage(update.message.chat_id, message)
    except Exception as ex:
        bot.sendMessage(update.message.chat_id,
                        "Inserisci un numero da 1 a 40 per ottenere informazioni sul gruppo.")
        ReplyStatus.groupresponse = True
        log.error(ex.message)


def direttivo(bot, update):
    ReplyStatus.allfalse()
    try:
        chat_id = update.message.chat_id
        bot.sendMessage(chat_id=chat_id,
                        force_reply=True,
                        text="Rispondi a questo messaggio per recapitare un messaggio " + \
                             "al Direttivo. Segnalazioni, suggerimenti sono ben accetti." + \
                             "Eventuali abusi saranno puniti con un richiamo.\n")
    except Exception as ex:
        log.error(ex.message)
    ReplyStatus.direttivoresponse = True


# Metodo per getstire le risposte in chat

def textFilter(bot, update):
    if ReplyStatus.direttivoresponse:
        responseDirettivo(bot, update)
    elif ReplyStatus.groupresponse:
        responseGroup(bot, update)
    # else:
    # bot.sendMessage(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")


# Metodi che gestiscono le rispettive risposte

def responseDirettivo(bot, update):
    try:  # TODO Add datastore to failed message
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


def responseGroup(bot, update):
    try:
        text = update.message.text
        if text in groups:
            group(bot, update, (text, 0))
        else:
            bot.sendMessage(update.message.chat_id, "ID del gruppo non valido")
    except Exception as ex:
        bot.sendMessage(update.message.chat_id,
                        "Qualcosa è andato storto. Riprova più tardi.")
        log.error(ex.message)
    ReplyStatus.groupresponse = False
