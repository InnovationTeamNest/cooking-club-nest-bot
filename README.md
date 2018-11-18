# Cooking Club NEST Bot

**Cooking Club NEST Bot** is a Python-driven Telegram bot implementing the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) API, and run on a Google App Engine Standard environment.

This is the code powering @cooking-club-nest-bot.

The Bot's purpose is to inform people about their upcoming cleaning turns in a shared kitchen.

## Sample secrets.py file

In order to make the bot work, a file named secrets.py must be placed inside the root folder. It must contain:

```python
ccn_bot_token = # The BotFather token
group_chat_id = # The supergroup chat ID that will be used to inform people
direttivoid = # The authority of the Kitchen ID
url = # Google App Engine project URL
direttivo_names = # The authorities of the kitchen

# Direttivo Cooking Corner
access_token = # Google token
refresh_token = # Refresh token from Google account
token_expiry = # Google Token expiry

# App data
client_id = 
client_secret =
user_agent = 
token_uri = "https://accounts.google.com/o/oauth2/token"

groups = { ... }
```

## Sources

I would like to thank [@unmonoqueteclea](https://github.com/unmonoqueteclea) for its implementation of [telegramcalendar.py](https://github.com/unmonoqueteclea/calendar-telegram), used in this bot.

## Contribute
Feel free to contribute by forking the project and issuing a pull request. Any contribution will be assessed by the NEST Innovation Team before merging the pull request.

## To-Do

* Insert information about implemented functionality