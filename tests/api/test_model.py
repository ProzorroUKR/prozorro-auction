from fractions import Fraction

import unittest

from prozorro_auction.api.model import get_posted_bid
from prozorro_auction.utils.base import as_decimal


class GetPostedBidTestCase(unittest.TestCase):

    def test_get_posted_bid_default(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value
        }
        auction = {
            "auction_type": "default",
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "bids",
                    "bidder_id": bid["id"],
                    "amount": 100.1
                }
            ]
        }
        data = {
            "amount": 89.9
        }

        # Assert test data for floating point problem
        stage = auction["stages"][auction["current_stage"]]
        price_parts = [
            stage["amount"],
            auction["minimalStep"]["amount"] * -1
        ]
        assert sum(price_parts) != data["amount"]
        assert float(sum(map(as_decimal, price_parts))) == data["amount"]

        result = get_posted_bid(auction, bid, hash_value, data)

        self.assertEqual(result["amount"], 89.9)
        self.assertIn("time", result)

    def test_get_posted_bid_lcc(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "non_price_cost": 9.9
        }
        auction = {
            "auction_type": "lcc",
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "bids",
                    "bidder_id": bid["id"],
                    "amount": 90.2,
                    "amount_weighted": 100.1,
                }
            ]
        }
        data = {
            "amount": 80.0,
        }

        # Assert test data for floating point problem
        stage = auction["stages"][auction["current_stage"]]
        price_parts = [
            stage["amount_weighted"],
            bid["non_price_cost"] * -1,
            auction["minimalStep"]["amount"] * -1
        ]
        assert sum(price_parts) != data["amount"]
        assert float(sum(map(as_decimal, price_parts))) == data["amount"]

        result = get_posted_bid(auction, bid, hash_value, data)

        self.assertEqual(result["amount"], 80.0)
        self.assertIn("time", result)


    def test_get_posted_bid_meat(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "coeficient": 1.2
        }
        auction = {
            "auction_type": "meat",
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "bids",
                    "bidder_id": bid["id"],
                    "amount": 90.2,
                    "amount_features": 100.1,
                }
            ]
        }
        data = {
            "amount": 109.91,
        }

        result = get_posted_bid(auction, bid, hash_value, data)

        self.assertEqual(result["amount"], 109.91)
        self.assertIn("time", result)
