from prozorro_auction.settings import logger
from prozorro_auction.databridge.requests import patch_tender_auction, request_tender, get_tender_data
from prozorro_auction.databridge.model import copy_bid_tokens, build_urls_patch, set_auction_bidders_real_names
from prozorro_auction.databridge.storage import update_auction, read_auction
from prozorro_auction.chronograph.tasks import send_auction_results
from prozorro_auction.exceptions import SkipException
import pytz


async def schedule_auction(session, auction, tender):

    mode = auction["mode"]
    try:
        if auction["is_cancelled"]:
            logger.info(f"Cancelling {auction['_id']}")
            await update_auction(auction, insert=False)

        elif mode and mode.endswith("quick(mode:no-auction)"):
            await send_auction_results(session, auction, tender["bids"],
                                       request_tender_method=request_tender)  # to handle retries

        else:
            saved_auction = await read_auction(auction["_id"])
            if saved_auction:
                current_stage = saved_auction.get("current_stage")

                if current_stage is not None and current_stage not in [-101, -1]:
                    logger.info(f"Skipping {auction['_id']} already started at {saved_auction['start_at']}")
                    return

                min_time, max_time = sorted((pytz.utc.localize(saved_auction["start_at"]), auction["start_at"]))
                if (max_time - min_time).seconds < 1:
                    logger.info(f"Skipping {auction['_id']} already scheduled at {auction['start_at']}")
                    return

                # copy previous tokens, so the participation links remain valid
                copy_bid_tokens(saved_auction, auction)

            logger.info(f"Scheduling {auction['_id']} at {auction['start_at']}")
            if not saved_auction:  # we assume they were already set
                await post_auction_urls(session, auction, tender)
            await update_auction(auction, insert=True)
    except SkipException:
        logger.info(f"Skip scheduling {auction['_id']}. See the reason above")
        pass


async def post_auction_urls(session, auction, tender):
    """
    When auction is scheduled it's urls are posted to the tenders api
    """
    patch_data = build_urls_patch(auction, tender)
    await patch_tender_auction(session, tender["id"], auction["lot_id"], patch_data)
    logger.info(f"Set auction and participation urls for auction {auction['_id']}",
                extra={"MESSAGE_ID": "SET_AUCTION_URLS"})


async def reveal_auction_names(session, tender_id):
    try:
        tender = await get_tender_data(session, tender_id)
    except SkipException:
        return

    # get and reveal tenderer names
    if "bids" not in tender:
        logger.error(f"Bids info not public yet: tender_id", extra={"MESSAGE_ID": "BIDS_NOT_FOUND"})
        return

    if "lots" in tender:
        auction_ids = [f"{tender['id']}_{lot['id']}" for lot in tender.get("lots")]
    else:
        auction_ids = (tender['id'],)

    for auction_id in auction_ids:
        auction = await read_auction(auction_id)
        if auction is None:  # if auction is not in the db, we skip it
            logger.info(f"Not found; skipping {tender['id']} reveal task",
                        extra={"MESSAGE_ID": "AUCTION_NOT_FOUND"})
        else:
            if auction.get("names_revealed"):
                logger.info(f"Not found; skipping {tender['id']} reveal task",
                            extra={"MESSAGE_ID": "AUCTION_REVEAL_ALREADY_DONE"})
            else:
                set_auction_bidders_real_names(auction, tender["bids"])
                await update_auction(auction)
                logger.info(f"Success {tender['id']} reveal task",
                            extra={"MESSAGE_ID": "AUCTION_REVEAL_DONE"})
