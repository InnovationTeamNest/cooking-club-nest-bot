# -*- coding: utf-8 -*-
import datetime

from api import api
from bot.ccn_bot import fetch_turn_calendar
from common import MAX_ATTEMPTS

if __name__ == "__main__":
    import os

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    day = datetime.date.today()
    assigned_group = fetch_turn_calendar(day, MAX_ATTEMPTS)

    print(assigned_group)