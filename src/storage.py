from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from settings import (
    MONGODB_COLLECTION, MONGODB_URL, MONGODB_DATABASE, MONGODB_WRITE_CONCERN, MONGODB_ERROR_INTERVAL,
    logger, TZ, PROCESSING_LOCK
)
from pymongo.errors import PyMongoError
from pymongo import ASCENDING, DESCENDING
from datetime import datetime, timedelta
from time import time
from aiohttp import web
import asyncio


DB_CONNECTION = None
# List of indexes to be created in auctions collection
DB_INDEXES = [
    # {'keys': [('timer', ASCENDING)], 'sparse': True},
    {'keys': [('start_at', DESCENDING)]}
]


def get_mongodb_collection(collection_name=MONGODB_COLLECTION):
    global DB_CONNECTION
    DB_CONNECTION = DB_CONNECTION or AsyncIOMotorClient(MONGODB_URL, w=MONGODB_WRITE_CONCERN)
    db = getattr(DB_CONNECTION, MONGODB_DATABASE)
    collection = getattr(db, collection_name)
    return collection


# API methods
LIST_FIELDS = (
    "_id", "title", "title_en", "start_at", "procurementMethodType", "tenderID"
)
GET_FIELDS = (
    "_id", "procurementMethodType", "tenderID", "title", "title_en", "procuringEntity", "items",
    "start_at", "stages", "current_stage", "initial_bids", "modified",
)
UPDATE_CHRONOGRAPH_FIELDS = (
    "current_stage",
    "timer",
    "stages",
    "bids",  # to publish posted bids
    "initial_bids",
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
        raise web.HTTPServiceUnavailable()
    else:
        if not result:
            raise web.HTTPNotFound()
        return result


# Bridge methods
async def prepare_storage():
    collection = get_mongodb_collection()
    for index in DB_INDEXES:
        while True:
            try:
                r = await collection.create_index(**index, background=True)
            except PyMongoError as e:
                logger.warning(f"Prep storage {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
                await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            else:
                logger.info(f"Created index: {r}", extra={"MESSAGE_ID": "MONGODB_INDEX_SUCCESS"})
                break


@asynccontextmanager
async def read_and_update(auction_id):
    auction = await read_auction(auction_id)
    yield auction
    await asyncio.shield(update_auction(auction))


async def read_auction(auction_id):
    collection = get_mongodb_collection()
    while True:
        try:
            return await collection.find_one({'_id': auction_id})
        except PyMongoError as e:
            logger.error(f"Get auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)


async def update_auction(data, insert=True, fields=None):
    collection = get_mongodb_collection()
    set_data = {k: v for k, v in data.items() if k in fields} if fields else data
    while True:
        try:
            result = await collection.update_one(
                {
                    "_id": data["_id"]
                },
                {
                    "$set": set_data,
                    "$currentDate": {"modified": True}
                },
                upsert=insert
            )
            return result.upserted_id
        except PyMongoError as e:
            logger.error(f"Save auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)


@asynccontextmanager
async def read_expired_timer_and_update():
    collection = get_mongodb_collection()
    _start_time = time()
    current_ts = datetime.now(tz=TZ)
    # this is needed to guarantee that this object will not be touched by another chronograph
    processing_lock = timedelta(seconds=PROCESSING_LOCK)
    auction = await collection.find_one_and_update(
        {'timer': {'$exists': True, '$lte': current_ts}},
        {'$set': {'timer': current_ts + processing_lock}}
    )
    if auction:
        yield auction
        await update_auction(auction, fields=UPDATE_CHRONOGRAPH_FIELDS)
        _end_time = time()
        processing_time = _end_time - _start_time
        if processing_time >= PROCESSING_LOCK:
            message = (
                f"Auction {auction['_id']} processing time equals to {processing_time} seconds"
                f"and is bigger than processing lock time - {PROCESSING_LOCK} seconds."
                "This may lead to inconsistency of data!"
            )
            logger.critical(message)
        else:
            logger.info(f"Processed auction {auction['_id']}, time - {processing_time}")
    else:
        yield None
