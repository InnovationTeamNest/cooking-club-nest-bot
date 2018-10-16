# -*- coding: utf-8 -*-
import datetime
from timeit import default_timer as timer

import telegram
from flask import Flask, request

import ccn_bot
from secrets import url, ccn_bot_token

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Cooking Club Nest Bot is running.", 200


@app.route('/turn', methods=['GET'])
def turn():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        code = ccn_bot.check_turn()
        return "Request completed in " + str((timer() - start_time)) + " seconds.", code
    else:
        return "Access Denied", 403


@app.route('/weekly', methods=['GET'])
def weekly():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        ccn_bot.weekly_notification(datetime.date.today())
        return "Request completed in " + str((timer() - start_time)) + " seconds.", 200
    else:
        return "Access Denied", 403


@app.route('/set_webhook', methods=['GET'])
def wb():
    if 'X-Appengine-Cron' in request.headers:
        from webhook import dispatcher_setup, bot
        dispatcher_setup()  # Ogni volta che si carica una nuova versione, bisogna rifare il setup del bot!
        res = bot.setWebhook(url + ccn_bot_token)
        if res:
            return "Success!", 200
        else:
            return "Webhook setup failed...", 500
    else:
        return "Access Denied", 403


@app.route('/' + ccn_bot.ccn_bot_token, methods=['POST'])
def updates():
    from webhook import webhook, bot

    update = telegram.Update.de_json(request.get_json(force=True), bot)
    return webhook(update, 0)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
