import unittest

from copy import deepcopy
from fractions import Fraction
from barbecue import calculate_coeficient, cooking

from prozorro_auction.databridge.importers import (
    AuctionDefaultBidImporter,
    AuctionMEATBidImporter,
    AuctionLCCBidImporter,
)

from tests.base import (
    test_tender_data,
    test_tender_data_multilot,
    test_tender_data_features,
    test_tender_data_lcc,
)


class AuctionBidImporterTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_keys = (
            "id",
            "hash",
            "name",
            "date",
            "value",
        )

    def test_bid(self):
        tender = deepcopy(test_tender_data)
        bid = tender["bids"][0]

        result = AuctionDefaultBidImporter(bid).import_auction_bid_data()

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))
        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])

    def test_bid_multilot(self):
        tender = deepcopy(test_tender_data_multilot)
        bid = tender["bids"][0]
        lot_value = bid["lotValues"][0]

        result = AuctionDefaultBidImporter(bid).import_auction_bid_data(lot_value)

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))
        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], lot_value["date"])
        self.assertEqual(result["value"], lot_value["value"])


class ImportBidMEATTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_keys = (
            "id",
            "hash",
            "name",
            "date",
            "value",
            "parameters",
            "coeficient",
            "amount_features",
        )

    def test_bid_parameters(self):
        tender = deepcopy(test_tender_data_features)
        features = tender["features"]
        bid = tender["bids"][0]
        parameters = bid["parameters"]

        expected_coeficient = str(calculate_coeficient(features, parameters))
        self.assertEqual(expected_coeficient, "16212958658533786/12610078956637389")

        expected_amount_features = str(cooking(bid["value"]["amount"], features, parameters, reverse=False))
        self.assertEqual(expected_amount_features, "5914127030662935441/16212958658533786")

        result = AuctionMEATBidImporter(bid, features=features).import_auction_bid_data()

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))

        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])
        self.assertEqual(result["parameters"], bid["parameters"])
        self.assertEqual(result["coeficient"], expected_coeficient)
        self.assertEqual(result["amount_features"], expected_amount_features)

    def test_bid_parameters_esco(self):
        tender = deepcopy(test_tender_data_features)
        features = tender["features"]
        bid = tender["bids"][0]
        bid["value"]["amountPerformance"] = 600
        parameters = bid["parameters"]

        expected_coeficient = str(calculate_coeficient(features, parameters))
        self.assertEqual(expected_coeficient, "16212958658533786/12610078956637389")

        expected_amount_features = str(cooking(
            str(Fraction(bid["value"]["amountPerformance"])),
            features, parameters, reverse=True)
        )
        self.assertEqual(expected_amount_features, "3242591731706757200/4203359652212463")

        result = AuctionMEATBidImporter(bid, features=features).import_auction_bid_data()

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))

        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])
        self.assertEqual(result["parameters"], bid["parameters"])
        self.assertEqual(result["coeficient"], expected_coeficient)
        self.assertEqual(result["amount_features"], expected_amount_features)


class ImportBidLCCTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_keys = (
            "id",
            "hash",
            "name",
            "date",
            "value",
            "amount_weighted",
        )

    def test_bid_lcc(self):
        tender = deepcopy(test_tender_data_lcc)
        criteria = tender["criteria"]
        bid = tender["bids"][0]
        responses = bid["requirementResponses"]

        result = AuctionLCCBidImporter(bid).import_auction_bid_data()

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))

        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])
        self.assertEqual(result["amount_weighted"], bid["value"]["amount"])
