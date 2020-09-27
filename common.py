import datetime

days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

MAX_SEARCH_RESULTS = 20
MIN_GROUPS = 1
MAX_GROUPS = 35
MAX_ATTEMPTS = 3

LOG_FORMAT = '[%(levelname)s] %(message)s (%(filename)s:%(lineno)d:%(funcName)s)'


def get_message_prefix(date, caps=False):
    """
    Metodo che prende in ingresso date, in formato datetime, e phrase,
    un parametro per regolare la frase in uscita.
    Utilizzato per discriminare oggi, domani dagli altri giorni nelle frasi.
    """
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    if caps:
        if date.day == today.day:
            message = "Oggi"
        elif date.day == tomorrow.day:
            message = "Domani"
        else:
            message = "Il " + date.strftime("%d/%m/%Y")
    else:
        if date.day == today.day:
            message = "oggi"
        elif date.day == tomorrow.day:
            message = "domani"
        else:
            message = "il " + date.strftime("%d/%m/%Y")
    return message


def get_day_name_and_number(date):
    return f"{days[date.weekday()]} {date.strftime('%d').lstrip('0')}/{date.strftime('%m').lstrip('0')}"


def flatten(__list): return [item for sublist in __list for item in sublist]


def stringify(__tuple):
    if len(__tuple) == 1:
        return str(__tuple[0])
    elif len(__tuple) == 2:
        return f"{str(__tuple[0])} e {str(__tuple[1])}"
    else:
        return str(__tuple)[1:-1]
