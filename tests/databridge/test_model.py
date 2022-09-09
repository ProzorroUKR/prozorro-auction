import unittest

from copy import deepcopy
from barbecue import calculate_coeficient, cooking

from prozorro_auction.databridge.model import (
    build_urls_patch,
    get_data_from_tender,
)
from prozorro_auction.databridge.model import (
    generate_auction_id,
    is_auction_cancelled,
    get_items,
    get_auction_type,
)
from prozorro_auction.settings import AUCTION_HOST

from tests.base import (
    test_tender_data,
    test_tender_data_multilot,
    test_tender_data_features,
    test_tender_data_lcc,
    test_tender_data_mixed,
    test_tender_data_esco,
    test_tender_data_esco_features,
    test_tender_data_esco_multilot,
)


class GetDataFromTenderTestCase(unittest.TestCase):
    def assert_auction_keys(self, results):
        expected_keys = (
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
            "criteria",
        )

        expected_item_keys = (
            "id",
            "description",
            "description_en",
            "description_ru",
            "quantity",
            "unit",
            "relatedLot",
        )

        for auction in results:
            auction_keys = set(auction.keys())
            self.assertTrue(auction_keys.issubset(expected_keys))
            for item in auction["items"]:
                items_keys = set(item.keys())
                self.assertTrue(items_keys.issubset(expected_item_keys))

    def assert_auction_basic_fields(self, result, tender):
        self.assertEqual(result["tender_id"], tender["id"])
        self.assertEqual(result["mode"], False)
        self.assertEqual(result["title"], tender["title"])
        self.assertEqual(result["procurementMethodType"], tender["procurementMethodType"])
        self.assertEqual(result["procuringEntity"], tender["procuringEntity"])
        self.assertEqual(result["start_at"], tender["auctionPeriod"]["startDate"])
        self.assertEqual(result["is_cancelled"], False)

    def assert_auction_fields(self, result, tender):
        self.assert_auction_basic_fields(result, tender)
        self.assertEqual(result["_id"], tender["id"])
        self.assertEqual(result["lot_id"], None)
        self.assertEqual(result["items"], get_items(tender))
        if tender["procurementMethodType"] == "esco":
            self.assertEqual(result["minimalStepPercentage"], tender["minimalStepPercentage"])
        else:
            self.assertEqual(result["value"], tender["value"])
            self.assertEqual(result["minimalStep"], tender["minimalStep"])

    def assert_auction_multilot_fields(self, result, tender, lot):
        self.assert_auction_basic_fields(result, tender)
        self.assertEqual(result["_id"], f"{tender['id']}_{result['lot_id']}")
        self.assertIn(result["lot_id"], map(lambda lot: lot["id"], tender["lots"]))
        self.assertEqual(result["items"], get_items(tender, lot))
        if tender["procurementMethodType"] == "esco":
            self.assertEqual(result["minimalStepPercentage"], lot["minimalStepPercentage"])
        else:
            self.assertEqual(result["value"], lot["value"])
            self.assertEqual(result["minimalStep"], lot["minimalStep"])

    def assert_auction_bid_fields(self, bid_result, original_bid):
        self.assertEqual(bid_result["id"], original_bid["id"])
        self.assertEqual(len(bid_result["hash"]), 32)
        self.assertEqual(bid_result["name"], original_bid["tenderers"][0]["name"])
        self.assertEqual(bid_result["date"], original_bid["date"])
        self.assertEqual(bid_result["value"], original_bid["value"])

    def assert_auction_multilot_bid_fields(self, bid_result, original_bid, original_lot_value):
        self.assertEqual(bid_result["id"], original_bid["id"])
        self.assertEqual(len(bid_result["hash"]), 32)
        self.assertEqual(bid_result["name"], original_bid["tenderers"][0]["name"])
        self.assertEqual(bid_result["date"], original_lot_value["date"])
        self.assertEqual(bid_result["value"], original_lot_value["value"])

    def assert_auction_default(self, tender):
        results = list(get_data_from_tender(tender))

        self.assert_auction_keys(results)
        self.assertEqual(len(results), 1)

        result = results[0]
        self.assert_auction_fields(result, tender)
        self.assertEqual(result["auction_type"], "default")
        self.assertEqual(result["features"], [])
        self.assertEqual(len(result["bids"]), 2)
        for bid_result in result["bids"]:
            bid = next(filter(
                lambda bid: bid["id"] == bid_result["id"],
                tender["bids"]
            ))
            self.assert_auction_bid_fields(bid_result, bid)

    def assert_auction_default_multilot(self, tender):
        results = list(get_data_from_tender(tender))
        self.assert_auction_keys(results)
        self.assertEqual(len(results), len(tender["lots"]))
        for result in results:
            lot = next(filter(
                lambda lot: lot["id"] == result["lot_id"],
                tender["lots"]
            ))
            self.assert_auction_multilot_fields(result, tender, lot)
            self.assertEqual(result["auction_type"], "default")
            self.assertEqual(result["features"], [])
            bids = list(filter(
                lambda bid: list(filter(
                    lambda lot_value: lot_value["relatedLot"] == result["lot_id"],
                    bid["lotValues"]
                )),
                tender["bids"]
            ))
            self.assertEqual(len(result["bids"]), len(bids))
            for bid_result in result["bids"]:
                bid = next(filter(
                    lambda bid: bid["id"] == bid_result["id"],
                    tender["bids"]
                ))
                lot_value = next(filter(
                    lambda lot_value: lot_value["relatedLot"] == result["lot_id"],
                    bid["lotValues"]
                ))
                self.assert_auction_multilot_bid_fields(bid_result, bid, lot_value)

    def assert_auction_meat(self, tender):
        results = list(get_data_from_tender(tender))
        self.assert_auction_keys(results)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assert_auction_fields(result, tender)
        self.assertEqual(result["auction_type"], "meat")
        self.assertEqual(result["features"], tender["features"])
        self.assertEqual(len(result["bids"]), 2)
        for bid_result in result["bids"]:
            bid = next(filter(
                lambda bid: bid["id"] == bid_result["id"],
                tender["bids"]
            ))
            self.assert_auction_bid_fields(bid_result, bid)
            self.assertTrue(len(bid_result["parameters"]) > 0)
            self.assertEqual(bid_result["parameters"], bid["parameters"])
            expected_coeficient = str(calculate_coeficient(
                tender["features"],
                bid["parameters"]
            ))
            self.assertEqual(bid_result["coeficient"], expected_coeficient)
            expected_amount_features = str(cooking(
                bid["value"]["amount"],
                tender["features"],
                bid["parameters"],
                reverse=False
            ))
            self.assertEqual(bid_result["amount_features"], expected_amount_features)

    def assert_auction_lcc(self, tender):
        results = list(get_data_from_tender(tender))
        self.assert_auction_keys(results)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assert_auction_fields(result, tender)
        self.assertEqual(result["auction_type"], "lcc")
        self.assertEqual(result["features"], [])
        self.assertEqual(len(result["criteria"]), 4)
        self.assertEqual(result["criteria"], tender["criteria"])
        self.assertEqual(len(result["bids"]), 2)
        for bid_result in result["bids"]:
            bid = next(filter(
                lambda bid: bid["id"] == bid_result["id"],
                tender["bids"]
            ))
            self.assert_auction_bid_fields(bid_result, bid)
            self.assertEqual(bid_result["responses"], bid["requirementResponses"])

    def assert_auction_mixed(self, tender):
        results = list(get_data_from_tender(tender))
        self.assert_auction_keys(results)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assert_auction_fields(result, tender)
        self.assertEqual(result["auction_type"], "mixed")
        self.assertEqual(result["features"], tender["features"])
        self.assertEqual(len(result["criteria"]), 4)
        self.assertEqual(result["criteria"], tender["criteria"])
        self.assertEqual(len(result["bids"]), 2)
        for bid_result in result["bids"]:
            bid = next(filter(
                lambda bid: bid["id"] == bid_result["id"],
                tender["bids"]
            ))
            self.assert_auction_bid_fields(bid_result, bid)

    def test_get_data_default(self):
        tender = deepcopy(test_tender_data)
        self.assert_auction_default(tender)

    def test_get_data_default_esco(self):
        tender = deepcopy(test_tender_data_esco)
        assert tender["procurementMethodType"] == "esco"
        self.assert_auction_default(tender)

    def test_get_data_default_multilot(self):
        tender = deepcopy(test_tender_data_multilot)
        self.assert_auction_default_multilot(tender)

    def test_get_data_default_multilot_esco(self):
        tender = deepcopy(test_tender_data_esco_multilot)
        assert tender["procurementMethodType"] == "esco"
        self.assert_auction_default_multilot(tender)

    def test_get_data_meat(self):
        tender = deepcopy(test_tender_data_features)
        self.assert_auction_meat(tender)

    def test_get_data_meat_esco(self):
        tender = deepcopy(test_tender_data_esco_features)
        assert tender["procurementMethodType"] == "esco"
        self.assert_auction_meat(tender)

    def test_get_data_lcc(self):
        tender = deepcopy(test_tender_data_lcc)
        self.assert_auction_lcc(tender)

    def test_get_data_mixed(self):
        tender = deepcopy(test_tender_data_mixed)
        self.assert_auction_mixed(tender)


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
        tender = {"bids": [{}]}
        auction = {"features": [], "criteria": []}
        self.assertEqual(get_auction_type(auction, tender), "default")

    def test_meat(self):
        tender = {"bids": [{}]}
        auction = {"features": [{}], "criteria": []}
        self.assertEqual(get_auction_type(auction, tender), "meat")

    def test_lcc(self):
        tender = {"awardCriteria": "lifeCycleCost", "bids": [{}]}
        auction = {"features": [], "criteria": [{}]}
        self.assertEqual(get_auction_type(auction, tender), "lcc")

    def test_mixed(self):
        tender = {"awardCriteria": "lifeCycleCost", "bids":[{"weightedValue": {}}]}
        auction = {"features": [], "criteria": [{}]}
        self.assertEqual(get_auction_type(auction, tender), "mixed")


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
        tender = deepcopy(test_tender_data)

        results = get_items(tender)

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result, {
            "description": "футляри до державних нагород",
            "quantity": 5,
            "unit": {"code": "44617100-9", "name": "item"},
        })

    def test_tender_multilot(self):
        tender = deepcopy(test_tender_data_multilot)
        lot = tender["lots"][0]

        results = get_items(tender, lot)

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result, {
            "description": "футляри до державних нагород",
            "quantity": 5,
            "unit": {"code": "44617100-9", "name": "item"},
            "relatedLot": lot["id"],
        })


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
