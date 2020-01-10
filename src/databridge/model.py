from copy import deepcopy
from settings import logger
from datetime import timedelta
from fractions import Fraction
from utils import convert_datetime, get_now
import uuid


def vn_max(features):
    return sum(max(j['value'] for j in i['enum']) for i in features)


def calculate_ratio(features, parameters):
    v_max = Fraction(vn_max(features))
    vn = sum([Fraction(i['value']) for i in parameters])
    result = 1 + vn / (1 - v_max)
    return result.numerator, result.denominator


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
    active_bids = [b for b in tender.get("bids", []) if b["status"] == "active"]
    tender_auction = dict(
        is_cancelled=tender.get("status") in ("cancelled", "unsuccessful"),
        tender_id=tender.get("id"),
        title=tender.get("title"),
        title_en=tender.get("title_en"),
        description=tender.get("description"),
        description_en=tender.get("description_en"),
        tenderID=tender.get("tenderID", ""),
        procurementMethodType=tender.get("procurementMethodType"),
        procuringEntity=tender.get("procuringEntity"),
        minimalStep=tender.get("minimalStep"),
        value=tender.get("value"),
        items=items,
        features=features,
        auction_type="meat" if features else "default",
    )

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
                        if lot_bid['relatedLot'] == lot["id"] and lot_bid.get('status', 'active') == 'active':
                            bid_data = {
                                'id': b['id'],
                                'hash': uuid.uuid4().hex,
                                'name': b['tenderers'][0]['name'] if "tenderers" in b else None,
                                'date': lot_bid['date'],
                                'value': lot_bid['value']
                            }
                            if 'parameters' in b:
                                bid_data['parameters'] = [i for i in b['parameters']
                                                          if i['code'] in codes]
                                bid_data['coeficient'] = calculate_ratio(tender["features"], bid_data['parameters'])
                            auction["bids"].append(bid_data)
                yield auction
    else:
        tender_auction["start_at"] = tender.get("auctionPeriod", {}).get("startDate")
        if tender_auction["start_at"] is not None:
            tender_auction["_id"] = tender["id"]
            tender_auction["lot_id"] = None
            tender_auction["bids"] = [
                dict(
                    id=b['id'],
                    hash=uuid.uuid4().hex,
                    name=b['tenderers'][0]['name'] if "tenderers" in b else None,
                    date=b['date'],
                    value=b['value'],
                )
                for b in active_bids
            ]
            yield tender_auction


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


def get_auctions_from_tender(tender):
    for auction in get_data_from_tender(tender):
        auction["start_at"] = convert_datetime(auction["start_at"])
        if auction["start_at"] < get_now():
            logger.info(f"Skipping {auction['_id']} start date {auction['start_at']} in the past")

        fast_forward = tender.get("submissionMethodDetails") == "quick(mode:fast-forward)"
        if fast_forward:
            auction["start_at"] = get_now() + timedelta(seconds=1)
        auction["stages"] = build_stages(auction, fast_forward)
        auction["timer"] = auction["start_at"]   # for chronograph update
        yield auction


def build_stages(tender, fast_forward=False):
    start_at = tender["start_at"]
    two_min = 2 * 50
    five_min = 5 * 60
    if fast_forward:
        two_min = five_min = 0

    stages = []
    for n in range(3):  # rounds
        stages.append(
            dict(
                start=start_at,
                type="pause"
            )
        )
        start_at += timedelta(seconds=two_min if n else five_min)
        for _ in range(len(tender["bids"])):
            stages.append(
                dict(
                    start=start_at,
                    type="bid",
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
