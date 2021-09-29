import datetime
import re

days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

MIN_GROUPS = 1
MAX_GROUPS = 35
MAX_ATTEMPTS = 3

LOG_FORMAT = '[%(levelname)s] %(message)s (%(filename)s:%(lineno)d:%(funcName)s)'


def flatten(__list): return [item for sublist in __list for item in sublist]


def get_day_name(timedelta):
    __day = datetime.date.today() + datetime.timedelta(days=timedelta)
    return days[__day.weekday()] + " " + str(__day.day)


def stringify(__tuple):
    if len(__tuple) == 1:
        return str(__tuple[0])
    elif len(__tuple) == 2:
        return f"{str(__tuple[0])} e {str(__tuple[1])}"
    else:
        return str(__tuple)[1:-1]


def calendar_to_int_tuple(summary):
    # Parses a string of the following format:
    # (?:[0-9]*-?)*
    raw_groups = [i for i in re.findall(r"(?:[0-9]*-?)*", summary) if i != ""]
    if len(raw_groups) < 1 or len(raw_groups) > 2:
        raise ValueError(f"Can have either one or two groups per day, not anything else! (len={str(len(raw_groups))})")
    elif len(raw_groups) == 1:
        return tuple((int(i) for i in raw_groups[0].split('-')))
    else:
        target_list = []
        for items in raw_groups:
            target_list.append(tuple((int(i) for i in items.split('-'))))
        return target_list
