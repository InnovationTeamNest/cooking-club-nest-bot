# -*- coding: utf-8 -*-
import datetime
import logging as log

from cron import services
from common import LOG_FORMAT

if __name__ == "__main__":
    import os

    log.basicConfig(level=log.INFO, format=LOG_FORMAT)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    services.turn(0)
