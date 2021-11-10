from aiohttp import web
from prozorro_auction.settings import TZ
from datetime import datetime
import json
import pytz

FORWARDED_FOR_DELIMITER = ','
FORWARDED_FOR_EXCLUDE_PREFIX = '172.'


def json_serialize(obj):
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = pytz.utc.localize(obj).astimezone(TZ)
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def json_dumps(*args, **kwargs):
    kwargs["default"] = json_serialize
    return json.dumps(*args, **kwargs)


def json_response(data, status=200):
    return web.json_response(data, status=status, dumps=json_dumps)


def get_forwarded_for(request):
    return FORWARDED_FOR_DELIMITER.join(request.headers.getall("X-Forwarded-For"))


def get_remote_addr(request):
    remote_addr = FORWARDED_FOR_DELIMITER.join([
         ip.strip() for ip in get_forwarded_for(request).split(FORWARDED_FOR_DELIMITER)
         if not ip.strip().startswith(FORWARDED_FOR_EXCLUDE_PREFIX)
    ])
    return remote_addr or request.remote


class HTTPError(web.HTTPError):

    def __init__(self, error, **kwargs):
        kwargs["content_type"] = "application/json"
        kwargs["text"] = json_dumps(dict(error=error))
        super(HTTPError, self).__init__(**kwargs)


class ValidationError(HTTPError):
    status_code = 400


class ForbiddenError(HTTPError):
    status_code = 401
