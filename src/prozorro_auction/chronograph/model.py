from yaml import dump
from fractions import Fraction
from prozorro_auction.utils.costs import (
    float as float_costs_utils,
    fraction as fraction_costs_utils,
)
from prozorro_auction.utils.base import get_now, datetime_to_str, copy_dict
from prozorro_auction.constants import AuctionType
import logging


logger = logging.getLogger(__name__)


def sort_bids(bids):
    is_esco = is_esco_bids(bids)
    auction_type = get_bids_auction_type(bids)
    if auction_type == AuctionType.MEAT:
        def get_amount(b):
            return Fraction(b["amount_features"])
    elif auction_type == AuctionType.LCC:
        if is_esco:
            raise NotImplementedError()
        else:
            def get_amount(b):
                return b["amount_weighted"]
    else:
        if is_esco:
            def get_amount(b):
                return Fraction(b["value"]["amountPerformance"])
        else:
            def get_amount(b):
                return b["value"]["amount"]
    result = sorted(
        bids,
        key=lambda b: (
            get_amount(b),
            b["date"]
        ),
        reverse=not is_esco
    )
    return result


def get_bid_auction_type(bid):
    if bid.get("amount_features"):
        return AuctionType.MEAT
    elif bid.get("amount_weighted"):
        return AuctionType.LCC
    else:
        return AuctionType.DEFAULT


def get_bids_auction_type(bids):
    auction_types = list(map(get_bid_auction_type, bids))
    auction_types_priority = [
        AuctionType.MEAT,
        AuctionType.LCC,
        AuctionType.DEFAULT,
    ]
    return next(
        auction_type for auction_type in auction_types_priority
        if auction_type in auction_types
    )


def is_esco_bid(bid):
    return "amountPerformance" in bid["value"]


def is_esco_bids(bids):
    return any(is_esco_bid(bid) for bid in bids)


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


def update_auction_results(auction):
    auction["results"] = []
    for bid in sort_bids(auction["bids"]):
        result = {
            "label": get_label_dict(
                get_bidder_number(bid["id"], auction["initial_bids"])
            )
        }
        copy_bid_stage_fields(bid, result)
        auction["results"].append(result)


def publish_bids_made_in_current_stage(auction):
    current_stage = auction.get("current_stage")
    stage = auction["stages"][current_stage]
    stage["publish_time"] = get_now()
    bidder_id = stage["bidder_id"]
    if bidder_id is None:
        logger.critical(f"Bidder stage bidder is not set {current_stage}")
    else:
        for bid in auction["bids"]:
            if bid["id"] == bidder_id:
                bid_stages = bid.get("stages")
                current_stage_str = str(current_stage)
                if bid_stages and current_stage_str in bid_stages:
                    bid_stage_items = bid_stages[current_stage_str]
                    # update private fields
                    bid["date"] = bid_stage_items.pop("time")  # we just can't be consistent on field names
                    bid["value"].update(bid_stage_items)
                    if auction["auction_type"] == AuctionType.MEAT.value:
                        if is_esco_bid(bid):
                            bid['amount_features'] = str(fraction_costs_utils.amount_to_features(
                                amount=bid["value"]['amountPerformance'],
                                coeficient=bid["coeficient"],
                                reverse=False,
                            ))
                        else:
                            bid['amount_features'] = str(fraction_costs_utils.amount_to_features(
                                amount=bid["value"]['amount'],
                                coeficient=bid["coeficient"],
                                reverse=True,
                            ))
                    elif auction["auction_type"] == AuctionType.LCC.value:
                        if is_esco_bid(bid):
                            raise NotImplementedError()
                        else:
                            bid['amount_weighted'] = float_costs_utils.amount_to_weighted(
                                amount=bid["value"]['amount'],
                                non_price_cost=bid["non_price_cost"],
                                reverse=True,
                            )
                    # update public stage fields
                    copy_bid_stage_fields(bid, stage)
                    stage["changed"] = True

                    logger.info(f"Publishing bidder {bidder_id} posted bid: {bid_stages[current_stage_str]}")
                else:
                    logger.info(f"Bidder {bidder_id} has not changed its bid")
                break
        else:
            logger.critical(f"WTF bidder from {current_stage} not found")


def _build_bidder_object(bid):
    """
    TODO: mb refactoring with the method below
    """
    result = dict(
        bidder=bid["id"],
        time=datetime_to_str(bid["date"])
    )
    is_esco = is_esco_bid(bid)
    if is_esco:
        result.update(
            amount=str(Fraction(bid["value"]["amountPerformance"])),
            contractDuration={
                "years": bid["value"]["contractDuration"]["years"],
                "days": bid["value"]["contractDuration"]["days"],
            },
            yearlyPaymentsPercentage=bid["value"]["yearlyPaymentsPercentage"]
        )
    else:
        result.update(
            amount=bid["value"]["amount"]
        )

    auction_type = get_bid_auction_type(bid)
    if auction_type == AuctionType.MEAT:
        result.update(
            amount_features=bid["amount_features"],
            coeficient=bid["coeficient"],
        )
    elif auction_type == AuctionType.LCC:
        if is_esco:
            raise NotImplementedError()
        result.update(
            amount_weighted=bid["amount_weighted"],
            non_price_cost=bid["non_price_cost"],
        )
    return result


def copy_bid_stage_fields(bid, stage):
    fields = dict(
        bidder_id=bid["id"],
        time=bid["date"],
    )

    meat_fields = ("amount_features", "coeficient")
    lcc_fields = ("amount_weighted", "non_price_cost")
    for f in meat_fields + lcc_fields:
        if f in bid:
            fields[f] = bid[f]

    bid_value = bid["value"]

    bid_value_fields = ("amount",)
    bid_value_esco_fields = ("yearlyPaymentsPercentage", "annualCostsReduction")
    for f in bid_value_fields + bid_value_esco_fields:
        if f in bid_value:
            fields[f] = bid_value[f]

    if is_esco_bid(bid):  # esco "amountPerformance" is shown as "amount" in the round data
        fields["amount"] = str(Fraction(bid["value"]["amountPerformance"]))

        if "contractDuration" in bid_value:
            duration = bid_value["contractDuration"]
            fields.update(
                contractDurationDays=duration["days"],
                contractDurationYears=duration["years"],
            )
    stage.update(fields)


def build_audit_document(auction):

    bidder_map = {
        "bidder_id": "bidder",
        "time": "date",
    }

    timeline = {
        "auction_start": {
            "initial_bids": [
                {
                    bidder_map[k] if k in bidder_map else k: v
                    for k, v in bid.items()
                }
                for bid in auction["initial_bids"]
            ],
            "time": datetime_to_str(auction["start_at"]),
        },
        "results": {
            "bids": [_build_bidder_object(b) for b in auction["bids"]],
            "time": datetime_to_str(auction["stages"][-1]["start"])
        }

    }
    audit = {
        "id": auction["_id"],
        "tenderId": auction["tenderID"],
        "tender_id": auction["tender_id"],
        "timeline": timeline
    }
    if auction["lot_id"]:
        audit["lot_id"] = auction["lot_id"]

    round_number = turn = 0
    for stage in auction["stages"]:
        if stage["type"] == "pause":
            round_number += 1
            turn = 0
        elif stage["type"] == "bids":
            turn += 1
            label = f"round_{round_number}"
            if label not in timeline:
                timeline[label] = {}
            timeline[label][f"turn_{turn}"] = dict(
                amount=stage["amount"],
                bidder=stage["bidder_id"],
                time=datetime_to_str(stage["publish_time"])
            )

            if stage.get("changed", False):
                timeline[label][f"turn_{turn}"]["bid_time"] = datetime_to_str(stage["time"])

            if auction["auction_type"] == AuctionType.MEAT.value:
                timeline[label][f"turn_{turn}"]["amount_features"] = str(stage.get("amount_features"))
                timeline[label][f"turn_{turn}"]["coeficient"] = str(stage.get("coeficient"))

            if auction["auction_type"] == AuctionType.LCC.value:
                timeline[label][f"turn_{turn}"]["amount_weighted"] = stage.get("amount_weighted")
                timeline[label][f"turn_{turn}"]["non_price_cost"] = stage.get("non_price_cost")

    # safe_dump couldn't convert [<class 'bson.int64.Int64'>, 2238300000]
    file_data = dump(audit, default_flow_style=False, encoding="utf-8", allow_unicode=True)
    file_name = f"audit_{auction['_id']}.yaml"
    return file_name, file_data


def get_doc_id_from_filename(documents, file_name):
    for doc in documents:
        if doc["title"] == file_name:
            return doc["id"]


def _bid_patch_fields(bid):
    result = {
        "date": datetime_to_str(bid["date"]),
        "value": copy_dict(bid["value"], ("amount", "contractDuration", "yearlyPaymentsPercentage")),
    }
    if "amount_weighted" in bid:
        result["weightedValue"] = {
            "amount": bid["amount_weighted"]
        }
    return result


def build_results_bids_patch(auction, tender_bids):
    bids_patch = []
    data = {'data': {'bids': bids_patch}}
    for bid_info in tender_bids:
        patch_line = {}
        bids_patch.append(patch_line)

        for bid in auction["bids"]:
            if bid_info["id"] == bid["id"]:
                if auction["lot_id"]:
                    patch_line.update(
                        lotValues=[
                            _bid_patch_fields(bid)
                            if auction["lot_id"] == lot_bid['relatedLot']
                            else {}
                            for lot_bid in bid_info['lotValues']
                        ]
                    )
                else:
                    patch_line.update(
                        _bid_patch_fields(bid)
                    )
                break
    return data


def get_verbose_current_stage(auction):
    current_stage = auction.get("current_stage")
    if 0 <= current_stage < len(auction["stages"]):
        return auction["stages"][current_stage].get("type")
    else:
        return f"Stage: {current_stage}"
