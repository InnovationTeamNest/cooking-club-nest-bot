# -*- coding: utf-8 -*-
import datetime
import logging as log

import flask

from common import LOG_FORMAT
from cron import helpers

if __name__ == "__main__":
    # from main import app
    # app.run()
    import os

    log.basicConfig(level=log.INFO, format=LOG_FORMAT)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    # assigned_group = fetch_turn_calendar(datetime.date.today(), 0)
    # today = time.strftime(str("%d/%m/%Y"))
    # send_cron_notification(today, assigned_group)

    helpers.weekly_notification(datetime.date(2022,5,2))
