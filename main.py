# -*- coding: utf-8 -*-

import datetime
from timeit import default_timer as timer

import webapp2

import ccn_bot
from webhook import WebHookHandler, UpdateHandler


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Cooking Club Nest Bot is running.")


class TurnHandler(webapp2.RequestHandler):
    def get(self):
        start_time = timer()
        ccn_bot.check_turn()
        self.response.write("Request completed in " +
                            str((timer() - start_time)) + " seconds.")


class WeeklyHandler(webapp2.RequestHandler):
    def get(self):
        start_time = timer()
        ccn_bot.weekly_notification(datetime.date.today())
        self.response.write("Request completed in " +
                            str((timer() - start_time)) + " seconds.")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/turn', TurnHandler),
    ('/set_webhook', WebHookHandler),
    ('/weekly', WeeklyHandler),
    ('/' + ccn_bot.ccn_bot_token, UpdateHandler)
], debug=True)
