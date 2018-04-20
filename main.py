# -*- coding: utf-8 -*-

import webapp2
import ccn_bot
from timeit import default_timer as timer


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Cooking Club Nest Bot is running.")


class TurnHandler(webapp2.RequestHandler):
    def get(self):
        start_time = timer()
        ccn_bot.check_turn()
        self.response.write("Request completed in " +
                            str((timer() - start_time)) + " seconds.")


class WebHookHandler(webapp2.RequestHandler):
    def set_webhook(self):
        ccn_bot.setwebhook(self)

    def webhook_handler(self):
        ccn_bot.webhook_handler(self)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/turn', TurnHandler),
    ('/setwebhook', WebHookHandler.set_webhook()),
    ('/' + ccn_bot.ccn_bot_token, WebHookHandler.webhook_handler())
], debug=True)