from prozorro_auction.storage import get_mongodb_collection
from prozorro_auction.settings import logger, PROCESSING_LOCK, MONGODB_ERROR_INTERVAL
from prozorro_auction.utils import get_now
from pymongo.errors import PyMongoError
from pymongo.collection import ReturnDocument
from datetime import timedelta
import asyncio


UPDATE_CHRONOGRAPH_FIELDS = (
    "current_stage",
    "finished_stage",
    "timer",
    "chronograph_errors_count",
    "stages",
    "initial_bids",
    "results",
    "bids",  # to publish posted bids
    "_audit_document_posted",
    "_auction_results_sent",
)


async def increase_and_read_expired_timer():
    collection = get_mongodb_collection()
    while True:
        current_ts = get_now()
        # this is needed to guarantee that this object will not be touched by another chronograph
        processing_lock = timedelta(seconds=PROCESSING_LOCK)
        try:
            auction = await collection.find_one_and_update(
                {'timer': {'$exists': True, '$lte': current_ts}},
                {'$set': {'timer': current_ts + processing_lock}},
                return_document=ReturnDocument.AFTER
            )
        except PyMongoError as e:
            logger.warning(f"Read timer error {type(e)}: {e}",
                           extra={"MESSAGE_ID": "CHRONOGRAPH_MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
        else:
            return auction


async def update_auction(data, update_date=True):
    collection = get_mongodb_collection()
    set_data = {k: v for k, v in data.items() if k in UPDATE_CHRONOGRAPH_FIELDS}
    update = {}

    if update_date:
        update["$currentDate"] = {"modified": True}

    if "timer" in set_data and set_data["timer"] is None:
        del set_data["timer"]
        update["$unset"] = {"timer": ""}

    if set_data:
        update["$set"] = set_data

    if not update:
        logger.critical(f"There is nothing to update: {data}")
        return

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
