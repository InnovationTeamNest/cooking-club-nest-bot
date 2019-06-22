# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    import ccn_bot
    import datetime

    #ccn_bot.weekly_notification(datetime.date(2019, 6, 17))
    ccn_bot.check_turn()
