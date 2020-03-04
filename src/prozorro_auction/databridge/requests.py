from prozorro_auction.base_requests import request_tender as base_request_tender
from prozorro_auction.settings import logger
from prozorro_auction.exceptions import RequestRetryException, SkipException
from contextlib import contextmanager
import asyncio


async def get_tender_document(session, tender, private_only=False, public_only=False):
    # TODO add to /auction api response required public data (procuringEntity, title, description..
    # TODO .. bid.tenderers ?
    if public_only:
        public_data = await get_tender_data(session, tender["id"])
        tender.update(public_data)
    elif private_only:
        private_data = await get_tender_data(session, tender["id"], url_suffix="/auction")
        tender.update(private_data)
    else:
        public_data, private_data = await asyncio.gather(
            get_tender_data(session, tender["id"]),
            get_tender_data(session, tender["id"], url_suffix="/auction")
        )
        tender.update(public_data)
        tender.update(private_data)
        for bid in tender.get("bids", ""):
            for public_bid in public_data.get("bids", ""):
                if bid["id"] == public_bid["id"]:
                    bid.update(public_bid)
        for lot in tender.get("lots", ""):
            for public_lot in public_data.get("lots", ""):
                if lot["id"] == public_lot["id"]:
                    lot.update(public_lot)
    return tender


async def get_tender_data(session, tender_id, url_suffix=""):
    return await request_tender(session, tender_id, url_suffix=url_suffix)


async def patch_tender_auction(session, tender_id, lot_id, json):
    suffix = f"/auction/{lot_id}" if lot_id else "/auction"
    return await request_tender(session, tender_id, json, url_suffix=suffix,  method_name="patch")


async def request_tender(session, tender_id, json=None, method_name="get", url_suffix="", retries=20):
    while True:
        try:
            result = await base_request_tender(session=session, tender_id=tender_id, json=json,
                                               method_name=method_name, url_suffix=url_suffix)
        except RequestRetryException as e:
            if e.response and e.response.status == 403:
                logger.warning(f"Skip processing {tender_id} as we get 403 response")
                raise SkipException()

            retries -= 1
            if retries < 1:
                logger.critical("Too many retries while requesting tender",
                                extra={"MESSAGE_ID": "TOO_MANY_REQUEST_RETRIES"})
            await asyncio.sleep(e.timeout)
        else:
            return result
