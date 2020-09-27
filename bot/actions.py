# # -*- coding: utf-8 -*-
#
# import logging as log
#
# from telegram import ChatAction
#
# from api import api
# from common import MAX_SEARCH_RESULTS, MAX_GROUPS, MIN_GROUPS
# from secrets import direttivo_names
#
#
# class ReplyStatus:  # Classe ausilaria, un quick fix per gestire tutti i tipi di risposte dei metodi
#     # direttivoresponse = False
#     groupresponse = False
#     searchresponse = False
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def allfalse():
#         # ReplyStatus.direttivoresponse = False
#         ReplyStatus.groupresponse = False
#         ReplyStatus.searchresponse = False
#
#
# # Metodo per getstire le risposte in chat
#
# def text_filter(bot, update):  # Strettamente collegata alla classe definita in precedenza
#     # if ReplyStatus.direttivoresponse:
#     #     response_direttivo(bot, update)
#     if ReplyStatus.groupresponse:
#         response_group(bot, update)
#     elif ReplyStatus.searchresponse:
#         response_search(bot, update)
#
#
# # Metodi di base, start, help e info
#
# def start(bot, update):
#     try:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text="Ciao! Questo è il bot del Cooking Corner del NEST, mantenuto dal club Tech@NEST. "
#                               "Per iniziare scrivi un comando o scrivi /help per aiuto.")
#     except Exception as ex:
#         log.info("Unable to send Telegram message!\n")
#         log.critical(ex)
#
#
# def help(bot, update):
#     try:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text="/info - Ottieni informazioni sul bot e sul Direttivo del Cooking Corner"
#                               "\n/turno - Cerca tra i turni del mese"
#                               "\n/oggi - Mostra il turno di oggi"
#                               "\n/domani - Mostra il turno di domani"
#                               "\n/gruppo <#> - Mostra i membri di un certo gruppo"
#                               "\n/cerca <Persona> - Cerca una persona tra i gruppi")
#     #                         "\n/direttivo - Contatta il Direttivo del Cooking Corner")
#     except Exception as ex:
#         log.info("Unable to send Telegram message!\n")
#         log.critical(ex)
#
#
# def info(bot, update):
#     try:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text=f"Ciao! Questo bot è stato creato dal club Tech@Nest durante un Hackathon il 19/11/"
#                               f"2017. Il bot è stato ideato da Gianvito Taneburgo, ora non più al Nest. Al momento"
#                               f" il bot è mantenuto da Matteo Franzil, se serve aiuto conttattalo su @mfranzil."
#                               f"\n\n*Membri del Direttivo*:\n{direttivo_names}",
#                          parse_mode="Markdown")
#     except Exception as ex:
#         log.info("Unable to send Telegram message!\n")
#         log.critical(ex)
#
#
# # Metodi che supportano le risposte dirette in chat
#
# # def direttivo(bot, update):
# #     ReplyStatus.allfalse()
# #     try:
# #         bot.send_message(chat_id=update.message.chat_id,
# #                          text="Il direttivo è composto dalle seguenti persone."
# #                               " Segnalazioni, suggerimenti sono ben accetti.\n")
# #     except Exception as ex:
# #         log.critical(ex)
# #     ReplyStatus.direttivoresponse = True
#
#
# def group(bot, update, args):
#     ReplyStatus.allfalse()
#     try:
#         args = str(args[0])
#         if int(args) - 1 in range(MAX_GROUPS) and int(args) <= MAX_GROUPS:
#             people = api.get_group_by_id(args)
#             message = f"Il gruppo {args} è formato da {', '.join(people)}."
#         else:
#             message = f"Numero del gruppo inesistente. Sintassi: /gruppo <numero {MIN_GROUPS}-{MAX_GROUPS}>"
#     except IndexError as ex:
#         message = f"Numero del gruppo inesistente. Sintassi: /gruppo <numero {MIN_GROUPS}-{MAX_GROUPS}>"
#         ReplyStatus.groupresponse = False
#         log.critical(ex)
#     except Exception as ex:
#         message = f"Inserisci un numero da {MIN_GROUPS} a {MAX_GROUPS} per ottenere informazioni sul gruppo."
#         ReplyStatus.groupresponse = True
#         log.critical(ex)
#     bot.send_message(chat_id=update.message.chat_id, text=message)
#
#
# def search(bot, update, args):
#     ReplyStatus.allfalse()
#     try:
#         dictionary_search(bot, update, args[0])
#     except Exception as ex:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text="Inserisci il nome (anche in parte) della persona di cui vuoi sapere il gruppo.")
#         ReplyStatus.searchresponse = True
#         log.critical(ex)
#
#
# # Metodi che gestiscono le rispettive risposte
# # def response_direttivo(bot, update):
# #     try:
# #         user = update.message.from_user
# #         name = f"{user.first_name} {user.last_name}" if user.last_name is None else user.first_name
# #         bot.send_message(chat_id=direttivo_id, text=f"{name} scrive:\n\n{update.message.text}")
# #         bot.send_message(chat_id=update.message.chat_id, text="Messaggio inviato con successo.")
# #     except Exception as ex:
# #         log.critical(ex)
# #     ReplyStatus.direttivoresponse = False
#
#
# def response_group(bot, update):
#     group(bot, update, (update.message.text, 0))
#     ReplyStatus.groupresponse = False
#
#
# def response_search(bot, update):
#     dictionary_search(bot, update, update.message.text)
#     ReplyStatus.searchresponse = False
#
#
# # Metodi corollari:
# # Metodo di ricerca nel dizionario delle persone, usato da search e responseSearch
#
# def dictionary_search(bot, update, name):
#     try:
#         found = 0
#         results = []
#         bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
#
#         for number, member in api.get_all_group_tuples():
#             if name.lower() in member.lower():
#                 results.append(f"\n{member} si trova nel gruppo {number}")
#                 found += 1
#         # E' necessario gestire sia zero persone che troppe (20+) in questo caso
#         if found == 0:
#             text = "Persona non trovata."
#         elif 0 < found < MAX_SEARCH_RESULTS:
#             text = "".join(results)
#         else:
#             text = f"Troppi risultati trovati ({found}), prova con un parametro più restrittivo."
#     except Exception as ex:
#         text = "Errore! Parametro di ricerca non valido."
#         log.critical(ex)
#
#     bot.send_message(chat_id=update.message.chat_id, text=text)
