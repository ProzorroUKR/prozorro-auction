import json
import operator
from dateutil.parser import parse
from prozorro_auction.settings import DEPRECATED_AUCTION_CONFIG_PATH
from prozorro_auction.settings import logger

VALID_AUCTION_TYPES = ("new", "deprecated")


def is_tender_processed_by_auction(_tender, auction_type):
    with open(DEPRECATED_AUCTION_CONFIG_PATH) as _file:
        config_data = json.load(_file)

    if auction_type not in VALID_AUCTION_TYPES:
        raise ValueError("Auction type must be one of ".format(VALID_AUCTION_TYPES))

    tender_period_start_date_str = _tender.get("tenderPeriod", {}).get("startDate", None)
    if not tender_period_start_date_str:
        logger.error("There is no tenderPeriod startDate in tender {}".format(_tender["id"]))
        tender_period_start_date_str = "2000-01-01T00:00:00+00:00"

    tender_period_start_date = parse(tender_period_start_date_str)
    _filters_statuses = []

    for filter_key, filter_data in config_data.items():
        _filters_statuses.append(
            is_match_criteria(filter_data, _tender, filter_key, tender_period_start_date)
        )

    if auction_type == VALID_AUCTION_TYPES[0]:
        return any(_filters_statuses)
    else:
        return all(map(operator.not_, _filters_statuses))


def is_match_criteria(filter_data, _tender, _filter_key, tender_period_start_date):
    try:
        tender_field_value = _tender[_filter_key]
    except KeyError:
        logger.error("There is no {} field in tender {}".format(_filter_key, _tender["id"]))
        return False
    else:
        param_start_date = filter_data.get(tender_field_value, None)

        try:
            config_start_date = parse(param_start_date)
        except ValueError:
            logger.error("Invalid Date string {} for {} filter key".format(param_start_date, _filter_key))
            return False
        except TypeError:
            return False
        else:
            if tender_period_start_date >= config_start_date:
                return True
            else:
                return False
