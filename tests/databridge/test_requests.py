import pytest
from unittest.mock import patch, MagicMock
from copy import deepcopy

from prozorro_auction.databridge.requests import get_tender_document
from prozorro_auction.exceptions import SkipException

from tests.base import AsyncMock, test_tender_data, test_bids


@pytest.mark.asyncio
async def test_get_tender_document_for_new_auction():
    session = MagicMock()
    tender_data = deepcopy(test_tender_data)
    tender_data["id"] = "test_id"

    tender_response = MagicMock(
        status=200,
        json=AsyncMock(
            return_value={"data": tender_data}
        )
    )
    auction_response = MagicMock(
        status=200,
        json=AsyncMock(
            return_value={"data": {"bids": test_bids}}
        )
    )
    session.get = AsyncMock(side_effect=[
        tender_response,
        auction_response,
    ])

    tender = {"id": tender_data["id"]}
    tender_data["submissionMethodDetails"] = "quick"

    tender = await get_tender_document(session, tender)
    tender_data["bids"] = test_bids
    assert tender_data == tender


@pytest.mark.asyncio
async def test_get_tender_document_without_bids(caplog):
    session = MagicMock()
    tender_data = deepcopy(test_tender_data)
    tender_data.pop("bids")
    tender_response = MagicMock(
        status=200,
        json=AsyncMock(
            return_value={"data": tender_data}
        )
    )
    empty_response = MagicMock(
        status=200,
        json=AsyncMock(
            return_value={"data": {}}
        )
    )
    session.get = AsyncMock(side_effect=[
        tender_response,
        empty_response
    ])

    tender = {"id": "test_id"}

    with pytest.raises(SkipException):
        with patch("prozorro_auction.databridge.requests.logger.info") as mock_logger_info:
            await get_tender_document(session, tender)
    mock_logger_info.assert_called_once_with(f"Skip processing {tender_data['id']} as there are no bids")
