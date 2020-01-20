from prozorro_auction.exceptions import RequestRetryException
from prozorro_auction.settings import logger, CONNECTION_ERROR_INTERVAL, TOO_MANY_REQUESTS_INTERVAL, BASE_URL
from json.decoder import JSONDecodeError
import aiohttp


async def request_tender(session, tender_id, json=None, method_name="get", url_suffix=""):
    method = getattr(session, method_name)
    kwargs = {}
    if json:
        kwargs["json"] = json
    try:
        resp = await method(f"{BASE_URL}/{tender_id}{url_suffix}", **kwargs)
    except aiohttp.ClientError as e:
        logger.warning(f"Error for {tender_id} {type(e)}: {e}", extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
        resp = None
    else:
        if resp.status in (200, 201):
            try:
                response = await resp.json()
            except (aiohttp.ClientPayloadError, JSONDecodeError) as e:
                logger.warning(e, extra={"MESSAGE_ID": "HTTP_EXCEPTION"})
            else:
                return response["data"]
        elif resp.status == 412:
            logger.warning("Precondition Failed while requesting tender",
                           extra={"MESSAGE_ID": "PRECONDITION_FAILED"})
            raise RequestRetryException()
        elif resp.status == 429:
            logger.warning("Too many requests while requesting tender",
                           extra={"MESSAGE_ID": "TOO_MANY_REQUESTS"})
            raise RequestRetryException(timeout=TOO_MANY_REQUESTS_INTERVAL)
        elif resp.status == 409:
            logger.warning(f"Resource error while requesting tender {tender_id}",
                           extra={"MESSAGE_ID": "RESOURCE_ERROR"})
        else:
            resp_text = await resp.text()
            logger.error(
                f"Error on requesting tender {method_name} {tender_id}: {resp.status} {resp_text}",
                extra={"MESSAGE_ID": "REQUEST_UNEXPECTED_ERROR"}
            )

    raise RequestRetryException(timeout=CONNECTION_ERROR_INTERVAL, response=resp)  # default raise
