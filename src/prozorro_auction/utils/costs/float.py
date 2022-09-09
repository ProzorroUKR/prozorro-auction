from prozorro_auction.utils.base import as_decimal


def amount_to_weighted(amount, non_price_cost, reverse=True):
    if reverse:
        return float(as_decimal(amount) + as_decimal(non_price_cost))
    else:
        return float(as_decimal(amount) - as_decimal(non_price_cost))

def amount_from_weighted(amount_weighted, non_price_cost, reverse=True):
    if reverse:
        return float(as_decimal(amount_weighted) - as_decimal(non_price_cost))
    else:
        return float(as_decimal(amount_weighted) + as_decimal(non_price_cost))

def amount_to_mixed_weighted(amount, denominator, addition):
    return float(as_decimal(amount) / as_decimal(denominator) + as_decimal(addition))

def amount_from_mixed_weighted(amount_weighted, denominator, addition):
    return float((as_decimal(amount_weighted) - as_decimal(addition)) * as_decimal(denominator))

def amount_allowed(amount, min_step_amount, reverse=True):
    if reverse:
        return float(as_decimal(amount) - as_decimal(min_step_amount))
    else:
        return float(as_decimal(amount) + as_decimal(min_step_amount))
