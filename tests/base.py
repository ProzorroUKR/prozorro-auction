import uuid
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
    "contactPoint": {
        "name": u"Державне управління справами",
        "telephone": u"0440000000"
    },
    "scale": "micro",
}

test_author = test_organization.copy()

test_procuring_entity = test_author.copy()
test_procuring_entity["kind"] = "general"
test_milestones = [
    {
        "id": "a" * 32,
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {
            "days": 2,
            "type": "banking"
        },
        "sequenceNumber": 0,
        "percentage": 45.55,
    },
    {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {
            "days": 900,
            "type": "calendar"
        },
        "sequenceNumber": 0,
        "percentage": 54.45,
    },
]

test_item = {
    "description": u"футляри до державних нагород",
    "classification": {
        "scheme": u"ДК021",
        "id": u"44617100-9",
        "description": u"Cartons"
    },
    "additionalClassifications": [
        {
            "scheme": u"ДКПП",
            "id": u"17.21.1",
            "description": u"папір і картон гофровані, паперова й картонна тара"
        }
    ],
    "unit": {
        "name": u"item",
        "code": u"44617100-9"
    },
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
    "id": uuid.uuid4().hex,
    "title": u"футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_procuring_entity,
    "value": {
        "amount": 500,
        "currency": u"UAH"
    },
    "minimalStep": {
        "amount": 35,
        "currency": u"UAH"
    },
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
        "tenderPeriod": {
            "startDate": (now - timedelta(days=7)).isoformat(),
            "endDate": (now).isoformat()
        },
        "auctionPeriod": {
            "startDate": (now).isoformat()
        },
    }
)

test_features_item_id = uuid.uuid4().hex
test_features = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_features_item_id,
        "title": "Потужність всмоктування",
        "title_en": "Air Intake",
        "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [{"value": 0.1, "title": "До 1000 Вт"}, {"value": 0.15, "title": "Більше 1000 Вт"}],
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": "Років на ринку",
        "title_en": "Years trading",
        "description": "Кількість років, які організація учасник працює на ринку",
        "enum": [
            {"value": 0.05, "title": "До 3 років"},
            {"value": 0.1, "title": "Більше 3 років, менше 5 років"},
            {"value": 0.15, "title": "Більше 5 років"},
        ],
    },
]

test_features_tender_data = test_tender_data.copy()
test_features_item = test_features_tender_data["items"][0].copy()
test_features_item["id"] = test_features_item_id
test_features_tender_data["items"] = [test_features_item]
test_features_tender_data["features"] = test_features

test_bids = [
    {
        "id": uuid.uuid4().hex,
        "date": get_now(),
        "tenderers": [test_organization],
        "value": {
            "amount": 469,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    },
    {
        "id": uuid.uuid4().hex,
        "date": get_now(),
        "tenderers": [test_organization],
        "value": {
            "amount": 479,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    },
]

test_parameters_bids = deepcopy(test_bids)
test_parameters_bids[0]["parameters"] = [
    {
        "code": i["code"],
        "value": 0.1
    }
    for i in test_features_tender_data["features"]
]
test_parameters_bids[1]["parameters"] = [
    {
        "code": i["code"],
        "value": 0.15
    }
    for i in test_features_tender_data["features"]
]

test_lots = [
    {
        "id": uuid.uuid4().hex,
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_data["value"],
        "minimalStep": test_tender_data["minimalStep"],
    },
    {
        "id": uuid.uuid4().hex,
        "title": "lot title 2",
        "description": "lot description 2",
        "value": test_tender_data["value"],
        "minimalStep": test_tender_data["minimalStep"],
    }
]

test_items_multilot = [
    deepcopy(test_item),
    deepcopy(test_item),
]
test_items_multilot[0]["relatedLot"] = test_lots[0]["id"]
test_items_multilot[1]["relatedLot"] = test_lots[1]["id"]

test_tender_data_multilot = deepcopy(test_tender_data)
test_tender_data_multilot["lots"] = test_lots
test_tender_data_multilot["items"] = test_items_multilot

test_bids_multilot = [
    {
        "id": uuid.uuid4().hex,
        "date": get_now().isoformat(),
        "tenderers": [test_organization],
        "lotValues": [
            {
                "relatedLot": test_lots[0]["id"],
                "date": get_now().isoformat(),
                "status": "active",
                "value": {
                    "amount": 469,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ],
    },
    {
        "id": uuid.uuid4().hex,
        "date": get_now().isoformat(),
        "tenderers": [test_organization],
        "lotValues": [
            {
                "relatedLot": test_lots[1]["id"],
                "date": get_now().isoformat(),
                "status": "active",
                "value": {
                    "amount": 479,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ],
    },
]


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

    async def __aexit__(self, *_):
        pass

    async def __aenter__(self):
        return self
