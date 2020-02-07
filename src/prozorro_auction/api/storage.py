from prozorro_auction.storage import get_mongodb_collection
from prozorro_auction.settings import logger, MONGODB_ERROR_INTERVAL
from pymongo import DESCENDING
from pymongo.collection import ReturnDocument
from pymongo.errors import PyMongoError
from aiohttp import web
import asyncio

LIST_FIELDS = (
    "_id", "title", "title_en", "start_at", "procurementMethodType", "tenderID"
)
GET_FIELDS = (
    "_id", "auction_type", "procurementMethodType", "tenderID", "title", "title_en", "procuringEntity", "items", "features",
    "start_at", "stages", "current_stage", "initial_bids", "results", "modified", "minimalStep",
    "minimalStepPercentage", "noticePublicationDate", "NBUdiscountRate",  # esco
)


def to_projections(fields):
    return {field: 1 for field in fields}


async def read_auction_list(skip, limit=10):
    collection = get_mongodb_collection()
    auctions = []
    cursor = collection.find({}, to_projections(LIST_FIELDS)).sort("start", DESCENDING)
    async for obj in cursor.skip(skip * limit).limit(limit):
        auctions.append(obj)
    return auctions


async def get_auction(auction_id, fields=GET_FIELDS):
    collection = get_mongodb_collection()
    try:
        result = await collection.find_one({'_id': auction_id}, to_projections(fields))
    except PyMongoError as e:
        logger.error(f"Get auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
        raise web.HTTPInternalServerError()
    else:
        if not result:
            raise web.HTTPNotFound()
        return result


async def watch_changed_docs():
    collection = get_mongodb_collection()
    resume_after = None

    while True:
        logger.info(f"Start watching mongodb changes after {resume_after}")
        changes = collection.watch(full_document="updateLookup", resume_after=resume_after)

        while True:
            try:
                change = await changes.next()
            except PyMongoError as e:
                logger.error(f"Got feed error {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
                await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            except StopAsyncIteration as e:
                logger.exception(e)
                resume_after = None
                break
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            else:
                resume_after = change["_id"]
                if "fullDocument" in change:   # present in insert/update changes
                    auction = {k: v
                               for k, v in change["fullDocument"].items()
                               if k in GET_FIELDS}
                    yield auction


async def insert_auction(data):
    collection = get_mongodb_collection()
    try:
        result = await collection.update_one(
            {
                "_id": data["_id"]
            },
            {
                "$set": data,
                "$currentDate": {"modified": True}
            },
            upsert=True
        )
        return result.upserted_id
    except PyMongoError as e:
        logger.error(f"Save auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
        raise web.HTTPInternalServerError()


async def update_auction_bid_stage(auction_id, bid_id, stage_id, value):
    collection = get_mongodb_collection()
    try:
        result = await collection.find_one_and_update(
            {"_id": auction_id},
            {
                "$set" if value else "$unset": {
                    f"bids.$[bid].stages.{stage_id}": value
                },
            },
            array_filters=[
                {"bid.id": bid_id},
            ],
            return_document=ReturnDocument.AFTER
        )
        return result
    except PyMongoError as e:
        logger.error(f"Save auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
        raise web.HTTPInternalServerError()
