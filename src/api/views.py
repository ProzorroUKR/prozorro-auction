from settings import logger, TZ
from api.storage import read_auction_list, get_auction, insert_auction, update_auction_bid_stage
from api.utils import json_response, ValidationError
from api.model import get_test_auction, validate_posted_bid_amount
from databridge.model import build_stages
from aiohttp import web
from utils import get_now


routes = web.RouteTableDef()


@routes.get('/api')
async def ping(request):
    return json_response({'text': 'pong'}, status=200)


@routes.get('/api/create_test')
async def create_test(request):
    data = get_test_auction()
    data["stages"] = build_stages(data)
    await insert_auction(data)
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
    hash_value = request.rel_url.query.get("hash")
    data = await request.json()

    auction = await get_auction(_id, fields=("bids", "stages", "current_stage", "features", "minimalStep"))

    amount = validate_posted_bid_amount(auction, bidder_id, hash_value, data)
    stage_value = "" if amount == -1 else dict(amount=amount, time=get_now())

    await update_auction_bid_stage(_id, bidder_id, auction["current_stage"], stage_value)

    logger.info(f"Bidder {bidder_id} posted bid: {amount}")
    return json_response({"amount": amount}, status=200)


@routes.post('/api/auctions/{auction_id}/check_authorization')
async def check_authorization(request):
    data = await request.json()
    if "bidder_id" in data and "hash" in data:
        bidder_id, token = data["bidder_id"], data["hash"]
        client_id = data.get("client_id")

        _id = request.match_info["auction_id"]
        auction = await get_auction(_id, fields=("bids", "stages", "current_stage"))

        for bid in auction["bids"]:
            if bid["id"] == bidder_id:
                if bid["hash"] != token:
                    raise web.HTTPUnauthorized(text="hash is invalid")

                # get bids saved amount on this stage
                amount = None
                current_stage = auction.get("current_stage", 0)
                auction_stage = auction["stages"][current_stage]
                if auction_stage["type"] == "bids" and auction_stage["bidder_id"] == bidder_id:
                    amount = bid.get("stages", {}).get(str(current_stage), {}).get("amount")

                resp_data = {"amount": amount}
                logger.info(f"Bidder {bidder_id} from {client_id} has passed check authorization: {amount}")

                if "coeficient" in bid:
                    resp_data["coeficient"] = str(bid["coeficient"])
                return json_response(resp_data, status=200)
        else:
            raise web.HTTPUnauthorized(text="Bidder not found")
    else:
        raise web.HTTPUnauthorized(text="bidder_id or hash not provided")
