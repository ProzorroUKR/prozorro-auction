from prozorro_auction.api.utils import ValidationError, ForbiddenError
from prozorro_auction.settings import logger, TZ
from fractions import Fraction
from datetime import datetime, timedelta
import uuid


def get_test_auction():
    uid = uuid.uuid4().hex
    start_at = datetime.now(tz=TZ) + timedelta(seconds=30)
    data = dict(
        _id=uid,
        lot_id=None,
        tender_id="",
        mode=None,
        current_stage=-1,
        minimalStep={
            "currency": "UAH",
            "amount": 35,
            "valueAddedTaxIncluded": True
        },
        procurementMethodType="belowThreshold",
        tenderID=f"UA-{uid}",
        start_at=start_at,
        timer=start_at,
        procuringEntity=dict(
            name="procuringEntity Name",
            name_en="procuringEntity Name EN",
        ),
        title="Title",
        title_en="Title En",
        bids=[
            {
                "id": "a" * 32,
                "hash": uuid.uuid4().hex,
                "date": "2019-08-12T14:53:52+03:00",
                "name": "Bidder#1 Name",
                "value": {"amount": 132.22},
            },
            {
                "id": "b" * 32,
                "hash": uuid.uuid4().hex,
                "date": "2019-08-12T15:53:52+03:00",
                "name": "Bidder#2 Name",
                "value": {"amount": 232.66},
            }
        ]
    )
    return data


def validate_posted_bid_amount(auction, bidder_id, hash_value, data):
    for bid in auction["bids"]:
        if bid["id"] == bidder_id:
            current_stage = auction.get("current_stage", 0)
            auction_stage = auction["stages"][current_stage]

            if bid["hash"] != hash_value:
                raise ForbiddenError("Invalid hash")

            if auction_stage["type"] != "bids":
                raise ValidationError("Stage not for bidding")

            if auction_stage["bidder_id"] != bidder_id:
                raise ValidationError("Not valid bidder")

            if "amount" not in data:
                raise ValidationError('Bid amount is required')

            amount = data["amount"]
            if amount <= 0.0 and amount != -1:  # -1 means cancelling this stage bid (should be deleted from db)
                raise ValidationError('Too low value')

            if auction["features"]:
                minimal_bid = auction_stage['amount_features']
                minimal = Fraction(minimal_bid) * Fraction(bid["coeficient"])
                minimal -= Fraction(auction['minimalStep']['amount'])
                if amount > minimal:
                    raise ValidationError(u'Too high value')
            else:
                minimal_bid = auction_stage['amount']
                max_allowed = minimal_bid - auction['minimalStep']['amount']
                max_allowed = float(
                    str(max_allowed))  # convert floats to more likely values, ex 0.19999999999999996 to 0.2
                if amount > max_allowed:
                    raise ValidationError(u'Too high value')

            return amount

    else:
        raise ValidationError(f"Invalid bidder_id {bidder_id}")
