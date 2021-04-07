import unittest
from fractions import Fraction

from barbecue import calculate_coeficient, cooking

from prozorro_auction.databridge.model import (
    build_urls_patch,
    import_bid,
    get_data_from_tender,
    generate_auction_id,
    get_auction_type,
    is_auction_cancelled,
    get_items,
)
from prozorro_auction.settings import AUCTION_HOST

from ..base import (
    test_bids,
    test_bids_multilot,
    test_parameters_bids,
    test_features_tender_data,
    test_tender_data,
    test_tender_data_multilot,
)


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


class ImportBidTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_keys = (
            "id",
            "hash",
            "name",
            "date",
            "value",
        )
        cls.expected_parameters_keys = (
            "id",
            "hash",
            "name",
            "date",
            "value",
            "parameters",
            "coeficient",
            "amount_features",
        )

    def test_bid(self):
        bid = test_bids[0]

        result = import_bid(bid, bid, None, None, None, None)

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))
        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])

    def test_bid_multilot(self):
        bid = test_bids_multilot[0]
        lot_bid = bid["lotValues"][0]

        result = import_bid(bid, lot_bid, None, None, None, None)

        self.assertTrue(set(result.keys()).issubset(self.expected_keys))
        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], lot_bid["date"])
        self.assertEqual(result["value"], lot_bid["value"])

    def test_bid_parameters(self):
        tender = test_features_tender_data
        features = tender["features"]
        bid = test_parameters_bids[0]
        parameters = bid["parameters"]

        expected_coeficient = str(calculate_coeficient(features, parameters))
        self.assertEqual(expected_coeficient, "16212958658533786/12610078956637389")

        expected_amount_features = str(cooking(bid["value"]["amount"], features, parameters, reverse=False))
        self.assertEqual(expected_amount_features, "5914127030662935441/16212958658533786")

        result = import_bid(bid, bid, features, parameters, None, None)

        self.assertTrue(set(result.keys()).issubset(self.expected_parameters_keys))

        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])
        self.assertEqual(result["parameters"], bid["parameters"])
        self.assertEqual(result["coeficient"], expected_coeficient)
        self.assertEqual(result["amount_features"], expected_amount_features)

    def test_bid_parameters_esco(self):
        tender = test_features_tender_data
        features = tender["features"]
        bid = test_parameters_bids[0]
        bid["value"]["amountPerformance"] = 600
        parameters = bid["parameters"]

        expected_coeficient = str(calculate_coeficient(features, parameters))
        self.assertEqual(expected_coeficient, "16212958658533786/12610078956637389")

        expected_amount_features = str(cooking(
            str(Fraction(bid["value"]["amountPerformance"])),
            features, parameters, reverse=True)
        )
        self.assertEqual(expected_amount_features, "3242591731706757200/4203359652212463")

        result = import_bid(bid, bid, features, parameters, None, None)

        self.assertTrue(set(result.keys()).issubset(self.expected_parameters_keys))

        self.assertEqual(result["id"], bid["id"])
        self.assertEqual(result["name"], bid["tenderers"][0]["name"])
        self.assertEqual(result["date"], bid["date"])
        self.assertEqual(result["value"], bid["value"])
        self.assertEqual(result["parameters"], bid["parameters"])
        self.assertEqual(result["coeficient"], expected_coeficient)
        self.assertEqual(result["amount_features"], expected_amount_features)


class GetDataFromTenderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_keys = (
            "tender_id",
            "tenderID",
            "mode",
            "is_cancelled",
            "items",
            "features",
            "auction_type",
            "title",
            "title_en",
            "description",
            "description_en",
            "procurementMethodType",
            "procuringEntity",
            "minimalStep",
            "value",
            "start_at",
            "_id",
            "lot_id",
            "bids",
            "bids",
            "NBUdiscountRate",
            "noticePublicationDate",
            "minimalStepPercentage",
            "fundingKind",
            "yearlyPaymentsPercentageRange",
        )

        cls.expected_item_keys = (
            "id",
            "description",
            "description_en",
            "description_ru",
            "quantity",
            "unit",
            "relatedLot",
        )

    def test_get_data(self):
        tender = test_tender_data

        result = list(get_data_from_tender(tender))

        for auction in result:
            auction_keys = set(auction.keys())
            self.assertTrue(auction_keys.issubset(self.expected_keys))
            for item in auction["items"]:
                items_keys = set(item.keys())
                self.assertTrue(items_keys.issubset(self.expected_item_keys))

    def test_get_data_with_features(self):
        tender = test_features_tender_data

        result = list(get_data_from_tender(tender))

        for auction in result:
            auction_keys = set(auction.keys())
            self.assertTrue(auction_keys.issubset(self.expected_keys))
            self.assertIn("features", auction_keys)
            for item in auction["items"]:
                items_keys = set(item.keys())
                self.assertTrue(items_keys.issubset(self.expected_item_keys))


class GenerateLotAuctionIdTestCase(unittest.TestCase):

    def test_tender(self):
        tender = {"id": "tender_id"}
        self.assertEqual(generate_auction_id(tender), "tender_id")

    def test_lot(self):
        tender = {"id": "tender_id"}
        lot = {"id": "lot_id"}
        self.assertEqual(generate_auction_id(tender, lot), "tender_id_lot_id")


class GetAuctionTypeTestCase(unittest.TestCase):

    def test_default(self):
        tender = {}
        self.assertEqual(get_auction_type(tender), "default")

    def test_meat(self):
        tender = {"features": [{}]}
        self.assertEqual(get_auction_type(tender), "meat")


class IsAuctionCancelledTestCase(unittest.TestCase):

    def test_cancelled_with_cancelled(self):
        tender = {"status": "cancelled"}
        self.assertTrue(is_auction_cancelled(tender))

    def test_cancelled_with_unsuccessful(self):
        tender = {"status": "unsuccessful"}
        self.assertTrue(is_auction_cancelled(tender))

    def test_not_cancelled(self):
        tender = {"status": "not_cancelled_or_unsuccessful"}
        self.assertFalse(is_auction_cancelled(tender))

    def test_multilot_cancelled_with_tender_cancelled(self):
        tender = {"status": "cancelled"}
        lot = {}
        self.assertTrue(is_auction_cancelled(tender, lot))

    def test_multilot_cancelled_with_tender_unsuccessful(self):
        tender = {"status": "unsuccessful"}
        lot = {}
        self.assertTrue(is_auction_cancelled(tender, lot))

    def test_multilot_cancelled_lot_not_active(self):
        tender = {"status": "not_cancelled_or_unsuccessful"}
        lot = {"status": "not_active"}
        self.assertTrue(is_auction_cancelled(tender, lot))

    def test_multilot_not_cancelled(self):
        tender = {"status": "not_cancelled_or_unsuccessful"}
        lot = {"status": "active"}
        self.assertFalse(is_auction_cancelled(tender))


class GetItemsTestCase(unittest.TestCase):

    def test_tender(self):
        tender = test_tender_data

        result = get_items(tender)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {
            "description": "футляри до державних нагород",
            "quantity": 5,
            "unit": {"code": "44617100-9", "name": "item"},
        })

    def test_tender_multilot(self):
        tender = test_tender_data_multilot
        lot = tender["lots"][0]

        result = get_items(tender, lot)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {
            "description": "футляри до державних нагород",
            "quantity": 5,
            "unit": {"code": "44617100-9", "name": "item"},
            "relatedLot": lot["id"],
        })
