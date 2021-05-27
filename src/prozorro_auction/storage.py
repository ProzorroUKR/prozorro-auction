from motor.motor_asyncio import AsyncIOMotorClient
from prozorro_auction.settings import (
    MONGODB_COLLECTION, MONGODB_URL,
    MONGODB_DATABASE,
    WRITE_CONCERN, READ_PREFERENCE, READ_CONCERN,
)
DB_CONNECTION = None


def get_mongodb_collection(collection_name=MONGODB_COLLECTION):
    global DB_CONNECTION
    DB_CONNECTION = DB_CONNECTION or AsyncIOMotorClient(MONGODB_URL)
    db = DB_CONNECTION.get_database(
        MONGODB_DATABASE,
        read_preference=READ_PREFERENCE,
        write_concern=WRITE_CONCERN,
        read_concern=READ_CONCERN,
    )
    collection = getattr(db, collection_name)
    return collection
