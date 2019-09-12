# Cooking Club NEST Bot

**Cooking Club NEST Bot** is a Python-driven Telegram bot implementing the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) API, and run on a Google App Engine Standard environment.

This is the code powering `@cooking-club-nest-bot`.

## Features

The Bot's purpose is to inform people about their upcoming cleaning turns in a shared kitchen.

In this model, a shared kitchen consists of an arbitrary number of groups sharing a working space, fridges and cleaning turns. Each group (currently) supports up to 8 people. An oligarchy of people (called kitchen authorities) rule the kitchen and punish misbehaving members.

Each day, the Bot makes an API call to a Google Calendar and checks the assigned group; then makes a second API call to Google Sheets to check the list of people in that particular group. It then proceeds to send this information to a Telegram supergroup.

The bot, when summoned in chat mode, additionally supports the following features:
* Querying for turns, given any day of the month
* Querying for group composition, given the number
* Global search for members (including partial search)
* Private reports to the kitchen authority

## Setup

In order to make the bot work, a file named secrets.py must be placed inside the root folder. It must contain:

```python
ccn_bot_token = ""   # The BotFather token
group_chat_id = ""   # The supergroup chat ID that will be used to inform people
direttivoid = ""     # The headauthority of the Kitchen ID
url = ""             # Google App Engine project URL
direttivo_names = "" # The authorities of the kitchen, as a string containing names (used for information purposes)
spreadsheet_ID = ""  # The Google Spreadsheet used for the names
```

Additionally, the following will be needed:

* A Google Calendar, containing all-day events with the numzber of the group as the title
* A Google Spreadsheet, containing member names as strings, ordered by row (e.g. row 1 contains group 1, with cell A1 through H1 containing members)

Both sources will need to be either public or accessible by the Google Account linked to the bot.
## Sources

I would like to thank [@unmonoqueteclea](https://github.com/unmonoqueteclea) for its implementation of [telegramcalendar.py](https://github.com/unmonoqueteclea/calendar-telegram), used in this bot.

## Contribute

Feel free to contribute by forking the project and issuing a pull request. Any contribution will be assessed by the NEST Innovation Team before merging the pull request.

