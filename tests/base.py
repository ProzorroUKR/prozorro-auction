from unittest.mock import MagicMock
from datetime import timedelta
from copy import deepcopy

from prozorro_auction.utils import get_now

now = get_now()

test_identifier = {
    "scheme": u"UA-EDR",
    "id": u"00037256",
    "uri": u"http://www.dus.gov.ua/",
    "legalName": u"Державне управління справами",
}

test_organization = {
    "name": u"Державне управління справами",
    "identifier": test_identifier,
    "address": {
        "countryName": u"Україна",
        "postalCode": u"01220",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {"name": u"Державне управління справами", "telephone": u"0440000000"},
    "scale": "micro",
}

test_author = test_organization.copy()


test_procuringEntity = test_author.copy()
test_procuringEntity["kind"] = "general"
test_milestones = [
    {
        "id": "a" * 32,
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {"days": 2, "type": "banking"},
        "sequenceNumber": 0,
        "percentage": 45.55,
    },
    {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {"days": 900, "type": "calendar"},
        "sequenceNumber": 0,
        "percentage": 54.45,
    },
]

test_item = {
    "description": u"футляри до державних нагород",
    "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
    "additionalClassifications": [
        {"scheme": u"ДКПП", "id": u"17.21.1", "description": u"папір і картон гофровані, паперова й картонна тара"}
    ],
    "unit": {"name": u"item", "code": u"44617100-9"},
    "quantity": 5,
    "deliveryDate": {
        "startDate": (now + timedelta(days=2)).isoformat(),
        "endDate": (now + timedelta(days=5)).isoformat(),
    },
    "deliveryAddress": {
        "countryName": u"Україна",
        "postalCode": "79000",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова 1",
    },
}

test_tender_data = {
    "title": u"футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_procuringEntity,
    "value": {"amount": 500, "currency": u"UAH"},
    "minimalStep": {"amount": 35, "currency": u"UAH"},
    "items": [deepcopy(test_item)],
    "procurementMethodType": "belowThreshold",
    "milestones": test_milestones,
}

test_tender_data.update(
    {
        "enquiryPeriod": {
            "startDate": (now - timedelta(days=14)).isoformat(),
            "endDate": (now - timedelta(days=7)).isoformat(),
        },
        "tenderPeriod": {"startDate": (now - timedelta(days=7)).isoformat(), "endDate": (now).isoformat()},
        "auctionPeriod": {"startDate": (now).isoformat()},
    }
)

test_bids = [
    {"tenderers": [test_organization], "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}},
    {"tenderers": [test_organization], "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True}},
]


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

    async def __aexit__(self, *_):
        pass

    async def __aenter__(self):
        return self
