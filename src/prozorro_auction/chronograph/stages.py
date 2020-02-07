from prozorro_auction.settings import logger, API_HEADERS
from datetime import datetime
from prozorro_auction.chronograph.tasks import upload_audit_document, send_auction_results
from prozorro_auction.chronograph.model import (
    sort_bids, get_label_dict, get_bidder_number, update_auction_results,
    publish_bids_made_in_current_stage, copy_bid_stage_fields,
)
from prozorro_auction.chronograph.requests import get_tender_documents, get_tender_bids, get_tender_public_bids
import aiohttp


async def tick_auction(auction):
    current_stage = auction.get("current_stage", -1)
    stages = auction.get("stages")

    next_stage_index = current_stage + 1
    if next_stage_index >= len(stages):
        return logger.error(f"Chronograph tries to update {auction['_id']} "
                            f"to a non-existed stage {next_stage_index}")

    next_stage = stages[next_stage_index]
    if next_stage["start"] > datetime.now():
        return logger.error(f"Chronograph tries to update {auction['_id']} too early {next_stage['start']}")

    # TODO: mb "end stage" and "start stage" methods should be proceeded distinctly
    # run end stage method
    if current_stage > -1:
        this_stage = stages[current_stage]
        end_method = globals().get(f"on_end_stage_{this_stage['type']}")
        if end_method:
            await end_method(auction)

    # start next stage method
    start_method = globals().get(f"on_start_stage_{next_stage['type']}")
    if start_method:
        await start_method(auction)

    # update stage fields
    auction["current_stage"] = next_stage_index
    next_stage = auction["current_stage"] + 1
    if next_stage < len(stages):
        auction["timer"] = stages[next_stage]["start"]
    else:
        auction["timer"] = None


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
    """
    1 upload audit document
    2 send auction results to tenders api
    """
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        # post audit document
        tender_documents = await get_tender_documents(session, auction["tender_id"])  # public data
        await upload_audit_document(session, auction, tender_documents)

        # send results to the api
        tender_bids = await get_tender_bids(session, auction["tender_id"])   # private data
        await send_auction_results(session, auction, tender_bids)


async def on_start_stage_announcement(auction):
    """
    reveal tenderer names
    """
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        tender_bids = await get_tender_public_bids(session, auction["tender_id"])  # should be public now
        bid_names = {
            b["id"]: b["tenderers"][0]["name"]
            for b in tender_bids
        }
        for section_name in ("initial_bids", "stages", "results"):
            for section in auction[section_name]:
                if "bidder_id" in section and section['bidder_id'] in bid_names:
                    section["label"] = dict(
                        uk=bid_names[section['bidder_id']],
                        ru=bid_names[section['bidder_id']],
                        en=bid_names[section['bidder_id']],
                    )

