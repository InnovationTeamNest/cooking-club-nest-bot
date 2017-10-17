from telegram import Bot  # Which one to choose?

import secrets


def main():
    ccn_bot = Bot(secrets.ccn_bot_token)

    for u in ccn_bot.get_updates():
        print(u)

    message = "Let's save the kitchen together!"
    my_chat_id = None  # set a string here with your id, e.g.: "12345"
    # ccn_bot.sendMessage(my_chat_id, message)

if __name__ == '__main__':
    main()
