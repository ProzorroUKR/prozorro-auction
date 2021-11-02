from prozorro_auction.api.utils import ValidationError, ForbiddenError
from prozorro_auction.constants import AuctionType, ProcurementMethodType
from prozorro_auction.utils.costs import (
    float as float_costs_utils,
    fraction as fraction_costs_utils,
)
from prozorro_auction.utils.base import get_now
from esculator import npv
from fractions import Fraction
from iso8601 import parse_date


NPV_CALCULATION_DURATION = 20  # accounting period, years
DAYS_IN_YEAR = 365
MAX_CONTRACT_DURATION = 15


def get_bid_by_bidder_id(auction, bidder_id):
    for bid in auction["bids"]:
        if bid["id"] == bidder_id:
            return bid
    else:
        raise ValidationError(f"Invalid bidder_id {bidder_id}")


def get_posted_bid(auction, bid, hash_value, data):
    current_stage = auction.get("current_stage", 0)
    auction_stage = auction["stages"][current_stage]

    if bid["hash"] != hash_value:
        raise ForbiddenError("Invalid hash")

    if auction_stage["type"] != "bids":
        raise ValidationError("Stage not for bidding")

    if auction_stage["bidder_id"] != bid["id"]:
        raise ValidationError("Not valid bidder")

    if auction["procurementMethodType"] == ProcurementMethodType.ESCO.value:
        posted_bid = validated = _validate_esco_fields(auction, auction_stage, bid, data)
    else:
        validated = _validate_amount(auction, auction_stage, bid, data)
        posted_bid = dict(amount=validated)

    if validated == -1:
        return ""  # cancellation of the posted bid this round
    else:
        posted_bid["time"] = get_now().isoformat()
    return posted_bid


def get_stage_auction_type(stage):
    if stage.get("amount_features"):
        return AuctionType.MEAT
    elif stage.get("amount_weighted"):
        return AuctionType.LCC
    else:
        return AuctionType.DEFAULT


def _validate_amount(auction, auction_stage, bid, data):
    if "amount" not in data:
        raise ValidationError('Bid amount is required')

    amount = data["amount"]
    if amount <= 0.0 and amount != -1:  # -1 means cancelling this stage bid (should be deleted from db)
        raise ValidationError('Too low value')

    auction_type = get_stage_auction_type(auction_stage)
    if auction_type == AuctionType.DEFAULT:
        max_allowed = float_costs_utils.amount_allowed(
            amount=auction_stage['amount'],
            min_step_amount=auction['minimalStep']['amount'],
            reverse=True,
        )
        if amount > max_allowed:
            raise ValidationError(u'Too high value')
    elif auction_type == AuctionType.MEAT:
        calculated_amount = fraction_costs_utils.amount_from_features(
            amount_features=auction_stage['amount_features'],
            coeficient=bid["coeficient"],
            reverse=True,
        )
        max_allowed = fraction_costs_utils.amount_allowed(
            amount=calculated_amount,
            min_step_amount=auction['minimalStep']['amount'],
            reverse=True,
        )
        if amount > max_allowed:
            raise ValidationError(u'Too high value')
    elif auction_type == AuctionType.LCC:
        calculated_amount = float_costs_utils.amount_from_weighted(
            amount_weighted=auction_stage['amount_weighted'],
            non_price_cost=bid["non_price_cost"],
            reverse=True,
        )
        max_allowed = float_costs_utils.amount_allowed(
            amount=calculated_amount,
            min_step_amount=auction['minimalStep']['amount'],
            reverse=True,
        )
        if amount > max_allowed:
            raise ValidationError(u'Too high value')
    else:
        message = f"Auction type {auction_type.value} is not supported"
        raise ValidationError(message)

    return amount


def _validate_esco_fields(auction, auction_stage, bid, data):
    if "yearlyPaymentsPercentage" not in data:
        raise ValidationError('Provide yearlyPaymentsPercentage')
    yearly_percentage = data["yearlyPaymentsPercentage"]
    if yearly_percentage == -1:  # it's cancelling of the previous bid
        return yearly_percentage

    kind = auction.get("fundingKind", "")
    yearly_percentage_fraction = Fraction(str(yearly_percentage))
    if kind == "other":
        if yearly_percentage_fraction < Fraction("0.8") or yearly_percentage_fraction > Fraction("1"):
            raise ValidationError("Percentage value must be between 80 and 100")
    elif kind == 'budget':
        yearly_payments_percentage_range = auction['yearlyPaymentsPercentageRange']
        if (
            yearly_percentage_fraction < Fraction('0') or
            yearly_percentage_fraction > Fraction(str(yearly_payments_percentage_range))
        ):
            message = u'Percentage value must be between 0 and {}'.format(
                yearly_payments_percentage_range * 100)
            raise ValidationError(message)

    contract_duration = data["contractDuration"]
    min_val, max_val = 0, MAX_CONTRACT_DURATION
    if contract_duration < min_val or contract_duration > max_val:
        raise ValidationError(f"contractDuration must be between {min_val} and {max_val}.")

    duration_days = data["contractDurationDays"]
    min_val, max_val = 0, DAYS_IN_YEAR - 1
    if duration_days < min_val or duration_days > max_val:
        raise ValidationError(f"contractDurationDays must be between {min_val} and {max_val}.")
    if (Fraction(duration_days, DAYS_IN_YEAR) + contract_duration) > MAX_CONTRACT_DURATION:
        raise ValidationError(f"Maximum contract duration is {MAX_CONTRACT_DURATION} years")
    if contract_duration + duration_days == 0:
        raise ValidationError("You can't bid 0 days and 0 years")

    amount = npv(
        contract_duration,
        duration_days,
        yearly_percentage,
        bid["value"]['annualCostsReduction'],
        parse_date(auction['noticePublicationDate']),
        auction['NBUdiscountRate']
    )

    auction_type = get_stage_auction_type(auction_stage)
    if auction_type == AuctionType.DEFAULT:
        min_allowed = fraction_costs_utils.amount_allowed_percentage(
            amount=auction_stage['amount'],
            min_step_percentage=auction['minimalStepPercentage'],
            reverse=False,
        )
        if amount < min_allowed:
            message = 'Amount NPV: Too low value'
            raise ValidationError(message)
    elif auction_type == AuctionType.MEAT:
        calculated_amount = fraction_costs_utils.amount_from_features(
            amount_features=auction_stage['amount_features'],
            coeficient=bid["coeficient"],
            reverse=False,
        )
        min_allowed = fraction_costs_utils.amount_allowed_percentage(
            amount=calculated_amount,
            min_step_percentage=auction['minimalStepPercentage'],
            reverse=False,
        )
        if amount < min_allowed:
            message = 'Amount NPV: Too low value'
            raise ValidationError(message)
    elif auction_type == AuctionType.LCC:
        message = f"Auction type {auction_type.value} is not supported for esco procurement method type"
        raise ValidationError(message)
    else:
        message = f"Auction type {auction_type.value} is not supported"
        raise ValidationError(message)

    esco_bid_fields = dict(
        amountPerformance=str(amount),
        contractDuration=dict(
            years=contract_duration,
            days=duration_days,
        ),
        yearlyPaymentsPercentage=yearly_percentage,
    )
    return esco_bid_fields


def get_bid_response_data(auction, bid):
    current_stage = auction.get("current_stage", 0)
    try:
        auction_stage = auction["stages"][current_stage]
    except IndexError:
        return {}

    if auction["procurementMethodType"] == ProcurementMethodType.ESCO.value:
        bid_data = None
        if auction_stage["type"] == "bids" and auction_stage["bidder_id"] == bid["id"]:
            bid_data = bid.get("stages", {}).get(str(current_stage), {})
        if bid_data:
            bid_data["changed"] = True
        else:  # for esco we return latest saved bid if no bids made in the current round
            bid_data = bid["value"]
        resp_data = {
            "contractDurationYears": bid_data["contractDuration"]["years"],
            "contractDurationDays": bid_data["contractDuration"]["days"],
            "yearlyPaymentsPercentage": bid_data["yearlyPaymentsPercentage"],
            "changed": bid_data.get("changed", False),  # to show "edit bid" button
        }
    else:
        # get bids saved amount on this stage
        amount = None
        if auction_stage["type"] == "bids" and auction_stage["bidder_id"] == bid["id"]:
            amount = bid.get("stages", {}).get(str(current_stage), {}).get("amount")
        resp_data = {"amount": amount}

    return resp_data
