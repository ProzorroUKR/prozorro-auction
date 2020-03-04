from prozorro_auction.settings import DS_URL, DS_HEADERS, CONNECTION_ERROR_INTERVAL, logger
from prozorro_auction.exceptions import RequestRetryException, RetryException
from json.decoder import JSONDecodeError
from prozorro_auction.base_requests import request_tender
import aiohttp


# DS REQUESTS
async def upload_document(session, file_name, data):
    form_data = aiohttp.FormData()
    form_data.add_field("file", data, filename=file_name)
    while True:
        try:
            resp = await session.post(DS_URL, data=form_data, headers=DS_HEADERS)
        except aiohttp.ClientError as e:
            logger.warning(f"Error on file upload {type(e)}: {e}", extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
            raise RequestRetryException(CONNECTION_ERROR_INTERVAL)
        else:
            if resp.status in (200, 201):
                try:
                    response = await resp.json()
                except (aiohttp.ClientPayloadError, JSONDecodeError) as e:
                    logger.warning(e, extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
                    raise RequestRetryException(CONNECTION_ERROR_INTERVAL)
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
                raise RequestRetryException(CONNECTION_ERROR_INTERVAL)


# TENDER REQUESTS
async def get_tender_documents(session, tender_id):
    data = await request_tender(session, tender_id)
    return data.get("documents", "")


async def get_tender_public_bids(session, tender_id):
    data = await request_tender(session, tender_id)
    try:
        bids = data["bids"]
    except KeyError:
        logger.warning(f"Bids info not public yet: {tender_id}", extra={"MESSAGE_ID": "BIDS_NOT_FOUND"})
        raise RetryException()
    else:
        return bids


async def get_tender_bids(session, tender_id):
    data = await request_tender(session, tender_id, url_suffix="/auction")
    return data.get("bids", "")


async def post_tender_auction(session, tender_id, json, request_tender_method=None):
    request_tender_method = request_tender_method or request_tender
    return await request_tender_method(session, tender_id, json, url_suffix="/auction", method_name="post")


async def publish_tender_document(session, tender_id, data, doc_id=None):
    if doc_id:
        method_name = "put"
        url_suffix = f"/documents/{doc_id}"
    else:
        method_name = "post"
        url_suffix = "/documents"
    return await request_tender(session, tender_id, dict(data=data), url_suffix=url_suffix, method_name=method_name)
