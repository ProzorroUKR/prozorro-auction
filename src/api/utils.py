from aiohttp import web
from settings import TZ, logger
from datetime import datetime
import json
import pytz


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


class HTTPError(web.HTTPError):

    def __init__(self, error, **kwargs):
        kwargs["content_type"] = "application/json"
        kwargs["text"] = json_dumps(dict(error=error))
        super(HTTPError, self).__init__(**kwargs)


class ValidationError(HTTPError):
    status_code = 400


class ForbiddenError(HTTPError):
    status_code = 401

