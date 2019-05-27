# -*- coding: utf-8 -*-

import logging as log

from telegram import ChatAction

import api
from common import MAX_MESSAGES, MAX_GROUPS
from secrets import direttivo_names, direttivo_id


class ReplyStatus:  # Classe ausilaria, un quick fix per gestire tutti i tipi di risposte dei metodi
    direttivoresponse = False
    groupresponse = False
    searchresponse = False

    def __init__(self):
        pass

    @staticmethod
    def allfalse():
        ReplyStatus.direttivoresponse = False
        ReplyStatus.groupresponse = False
        ReplyStatus.searchresponse = False


# Metodo per getstire le risposte in chat

def text_filter(bot, update):  # Strettamente collegata alla classe definita in precedenza
    if ReplyStatus.direttivoresponse:
        response_direttivo(bot, update)
    elif ReplyStatus.groupresponse:
        response_group(bot, update)
    elif ReplyStatus.searchresponse:
        response_search(bot, update)
    else:
        pass


# Metodi di base, start, help e info

def start(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Ciao! Questo è il bot del Cooking Corner del Nest, mantenuto dal club Tech@Nest."
                              + ". Per iniziare scrivi un comando o scrivi /help per aiuto.\nOgni altra richiesta "
                                "verrà ignorata.")
    except Exception as ex:
        log.info("Unable to send Telegram message!\n")
        log.critical(ex)


def help(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="/info - Ottieni informazioni sul bot e sul Direttivo del Cooking Corner"
                              "\n/turno - Cerca tra i turni del mese"
                              "\n/oggi - Mostra il turno di oggi"
                              "\n/domani - Mostra il turno di domani"
                              "\n/gruppo <#> - Mostra i membri di un certo gruppo"
                              "\n/cerca <Persona> - Cerca una persona tra i gruppi"
                              "\n/direttivo - Contatta il Direttivo del Cooking Corner")
    except Exception as ex:
        log.info("Unable to send Telegram message!\n")
        log.critical(ex)


def info(bot, update):
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text=f"Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackathon il 19/11/"
                              f"2017. Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest. Al momento"
                              f" il bot è mantenuto da Matteo Franzil, se serve aiuto conttattalo su @mfranzil."
                              f"\n\n*Membri del Direttivo*:\n{direttivo_names}")
    except Exception as ex:
        log.info("Unable to send Telegram message!\n")
        log.critical(ex)


# Metodi che supportano le risposte dirette in chat

def direttivo(bot, update):
    ReplyStatus.allfalse()
    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Rispondi a questo messaggio per recapitare un messaggio "
                              "al Direttivo. Segnalazioni, suggerimenti sono ben accetti. "
                              "Eventuali abusi saranno puniti con un richiamo.\n")
    except Exception as ex:
        log.critical(ex)
    ReplyStatus.direttivoresponse = True


def group(bot, update, args):
    ReplyStatus.allfalse()
    try:
        args = str(args[0])
        if args in api.get_group_numbers() and int(args) <= MAX_GROUPS:
            people = api.get_group(args)
            message = f"Il gruppo {args} è formato da {', '.join(people)}."
        else:
            message = "ID del gruppo non valido"
    except Exception as ex:
        message = f"Inserisci un numero da 1 a {str(MAX_GROUPS)} per ottenere informazioni sul gruppo."
        ReplyStatus.groupresponse = True
        log.critical(ex)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def search(bot, update, args):
    ReplyStatus.allfalse()
    try:
        dictionary_search(bot, update, args[0])
    except Exception as ex:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Inserisci il nome (anche in parte) della persona di cui vuoi sapere il gruppo.")
        ReplyStatus.searchresponse = True
        log.critical(ex)


# Metodi che gestiscono le rispettive risposte
def response_direttivo(bot, update):
    try:
        user = update.message.from_user
        name = f"{user.first_name} {user.last_name}" if user.last_name is None else user.first_name
        bot.send_message(chat_id=direttivo_id, text=f"{name} scrive:\n\n{update.message.text}")
        bot.send_message(chat_id=update.message.chat_id, text="Messaggio inviato con successo.")
    except Exception as ex:
        log.critical(ex)
    ReplyStatus.direttivoresponse = False


def response_group(bot, update):
    group(bot, update, (update.message.text, 0))
    ReplyStatus.groupresponse = False


def response_search(bot, update):
    dictionary_search(bot, update, update.message.text)
    ReplyStatus.searchresponse = False


# Metodi corollari:
# Metodo di ricerca nel dizionario delle persone, usato da search e responseSearch

def dictionary_search(bot, update, name):
    try:
        found = 0
        results = []
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

        for number, group_members in api.get_number_members_tuple():
            for member in group_members:
                if name.lower() in member.lower():
                    results.append(f"\n{member} si trova nel gruppo {str(number)}")
                    found += 1
        # E' necessario gestire sia zero persone che troppe (20+) in questo caso
        if found == 0:
            text = "Persona non trovata."
        elif 0 < found < MAX_MESSAGES:
            text = "".join(results)
        else:
            text = f"Troppi risultati trovati ({str(found)}+), prova con un parametro più restrittivo."
    except Exception as ex:
        text = "Errore! Parametro di ricerca non valido."
        log.critical(ex)

    bot.send_message(chat_id=update.message.chat_id, text=text)
