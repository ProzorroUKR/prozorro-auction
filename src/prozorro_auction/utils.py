from datetime import datetime
from prozorro_auction.settings import TZ
from iso8601 import parse_date
import pytz


def get_now():
    return datetime.now(tz=TZ)


def convert_datetime(datetime_stamp):
    return parse_date(datetime_stamp).astimezone(TZ)


def datetime_to_str(dt):
    if isinstance(dt, str):
        return dt
    return pytz.utc.localize(dt).astimezone(TZ).isoformat()


def copy_dict(original, keys):
    return {key: value for key, value in original.items() if key in keys}


def copy_fields(dest, source, fields):
    for field in fields:
        if field in source:
            dest[field] = source[field]
