import logging
import asyncio
from prozorro_crawler.logging import log_context

from prozorro_auction.api.storage import watch_changed_docs

logger = logging.getLogger(__name__)


AUCTION_FEED = None

def get_auction_feed():
    global AUCTION_FEED
    AUCTION_FEED = AUCTION_FEED or AuctionFeed()
    return AUCTION_FEED


MESSAGE_CHANGES_FOUND = 1
MESSAGE_TIMEOUT = 0

class AuctionFeed:

    def __init__(self):
        self._auctions = {}
        asyncio.create_task(self._process_changes_loop())

    async def get(self, auction_id, socket, timeout=60):
        auction = self._auctions.get(auction_id, {})
        subscribers = auction.get("subscribers", {})
        subscriber = subscribers.get(socket)
        if subscriber:
            asyncio.create_task(self._process_timeout(subscriber, timeout))
            message = await subscriber.get()
            if message == MESSAGE_TIMEOUT:
                return
        auction_doc = auction.get("doc")
        return auction_doc

    def subscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            subscribers = {}
            self._auctions[auction_id] = dict(doc=None, subscribers=subscribers)
        else:
            subscribers = self._auctions[auction_id]["subscribers"]

        subscriber = asyncio.Queue(maxsize=10)
        subscribers[socket] = subscriber

    def unsubscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            return logger.critical(f"Auction id {auction_id} not in self._auctions")

        subscribers = self._auctions[auction_id]["subscribers"]
        subscribers.pop(socket)

        if not subscribers:
            logger.info(f"Empty subscribers set for {auction_id}: discarding its cached object")
            del self._auctions[auction_id]

    async def _process_timeout(self, subscriber, timeout):
        await asyncio.sleep(timeout)
        await subscriber.put(MESSAGE_TIMEOUT)

    async def _process_changes_loop(self):

        async for auction in watch_changed_docs():
            auction_id = auction["_id"]
            with log_context(AUCTION_ID=auction_id):
                logger.info(f"Capture change of auction")

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

                            subscriber.put_nowait(MESSAGE_CHANGES_FOUND)

                        for socket in dead_sockets:
                            await socket.close()
                            logger.info('Force close of socket that is not reading data')
                            subscribers.pop(socket)

async def ping_ws(socket):
    try:
        while not socket.closed:
            await asyncio.sleep(5)
            await socket.send_str("PING")  # send it, so client is sure that connection is fine
            res = await socket.receive(timeout=5)
    except (ConnectionResetError, asyncio.CancelledError, asyncio.TimeoutError) as e:
        logger.info(f"Error at ping: {e}")
        await socket.close()
