from datetime import datetime
import time
from configuration import APP_CONFIG


def get_current_day_timestamp():
    now = datetime.now()
    return now.hour * 3600 + now.minute * 60


def get_current_timestamp():
    """
    This function returns the current timestamp in seconds.
    :return:
    """
    return int(datetime.now().timestamp())


def dprint(str_to_print, priority_level=1, preprint="", hashtag_display=True, date_display=True, source=None):
    """
    This function is used to print debug messages
    :param str_to_print:
    :param priority_level:
    :param preprint:
    :param hashtag_display:
    :param date_display:
    :param source:
    :return:
    """
    if APP_CONFIG.PRIORITY_DEBUG_LEVEL >= priority_level:
        str_ident = "".join("-" for _ in range(priority_level))

        # Date display
        if date_display:
            date = f" [{time.strftime('%d/%m/%y, %H:%M:%S', time.localtime()) + '.{:03d}'.format(int(time.time() * 1000) % 1000)}] "
        else:
            date = ""

        output = f"{preprint}{date}"

        if source:
            output += f" [{source}] "
        if hashtag_display:
            output += f"#{str_ident} "

        output += str_to_print
        print(output)
