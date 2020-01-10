from aiohttp import web
from settings import PORT, TZ, logger
from storage import read_auction_list, get_auction, update_auction
from datetime import datetime, timedelta
from databridge.model import build_stages
from utils import get_now
import json
import uuid
import pytz

routes = web.RouteTableDef()


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


@routes.get('/api')
async def ping(request):
    return json_response({'text': 'pong'}, status=200)


@routes.get('/api/create_test')
async def create_test(request):
    uid = uuid.uuid4().hex
    start_at = datetime.now(tz=TZ) + timedelta(seconds=30)
    data = dict(
        _id=uid,
        procurementMethodType="belowThreshold",
        tenderID=f"UA-{uid}",
        start_at=start_at,
        timer=start_at,
        procuringEntity=dict(
            name="procuringEntity Name",
            name_en="procuringEntity Name EN",
        ),
        title="Title",
        title_en="Title En",
        bids=[
            {
                "id": "a" * 32,
                "hash": uuid.uuid4().hex,
                "date": "2019-08-12T14:53:52+03:00",
                "name": "Bidder#1 Name",
                "value": 132.22,
            },
            {
                "id": "b" * 32,
                "hash": uuid.uuid4().hex,
                "date": "2019-08-12T15:53:52+03:00",
                "name": "Bidder#2 Name",
                "value": 232.66,
            }
        ]
    )
    data["stages"] = build_stages(data)
    await update_auction(data, insert=True)
    return json_response(data, status=200)


@routes.get('/api/auctions')
async def auction_list(request):
    _skip_param = int(request.query.get('page', 1)) - 1
    list_auction = await read_auction_list(_skip_param)
    return json_response(list_auction, status=200)


@routes.get('/api/auctions/{auction_id}')
async def get_auction_by_id(request):
    _id = request.match_info['auction_id']
    auction = await get_auction(_id)
    return json_response(auction, status=200)


@routes.post('/api/log')
async def auction_log(request):
    data = await request.json()
    message = data.pop("MESSAGE", "Auction client log")
    data["SYSLOG_IDENTIFIER"] = "AUCTION_CLIENT"
    logger.info(message, extra=data)
    return json_response({"result": "ok"}, status=200)


@routes.post('/api/auctions/{auction_id}/bids/{bidder_id}')
async def post_bid(request):
    _id = request.match_info["auction_id"]
    bidder_id = request.match_info["bidder_id"]

    auction = await get_auction(_id, fields=("bids", "stages", "current_stage"))

    for bid in auction["bids"]:
        if bid["id"] == bidder_id:

            current_stage = auction.get("current_stage", 0)
            auction_stage = auction["stages"][current_stage]
            if auction_stage["type"] != "bid" or auction_stage["bidder"] != bidder_id:
                raise web.HTTPBadRequest(text='You are not allowed to bid at the moment')

            hash_value = request.rel_url.query.get("hash")
            if bid["hash"] != hash_value:
                raise web.HTTPForbidden()

            data = await request.json()
            if "value" not in data:
                raise web.HTTPBadRequest(text='"value" is required')

            value = data["value"]

            stages = bid.get("stages", {})
            stages[str(current_stage)] = dict(amount=value, time=get_now())
            bid["stages"] = stages

            await update_auction(auction, fields=("bids",))

            logger.info(f"Bidder {bidder_id} posted bid: {value}")
            return json_response({"value": value}, status=200)
    else:
        raise web.HTTPNotFound()


def create_application():
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(create_application(), port=PORT)
