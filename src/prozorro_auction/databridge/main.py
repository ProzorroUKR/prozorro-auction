# -*- coding: utf-8 -*-
from prozorro_crawler.main import main
from prozorro_auction.databridge.tasks import schedule_auction
from prozorro_auction.databridge.model import get_auctions_from_tender, get_canceled_auctions_from_tender
from prozorro_auction.databridge.requests import get_tender_document
from prozorro_auction.databridge.storage import prepare_storage, update_auction
from prozorro_auction.settings import API_TOKEN, PROCUREMENT_TYPES, logger
import asyncio


async def process_tender_data(session, tender):
    if tender["procurementMethodType"] in PROCUREMENT_TYPES:
        tasks = []
        if tender["status"] == "active.auction":
            # updating tender data with the fill private and public data
            tender = await get_tender_document(session, tender)
            # processing auctions
            for auction in get_auctions_from_tender(tender):
                tasks.append(schedule_auction(session, auction, tender))

        elif tender["status"] == "cancelled":
            logger.info(f"Cancelling {tender['id']} auctions")
            for auction in get_canceled_auctions_from_tender(tender):
                tasks.append(
                    update_auction(auction, insert=False)
                )
        await asyncio.gather(*tasks)
    else:
        logger.info(f"Skipping {tender['id']} as {tender['procurementMethodType']} not in PROCUREMENT_TYPES")


async def auction_data_handler(session, items):
    process_items_tasks = (process_tender_data(session, item) for item in items)
    await asyncio.gather(*process_items_tasks)


if __name__ == '__main__':
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "User-Agent": "Auction bridge 2.0",
    }
    main(auction_data_handler, init_task=prepare_storage, additional_headers=headers)
