from datetime import datetime
from prozorro_auction.settings import TZ
from iso8601 import parse_date
from fractions import Fraction
import pytz


def get_now():
    return datetime.now(tz=TZ)


def convert_datetime(datetime_stamp):
    return parse_date(datetime_stamp).astimezone(TZ)


def datetime_to_str(dt):
    if isinstance(dt, str):
        return dt
    return pytz.utc.localize(dt).astimezone(TZ).isoformat()


#  barbecue
def vn_max(features):
    return sum(max(j['value'] for j in i['enum']) for i in features)


def calculate_coeficient(features, parameters):
    v_max = Fraction(vn_max(features))
    vn = sum([Fraction(i['value']) for i in parameters])
    result = 1 + vn / (1 - v_max)
    return result


def cooking(price, features=None, parameters=None, reverse=False):
    if not features or not parameters:
        return price
    coef = calculate_coeficient(features, parameters)
    return Fraction(price) * coef if reverse else Fraction(price) / coef

