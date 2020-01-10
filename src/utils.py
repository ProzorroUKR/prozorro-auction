from datetime import datetime
from settings import TZ
from iso8601 import parse_date


def get_now():
    return datetime.now(tz=TZ)


def convert_datetime(datetime_stamp):
    return parse_date(datetime_stamp).astimezone(TZ)

