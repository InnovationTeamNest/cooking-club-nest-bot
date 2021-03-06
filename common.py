import datetime

days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ranges = ["11:00-11:30", "11:30-12:00", "12:00-12:30", "12:30-13:00", "13:00-13:30", "13:30-14:00", "14:00-14:30"]

MAX_SEARCH_RESULTS = 20
MIN_GROUPS = 1
MAX_GROUPS = 35
MAX_ATTEMPTS = 3

LOG_FORMAT = '[%(levelname)s] %(message)s (%(filename)s:%(lineno)d:%(funcName)s)'


def flatten(__list): return [item for sublist in __list for item in sublist]


def stringify(__tuple):
    if len(__tuple) == 1:
        return str(__tuple[0])
    elif len(__tuple) == 2:
        return f"{str(__tuple[0])} e {str(__tuple[1])}"
    else:
        return str(__tuple)[1:-1]


def calendar_to_int_tuple(list):
    target_list = []
    for item in str(list).split(" "):
        try:
            target_list.append(int(item))
        except ValueError:
            pass

    return tuple(target_list)