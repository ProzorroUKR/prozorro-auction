import uuid

from copy import deepcopy
from datetime import timedelta
from barbecue import cooking, calculate_coeficient
from fractions import Fraction

from prozorro_auction.utils import convert_datetime, get_now
from prozorro_auction.settings import (
    logger,
    TEST_MODE,
    AUCTION_HOST,
    QUICK_MODE_FAST_AUCTION_START_AFTER,
)


def get_data_from_tender(tender):
    """
    Get data from tender that we need for auction.

    :param tender: tender dict
    :return: auction dict
    """
    active_bids = filter_active_bids(tender.get("bids", []))

    tender_auction = dict(
        tender_id=tender.get("id"),
        mode=TEST_MODE and tender.get("submissionMethodDetails"),
        auction_type=get_auction_type(tender),
    )

    copy_fields = (
        "tenderID", "title", "title_en", "description", "description_en",
        "procurementMethodType", "procuringEntity", "minimalStep", "value",
        "NBUdiscountRate", "noticePublicationDate", "minimalStepPercentage",
        "fundingKind", "yearlyPaymentsPercentageRange",
    )
    for f in copy_fields:
        if f in tender:
            tender_auction[f] = tender[f]

    if "lots" in tender:
        for lot in tender["lots"]:
            start_at = lot.get("auctionPeriod", {}).get("startDate")
            if start_at is not None:
                features = tender.get("features", [])
                auction = deepcopy(tender_auction)
                auction["start_at"] = start_at
                auction["_id"] = generate_auction_id(tender, lot)
                auction["lot_id"] = lot["id"]
                auction["is_cancelled"] = is_auction_cancelled(tender, lot)
                lot_items = get_items(tender, lot)
                lot_features = filter_lot_features(features, lot, lot_items)
                auction["items"] = lot_items
                auction["features"] = lot_features
                auction["bids"] = import_lot_bids(active_bids, lot, lot_features, features)
                yield auction
    else:
        start_at = tender.get("auctionPeriod", {}).get("startDate")
        if start_at is not None:
            tender_auction["start_at"] = start_at
            tender_auction["_id"] = generate_auction_id(tender)
            tender_auction["lot_id"] = None
            tender_auction["is_cancelled"] = is_auction_cancelled(tender)
            tender_auction["items"] = get_items(tender)
            features = tender.get("features", [])
            tender_auction["features"] = features
            tender_auction["bids"] = import_tender_bids(active_bids, features)
            yield tender_auction


def import_tender_bids(active_bids, features):
    """
    Get bids data

    :param active_bids:
    :param features:
    :return:
    """
    bids_data = []
    for bid in active_bids:
        parameters = bid.get("parameters")
        bid_data = import_bid(bid, bid, features, parameters, None, None)
        bids_data.append(bid_data)
    return bids_data


def import_lot_bids(active_bids, lot, lot_features, features):
    """
    Get bids data for each lot value.

    :param active_bids:
    :param lot_features:
    :param features:
    :param lot:
    :return:
    """
    bids_data = []
    lot_feature_codes = {feature["code"] for feature in lot_features}
    for bid in active_bids:
        for lot_value in bid["lotValues"]:
            status = lot_value.get("status", "active")
            if lot_value["relatedLot"] == lot["id"] and status == "active":
                lot_parameters = [
                    parameter for parameter in bid.get("parameters", "")
                    if parameter["code"] in lot_feature_codes
                ]
                bid_data = import_bid(bid, lot_value, features, lot_parameters, None, None)
                bids_data.append(bid_data)
    return bids_data


def import_bid(bid, bid_value_container, features, parameters, criteria, responses):
    """
    Get bid data with additional calculated data.

    :param bid: bid dict
    :param bid_value_container: lot values item dict in case of multilot or bid dict otherwise
    :param features: features list
    :param parameters: parameters list
    :param criteria: criteria list
    :param responses: requirement responses list
    :return:
    """
    bid_data = dict(
        id=bid["id"],
        hash=uuid.uuid4().hex,
        name=bid["tenderers"][0]["name"] if "tenderers" in bid else None,
        date=bid_value_container["date"],
        value=bid_value_container["value"],
    )
    if parameters:
        bid_data["parameters"] = parameters
        bid_data["coeficient"] = str(calculate_coeficient(features, parameters))
        if "amountPerformance" in bid_value_container["value"]:  # esco
            amount = str(Fraction(bid_value_container["value"]["amountPerformance"]))
            reverse = True
        else:
            amount = bid_value_container["value"]["amount"]
            reverse = False
        bid_data["amount_features"] = str(cooking(amount, features, parameters, reverse=reverse))
    return bid_data


def get_items(tender, lot=None):
    """
    Get lot related items

    :param tender:
    :param lot:
    :return:
    """
    items = filter_items_keys(tender.get("items", []))
    if lot:
        return list(filter(
            lambda item: item.get("relatedLot") == lot["id"],
            items
        ))
    return items


def generate_auction_id(tender, lot=None):
    """
    Generate auction id

    :param tender:
    :param lot:
    :return:
    """
    tender_id = tender["id"]
    if lot:
        lot_id = lot["id"]
        return f"{tender_id}_{lot_id}"
    return tender_id


def filter_obj_keys(initial, keys):
    """
    Filter keys for each item in list

    :param initial:
    :param keys:
    :return:
    """
    return [
        {
            k: v
            for k, v in obj.items()
            if k in keys
        } for obj in initial
    ]


def filter_items_keys(items):
    """
    Filter items fields that we need in auction

    :param items: list of items
    :return: list of items with filtered keys
    """
    return filter_obj_keys(items, (
        "id",
        "description",
        "description_en",
        "description_ru",
        "quantity",
        "unit",
        "relatedLot",
    ))

def filter_active_bids(bids):
    """
    Filter bids with active status.
    Note: belowThreshold doesn't return "status" fields for auction role.

    :param bids:
    :return:
    """
    return [
        b for b in bids
        if b.get("status", "active") == "active"
    ]


def get_auction_type(tender):
    """
    Get auction type:
    - default
    - meat (if tender has features)

    :param tender:
    :return:
    """
    if tender.get("features", []):
        return "meat"
    return "default"


def is_auction_cancelled(tender, lot=None):
    """
    Detect if auction is cancelled

    :param tender:
    :return:
    """
    is_tender_cancelled = tender.get("status") in ("cancelled", "unsuccessful")
    if lot:
        return is_tender_cancelled or lot.get("status") != "active"
    return is_tender_cancelled


def filter_lot_features(features, lot, items):
    """
    Filter features related to lot or lot items

    :param features:
    :param items:
    :param lot:
    :return:
    """
    return list(filter(
        lambda feature:
        feature["featureOf"] == "tenderer"
        or feature["featureOf"] == "lot" and feature["relatedItem"] == lot["id"]
        or feature["featureOf"] == "item" and feature["relatedItem"] in {
            item["id"] for item in items
        },
        features
    ))


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
    """
    Generate patch data with auction urls.

    :param auction: auction dict
    :param tender: tender dict
    :return:
    """
    auction_url = f"{AUCTION_HOST}/tenders/{auction['_id']}"
    patch_bids = []
    patch_data = {"data": {"bids": patch_bids}}

    if auction["lot_id"]:
        patch_data["data"]["lots"] = [
            {"auctionUrl": auction_url}
            if auction["lot_id"] == lot["id"]
            else {}
            for lot in tender["lots"]
        ]
    else:
        patch_data["data"]["auctionUrl"] = auction_url

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
                            if auction["lot_id"] == lot_bid['relatedLot'] else {}
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
    """
    Get all auctions that should be started with stages.

    :param tender: tender dict
    :return: auction dict
    """
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
    """
    Build stages for auction

    :param auction: auction dict
    :return: list of stages dicts
    """
    mode = auction["mode"]
    if mode and mode.endswith("quick(mode:fast-forward)"):
        two_min = five_min = 0
        auction["start_at"] = get_now()
    elif mode and mode.endswith("quick(mode:fast-auction)"):
        auction["start_at"] = (get_now() + timedelta(
            minutes=QUICK_MODE_FAST_AUCTION_START_AFTER)
        )
        two_min = 2 * 60
        five_min = 5 * 60
    else:
        two_min = 2 * 60
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
