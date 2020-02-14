from prozorro_auction.databridge.model import build_urls_patch
from prozorro_auction.settings import AUCTION_HOST
import unittest


class BuildUrlsPatchTestCase(unittest.TestCase):

    def test_simple(self):
        auction = {
            "_id": "123",
            "lot_id": None,
            "bids": [
                {
                    "id": "a",
                    "hash": "1",
                },
                {
                    "id": "b",
                    "hash": "22"
                },
            ]
        }
        tender = {
            "bids": [
                {
                    "id": "c",
                },
                {
                    "id": "a",
                },
                {
                    "id": "b",
                },
            ]
        }

        patch_obj = build_urls_patch(auction, tender)
        b1 = auction["bids"][0]
        b2 = auction["bids"][1]
        self.assertEqual(
            patch_obj["data"],
            {
                "auctionUrl": f"{AUCTION_HOST}/tenders/{auction['_id']}",
                "bids": [
                    {},
                    {
                        "participationUrl":
                        f"{AUCTION_HOST}/tenders/{auction['_id']}/login?bidder_id={b1['id']}&hash={b1['hash']}"
                    },
                    {
                        "participationUrl":
                        f"{AUCTION_HOST}/tenders/{auction['_id']}/login?bidder_id={b2['id']}&hash={b2['hash']}"
                    },
                ]
            }
        )

    def test_lots(self):
        auction = {
            "_id": "123",
            "lot_id": "lot_id_1",
            "bids": [
                {
                    "id": "a",
                    "hash": "1",
                },
                {
                    "id": "b",
                    "hash": "22"
                },
            ]
        }
        tender = {
            "bids": [
                {
                    "id": "c",
                },
                {
                    "id": "a",
                    "lotValues": [
                        {
                            "relatedLot": "lot_id_0",
                        },
                        {
                            "relatedLot": "lot_id_1",
                        }
                    ]
                },
                {
                    "id": "b",
                    "lotValues": [
                        {
                            "relatedLot": "lot_id_1",
                        }
                    ]
                },
            ],
            "lots": [
                {
                    "id": "lot_id_0"
                },
                {
                    "id": "lot_id_1"
                },
            ]
        }

        patch_obj = build_urls_patch(auction, tender)
        b1 = auction["bids"][0]
        b2 = auction["bids"][1]
        self.assertEqual(
            patch_obj["data"],
            {
                "bids": [
                    {},
                    {
                        "lotValues": [
                            {},
                            {
                                "participationUrl":
                                f"{AUCTION_HOST}/tenders/{auction['_id']}/login?bidder_id={b1['id']}&hash={b1['hash']}"
                            }
                        ]
                    },
                    {
                        "lotValues": [
                            {
                                "participationUrl":
                                f"{AUCTION_HOST}/tenders/{auction['_id']}/login?bidder_id={b2['id']}&hash={b2['hash']}"
                            }
                        ]
                    }
                ],
                "lots": [
                    {},
                    {"auctionUrl": f"{AUCTION_HOST}/tenders/{auction['_id']}"}
                ]
            }
        )
