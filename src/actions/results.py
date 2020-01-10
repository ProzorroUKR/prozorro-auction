from api_requests import upload_document, publish_tender_document, post_tender_auction
from settings import logger
from yaml import safe_dump


async def upload_audit_document(session, auction, tender):
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
        "tenderId": tender.get("tenderID", ""),
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

    file_name = f"audit_{auction['_id']}.yaml"
    data = await upload_document(session, file_name, safe_dump(audit, default_flow_style=False))
    for doc in tender.get("documents", ""):
        if doc["title"] == file_name:
            doc_id = doc["id"]
            break
    else:
        doc_id = None
    result = await publish_tender_document(session, auction["tender_id"], data, doc_id=doc_id)
    logger.info(
        f"Published {file_name} with id {result['id']}",
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )


async def send_auction_results(session, auction, tender):
    bids = []
    data = {'data': {'bids': bids}}
    for bid_info in tender["bids"]:
        for bid in auction["bids"]:
            if bid_info["id"] == bid["id"]:
                if auction["lot_id"]:
                    patch_lot_values = []
                    for lot_bid in bid_info['lotValues']:
                        if auction["lot_id"] == lot_bid['relatedLot']:
                            patch_lot_values.append(
                                {
                                    "value": {"amount": bid["value"]["amount"]},
                                    "date": bid["date"],
                                }
                            )
                        else:
                            patch_lot_values.append({})
                    bids.append(
                        {
                            "lotValues": patch_lot_values
                        }
                    )
                else:
                    bids.append({
                        "value": {"amount": bid["value"]["amount"]},
                        "date": bid["date"],
                    })
                break
        else:
            bids.append({})

    await post_tender_auction(session, auction["tender_id"], data)
    logger.info(
        "Approved data: {}".format(data),
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )
