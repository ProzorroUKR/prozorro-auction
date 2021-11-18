import pytest
from unittest import TestCase
from unittest.mock import patch

from prozorro_auction.api.model import (
    get_posted_bid, get_bid_response_data, ForbiddenError, ValidationError,
    get_bid_by_bidder_id, _validate_esco_fields, _validate_amount
)
from prozorro_auction.utils.base import as_decimal


class GetPostedBidTestCase(TestCase):
    @patch("prozorro_auction.api.model._validate_amount", return_value=89.9)
    def test_get_posted_bid_default(self, _):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value
        }
        auction = {
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

    @patch("prozorro_auction.api.model._validate_amount", return_value=80.0)
    def test_get_posted_bid_lcc(self, _):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "non_price_cost": 9.9
        }
        auction = {
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

    @patch("prozorro_auction.api.model._validate_amount", return_value=109.91)
    def test_get_posted_bid_meat(self, _):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "coeficient": 1.2
        }
        auction = {
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

    def test_get_posted_bid_forbiddenerror(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": "not_equal_hash_value",
            "coeficient": 1.2
        }
        auction = {
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
        with self.assertRaises(ForbiddenError) as ctx:
            get_posted_bid(auction, bid, hash_value, data)
        expected_msg = '{"error": "Invalid hash"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    def test_get_posted_bid_validationerror_stage_not_for_bidding(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "Nobids",
                    "bidder_id": bid["id"],
                    "amount": 90.2,
                    "amount_features": 100.1,
                }
            ]
        }
        data = {
            "amount": 109.91,
        }
        with self.assertRaises(ValidationError) as ctx:
            get_posted_bid(auction, bid, hash_value, data)
        expected_msg = '{"error": "Stage not for bidding"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    def test_get_posted_bid_validationerror_not_valid_bidder(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "bids",
                    "bidder_id": "new_id",
                    "amount": 90.2,
                    "amount_features": 100.1,
                }
            ]
        }
        data = {
            "amount": 109.91,
        }
        with self.assertRaises(ValidationError) as ctx:
            get_posted_bid(auction, bid, hash_value, data)
        expected_msg = '{"error": "Not valid bidder"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    @patch("prozorro_auction.api.model._validate_amount", return_value=-1)
    def test_get_posted_bid_amount_minus_one(self, _):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value,
            "coeficient": 1.2
        }
        auction = {
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
            "amount": -1,
        }
        return_result = get_posted_bid(auction, bid, hash_value, data)
        assert return_result == ""


class ValidateAmount(TestCase):
    def test_validate_amount_validationerror_bid_amount(self):
        bid = {"id": "bid_id", "hash": "hash_value"}
        auction = {
            "auction_type": "default",
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {"amount": 10.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount": 100.1}
            ]
        }
        data = {"item": 89.9}
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 100.1}
        with self.assertRaises(ValidationError) as ctx:
            _validate_amount(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Bid amount is required"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    def test_validate_amount_validationerror_low_value(self):
        hash_value = "hash_value"
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 100.1}
        bid = {"id": "bid_id", "hash": hash_value}
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {"amount": 10.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount": 100.1}
            ]
        }
        data = {"amount": 0.0}

        with self.assertRaises(ValidationError) as ctx:
            _validate_amount(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Too low value"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.float_costs_utils.amount_allowed", return_value=69.9)
    def test_validate_amount_auctiontype_default_validationerror_high_value(self, _):
        hash_value = "hash_value"
        bid = {"id": "bid_id", "hash": hash_value}
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 100.1}
        auction = {
            "auction_type": "default",
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {"amount": 30.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount": 100.1}
            ]
        }
        data = {"amount": 89.9}

        with self.assertRaises(ValidationError) as ctx:
            _validate_amount(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Too high value"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.float_costs_utils.amount_allowed", return_value=69.9)
    def test_validate_amount_auctiontype_meat_validationerror_high_value(self, _):
        hash_value = "hash_value"
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 100.1}
        bid = {"id": "bid_id", "hash": hash_value, "coeficient": 10}
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {"amount": 30.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount_features": 1.0,
                 "amount": 100.1}
            ]
        }
        data = {"amount": 89.9}

        with self.assertRaises(ValidationError) as ctx:
            _validate_amount(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Too high value"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.float_costs_utils.amount_allowed", return_value=69.9)
    def test_validate_amount_auctiontype_lcc_validationerror_high_value(self, _):
        hash_value = "hash_value"
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 100.1}
        bid = {"id": "bid_id", "hash": hash_value, "coeficient": 10, "non_price_cost": 1}
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {"amount": 30.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount_weighted": 1.0,
                 "amount": 100.1}
            ]
        }
        data = {"amount": 89.9}

        with self.assertRaises(ValidationError) as ctx:
            _validate_amount(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Too high value"}'
        self.assertEqual(ctx.exception.text, expected_msg)


class GetBidResponseData(TestCase):
    def test_get_bid_response_data_amount_none(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value
        }
        auction = {
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
        return_result = get_bid_response_data(auction, bid)
        assert return_result == {'amount': None}

    def test_get_bid_response_data_indexerror(self):
        hash_value = "hash_value"
        bid = {
            "id": "bid_id",
            "hash": hash_value
        }
        auction = {
            "procurementMethodType": "aboveThresholdUA",
            "current_stage": 1,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [{"key": "value"}]
        }
        return_result = get_bid_response_data(auction, bid)
        assert {} == return_result

    def test_get_bid_response_data_esco_resp_data(self):
        hash_value = "hash_value"
        bid_data = {"contractDuration": {
            "years": "2000",
            "days": "20"
        },
            "yearlyPaymentsPercentage": 25
        }
        bid = {"id": "bid_id", "hash": hash_value, "value": bid_data}
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "minimalStep": {"amount": 10.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount": 100.1}
            ]
        }
        expect_result = {
            'contractDurationYears': '2000',
            'contractDurationDays': '20',
            'yearlyPaymentsPercentage': 25,
            'changed': False
        }

        return_result = get_bid_response_data(auction, bid)
        assert return_result == expect_result

        bid["stages"] = {"1": bid_data}
        return_result = get_bid_response_data(auction, bid)
        expect_result["changed"] = True
        assert return_result == expect_result

    def test_get_bid_response_data_esco_keyerror(self):
        hash_value = "hash_value"
        bid = {"id": "bid_id", "hash": hash_value}
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "minimalStep": {"amount": 10.2},
            "stages": [
                {},
                {"type": "bids",
                 "bidder_id": bid["id"],
                 "amount": 100.1}
            ]
        }
        with pytest.raises(KeyError) as e:
            get_bid_response_data(auction, bid)
        assert "'value'" == str(e.value)


class GetBidByBidderId(TestCase):
    def test_get_bid_by_bidder_id_return(self):
        bidder_id = "bid_id"
        auction = {
            "bids": [
                {"id": bidder_id}
            ]
        }
        return_result = get_bid_by_bidder_id(auction, bidder_id)
        assert return_result == {"id": bidder_id}

    def test_get_bid_by_bidder_id_raise(self):
        bidder_id = "bid_id"
        auction = {
            "bids": [
                {"id": "other_bidder_id"}
            ]
        }
        with self.assertRaises(ValidationError) as ctx:
            get_bid_by_bidder_id(auction, bidder_id)
        expected_msg = '{"error": "Invalid bidder_id bid_id"}'
        self.assertEqual(ctx.exception.text, expected_msg)


class ValidateEscoFields(TestCase):
    def test_validate_esco_fields_validationerror_yearlypaymentspercentage(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
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
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as ctx:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Provide yearlyPaymentsPercentage"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    def test_validate_esco_fields_return_yearly_percentage(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
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
            "yearlyPaymentsPercentage": -1,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}

        expect_result = -1
        actual_result = _validate_esco_fields(auction, auction_stage, bid, data)
        assert expect_result == actual_result

    def test_validate_esco_fields_validationerror_percentage_value_between_80_and_100(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "fundingKind": "other",
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
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as ctx:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Percentage value must be between 80 and 100"}'
        self.assertEqual(ctx.exception.text, expected_msg)

    def test_validate_esco_fields_validationerror_percentage_value_must_be_0(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
            "fundingKind": "budget",
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
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Percentage value must be between 0 and -50.0"}'
        self.assertEqual(context.exception.text, expected_msg)

    def test_validate_esco_fields_validationerror_contractduration_value_must_beetween_min_val_and_max_val(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
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
            "contractDuration": 20,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "contractDuration must be between 0 and 15."}'
        self.assertEqual(context.exception.text, expected_msg)

    def test_validate_esco_fields_validationerror_contractdurationdays_value_must_beetween_min_val_and_max_val(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
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
            "contractDuration": 10,
            "contractDurationDays": 400,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "contractDurationDays must be between 0 and 364."}'
        self.assertEqual(context.exception.text, expected_msg)

    def test_validate_esco_fields_validationerror_maximum_contract_duration(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
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
            "contractDuration": 15,
            "contractDurationDays": 364,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Maximum contract duration is 15 years"}'
        self.assertEqual(context.exception.text, expected_msg)

    def test_validate_esco_fields_validationerror_0_days_0_years(self):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2
        }
        auction = {
            "procurementMethodType": "esco",
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
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
            "contractDuration": 0,
            "contractDurationDays": 0,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "You can\'t bid 0 days and 0 years"}'
        self.assertEqual(context.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.fraction_costs_utils.amount_allowed_percentage",
           return_value=6347260724825293/35184372088832)
    @patch("prozorro_auction.api.model.npv", return_value=319/36500)
    def test_validate_esco_fields_auction_type_default_validationerror_amount_npv_too_low_value(self, *args):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2,
            "value": {"annualCostsReduction": [0] * 20 + [0.01]}
        }
        auction = {
            "NBUdiscountRate": 0.0000,
            "noticePublicationDate": "2021-11-15T15:43:37",
            "procurementMethodType": "default",
            "minimalStepPercentage": 1,
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": -0.5,
            "minimalStep": {
                "amount": 10.2
            },
            "stages": [
                {},
                {
                    "type": "bids",
                    "bidder_id": bid["id"],
                    "amount": 90.2,
                }
            ]
        }
        data = {
            "amount": 109.91,
            "contractDuration": 1,
            "contractDurationDays": 0,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Amount NPV: Too low value"}'
        self.assertEqual(context.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.fraction_costs_utils.amount_allowed_percentage",
           return_value=27916201518226066435371554998059/304236144054775045100209700864)
    @patch("prozorro_auction.api.model.fraction_costs_utils.amount_from_features",
           return_value=450810322699786624/5404319552844595)
    @patch("prozorro_auction.api.model.npv", return_value=3/1460)
    def test_validate_esco_fields_auction_type_meat_validationerror_amount_npv_too_low_value(self, *args):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2,
            "value": {"annualCostsReduction": [0] * 20 + [0.01]}
        }
        auction = {
            "NBUdiscountRate": 0.0000,
            "noticePublicationDate": "2031-03-16T00:00:00+02:00",
            "procurementMethodType": "meat",
            "minimalStepPercentage": 0.1,
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": 0.5,
            "minimalStep": {"amount": 10.2},
            "stages": [{}, {"type": "bids", "bidder_id": bid["id"], "amount": 90.2, "amount_features": 100.1, }]
        }
        data = {
            "amount": 109.91,
            "contractDuration": 2,
            "contractDurationDays": 10,
            "yearlyPaymentsPercentage": 0.70,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}

        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Amount NPV: Too low value"}'
        self.assertEqual(context.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.npv", return_value=3/1460)
    def test_validate_esco_fields_auction_type_lcc_validationerror_amount_npv_too_low_value(self, *args):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2,
            "value": {
                "annualCostsReduction": [500.0] + [1000.0] * 20
            }
        }
        auction = {
            "NBUdiscountRate": 0.0000,
            "noticePublicationDate": "2021-11-15T15:43:37",
            "procurementMethodType": "lcc",
            "minimalStepPercentage": 1,
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": 0.5,
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
            "contractDuration": 1,
            "contractDurationDays": 0,
            "yearlyPaymentsPercentage": 0.3,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_weighted': 100.1}
        with self.assertRaises(ValidationError) as context:
            _validate_esco_fields(auction, auction_stage, bid, data)
        expected_msg = '{"error": "Auction type lcc is not supported for esco procurement method type"}'
        self.assertEqual(context.exception.text, expected_msg)

    @patch("prozorro_auction.api.model.fraction_costs_utils.amount_allowed_percentage",
           return_value=27916201518226066435371554998059/304236144054775045100209700864)
    @patch("prozorro_auction.api.model.fraction_costs_utils.amount_from_features",
           return_value=450810322699786624/5404319552844595)
    @patch("prozorro_auction.api.model.npv", return_value=787530/73)
    def test_validate_esco_fields_return_esco_bid_fields(self, *args):
        bid = {
            "id": "bid_id",
            "hash": "hash_value",
            "coeficient": 1.2,
            "value": {
                "annualCostsReduction": [500.0] + [1000.0] * 20
            }
        }
        auction = {
            "NBUdiscountRate": 0.000,
            "noticePublicationDate": "2021-03-16T00:00:00+02:00",
            "procurementMethodType": "meat",
            "minimalStepPercentage": 0.1,
            "current_stage": 1,
            "yearlyPaymentsPercentageRange": 0.5,
            "minimalStep": {"amount": 10.2},
            "stages": [{}, {"type": "bids", "bidder_id": bid["id"], "amount": 90.2, "amount_features": 100.1, }]
        }
        data = {
            "amount": 109.91,
            "contractDuration": 10,
            "contractDurationDays": 74,
            "yearlyPaymentsPercentage": 0.9,
        }
        auction_stage = {'type': 'bids', 'bidder_id': 'bid_id', 'amount': 90.2, 'amount_features': 100.1}
        return_result = _validate_esco_fields(auction, auction_stage, bid, data)
        expected_result = {'amountPerformance': '10788.082191780823', 'contractDuration': {'years': 10, 'days': 74}, 'yearlyPaymentsPercentage': 0.9}
        assert expected_result == return_result
