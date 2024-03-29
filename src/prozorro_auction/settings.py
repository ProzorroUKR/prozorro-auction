from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from prozorro_crawler.settings import *
from base64 import b64encode
import pytz
import os

from prozorro_auction.constants import PROCUREMENT_METHOD_TYPES_DEFAULT

API_PORT = int(os.environ.get("API_PORT", 8000))
TZ = pytz.timezone(os.environ.get("TZ", "Europe/Kiev"))
TEST_MODE = os.environ.get("TEST_MODE", False)


API_HOST = os.environ.get("API_HOST", "https://lb-api-sandbox.prozorro.gov.ua")
API_TOKEN = os.environ.get("API_TOKEN", "auction")
assert not API_HOST.endswith("/")
assert API_HOST.startswith("http")
BASE_URL = f"{API_HOST}/api/{API_VERSION}/tenders"
API_HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": CRAWLER_USER_AGENT,
}

DS_HOST = os.environ.get("DS_HOST", "https://upload-docs.prozorro.gov.ua")
assert not DS_HOST.endswith("/")
assert DS_HOST.startswith("http")
DS_URL = f"{DS_HOST}/upload"
DS_USER = os.environ.get("DS_USER", "bot")
DS_PASSWORD = os.environ.get("DS_PASSWORD", "bot")
DS_TOKEN = b64encode(f"{DS_USER}:{DS_PASSWORD}".encode()).decode()
DS_HEADERS = {
    "Authorization": f"Basic {DS_TOKEN}",
    "User-Agent": CRAWLER_USER_AGENT,
}


if "PROCUREMENT_TYPES" in os.environ:
    PROCUREMENT_TYPES = os.environ.get("PROCUREMENT_TYPES").split(",")
else:
    PROCUREMENT_TYPES = PROCUREMENT_METHOD_TYPES_DEFAULT


# replace defaults from crawler.settings
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "prozorro-auction")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "auctions")
READ_PREFERENCE = getattr(ReadPreference, os.environ.get("READ_PREFERENCE", "PRIMARY"))
raw_write_concert = os.environ.get("WRITE_CONCERN", "majority")
WRITE_CONCERN = WriteConcern(w=int(raw_write_concert) if raw_write_concert.isnumeric() else raw_write_concert)
READ_CONCERN = ReadConcern(level=os.environ.get("READ_CONCERN") or "majority")

# number of seconds to protect auction from other workers
PROCESSING_LOCK = float(os.getenv("PROCESSING_LOCK", 1))
AUCTION_HOST = os.getenv("AUCTION_HOST", "http://localhost:8080")
assert not AUCTION_HOST.endswith("/")
assert AUCTION_HOST.startswith("http")
QUICK_MODE_FAST_AUCTION_START_AFTER = int(os.getenv("QUICK_MODE_FAST_AUCTION_START_AFTER", 5))


LATENCY_TIME = float(os.getenv("LATENCY_TIME", 2 * 60))
SENTRY_DSN = os.environ.get("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT")

MASK_OBJECT_DATA_SINGLE = bool(os.environ.get("DEFAULT_MASK_OBJECT_DATA_SINGLE", False))
