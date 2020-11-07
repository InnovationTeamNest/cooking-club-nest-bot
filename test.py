# -*- coding: utf-8 -*-
import datetime
import logging as log
import time

from cron import services
from common import LOG_FORMAT
from cron.helpers import fetch_turn_calendar, send_cron_notification

if __name__ == "__main__":
    import os

    log.basicConfig(level=log.INFO, format=LOG_FORMAT)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    assigned_group = fetch_turn_calendar(datetime.date.today(), 0)
    today = time.strftime(str("%d/%m/%Y"))
    send_cron_notification(today, assigned_group)