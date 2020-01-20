from motor.motor_asyncio import AsyncIOMotorClient
from prozorro_auction.settings import (
    MONGODB_COLLECTION, MONGODB_URL,
    MONGODB_DATABASE, MONGODB_WRITE_CONCERN,
)
DB_CONNECTION = None


def get_mongodb_collection(collection_name=MONGODB_COLLECTION):
    global DB_CONNECTION
    DB_CONNECTION = DB_CONNECTION or AsyncIOMotorClient(MONGODB_URL, w=MONGODB_WRITE_CONCERN)
    db = getattr(DB_CONNECTION, MONGODB_DATABASE)
    collection = getattr(db, collection_name)
    return collection
