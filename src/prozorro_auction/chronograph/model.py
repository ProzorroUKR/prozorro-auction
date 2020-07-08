from prozorro_auction.settings import logger
from yaml import safe_dump
from prozorro_auction.utils import datetime_to_str
from fractions import Fraction


def sort_bids(bids):
    is_esco = any("amountPerformance" in b["value"] for b in bids)
    with_features = any(b.get("amount_features") for b in bids)
    if with_features:
        def get_amount(b):
            return Fraction(b["amount_features"])
    elif is_esco:
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
                    if auction["features"]:
                        if "amountPerformance" in bid["value"]:  # esco
                            amount_features = Fraction(bid["value"]['amountPerformance']) * Fraction(bid["coeficient"])
                        else:
                            amount_features = Fraction(bid["value"]['amount']) / Fraction(bid["coeficient"])
                        bid['amount_features'] = str(amount_features)
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
    if "amountPerformance" in bid["value"]:  # esco
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

    if "amount_features" in bid:
        result.update(
            amount_features=bid["amount_features"],
            coeficient=bid["coeficient"],
        )
    return result


def copy_bid_stage_fields(bid, stage):
    fields = dict(
        bidder_id=bid["id"],
        time=bid["date"],
    )
    for f in ("amount_features", "coeficient"):
        if f in bid:
            fields[f] = bid[f]

    bid_value = bid["value"]
    for f in ("amount", "yearlyPaymentsPercentage", "annualCostsReduction"):  # amount and esco fields
        if f in bid_value:
            fields[f] = bid_value[f]

    if "amountPerformance" in bid["value"]:  # esco "amountPerformance" is shown as "amount" in the round data
        fields["amount"] = str(Fraction(bid["value"]["amountPerformance"]))

    if "contractDuration" in bid_value:  # esco
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
                time=datetime_to_str(stage["time"])
            )
            if auction["features"]:
                timeline[label][f"turn_{turn}"]["amount_features"] = str(stage.get("amount_features"))
                timeline[label][f"turn_{turn}"]["coeficient"] = str(stage.get("coeficient"))
    file_data = safe_dump(audit, default_flow_style=False, encoding="utf-8", allow_unicode=True)
    file_name = f"audit_{auction['_id']}.yaml"
    return file_name, file_data


def get_doc_id_from_filename(documents, file_name):
    for doc in documents:
        if doc["title"] == file_name:
            return doc["id"]


def _bid_patch_fields(bid):
    value_fields = ("amount", "contractDuration", "yearlyPaymentsPercentage")
    result = {
        "date": datetime_to_str(bid["date"]),
        "value": {k: v for k, v in bid["value"].items() if k in value_fields}
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


def set_auction_bidders_real_names(auction, tender_bids):
    bidders = {
        b["id"]: b["tenderers"][0]
        for b in tender_bids
    }
    for section_name in ("initial_bids", "stages", "results"):
        for section in auction[section_name]:
            if "bidder_id" in section and section['bidder_id'] in bidders:
                bidder = bidders[section['bidder_id']]
                section["label"] = dict(
                    uk=bidder["name"],
                    ru=bidder.get("name_ru") or bidder["name"],
                    en=bidder.get("name_en") or bidder["name"],
                )
