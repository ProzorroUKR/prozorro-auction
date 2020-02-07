from prozorro_auction.chronograph.requests import (
    upload_document, publish_tender_document, post_tender_auction,
    get_tender_documents, get_tender_bids,
)
from prozorro_auction.chronograph.model import (
    build_audit_document, build_results_bids_patch, get_doc_id_from_filename
)
from prozorro_auction.settings import logger, API_HEADERS
import aiohttp


async def publish_auction_results(auction):
    """
    1 upload audit document
    2 send auction results to tenders api
    """
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        # post audit document
        tender_documents = await get_tender_documents(session, auction["tender_id"])  # public data
        await upload_audit_document(session, auction, tender_documents)

        # send results to the api
        tender_bids = await get_tender_bids(session, auction["tender_id"])  # private data
        await send_auction_results(session, auction, tender_bids)


async def upload_audit_document(session, auction, documents):
    file_name, file_data = build_audit_document(auction)
    doc_id = get_doc_id_from_filename(documents, file_name)
    data = await upload_document(session, file_name, file_data)
    result = await publish_tender_document(session, auction["tender_id"], data, doc_id=doc_id)
    logger.info(
        f"Published {file_name} with id {result['id']}",
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )


async def send_auction_results(session, auction, tender_bids):
    data = build_results_bids_patch(auction, tender_bids)
    await post_tender_auction(session, auction["tender_id"], data)
    logger.info(
        f"Auction {auction['_id']} results sent: {data}",
        extra={"MESSAGE_ID": "AUCTION_WORKER_API_APPROVED_DATA"}
    )
