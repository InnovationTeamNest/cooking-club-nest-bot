# -*- coding: utf-8 -*-

import webapp2
import ccn_bot
from webhook import WebHookHandler, WebHookSetter
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


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/turn', TurnHandler),
    ('/setwebhook', WebHookSetter),
    ('/' + ccn_bot.ccn_bot_token, WebHookHandler)
], debug=True)