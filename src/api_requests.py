from prozorro_crawler.main import get_response_data
from settings import logger, CONNECTION_ERROR_INTERVAL, TOO_MANY_REQUESTS_INTERVAL, BASE_URL, DS_URL, DS_HEADERS
from json.decoder import JSONDecodeError
import aiohttp
import asyncio


async def get_tender_document(session, tender, private_only=False, public_only=False):
    # TODO add to /auction api response required public data (procuringEntity, title, description..
    # TODO .. bid.tenderers
    if not private_only:
        public_data = await get_response_data(session, f"{BASE_URL}/{tender['id']}")
        tender.update(public_data)
        if public_only:
            return tender
    private_data = await get_response_data(session, f"{BASE_URL}/{tender['id']}/auction")
    tender.update(private_data)
    if private_only:
        return tender
    for bid in tender.get("bids", ""):
        for public_bid in public_data.get("bids", ""):
            if bid["id"] == public_bid["id"]:
                bid.update(public_bid)
    for lot in tender.get("lots", ""):
        for public_lot in public_data.get("lots", ""):
            if lot["id"] == public_lot["id"]:
                lot.update(public_lot)
    return tender


async def patch_tender_auction(session, tender_id, json):
    return await request_tender(session, tender_id, json, url_suffix="/auction",  method_name="patch")


async def post_tender_auction(session, tender_id, json):
    return await request_tender(session, tender_id, json, url_suffix="/auction", method_name="post")


async def publish_tender_document(session, tender_id, data, doc_id=None):
    if doc_id:
        method_name = "put"
        url_suffix = f"/documents/{doc_id}"
    else:
        method_name = "post"
        url_suffix = "/documents"
    return await request_tender(session, tender_id, dict(data=data), url_suffix=url_suffix, method_name=method_name)


async def request_tender(session, tender_id, json, method_name="patch", url_suffix="", retries=5):
    method = getattr(session, method_name)
    while True:
        try:
            resp = await method(f"{BASE_URL}/{tender_id}{url_suffix}", json=json)
        except aiohttp.ClientError as e:
            logger.warning(f"Error for {tender_id} {type(e)}: {e}", extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
            await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
        else:
            if resp.status in (200, 201):
                try:
                    response = await resp.json()
                except (aiohttp.ClientPayloadError, JSONDecodeError) as e:
                    logger.warning(e, extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
                    await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
                else:
                    return response["data"]
            elif resp.status == 429:
                logger.warning("Too many requests while requesting tender",
                               extra={"MESSAGE_ID": "TOO_MANY_REQUESTS"})
                await asyncio.sleep(TOO_MANY_REQUESTS_INTERVAL)
            elif resp.status == 409:
                logger.warning("Resource error while requesting tender",
                               extra={"MESSAGE_ID": "RESOURCE_ERROR"})
                await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
            else:
                retries -= 1
                getattr(logger, "error" if retries else "critical")(
                    "Error on requesting tender {}: {} {}".format(
                        method_name,
                        resp.status,
                        await resp.text()
                    ),
                    extra={"MESSAGE_ID": "REQUEST_UNEXPECTED_ERROR"}
                )
                if not retries:
                    return
                await asyncio.sleep(CONNECTION_ERROR_INTERVAL)


async def upload_document(session, file_name, data):
    form_data = aiohttp.FormData()
    form_data.add_field("file", data, filename=file_name)
    while True:
        try:
            resp = await session.post(DS_URL, data=form_data, headers=DS_HEADERS)
        except aiohttp.ClientError as e:
            logger.warning(f"Error on file upload {type(e)}: {e}", extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
            await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
        else:
            print(resp.headers)
            if resp.status == 200:
                try:
                    response = await resp.json()
                except (aiohttp.ClientPayloadError, JSONDecodeError) as e:
                    logger.warning(e, extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
                    await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
                else:
                    return response["data"]
            else:
                logger.warning(
                    "Error on file upload {}: {} {}".format(
                        file_name,
                        resp.status,
                        await resp.text()
                    ),
                    extra={"MESSAGE_ID": "REQUEST_UNEXPECTED_ERROR"}
                )
                await asyncio.sleep(CONNECTION_ERROR_INTERVAL)
