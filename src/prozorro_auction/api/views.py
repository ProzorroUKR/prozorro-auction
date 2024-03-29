from prozorro_auction.api.sockets import get_auction_feed, ping_ws
from prozorro_auction.constants import ProcurementMethodType
from prozorro_auction.logging import update_log_context
from prozorro_auction.api.storage import (
    read_auction_list,
    get_auction,
    update_auction_bid_stage,
)
from prozorro_auction.api.utils import (
    json_response,
    json_dumps,
    get_remote_addr,
)
from prozorro_auction.api.mask import mask_data
from prozorro_auction.api.model import (
    get_posted_bid,
    get_bid_response_data,
    get_bid_by_bidder_id,
)
from aiohttp import web
from prozorro_auction.utils.base import get_now
import asyncio
import logging

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.get('/api')
async def ping(request):
    return json_response({'text': 'pong'}, status=200)


@routes.get('/api/auctions')
async def auction_list(request):
    _skip_param = int(request.query.get('page', 1)) - 1
    list_auction = await read_auction_list(_skip_param)
    # mask data
    for a in list_auction:
        mask_data(a)
        a.pop("procuringEntity", "")
    return json_response(list_auction, status=200)


@routes.get('/api/auctions/{auction_id}')
async def get_auction_by_id(request):
    _id = request.match_info['auction_id']
    auction = await get_auction(_id)
    mask_data(auction)
    return json_response(auction, status=200)


@routes.post('/api/log')
async def auction_log(request):
    data = await request.json()
    log_msg = data.pop("MESSAGE", "Auction client log")
    if "ERROR_DATA" in data:
        data["ERROR_DATA"] = str(data["ERROR_DATA"])
    data["SYSLOG_IDENTIFIER"] = "AUCTION_CLIENT"
    data["REMOTE_ADDR"] = get_remote_addr(request)
    logger.info(log_msg, extra=data)
    return json_response({"result": "ok"}, status=200)


@routes.post('/api/auctions/{auction_id}/bids/{bidder_id}')
async def post_bid(request):
    _id = request.match_info["auction_id"]
    bidder_id = request.match_info["bidder_id"]
    client_id = request.cookies.get("client_id")
    hash_value = request.rel_url.query.get("hash")
    data = await request.json()
    auction = await get_auction(
        _id,
        fields=(
            "bids", "stages", "current_stage", "features", "minimalStep", "procurementMethodType",
            "fundingKind", "yearlyPaymentsPercentageRange", "NBUdiscountRate",
            "noticePublicationDate", "minimalStepPercentage",
        )
    )
    bid = get_bid_by_bidder_id(auction, bidder_id)

    posted_bid = get_posted_bid(auction, bid, hash_value, data)
    auction = await update_auction_bid_stage(_id, bidder_id, auction["current_stage"], posted_bid)
    bid = get_bid_by_bidder_id(auction, bidder_id)
    # updated "auction" value is important to build response using "get_bid_response_data" (at least for esco)

    if auction["procurementMethodType"] == ProcurementMethodType.ESCO.value:
        if posted_bid:
            log_msg = (
                f"Bidder {bidder_id} with client_id {client_id} placed bid "
                f"with total amount {posted_bid['amountPerformance']}, "
                f"yearly payments percentage = {posted_bid['yearlyPaymentsPercentage']}, "
                f"contract duration years = {posted_bid['contractDuration']['years']}, "
                f"contract duration days = {posted_bid['contractDuration']['days']} "
                f"in {get_now().isoformat()}"
            )  # "let me speak from my heart"
        else:
            log_msg = (
                f"Bidder {bidder_id} with client_id {client_id} canceled bids "
                f"in stage {auction['current_stage']} in {get_now().isoformat()}"
            )
    else:
        if posted_bid:
            log_msg = f"Bidder {bidder_id} posted bid: {posted_bid['amount']}"
        else:
            log_msg = f"Bidder {bidder_id} cancelled their bid"

    logger.info(
        log_msg,
        extra={
            "REMOTE_ADDR": get_remote_addr(request),
            "BIDDER_ID": bidder_id,
            "CLIENT_ID": client_id,
        }
    )
    resp_data = get_bid_response_data(auction, bid)
    return json_response(resp_data, status=200)


@routes.post('/api/auctions/{auction_id}/check_authorization')
async def check_authorization(request):
    data = await request.json()
    if "bidder_id" in data and "hash" in data:
        bidder_id, hash_value = data["bidder_id"], data["hash"]
        client_id = data.get("client_id")

        _id = request.match_info["auction_id"]
        auction = await get_auction(_id, fields=("bids", "stages", "current_stage", "procurementMethodType"))

        bid = get_bid_by_bidder_id(auction, bidder_id)
        if bid["hash"] != hash_value:
            raise web.HTTPUnauthorized(text="hash is invalid")

        resp_data = get_bid_response_data(auction, bid)
        logger.info(
            f"Bidder {bidder_id} from {client_id} has passed check authorization: {resp_data}",
            extra={
                "REMOTE_ADDR": get_remote_addr(request),
                "BIDDER_ID": bidder_id,
                "CLIENT_ID": client_id,
            }
        )

        if "coeficient" in bid:
            resp_data["coeficient"] = str(bid["coeficient"])

        if "non_price_cost" in bid:
            resp_data["non_price_cost"] = bid["non_price_cost"]

        if "addition" in bid:
            resp_data["addition"] = bid["addition"]

        if "denominator" in bid:
            resp_data["denominator"] = bid["denominator"]

        return json_response(resp_data, status=200)
    else:
        raise web.HTTPUnauthorized(text="bidder_id or hash not provided")


# --- WebSockets ----

@routes.get('/api/auctions/{auction_id}/ws')
async def ws_handler(request):
    socket = web.WebSocketResponse()
    await socket.prepare(request)

    auction_id = request.match_info['auction_id']
    update_log_context(AUCTION_ID=auction_id)
    logger.info('Feed client connected')

    loop = asyncio.get_event_loop()
    t = loop.create_task(ping_ws(socket, asyncio.current_task()))
    logger.info(f'Ping launched {t}')

    auction_feed = get_auction_feed()
    auction_feed.subscribe(auction_id, socket)
    try:
        while not socket.closed:
            auction = await auction_feed.get(auction_id, socket)
            await socket.send_json(auction, dumps=json_dumps)
    except ConnectionResetError as e:
        logger.info(f"ConnectionResetError at send updates {e}")
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Unsubscribe socket")
        auction_feed.unsubscribe(auction_id, socket)

    logger.info('Feed client disconnected')
    return socket
