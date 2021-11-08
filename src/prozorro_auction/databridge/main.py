from prozorro_crawler.main import main
from prozorro_auction.exceptions import SkipException
from prozorro_auction.databridge.tasks import schedule_auction, reveal_auction_names
from prozorro_auction.databridge.model import get_auctions_from_tender, get_canceled_auctions_from_tender
from prozorro_auction.databridge.requests import get_tender_document
from prozorro_auction.databridge.storage import prepare_storage, update_auction
from prozorro_auction.settings import API_TOKEN, PROCUREMENT_TYPES, SENTRY_DSN, CRAWLER_USER_AGENT
from prozorro_auction.logging import update_log_context, setup_logging, log_context
import asyncio
import sentry_sdk
import logging


logger = logging.getLogger(__name__)


async def process_tender_data(session, tender):
    procurement_method_type = tender.get("procurementMethodType")
    with log_context(TENDER_ID=tender['id']):
        if procurement_method_type in PROCUREMENT_TYPES:
            tasks = []
            if tender["status"] == "active.auction":
                # updating tender data with the fill private and public data
                try:
                    tender = await get_tender_document(session, tender)
                except SkipException:
                    return   # logging should be done just before raising this exc
                # processing auctions
                for auction in get_auctions_from_tender(tender):
                    tasks.append(schedule_auction(session, auction, tender))

            elif tender["status"] == "cancelled":
                logger.info(f"Cancelling auctions")
                for auction in get_canceled_auctions_from_tender(tender):
                    tasks.append(
                        update_auction(auction, insert=False)
                    )
            elif tender["status"] == "active.qualification":  # publish bidder names
                tasks.append(
                    reveal_auction_names(session, tender["id"])
                )
            await asyncio.gather(*tasks)
        else:
            logger.info(f"Skipping as {procurement_method_type} not in PROCUREMENT_TYPES")


async def auction_data_handler(session, items):
    process_items_tasks = (process_tender_data(session, item) for item in items)
    await asyncio.gather(*process_items_tasks)


if __name__ == '__main__':
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN)

    setup_logging()
    update_log_context(SYSLOG_IDENTIFIER="AUCTION_DATABRIDGE")
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "User-Agent": CRAWLER_USER_AGENT,
    }
    main(auction_data_handler, init_task=prepare_storage, additional_headers=headers)
