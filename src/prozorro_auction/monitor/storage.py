from prozorro_auction.storage import get_mongodb_collection
from prozorro_auction.settings import MONGODB_ERROR_INTERVAL
from pymongo.errors import PyMongoError
from pymongo import ASCENDING
import logging
import asyncio


logger = logging.getLogger(__name__)


async def get_minimum_timer_auction(now):
    collection = get_mongodb_collection()
    while True:
        try:
            auction = await collection.find_one(
                {'timer': {'$exists': True, '$lte': now}},
                projection=("_id", "timer"),
                sort=(("timer", ASCENDING),)
            )
        except PyMongoError as e:
            logger.warning(f"Read timer error {type(e)}: {e}",
                           extra={"MESSAGE_ID": "MONITOR_MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
        else:
            return auction


async def get_auction_count_by_timer(dt):
    collection = get_mongodb_collection()
    while True:
        try:
            count = await collection.count_documents(
                {'timer': {'$exists': True, '$lte': dt}},
            )
        except PyMongoError as e:
            logger.warning(f"Read timer error {type(e)}: {e}",
                           extra={"MESSAGE_ID": "MONITOR_MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
        else:
            return count
