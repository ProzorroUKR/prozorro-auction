from prozorro_auction.settings import logger
from prozorro_auction.api.storage import read_auction_list, get_auction, insert_auction, update_auction_bid_stage, watch_changed_docs
from prozorro_auction.api.utils import json_response, json_dumps
from prozorro_auction.api.model import get_test_auction, validate_posted_bid_amount
from prozorro_auction.databridge.model import build_stages
from aiohttp import web
from prozorro_auction.utils import get_now
import asyncio


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


# --- WebSockets ----

class AuctionFeed:
    def __init__(self):
        self._auctions = {}
        asyncio.ensure_future(self._process_changes_loop())

    def get(self, key):
        auction_doc = self._auctions.get(key, {}).get("doc")
        return auction_doc

    def subscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            subscribers = {}
            self._auctions[auction_id] = dict(doc=None, subscribers=subscribers)
        else:
            subscribers = self._auctions[auction_id]["subscribers"]

        queue = asyncio.Queue(maxsize=10)
        subscribers[socket] = queue
        return queue

    def unsubscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            return logger.critical(f"Auction id {auction_id} not in self._auctions")

        subscribers = self._auctions[auction_id]["subscribers"]
        subscribers.pop(socket)

        if not subscribers:
            logger.info(f"Empty subscribers set for {auction_id}: discarding its cached object")
            del self._auctions[auction_id]

    async def _process_changes_loop(self):

        async for auction in watch_changed_docs():
            auction_id = auction["_id"]
            logger.info(f"Capture change of {auction_id}")

            if auction_id in self._auctions:
                save_doc = self._auctions[auction_id]["doc"]
                if save_doc is None or save_doc["modified"] != auction["modified"]:
                    self._auctions[auction_id]["doc"] = auction
                    subscribers = self._auctions[auction_id]["subscribers"]
                    dead_sockets = []
                    for socket, subscriber in subscribers.items():
                        if subscriber.full():
                            dead_sockets.append(socket)
                            continue
                        subscriber.put_nowait(1)  # putting any object is fine

                    for socket in dead_sockets:
                        await socket.close()
                        logger.info('Force close of socket that is not reading data')
                        subscribers.pop(socket)


AUCTION_FEED = AuctionFeed()


def get_auction_feed():
    global AUCTION_FEED
    AUCTION_FEED = AUCTION_FEED or AuctionFeed()
    return AUCTION_FEED


async def ping_ws(ws):
    while not ws.closed:
        await asyncio.sleep(5)
        await ws.send_str("PING")  # send it, so client is sure that connection is fine
        res = await ws.receive(timeout=5)  # we do actually nothing if there is no pong
        logger.debug(f"Ping response: {res.data}")


@routes.get('/api/auctions/{auction_id}/ws')
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    auction_id = request.match_info['auction_id']
    log_extra = {"auction_id": auction_id}
    logger.info('Feed client connected', extra=log_extra)

    loop = asyncio.get_event_loop()
    t = loop.create_task(ping_ws(ws))
    logger.info(f'Ping launched {t}', extra=log_extra)

    auction_feed = get_auction_feed()
    feed = auction_feed.subscribe(auction_id, ws)
    try:
        while not ws.closed:
            await feed.get()  # will get 1 from _process_changes_loop
            await ws.send_json(auction_feed.get(auction_id), dumps=json_dumps)
    finally:
        logger.info("Unsubscribe socket")
        auction_feed.unsubscribe(auction_id, ws)

    logger.info('Feed client disconnected')
    return ws
