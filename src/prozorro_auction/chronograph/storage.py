from prozorro_auction.storage import get_mongodb_collection
from prozorro_auction.settings import logger, TZ, PROCESSING_LOCK, MONGODB_ERROR_INTERVAL
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
import asyncio


UPDATE_CHRONOGRAPH_FIELDS = (
    "current_stage",
    "timer",
    "chronograph_errors_count",
    "stages",
    "bids",  # to publish posted bids
    "initial_bids",
    "results",
)


async def increase_and_read_expired_timer():
    collection = get_mongodb_collection()
    while True:
        current_ts = datetime.now(tz=TZ)
        # this is needed to guarantee that this object will not be touched by another chronograph
        processing_lock = timedelta(seconds=PROCESSING_LOCK)
        try:
            auction = await collection.find_one_and_update(
                {'timer': {'$exists': True, '$lte': current_ts}},
                {'$set': {'timer': current_ts + processing_lock}}
            )
        except PyMongoError as e:
            logger.warning(f"Read timer error {type(e)}: {e}",
                           extra={"MESSAGE_ID": "CHRONOGRAPH_MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
        else:
            return auction


async def update_auction(data):
    collection = get_mongodb_collection()
    set_data = {k: v for k, v in data.items() if k in UPDATE_CHRONOGRAPH_FIELDS}
    update = {"$currentDate": {"modified": True}}

    if "timer" in set_data and set_data["timer"] is None:
        del set_data["timer"]
        update["$unset"] = {"timer": ""}

    if set_data:
        update["$set"] = set_data

    retries = 0
    while True:
        try:
            result = await collection.update_one(
                {"_id": data["_id"]},
                update,
                upsert=False
            )
            return result
        except PyMongoError as e:
            log_method = getattr(logger, "critical" if retries > 3 else "warning")
            log_method(f"Save auction error {type(e)}: {e}", extra={"MESSAGE_ID": "CHRONOGRAPH_MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            retries += 1
