import datetime
import logging as log

days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

MAX_MESSAGES = 20
MAX_GROUPS = 25
MAX_ATTEMPTS = 5

# Metodo che prende in ingresso date, in formato datetime, e phrase, un parametro per regolare la frase in uscita.
# Utilizzato per discriminare oggi, domani dagli altri giorni nelle frasi.


def day_to_string(date, phrase):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    if phrase:
        if date.day == today.day:
            message = "Oggi è"
        elif date.day == tomorrow.day:
            message = "Domani sarà"
        else:
            log.info(str(today.day) + " " + str(date.day))
            message = "Il " + date.strftime("%d/%m/%Y") + " è"
    else:
        if date.day == today.day:
            message = "oggi"
        elif date.day == tomorrow.day:
            message = "domani"
        else:
            message = "il " + date.strftime("%d/%m/%Y")
    return message


def translate_date(date):
    return f"{days[date.weekday()]} {date.strftime('%d').lstrip('0')}/{date.strftime('%m').lstrip('0')}"
