# -*- coding: utf-8 -*-

import datetime
import logging as log
import time

import telegram
from flask import Request

import cron.helpers
from api import api
from cron.helpers import fetch_turn_calendar, send_cron_notification
from secrets import ccn_bot_token, url

ccn_bot = telegram.Bot(ccn_bot_token)


def turn(counter=0):
    today = time.strftime(str("%d/%m/%Y"))

    log.info(f"Service started {today} at {time.strftime('%c')}")

    try:
        res = api.is_day_checked(today)
        if res:
            log.info(f"Day already checked ({today}), stopping")
            return 200
        else:
            log.info(f"Day not checked ({today}), proceeding")
    except Exception as ex:
        log.info("Exception during day checking")
        log.critical(ex)
        return 424

    assigned_group = fetch_turn_calendar(datetime.date.today(), counter)

    try:
        log.info(f"Today's turn: {assigned_group}")
        send_cron_notification(today, assigned_group)
    except Exception as ex:
        log.info("Exception during notification sending")
        log.critical(ex)
        return 424
    return 201


def set_webhook():
    # Ogni volta che si carica una nuova versione, bisogna rifare il setup del bot!
    cron.helpers.dispatcher_setup()
    res = ccn_bot.set_webhook(url + ccn_bot_token)
    if res:
        return "Success!", 200
    else:
        return "Webhook setup failed...", 500


def incoming_update(request: Request):
    update = telegram.Update.de_json(request.get_json(force=True, cache=False), ccn_bot)
    log.info(request.get_json(force=True, cache=False))
    log.info(update)
    res = cron.helpers.process(update)

    return res
