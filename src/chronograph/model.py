from settings import logger
from yaml import safe_dump


def sort_bids(bids):
    return sorted(bids, key=lambda b: (b["value"]["amount"], b["date"]), reverse=True)


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
    auction["results"] = [
        dict(
            bidder_id=bid["id"],
            amount=bid["value"]["amount"],
            time=bid["date"],
            label=get_label_dict(
                get_bidder_number(bid["id"], auction["initial_bids"])
            )
        )
        for bid in sort_bids(auction["bids"])
    ]


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
                if bid_stages and current_stage_str in bid_stages and \
                        bid_stages[current_stage_str].get("amount") is not None:
                    stage["changed"] = True
                    bid["value"]["amount"] = stage["amount"] = bid_stages[current_stage_str]["amount"]
                    bid["date"] = stage["time"] = bid_stages[current_stage_str]["time"]
                    logger.info(f"Publishing bidder {bidder_id} posted bid: {bid_stages[current_stage_str]}")
                else:
                    logger.info(f"Bidder {bidder_id} has not changed its bid")
                break
        else:
            logger.critical(f"WTF bidder from {current_stage} not found")


def build_audit_document(auction):
    timeline = {
        "auction_start": {
            "initial_bids": auction["initial_bids"],
            "time": auction["start_at"],
        },
        "results": {
            "bids": auction["bids"],
            "time": auction["stages"][-1]["start"]
        }

    }
    audit = {
        "id": auction["_id"],
        "tenderId": auction["tenderID"],
        "tender_id": auction["tender_id"],
        "lot_id": auction["lot_id"],
        "timeline": timeline
    }
    if auction["lot_id"]:
        audit["lot_id"] = auction["lot_id"]

    round_number = turn = 0
    for stage in auction["stages"]:
        if stage["type"] == "pause":
            round_number += 1
            turn = 0
        elif stage["type"] == "bid":
            turn += 1
            label = f"round_{round_number}"
            if label not in timeline:
                timeline[label] = {}
            timeline[label][f"turn_{turn}"] = dict(
                amount=stage["amount"],
                bidder=stage["bidder_id"],
                time=stage["start"]
            )
            if auction["features"]:
                timeline[label][f"turn_{turn}"]["amount_features"] = str(stage.get("amount_features"))
                timeline[label][f"turn_{turn}"]["coeficient"] = str(stage.get("coeficient"))

    file_data = safe_dump(audit, default_flow_style=False)
    file_name = f"audit_{auction['_id']}.yaml"
    return file_name, file_data


def get_doc_id_from_filename(documents, file_name):
    for doc in documents:
        if doc["title"] == file_name:
            return doc["id"]


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
                            {
                                "value": {"amount": bid["value"]["amount"]},
                                "date": bid["date"]
                            }
                            if auction["lot_id"] == lot_bid['relatedLot']
                            else {}
                            for lot_bid in bid_info['lotValues']
                        ]
                    )
                else:
                    patch_line.update(
                        value={"amount": bid["value"]["amount"]},
                        date=bid["date"],
                    )
                break
    return data
