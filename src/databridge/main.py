# -*- coding: utf-8 -*-
from prozorro_crawler.main import main
from databridge.model import (
    get_auctions_from_tender,
    get_canceled_auctions_from_tender,
    copy_bid_tokens,
)
from api_requests import get_tender_document, patch_tender_auction
from storage import prepare_storage, update_auction, read_auction
from settings import API_TOKEN, PROCUREMENT_TYPES, AUCTION_HOST, logger
from utils import get_now
import pytz
import asyncio


async def post_auction_urls(session, auction, tender):
    auction_url = f"{AUCTION_HOST}/tenders/{auction['_id']}"
    patch_bids = []
    patch_data = {"data": {"auctionUrl": auction_url, "bids": patch_bids}}
    for tender_bid in tender["bids"]:
        for bid in auction["bids"]:
            if tender_bid["id"] == bid["id"]:
                participation_url = f"{auction_url}/login?bidder_id={bid['id']}&hash={bid['hash']}"
                if auction["lot_id"]:
                    patch_lot_values = []
                    for lot_bid in tender_bid['lotValues']:
                        if auction["lot_id"] == lot_bid['relatedLot']:
                            patch_lot_values.append(
                                {
                                    "participationUrl": participation_url,
                                    "relatedLot": lot_bid["relatedLot"],
                                }
                            )
                        else:
                            patch_lot_values.append(
                                {"relatedLot": lot_bid["relatedLot"]}
                            )
                    patch_bids.append(
                        {
                            "lotValues": patch_lot_values,
                            "id": bid["id"]
                        }
                    )
                else:
                    patch_bids.append(
                        {
                            "participationUrl": participation_url,
                            "id": bid["id"]
                        }
                    )
                break
        else:
            patch_bids.append({"id": tender_bid["id"]})

    await patch_tender_auction(session, tender["id"], patch_data)
    logger.info(f"Set auction and participation urls for auction {auction['_id']}",
                extra={"MESSAGE_ID": "SET_AUCTION_URLS"})


async def schedule_auction(session, auction, saved_auction, tender):
    logger.info(f"Scheduling {auction['_id']} at {auction['start_at']}")
    if saved_auction:   # copy previous tokens, so the participation links remain valid
        copy_bid_tokens(saved_auction, auction)

    await update_auction(auction, insert=True)

    if not saved_auction:  # we assume they were already set
        await post_auction_urls(session, auction, tender)


async def process_tender_data(session, tender):
    if tender["procurementMethodType"] in PROCUREMENT_TYPES:
        tasks = []

        if tender["status"] == "active.auction":
            # getting tender data
            tender = await get_tender_document(session, tender)
            # processing auctions
            for auction in get_auctions_from_tender(tender):
                if auction.get("is_cancelled"):
                    logger.info(f"Cancelling {auction['_id']}")
                    tasks.append(update_auction(auction, insert=False))
                else:
                    saved_auction = await read_auction(auction["_id"])
                    if saved_auction:
                        if saved_auction.get("current_stage"):
                            logger.info(f"Skipping {auction['_id']} already started at {saved_auction['start_at']}")
                            continue

                        min_time, max_time = sorted((pytz.utc.localize(saved_auction["start_at"]), auction["start_at"]))
                        if (max_time - min_time).seconds < 1:
                            logger.info(f"Skipping {auction['_id']} already scheduled at {auction['start_at']}")
                            continue

                    tasks.append(schedule_auction(session, auction, saved_auction, tender))

        elif tender["status"] == "cancelled":
            logger.info(f"Cancelling {tender['id']} auctions")
            for auction in get_canceled_auctions_from_tender(tender):
                tasks.append(
                    update_auction(auction, insert=False)
                )

        await asyncio.gather(*tasks)


async def auction_data_handler(session, items):
    process_items_tasks = (process_tender_data(session, item) for item in items)
    await asyncio.gather(*process_items_tasks)


if __name__ == '__main__':
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "User-Agent": "Auction bridge 2.0",
    }
    main(auction_data_handler, init_task=prepare_storage, additional_headers=headers)
