from prozorro_auction.storage import get_mongodb_collection
from prozorro_auction.settings import MONGODB_ERROR_INTERVAL, logger
from pymongo.errors import PyMongoError
from pymongo import ASCENDING, DESCENDING
import asyncio

# List of indexes to be created in auctions collection
DB_INDEXES = [
    {'keys': [('timer', ASCENDING)], 'sparse': True},
    {'keys': [('start_at', DESCENDING)]}
]


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


async def read_auction(auction_id):
    collection = get_mongodb_collection()
    while True:
        try:
            return await collection.find_one({'_id': auction_id})
        except PyMongoError as e:
            logger.error(f"Get auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)


async def update_auction(data, insert=True):
    collection = get_mongodb_collection()
    while True:
        try:
            result = await collection.update_one(
                {
                    "_id": data["_id"]
                },
                {
                    "$set": data,
                    "$currentDate": {"modified": True}
                },
                upsert=insert
            )
            return result.upserted_id
        except PyMongoError as e:
            logger.error(f"Save auction {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
