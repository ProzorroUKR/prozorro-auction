from prozorro_auction.deprecated_auction_config_filter import is_tender_processed_by_auction
from mock import patch


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "simple.defense": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction():
    tender = {
        "procurementMethodType": "esco",
        "tenderPeriod": {
            "startDate": "2020-09-01T01:00:01+03:00",
            "endDate": "2020-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lowestCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "simple.defense": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction2():

    tender = {
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": {
            "startDate": "2021-10-01T01:00:01+03:00",
            "endDate": "2022-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lowestCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = True

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = False

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "simple.defense": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction3():
    tender = {
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": {
            "startDate": "2022-10-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lifeCycleCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = True

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = False

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": None,
            "simple.defense": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction4():
    tender = {
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lifeCycleCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = True

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = False

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction5():
    tender = {
        "procurementMethodType": "aboveThresholdUA.defense",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "unknown"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": None,
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction6():
    tender = {
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "unknown"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": "2021-01-01T01:00:01+03:00",
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction7():
    tender = {
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "unknown"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = True

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = False

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": "2021-01-01T01:00:01+03:00",
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction8():
    tender = {
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2020-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "unknown"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": "2021-01-01T01:00:01+03:00",
            "belowThreshold": "2021-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction9():
    tender = {
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2020-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lifeCycleCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "aboveThresholdEU": "2025-01-01T01:00:01+03:00",
            "belowThreshold": "2025-03-01T01:00:01+03:00"
        },
        "awardCriteria": {
            "lowestCost": None,
            "lifeCycleCost": "2021-01-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction10():
    tender = {
        "id": "12345ffc415e4d57ad7046aacc91b6e1",
        "procurementMethodType": "aboveThresholdEU",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lifeCycleCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = True

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = False

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "unknown_field": {
            "belowThreshold": "2025-03-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction11():
    tender = {
        "id": "12345ffc415e4d57ad7046aacc91b6e1",
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": {
            "startDate": "2022-11-01T01:00:01+03:00",
            "endDate": "2023-09-08T01:00:01+03:00",
        },
        "awardCriteria": "lifeCycleCost"
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result


@patch("prozorro_auction.deprecated_auction_config_filter.CONFIG_DATA", {
        "procurementMethodType": {
            "belowThreshold": "2020-03-01T01:00:01+03:00"
        }
    }
)
def test_is_tender_processed_by_auction12():
    tender = {
        "id": "12345ffc415e4d57ad7046aacc91b6e1",
        "procurementMethodType": "belowThreshold",
    }

    actual_result = is_tender_processed_by_auction(tender, auction_type='new')
    expected_result = False

    assert expected_result == actual_result

    actual_result = is_tender_processed_by_auction(tender, auction_type='deprecated')
    expected_result = True

    assert expected_result == actual_result
