from motor.motor_asyncio import AsyncIOMotorClient
from prozorro_auction.settings import (
    MONGODB_COLLECTION, MONGODB_URL,
    MONGODB_DATABASE,
    WRITE_CONCERN, READ_PREFERENCE, READ_CONCERN,
)
from bson.codec_options import CodecOptions, TypeDecoder, TypeRegistry, TypeCodec
from bson.decimal128 import Decimal128
from bson import Int64
from decimal import Decimal

DB_CONNECTION = None


def fallback_encoder(value):
    if isinstance(value, set):
        return list(value)
    return value


class Int64Decoder(TypeDecoder):
    """
    bson.Int64 is not converted to python int type by default
    that causes problems with converting this type to yaml
    also may cause more pain later
    """
    bson_type = Int64

    def transform_bson(self, value):
        return int(value)


class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)

    def transform_bson(self, value):
        return value.to_decimal()


type_registry = TypeRegistry(type_codecs=[Int64Decoder(), DecimalCodec()], fallback_encoder=fallback_encoder)
codec_options = CodecOptions(type_registry=type_registry)


def get_mongodb_collection(collection_name=MONGODB_COLLECTION):
    global DB_CONNECTION
    DB_CONNECTION = DB_CONNECTION or AsyncIOMotorClient(MONGODB_URL)
    db = DB_CONNECTION.get_database(
        MONGODB_DATABASE,
        read_preference=READ_PREFERENCE,
        write_concern=WRITE_CONCERN,
        read_concern=READ_CONCERN,
    )
    collection = db.get_collection(collection_name, codec_options=codec_options)
    return collection
