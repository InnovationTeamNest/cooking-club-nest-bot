# -*- coding: utf-8 -*-
import logging as log
from timeit import default_timer as timer

from flask import Flask, request

from cron import services
from common import LOG_FORMAT
from secrets import ccn_bot_token

app = Flask(__name__)


@app.before_first_request
def init():
    log.basicConfig(level=log.DEBUG, format=LOG_FORMAT)


@app.route('/', methods=['GET'])
def index():
    return "CCNBot in funzione.", 200


@app.route('/turn', methods=['GET'])
def turn():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        code = services.turn()
        return f"Richiesta completata in {timer() - start_time} secondi.", code
    else:
        return "Access restricted to AppEngine-Cron requests.", 403


@app.route('/set_webhook', methods=['GET'])
def wb():
    if 'X-Appengine-Cron' in request.headers:
        start_time = timer()
        code = services.set_webhook()
        return f"Richiesta completata in {timer() - start_time} secondi.", code
    else:
        return "Access restricted to AppEngine-Cron requests.", 403


@app.route('/' + ccn_bot_token, methods=['POST'])
def update():
    start_time = timer()
    code = services.incoming_update(request)
    return f"Richiesta completata in {timer() - start_time} secondi.", code
