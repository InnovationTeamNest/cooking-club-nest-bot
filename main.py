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

class UserHandler(webapp2.RequestHandler):
    def get(self):
        ccn_bot.messageHandler()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/turn', TurnHandler),
    ('/activateusermode', UserHandler)
], debug=True)