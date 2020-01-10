from settings import logger, API_HEADERS
from datetime import datetime
from actions.results import upload_audit_document, send_auction_results
from api_requests import get_tender_document, post_tender_auction
import aiohttp


async def tick_auction(auction):
    current_stage = auction.get("current_stage", -1)
    stages = auction.get("stages")

    next_stage_index = current_stage + 1
    if next_stage_index >= len(stages):
        return logger.warning(f"Chronograph tries to update {auction['id']} to a non-existed stage {next_stage_index}")

    next_stage = stages[next_stage_index]
    if next_stage["start"] > datetime.now():
        return logger.warning(f"Chronograph tries to update {auction['id']} too early {next_stage['start']}")

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


def get_label_dict(n):
    n += 1
    return dict(
        en=f"Bidder #{n}",
        uk=f"Учасник #{n}",
        ru=f"Участник #{n}",
    )


def get_bidder_number(uid, initial_bids):
    for n, bid in enumerate(initial_bids):
        if bid["bidder_id"] == uid:
            return n


async def on_start_stage_pause(auction):
    current_stage = auction.get("current_stage", -1)
    # set initial_bids
    if current_stage == -1:
        logger.info("Set initial bids")
        auction["initial_bids"] = [
            dict(
                bidder_id=bid["id"],
                amount=bid["value"]["amount"],
                time=bid["date"],
                label=get_label_dict(n),
            )
            for n, bid in enumerate(sort_bids(auction["bids"]))
        ]

    # set "bidder" for bid rounds according to the bids they made before
    stages = auction.get("stages")
    index = current_stage + 2
    logger.info(f"Set {index}:{index + len(auction['bids'])} bid stages order")
    for i, bid in enumerate(sort_bids(auction["bids"])):
        stages[index + i].update(
            bidder_id=bid["id"],
            label=get_label_dict(
                get_bidder_number(bid["id"], auction["initial_bids"])
            )
        )


def sort_bids(bids):
    return sorted(bids, key=lambda b: (b["value"]["amount"], b["date"]), reverse=True)


async def on_end_stage_bid(auction):
    """
    copy posted bid to "bids" field
    """
    current_stage = auction.get("current_stage")

    stage = auction["stages"][current_stage]
    bidder_id = stage["bidder_id"]
    if bidder_id is None:
        logger.critical(f"Bidder stage bidder is not set {current_stage}")
    else:
        for bid in auction["bids"]:
            if bid["id"] == bidder_id:
                bid_stages = bid.get("stages")
                current_stage_str = str(current_stage)
                if bid_stages and current_stage_str in bid_stages and \
                        bid_stages[current_stage_str].get("amount") is not None:
                    bid["value"]["amount"] = stage["amount"] = bid_stages[current_stage_str]["amount"]
                    bid["date"] = stage["time"] = bid_stages[current_stage_str]["time"]
                    logger.info(f"Publishing bidder {bidder_id} posted bid: {bid_stages[current_stage_str]}")
                else:
                    stage["amount"] = bid["value"]["amount"]
                    stage["time"] = bid["date"]
                    logger.info(f"Copying bidder {bidder_id} unchanged bid: {stage}")
                break


async def on_start_stage_pre_announcement(auction):
    """
    1 upload audit document
    2 send auction results to tenders api
    """
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        tender = await get_tender_document(session, {"id": auction["tender_id"]})
        await upload_audit_document(session, auction, tender)
        await send_auction_results(session, auction, tender)


async def on_start_stage_announcement(auction):
    """
    reveal tenderer names
    """
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        tender = await get_tender_document(session, {"id": auction["tender_id"]}, public_only=True)
        bid_names = {
            b["id"]: b["tenderers"][0]["name"]
            for b in tender.get("bids", "")
        }
        for section_name in ("initial_bids", "stages"):
            for section in auction[section_name]:
                if "bidder_id" in section and section['bidder_id'] in bid_names:
                    section["label"] = dict(
                        uk=bid_names[section['bidder_id']],
                        ru=bid_names[section['bidder_id']],
                        en=bid_names[section['bidder_id']],
                    )

