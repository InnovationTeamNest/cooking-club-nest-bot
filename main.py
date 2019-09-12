# -*- coding: utf-8 -*-
import datetime
import logging as log
from timeit import default_timer as timer

from flask import Flask, request

from bot import ccn_bot
from secrets import url, ccn_bot_token

app = Flask(__name__)


@app.before_first_request
def init():
    # Inizializzo il logging
    log.basicConfig(level=log.DEBUG, format=' - %(levelname)s - %(name)s - %(message)s')


@app.route('/', methods=['GET'])
def index():
    return "Cooking Club Nest Bot is running.", 200


@app.route('/turn', methods=['GET'])
def turn():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        code = ccn_bot.check_turn()
        return f"Request completed in {str((timer() - start_time))} seconds.", code
    else:
        return "Access Denied", 403


@app.route('/weekly', methods=['GET'])
def weekly():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        ccn_bot.weekly_notification(datetime.date.today())
        return f"Request completed in {str((timer() - start_time))} seconds.", 200
    else:
        return "Access Denied", 403


@app.route('/set_webhook', methods=['GET'])
def wb():
    if 'X-Appengine-Cron' in request.headers:
        from routing.webhook import dispatcher_setup, bot
        dispatcher_setup()  # Ogni volta che si carica una nuova versione, bisogna rifare il setup del bot!
        res = bot.setWebhook(url + ccn_bot_token)
        if res:
            return "Success!", 200
        else:
            return "Webhook setup failed...", 500
    else:
        return "Access Denied", 403


@app.route('/' + ccn_bot_token, methods=['POST'])
def update():
    import telegram
    from routing.webhook import bot, process

    # De-Jsonizzo l'update
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    # Loggo il contenuto dell'update
    log.info(update)
    # Faccio processare al dispatcher l'update
    process(update)

    return "See console for output", 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
