from copy import deepcopy
from prozorro_auction.settings import logger, TEST_MODE, AUCTION_HOST
from datetime import timedelta
from prozorro_auction.utils import convert_datetime, get_now
from barbecue import cooking, calculate_coeficient
from fractions import Fraction
import uuid


def filter_obj_keys(initial, keys):
    return [{k: v for k, v in obj.items() if k in keys} for obj in initial]


def get_data_from_tender(tender):
    features = tender.get("features", [])
    items = filter_obj_keys(
        tender.get("items", []),
        (
            "id",
            "description",
            "description_en",
            "description_ru",
            "quantity",
            "unit",
            "relatedLot",
        )
    )
    active_bids = [
        b for b in tender.get("bids", [])
        if b.get("status", "active") == "active"   # belowThreshold doesn't return "status" fields for auction role
    ]
    tender_auction = dict(
        tender_id=tender.get("id"),
        mode=TEST_MODE and tender.get("submissionMethodDetails"),
        is_cancelled=tender.get("status") in ("cancelled", "unsuccessful"),
        items=items,
        features=features,
        auction_type="meat" if features else "default",
    )

    copy_fields = (
        "tenderID", "title", "title_en", "description", "description_en",
        "procurementMethodType", "procuringEntity", "minimalStep", "value",
        "NBUdiscountRate", "noticePublicationDate", "minimalStepPercentage", "minValue",
        "fundingKind", "yearlyPaymentsPercentageRange",
    )
    for f in copy_fields:
        if f in tender:
            tender_auction[f] = tender[f]

    if "lots" in tender:
        for lot in tender["lots"]:
            start_at = lot.get("auctionPeriod", {}).get("startDate")
            if start_at is not None:
                auction = deepcopy(tender_auction)
                auction["start_at"] = start_at
                auction["_id"] = f"{tender['id']}_{lot['id']}"
                auction["lot_id"] = lot['id']
                auction["is_cancelled"] = auction["is_cancelled"] or lot.get("status") != "active"

                auction["items"] = list(filter(lambda i: i.get('relatedLot') == lot["id"], items))
                auction['features'] = list(filter(
                    lambda i:
                    i['featureOf'] == 'tenderer'
                    or i['featureOf'] == 'lot' and i['relatedItem'] == lot["id"]
                    or i['featureOf'] == 'item' and i['relatedItem'] in {i["id"] for i in auction["items"]},
                    features
                ))
                codes = {i['code'] for i in auction['features']}
                auction["bids"] = []
                for b in active_bids:
                    for lot_bid in b["lotValues"]:
                        if lot_bid["relatedLot"] == lot["id"] and lot_bid.get("status", "active") == "active":
                            parameters = [i for i in b.get("parameters", "") if i["code"] in codes]
                            bid_data = import_bid(b, lot_bid, features, parameters)
                            auction["bids"].append(bid_data)

                if tender["procurementMethodType"] == "esco":
                    auction["minValue"] = lot["value"]

                yield auction
    else:
        tender_auction["start_at"] = tender.get("auctionPeriod", {}).get("startDate")
        if tender_auction["start_at"] is not None:
            tender_auction["_id"] = tender["id"]
            tender_auction["lot_id"] = None
            tender_auction["bids"] = []
            for bid in active_bids:
                bid_data = import_bid(bid, bid, features, bid.get("parameters"))
                tender_auction["bids"].append(bid_data)
            yield tender_auction


def import_bid(bid, lot_bid, features, parameters):
    bid_data = dict(
        id=bid["id"],
        hash=uuid.uuid4().hex,
        name=bid["tenderers"][0]["name"] if "tenderers" in bid else None,
        date=lot_bid["date"],
        value=lot_bid["value"],
    )
    if parameters:
        bid_data["parameters"] = parameters
        bid_data["coeficient"] = str(calculate_coeficient(features, parameters))
        if "amountPerformance" in bid["value"]:  # esco
            amount = str(Fraction(bid["value"]["amountPerformance"]))
            reverse = True
        else:
            amount = bid["value"]["amount"]
            reverse = False
        bid_data["amount_features"] = str(cooking(amount, features, parameters, reverse=reverse))
    return bid_data


def copy_bid_tokens(source, dst):
    """
    The old auctions provide hashes that don't change after rescheduling,
    and I'm sure brokers can fail passing new links
    For now, we won't change auction links during rescheduling
    """
    for s in source["bids"]:
        for d in dst["bids"]:
            if s["id"] == d["id"]:
                d["hash"] = s["hash"]
                break


def build_urls_patch(auction, tender):
    auction_url = f"{AUCTION_HOST}/tenders/{auction['_id']}"
    patch_bids = []
    patch_data = {"data": {"auctionUrl": auction_url, "bids": patch_bids}}
    for tender_bid in tender["bids"]:
        bid_patch = {}
        patch_bids.append(bid_patch)

        for bid in auction["bids"]:
            if tender_bid["id"] == bid["id"]:
                participation_url = f"{auction_url}/login?bidder_id={bid['id']}&hash={bid['hash']}"
                if auction["lot_id"]:
                    bid_patch.update(
                        lotValues=[
                            {"participationUrl": participation_url}
                            if auction["lot_id"] == lot_bid['relatedLot'] else
                            {}
                            for lot_bid in tender_bid['lotValues']
                        ],
                    )
                else:
                    bid_patch.update(
                        participationUrl=participation_url,
                    )
                break

    return patch_data


def get_auctions_from_tender(tender):
    for auction in get_data_from_tender(tender):
        auction["start_at"] = convert_datetime(auction["start_at"])
        if auction["start_at"] < get_now():
            logger.info(f"Skipping {auction['_id']} start date {auction['start_at']} in the past")
        else:
            auction["stages"] = build_stages(auction)
            auction["current_stage"] = -1
            auction["timer"] = auction["start_at"]   # for chronograph update
            yield auction


def build_stages(auction):
    if auction["mode"] == "quick(mode:fast-forward)":
        two_min = five_min = 0
        auction["start_at"] = get_now()
    else:
        two_min = 2 * 50
        five_min = 5 * 60

    start_at = auction["start_at"]
    stages = []
    for n in range(3):  # rounds
        stages.append(
            dict(
                start=start_at,
                type="pause"
            )
        )
        start_at += timedelta(seconds=two_min if n else five_min)
        for _ in range(len(auction["bids"])):
            stages.append(
                dict(
                    start=start_at,
                    type="bids",
                    bidder_id="TBD",
                    label=dict(en="TBD", uk="TBD", ru="TBD"),
                )
            )
            start_at += timedelta(seconds=two_min)

    stages.append(
        dict(
            start=start_at,
            type="pre_announcement"
        )
    )
    stages.append(
        dict(
            start=start_at + timedelta(seconds=two_min),
            type="announcement"
        )
    )
    return stages


def get_canceled_auctions_from_tender(tender):
    if "lots" in tender:
        for lot in tender["lots"]:
            yield dict(
                _id=f"{tender['id']}_{lot['id']}",
                is_cancelled=True
            )
    else:
        yield dict(
            _id=f"{tender['id']}",
            is_cancelled=True
        )
