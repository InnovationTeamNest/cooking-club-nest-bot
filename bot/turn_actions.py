# # -*- coding: utf-8 -*-
# import datetime
# import logging as log
#
# from telegram import ReplyKeyboardRemove, ChatAction
#
# from api import api
# from bot.ccn_bot import fetch_turn_calendar
# from common import MAX_GROUPS, MAX_ATTEMPTS, get_message_prefix, stringify
# from lib.telegramcalendar import create_calendar, process_calendar_selection
#
#
# # Metodi di gestione dei turni
#
# def today_turn(bot, update):
#     turn(bot, datetime.date.today(), update.message.chat_id)
#
#
# def tomorrow_turn(bot, update):
#     turn(bot, datetime.date.today() + datetime.timedelta(days=1), update.message.chat_id)
#
#
# def turn(bot, day, chat_id):
#     assigned_group = fetch_turn_calendar(day, MAX_ATTEMPTS)
#     try:
#         if assigned_group:
#             people = api.get_group_by_id(assigned_group)
#             if type(assigned_group) is tuple:
#                 message = f"{get_message_prefix(day, True)} il turno dei" \
#                           f" gruppi {stringify(assigned_group)} composti da:\n\n" \
#                           f"{', '.join(people)}."
#             elif int(assigned_group) <= MAX_GROUPS:
#                 message = f"{get_message_prefix(day, True)} il turno del" \
#                           f" gruppo {assigned_group} composto da:\n\n" \
#                           f"{', '.join(people)}."
#             else:
#                 try:
#                     original_group = int(people[0])
#                 except Exception:
#                     original_group = -1
#
#                 if original_group == -1:
#                     message = f"{get_message_prefix(day, True)} il turno di {', '.join(people[1:])}" \
#                               f", che dovranno scontare il loro richiamo. "
#                 elif 0 < original_group <= MAX_GROUPS:
#                     original_group_people = api.get_group_by_id(original_group)
#                     message = f"{get_message_prefix(day, True)} il turno del" \
#                               f" gruppo {original_group} composto da " \
#                               f"{', '.join(original_group_people)}.\n\nIn aggiunta {', '.join(people[1:])}" \
#                               f" {'dovranno' if len(people[1:]) > 1 else 'dovrà'} scontare il loro richiamo. 🧹"
#                 else:
#                     raise AttributeError
#         else:
#             message = f"Nessun turno previsto per {get_message_prefix(day, False)}."
#     except Exception as ex:
#         log.info("An exception occurred!\n")
#         log.critical(ex)
#         message = "Errore nel server. Riprova tra qualche minuto."
#
#     bot.send_message(chat_id=chat_id, text=message)
#
#
# def turn_keyboard(bot, update):
#     try:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text="Scegli una data:",
#                          reply_markup=create_calendar())
#     except Exception as ex:
#         log.critical(ex)
#
#
# def inline_handler(bot, update):
#     selected, date = process_calendar_selection(bot, update)
#     if selected:
#         temp_message = bot.send_message(chat_id=update.callback_query.from_user.id,
#                                         text="Caricamento...",
#                                         reply_markup=ReplyKeyboardRemove())
#         bot.send_chat_action(chat_id=update.callback_query.from_user.id, action=ChatAction.TYPING)
#         temp_message.delete()
#         turn(bot, date, update.callback_query.from_user.id)
