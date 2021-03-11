import time
import datetime
import difflib
import os.path as path


def is_file_older_than_x_hours(file, hours=1):
    file_time = path.getmtime(file)
    # Check against 24 hours
    return ((time.time() - file_time) / 3600 > hours)


def convert_list_to_string(lst):
    return str(lst).translate(None, '[],\'')


def find_proper_channel(wrong_channel, channel_list):
    similiar_channels = []
    for x in channel_list:
        if difflib.SequenceMatcher(None, wrong_channel.lower(), x.lower()).ratio() > 0.5:
            similiar_channels.append(x)

    return similiar_channels


def extract_date(date, dateformat):
    d = datetime.datetime.strptime(date, dateformat)
    return datetime.date.strftime(d, "%d-%m-%y")


def extract_datetime(date, dateformat):
    d = datetime.datetime.strptime(date, dateformat)
    return datetime.date.strftime(d, "%d-%m-%y %H:%M")


def convert_to_epoch(date, date_format):
    return int(time.mktime(datetime.datetime.strptime(date, date_format).timetuple()))
