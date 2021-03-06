from prozorro_auction.chronograph.requests import (
    upload_document, publish_tender_document, post_tender_auction,
)
from prozorro_auction.chronograph.model import (
    build_audit_document, build_results_bids_patch, get_doc_id_from_filename
)
import logging

logger = logging.getLogger(__name__)


async def upload_audit_document(session, auction, documents):
    file_name, file_data = build_audit_document(auction)
    doc_id = get_doc_id_from_filename(documents, file_name)
    data = await upload_document(session, file_name, file_data)
    result = await publish_tender_document(session, auction["tender_id"], data, doc_id=doc_id)
    logger.info(
        f"Published {file_name} with id {result['id']}",
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )


async def send_auction_results(session, auction, tender_bids, request_tender_method=None):
    data = build_results_bids_patch(auction, tender_bids)
    await post_tender_auction(session, auction["tender_id"], auction["lot_id"], data, request_tender_method)
    logger.info(
        f"Auction results sent: {data}",
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )
