# Cooking Club NEST Bot

**Cooking Club NEST Bot** is a Python-driven Telegram bot implementing the 
[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) API, and run on a Google App 
Engine Flexible environment.

This is the code powering `@cooking-club-nest-bot`.

## Features

The Bot's purpose is to inform people about their upcoming cleaning turns in a shared kitchen.

In this model, a shared kitchen consists of an arbitrary number of groups sharing a working space, fridges and cleaning 
turns. Each group (currently) supports up to 4 people. An oligarchy of people (called kitchen authorities) rule the 
kitchen and punish misbehaving members.

Each day, the Bot makes an API call to a Google Calendar and checks the assigned group; then makes a second API call 
to Google Sheets to check the list of people in that particular group. It then proceeds to send this information to a 
Telegram supergroup.

Further functionalities recently added include polling for the turns of the following days, support for "punishment" 
turns, and additional information on kitchen turnout for each day.


## Setup

In order to make the bot work, a file named `secrets.py` must be placed inside the root folder. It must contain:

```python
ccn_bot_token = ""   # The BotFather token
group_chat_id = ""   # The supergroup chat ID that will be used to inform people
url = ""             # Google App Engine project URL
spreadsheet_id = ""  # The Google Sheet used for the names
calendar_id = ""     # The Google Calendar used for the events

```

Additionally, the following will be needed:

* A Google Calendar, containing all-day events with the numzber of the group as the title. The name of the calendar 
will need to be inserted in the `secrets.py` file.
* A Google Sheet, containing member names as strings, ordered by row (e.g. row 1 contains group 1, with cell A1 
through H1 containing members). The Sheet ID will need to be inserted into the `secrets.py` file.

Both sources will need to be either public or accessible by the Google Account linked to the bot.


## Contribute

Feel free to contribute by forking the project and issuing a pull request. Any contribution will be assessed by the 
NEST Innovation Team before merging the pull request.

