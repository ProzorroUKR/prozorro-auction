from prozorro_crawler.settings import *
from base64 import b64encode
import pytz
import os

API_PORT = int(os.environ.get("API_PORT", 8000))
TZ = pytz.timezone(os.environ.get("TZ", "Europe/Kiev"))
USER_AGENT = os.environ.get("USER_AGENT", "Auction 2.0")
TEST_MODE = os.environ.get("TEST_MODE", False)


API_HOST = os.environ.get("API_HOST", "https://lb-api-sandbox.prozorro.gov.ua")
API_TOKEN = os.environ.get("API_TOKEN", "auction")
assert not API_HOST.endswith("/")
assert API_HOST.startswith("http")
BASE_URL = f"{API_HOST}/api/{API_VERSION}/tenders"
API_HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": USER_AGENT,
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
    "User-Agent": USER_AGENT,
}


PROCUREMENT_TYPES = os.environ.get(
    "PROCUREMENT_TYPES",
    "closeFrameworkAgreementUA,belowThreshold,aboveThresholdEU,aboveThresholdUA,aboveThresholdUA.defense,"
    "competitiveDialogueEU.stage2,competitiveDialogueUA.stage2,esco"
).split(",")


# replace defaults from crawler.settings
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "prozorro-auction")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "auctions")
MONGODB_WRITE_CONCERN = os.environ.get("MONGODB_WRITE_CONCERN", "majority")

# number of seconds to protect auction from other workers
PROCESSING_LOCK = os.getenv("PROCESSING_LOCK", 1)
AUCTION_HOST = os.getenv("AUCTION_HOST", "http://localhost:8080")
assert not AUCTION_HOST.endswith("/")
assert AUCTION_HOST.startswith("http")


PREFIX_NEW_AUCTION = os.getenv("PREFIX_NEW_AUCTION", "")

