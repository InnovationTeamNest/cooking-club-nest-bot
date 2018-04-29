# -*- coding: utf-8 -*-

import datetime
import logging as log

from lib.telegramcalendar import telegramcalendar
from telegram import ChatAction, ReplyKeyboardRemove

from ccn_bot import fetch_turn_calendar, MAX_ATTEMPTS
from secrets import groups, direttivoid

MAX_MESSAGES = 20
MAX_GROUPS = 40


class ReplyStatus:  # Classe ausilaria, un quick fix per gestire tutti i tipi di risposte dei metodi
    direttivoresponse = False
    groupresponse = False
    searchresponse = False

    @staticmethod
    def allfalse():
        ReplyStatus.direttivoresponse = False
        ReplyStatus.groupresponse = False
        ReplyStatus.searchresponse = False


# Metodi di base, start, help e info

def start(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Ciao! Questo è il bot del Cooking Corner del Nest, mantenuto dal club Tech@Nest."
                              + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta "
                                "verrà ignorata.")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


def help(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="/info - Ottieni informazioni sul bot e sul Direttivo del Cooking Corner" +
                              "\n/turno - Cerca tra i turni del mese" +
                              "\n/oggi - Mostra il turno di oggi" +
                              "\n/domani - Mostra il turno di domani" +
                              "\n/gruppo <#> - Mostra i membri di un certo gruppo" +
                              "\n/cerca <Persona> - Cerca una persona tra i gruppi" +
                              "\n/direttivo - Conttatta il Direttivo del Cooking Corner")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


def info(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackaton nel novembre" +
                              " 2017. Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest. Al momento" +
                              " il bot è mantenuto da Matteo Franzil, se serve aiuto conttattalo su @mfranzil.")
        bot.send_message(chat_id=update.message.chat_id,
                         text="Membri del Direttivo:\n\nSofia Caruso, Matteo Franzil, Matteo Marra, " +
                              "Alice Massa, Francesco Misiano, Nicola Pozza, Giovanni Rachello. ")
    except Exception as ex:
        log.error("Unable to send Telegram message!\n" + ex.message)


# Metodi di gestione dei turni

def turn(bot, day, chat_id):
    assigned_group = fetch_turn_calendar(day, MAX_ATTEMPTS)
    try:
        if assigned_group:
            people = groups[assigned_group]
            if int(assigned_group) < MAX_GROUPS:
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


# Metodo per getstire le risposte in chat

def text_filter(bot, update):  # Strettamente collegata alla classe definita in precedenza
    if ReplyStatus.direttivoresponse:
        response_direttivo(bot, update)
    elif ReplyStatus.groupresponse:
        response_group(bot, update)
    elif ReplyStatus.searchresponse:
        response_search(bot, update)
    # else:
    # bot.send_message(update.message.chat_id, "Mi dispiace, posso solo risponderti se usi uno dei comandi in /help.")


# Metodi che supportano le risposte dirette in chat

def direttivo(bot, update):
    ReplyStatus.allfalse()
    try:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id,
                         text="Rispondi a questo messaggio per recapitare un messaggio " +
                              "al Direttivo. Segnalazioni, suggerimenti sono ben accetti." +
                              "Eventuali abusi saranno puniti con un richiamo.\n")
    except Exception as ex:
        log.error(ex.message)
    ReplyStatus.direttivoresponse = True


def group(bot, update, args):
    ReplyStatus.allfalse()
    try:
        args = args[0]
        if str(args) in groups and int(args) < MAX_GROUPS:
            people = groups[str(args)]
            message = "Il gruppo " + str(args) + " è formato da " + \
                      ", ".join(people) + "."
            bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="ID del gruppo non valido")
    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Inserisci un numero da 1 a " + str(
                             MAX_GROUPS) + " per ottenere informazioni sul gruppo.")
        ReplyStatus.groupresponse = True
        log.error(ex.message)


def search(bot, update, args):
    ReplyStatus.allfalse()
    try:
        args = args[0]
        dictionary_search(bot, update, args)
    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Inserisci il nome (anche in parte) della persona di cui vuoi sapere il gruppo.")
        ReplyStatus.searchresponse = True
        log.error(ex.message)


# Metodi che gestiscono le rispettive risposte

def response_direttivo(bot, update):
    try:  # TODO Add datastore for failed message
        user = update.message.from_user
        if user.last_name is None:
            bot.send_message(chat_id=direttivoid,
                             text=str(user.first_name) + " scrive:\n\n" + update.message.text)
        else:
            bot.send_message(chat_id=direttivoid, text=str(user.first_name) + " " + str(
                user.last_name) + " scrive:\n\n" + update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text="Messaggio inviato con successo.")
    except Exception as ex:
        log.error(ex.message)
    ReplyStatus.direttivoresponse = False


def response_group(bot, update):
    try:
        text = update.message.text
        if text in groups:
            group(bot, update, (text, 0))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="ID del gruppo non valido")
    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Qualcosa è andato storto. Riprova più tardi.")
        log.error(ex.message)
    ReplyStatus.groupresponse = False


def response_search(bot, update):
    try:
        dictionary_search(bot, update, update.message.text)
    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Qualcosa è andato storto. Riprova più tardi.")
        log.error(ex.message + " from method responseSearch")
    ReplyStatus.searchresponse = False


# Metodi corollari:
# Metodo di ricerca nel dizionario delle persone, usato da search e responseSearch

def dictionary_search(bot, update, name):
    try:
        found = 0
        retval = []
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

        for number, person in groups.iteritems():  # groups.items()  (Python 3)
            for i in person:
                if name.encode('ascii') in i:
                    retval.append(i + " si trova nel gruppo " + str(number))
                    found += 1
        # E' necessario gestire sia zero persone che troppe (20+) in questo caso
        if found == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Persona non trovata.")
        elif 0 < found < MAX_MESSAGES:
            for i in range(0, len(retval)):
                bot.send_message(chat_id=update.message.chat_id, text=retval[i])
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Troppi risultati trovati (" + str(found) +
                                  "), prova con un parametro più restrittivo.")

    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id, text="Errore! Parametro di ricerca non valido.")
        log.error(ex.message + "from method dictionarySearch")


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
