from prozorro_auction.settings import API_HEADERS
from datetime import datetime, timedelta
from prozorro_auction.chronograph.requests import get_tender_documents, get_tender_bids
from prozorro_auction.chronograph.tasks import upload_audit_document, send_auction_results
from prozorro_auction.chronograph.storage import update_auction
from prozorro_auction.utils.base import get_now
from prozorro_auction.chronograph.model import (
    sort_bids, get_label_dict, get_bidder_number, update_auction_results,
    publish_bids_made_in_current_stage, copy_bid_stage_fields,
)
from prozorro_auction.settings import LATENCY_TIME
import aiohttp
import logging

logger = logging.getLogger(__name__)


async def tick_auction(auction):
    now = datetime.now()
    current_stage = auction.get("current_stage", -1)

    stages = auction.get("stages")
    next_stage_index = current_stage + 1
    if next_stage_index >= len(stages):
        auction["timer"] = None
        return logger.error(f"Chronograph tries to update auction "
                            f"to a non-existed stage {next_stage_index}")

    next_stage = stages[next_stage_index]

    if next_stage["start"] > now:
        return logger.error(f"Chronograph tries to update auction too early {next_stage['start']}")

    if (
        next_stage["start"] + timedelta(seconds=LATENCY_TIME) < now
        and next_stage["type"] not in ("pre_announcement", "announcement")
    ):
        auction.update({"current_stage": -101, "results": [], "timer": None})
        return logger.info(f"Next stage in auction auction has not started and auction will be rescheduled")

    await run_stage_methods(auction, stages, current_stage)

    # update stage fields
    auction["current_stage"] = next_stage_index
    next_stage = auction["current_stage"] + 1
    if next_stage < len(stages):
        auction["timer"] = stages[next_stage]["start"]
    else:
        auction["timer"] = None


async def run_stage_methods(auction, stages, current_stage):
    # run end stage method
    finished_stage = auction.get("finished_stage")
    if current_stage > -1 and \
       current_stage != finished_stage:  # to run "on_end" methods only once in case of any exceptions after their run

        this_stage = stages[current_stage]
        end_method = globals().get(f"on_end_stage_{this_stage['type']}")
        if end_method:
            await end_method(auction)

        auction["finished_stage"] = current_stage

    # start next stage method
    next_stage = stages[current_stage + 1]
    start_method = globals().get(f"on_start_stage_{next_stage['type']}")
    if start_method:
        await start_method(auction)


async def on_start_stage_pause(auction):
    current_stage = auction.get("current_stage", -1)
    # set initial_bids
    if current_stage == -1:
        logger.info("Set initial bids")
        auction["initial_bids"] = []
        for n, bid in enumerate(sort_bids(auction["bids"])):
            initial_bid = dict(label=get_label_dict(n))
            copy_bid_stage_fields(bid, initial_bid)
            auction["initial_bids"].append(initial_bid)

        # and set the (possible) results section
        update_auction_results(auction)

    # set "bidder" for bid rounds according to the bids they made before
    stages = auction.get("stages")
    index = current_stage + 2
    logger.info(f"Set {index}:{index + len(auction['bids'])} bid stages order")
    for i, bid in enumerate(sort_bids(auction["bids"])):
        bid_stage = dict(
            label=get_label_dict(
                get_bidder_number(bid["id"], auction["initial_bids"])
            )
        )
        copy_bid_stage_fields(bid, bid_stage)
        stages[index + i].update(bid_stage)


async def on_end_stage_bids(auction):
    """
    copy posted bid to "bids" field
    """
    publish_bids_made_in_current_stage(auction)
    update_auction_results(auction)


async def on_start_stage_pre_announcement(auction):
    pass   # i don't want run long running tasks here, as it would delay finishing of the last bid stage


POSTPONE_ANNOUNCEMENT_TD = timedelta(seconds=2 * 60)


async def on_start_stage_announcement(auction):
    """
    1 upload audit document
    2 send auction results to tenders api
    """
    # increase timer as this task usually takes more than 2 sec
    await update_auction(
        {"_id": auction["_id"], "timer": get_now() + POSTPONE_ANNOUNCEMENT_TD},
        update_date=False
    )

    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        if not auction.get("_audit_document_posted"):
            # post audit document
            tender_documents = await get_tender_documents(session, auction["tender_id"])  # public data
            await upload_audit_document(session, auction, tender_documents)

            await update_auction(
                {"_id": auction["_id"], "_audit_document_posted": True},
                update_date=False
            )

        # send results to the api
        tender_bids = await get_tender_bids(session, auction["tender_id"])  # private data
        await send_auction_results(session, auction, tender_bids)
