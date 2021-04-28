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
    "bids": test_bids,
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

test_item_features_id = uuid.uuid4().hex
test_features = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_item_features_id,
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

test_tender_data_features = deepcopy(test_tender_data)
test_item_features = deepcopy(test_item)
test_item_features["id"] = test_item_features_id
test_tender_data_features["items"] = [test_item_features]
test_tender_data_features["features"] = test_features

test_bids_parameters = deepcopy(test_bids)
test_bids_parameters[0]["parameters"] = [
    {
        "code": i["code"],
        "value": 0.1
    }
    for i in test_tender_data_features["features"]
]
test_bids_parameters[1]["parameters"] = [
    {
        "code": i["code"],
        "value": 0.15
    }
    for i in test_tender_data_features["features"]
]
test_tender_data_features["bids"] = test_bids_parameters

test_lots = [
    {
        "id": uuid.uuid4().hex,
        "status": "active",
        "title": "lot title",
        "description": "lot description",
        "value": {
            "amount": test_tender_data["value"]["amount"] + 1,
            "currency": test_tender_data["value"]["currency"]
        },
        "minimalStep": {
            "amount": test_tender_data["minimalStep"]["amount"] + 1,
            "currency": test_tender_data["minimalStep"]["currency"]
        },
    },
    {
        "id": uuid.uuid4().hex,
        "status": "active",
        "title": "lot title 2",
        "description": "lot description 2",
        "value": {
            "amount": test_tender_data["value"]["amount"] + 2,
            "currency": test_tender_data["value"]["currency"]
        },
        "minimalStep": {
            "amount": test_tender_data["minimalStep"]["amount"] + 2,
            "currency": test_tender_data["minimalStep"]["currency"]
        },
    }
]

for test_lot in test_lots:
    test_lot.update(
        {
            "auctionPeriod": {
                "startDate": (now).isoformat()
            },
        }
    )

test_items_multilot = [
    deepcopy(test_item),
    deepcopy(test_item),
]
test_items_multilot[0]["relatedLot"] = test_lots[0]["id"]
test_items_multilot[1]["relatedLot"] = test_lots[1]["id"]

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
            },
            {
                "relatedLot": test_lots[0]["id"],
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

test_tender_data_multilot = deepcopy(test_tender_data)
test_tender_data_multilot["lots"] = test_lots
test_tender_data_multilot["items"] = test_items_multilot
test_tender_data_multilot["bids"] = test_bids_multilot


test_criteria_lcc = [
    {
        "title": "Витрати, пов’язані з користуванням",
        "description": "Для розрахунку витрат, пов’язаних з користуванням, замовник визначає у тендерній документації одиницю виміру життєвого циклу та зазначає вартість споживання електроенергії та інших ресурсів (наприклад поточні ціни на бензин або дані від Національної комісії, що здійснює державне регулювання у сферах енергетики та комунальних послуг щодо вартості електроенергії, тощо)",
        "source": "tenderer",
        "classification": {
            "scheme": "LCC",
            "id": "CRITERION.OTHER.LIFE_CYCLE_COST.COST_OF_USE"
        },
        "relatesTo": "tender",
        "legislation": [
            {
                "version": "2020-09-28",
                "identifier": {
                    "id": "1894",
                    "legalName": "Наказ Мінекономіки \"Про затвердження Примірної методики визначення вартості життєвого циклу\"",
                    "uri": "https://me.gov.ua/legislativeacts/Detail?lang=uk-UA&id=32140d03-d5eb-4988-8790-6d60d1c84a93"
                },
                "type": "NATIONAL_LEGISLATION",
                "article": "2.6"
            }
        ],
        "requirementGroups": [
            {
                "description": "Учасником процедури закупівлі надається інформація щодо",
                "requirements": [
                    {
                        "id": uuid.uuid4().hex,
                        "title": "Характеристик предмета закупівлі в частині споживання ресурсу під час користування предметом закупівлі протягом визначеного замовником періоду оцінки життєвого циклу",
                        "dataType": "number"
                    }
                ]
            }
        ]
    },
    {
        "title": "Витрати, пов’язані з обслуговуванням",
        "description": "Для розрахунку витрат, пов’язаних з обслуговуванням, замовник у тендерній документації серед переліку інформації, що надає учасник, може запитати інформацію щодо вартості обслуговування, ремонту та/або заміни складових предмета закупівлі за одиницю виміру життєвого циклу, а також документи від виробника про характеристики предмета закупівлі",
        "source": "tenderer",
        "classification": {
            "scheme": "LCC",
            "id": "CRITERION.OTHER.LIFE_CYCLE_COST.MAINTENANCE_COST"
        },
        "relatesTo": "tender",
        "legislation": [
            {
                "version": "2020-09-28",
                "identifier": {
                    "id": "1894",
                    "legalName": "Наказ Мінекономіки \"Про затвердження Примірної методики визначення вартості життєвого циклу\"",
                    "uri": "https://me.gov.ua/legislativeacts/Detail?lang=uk-UA&id=32140d03-d5eb-4988-8790-6d60d1c84a93"
                },
                "type": "NATIONAL_LEGISLATION",
                "article": "2.7"
            }
        ],
        "requirementGroups": [
            {
                "description": "Учасником процедури закупівлі надається інформація щодо",
                "requirements": [
                    {
                        "id": uuid.uuid4().hex,
                        "title": "Під час розрахунку вартості витрат, пов’язаних з обслуговуванням предмета закупівлі, застосовуються показники вартості обслуговування за одиницю виміру життєвого циклу або вартості заміни складових предмета закупівлі за одиницю виміру життєвого циклу, надані учасниками процедури закупівлі у тендерній пропозиції",
                        "dataType": "number"
                    }
                ]
            }
        ]
    },
    {
        "title": "Витрати, пов’язані з завершенням користування",
        "description": "Для розрахунку витрат, пов’язаних з завершенням користування, замовник у тендерній документації серед переліку інформації, що надає учасник процедури закупівлі, може запитати інформацію щодо вартості демонтажу, утилізації, переробки та інших витрат",
        "source": "tenderer",
        "classification": {
            "scheme": "LCC",
            "id": "CRITERION.OTHER.LIFE_CYCLE_COST.END_OF_LIFE_COST"
        },
        "relatesTo": "tender",
        "legislation": [
            {
                "version": "2020-09-28",
                "identifier": {
                    "id": "1894",
                    "legalName": "Наказ Мінекономіки \"Про затвердження Примірної методики визначення вартості життєвого циклу\"",
                    "uri": "https://me.gov.ua/legislativeacts/Detail?lang=uk-UA&id=32140d03-d5eb-4988-8790-6d60d1c84a93"
                },
                "type": "NATIONAL_LEGISLATION",
                "article": "2.8"
            }
        ],
        "requirementGroups": [
            {
                "description": "Учасником процедури закупівлі надається інформація щодо",
                "requirements": [
                    {
                        "id": uuid.uuid4().hex,
                        "title": "??",
                        "dataType": "number"
                    }
                ]
            }
        ]
    },
    {
        "title": "Витрати, пов’язані з захистом навколишнього середовища",
        "description": "Замовник додатково для розрахунку вартості життєвого циклу може використовувати параметри витрат, пов’язаних з захистом навколишнього середовища (вартість екологічних витрат)",
        "source": "tenderer",
        "classification": {
            "scheme": "LCC",
            "id": "CRITERION.OTHER.LIFE_CYCLE_COST.ECOLOGICAL_COST"
        },
        "relatesTo": "tender",
        "legislation": [
            {
                "version": "2020-09-28",
                "identifier": {
                    "id": "1894",
                    "legalName": "Наказ Мінекономіки \"Про затвердження Примірної методики визначення вартості життєвого циклу\"",
                    "uri": "https://me.gov.ua/legislativeacts/Detail?lang=uk-UA&id=32140d03-d5eb-4988-8790-6d60d1c84a93"
                },
                "type": "NATIONAL_LEGISLATION",
                "article": "2.9"
            }
        ],
        "requirementGroups": [
            {
                "description": "Учасником процедури закупівлі надається інформація щодо",
                "requirements": [
                    {
                        "id": uuid.uuid4().hex,
                        "title": "Для розрахунку вартості витрат, пов’язаних з захистом навколишнього середовища (вартість екологічних витрат) у формулі зазначаються сума податків та зборів, які нараховуються за викиди в атмосферне повітря окремих забруднюючих речовин, коефіцієнт викидів CO2 під час користування предметом закупівлі тощо",
                        "dataType": "number"
                    }
                ]
            }
        ]
    }
]

test_resposes_lcc = [
    {
        "value": "10",
        "description": "response to CRITERION.OTHER.LIFE_CYCLE_COST.COST_OF_USE",
        "evidences": [
            {
                "relatedDocument": {
                    "id": uuid.uuid4().hex,
                    "title": "name.doc"
                },
                "type": "document",
                "id": uuid.uuid4().hex,
                "title": "Requirement response"
            }
        ],
        "id": uuid.uuid4().hex,
        "requirement": {
            "id": test_criteria_lcc[0]["requirementGroups"][0]["requirements"][0]["id"],
            "title": "Учасник процедури закупівлі не є особою, до якої застосовано санкцію у вигляді заборони на здійснення у неї публічних закупівель товарів, робіт і послуг згідно із Законом України \"Про санкції\""
        },
        "title": "Requirement response"
    },
    {
        "value": "20",
        "description": "response to CRITERION.OTHER.LIFE_CYCLE_COST.MAINTENANCE_COST",
        "evidences": [
            {
                "relatedDocument": {
                    "id": uuid.uuid4().hex,
                    "title": "name.doc"
                },
                "type": "document",
                "id": uuid.uuid4().hex,
                "title": "Requirement response"
            }
        ],
        "id": uuid.uuid4().hex,
        "requirement": {
            "id": test_criteria_lcc[1]["requirementGroups"][0]["requirements"][0]["id"],
            "title": "Учасник процедури закупівлі не є особою, до якої застосовано санкцію у вигляді заборони на здійснення у неї публічних закупівель товарів, робіт і послуг згідно із Законом України \"Про санкції\""
        },
        "title": "Requirement response"
    },
    {
        "value": "30",
        "description": "response to CRITERION.OTHER.LIFE_CYCLE_COST.END_OF_LIFE_COST",
        "evidences": [
            {
                "relatedDocument": {
                    "id": uuid.uuid4().hex,
                    "title": "name.doc"
                },
                "type": "document",
                "id": uuid.uuid4().hex,
                "title": "Requirement response"
            }
        ],
        "id": uuid.uuid4().hex,
        "requirement": {
            "id": test_criteria_lcc[2]["requirementGroups"][0]["requirements"][0]["id"],
            "title": "Учасник процедури закупівлі не є особою, до якої застосовано санкцію у вигляді заборони на здійснення у неї публічних закупівель товарів, робіт і послуг згідно із Законом України \"Про санкції\""
        },
        "title": "Requirement response"
    },
    {
        "value": "40",
        "description": "response to CRITERION.OTHER.LIFE_CYCLE_COST.ECOLOGICAL_COST",
        "evidences": [
            {
                "relatedDocument": {
                    "id": uuid.uuid4().hex,
                    "title": "name.doc"
                },
                "type": "document",
                "id": uuid.uuid4().hex,
                "title": "Requirement response"
            }
        ],
        "id": uuid.uuid4().hex,
        "requirement": {
            "id": test_criteria_lcc[3]["requirementGroups"][0]["requirements"][0]["id"],
            "title": "Учасник процедури закупівлі не є особою, до якої застосовано санкцію у вигляді заборони на здійснення у неї публічних закупівель товарів, робіт і послуг згідно із Законом України \"Про санкції\""
        },
        "title": "Requirement response"
    },
]

test_tender_data_lcc = deepcopy(test_tender_data)
test_tender_data_lcc["awardCriteria"] = "lifeCycleCost"
test_tender_data_lcc["criteria"] = test_criteria_lcc

test_bids_lcc = deepcopy(test_bids)
test_bids_lcc[0]["requirementResponses"] = test_resposes_lcc
test_bids_lcc[1]["requirementResponses"] = test_resposes_lcc
test_tender_data_lcc["bids"] = test_bids_lcc

NBU_DISCOUNT_RATE = 0.22

test_tender_data_esco = deepcopy(test_tender_data)
test_tender_data_esco["procurementMethodType"] = "esco"
test_tender_data_esco["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_data_esco["minimalStepPercentage"] = 0.02712
test_tender_data_esco["fundingKind"] = "other"
test_tender_data_esco["yearlyPaymentsPercentageRange"] = 0.80000

del test_tender_data_esco["value"]
del test_tender_data_esco["minimalStep"]

test_bids_esco = deepcopy(test_bids)
for bid in test_bids_esco:
    bid["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [100] * 21,
        "contractDuration": {"years": 10, "days": 10},
    }

test_tender_data_esco["bids"] = test_bids_esco

test_tender_data_esco_features = deepcopy(test_tender_data_features)
test_tender_data_esco_features["procurementMethodType"] = "esco"
test_tender_data_esco_features["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_data_esco_features["minimalStepPercentage"] = 0.027
test_tender_data_esco_features["fundingKind"] = "other"
test_tender_data_esco_features["yearlyPaymentsPercentageRange"] = 0.80000

del test_tender_data_esco_features["value"]
del test_tender_data_esco_features["minimalStep"]

test_tender_data_esco_multilot = deepcopy(test_tender_data_multilot)
test_tender_data_esco_multilot["procurementMethodType"] = "esco"
test_tender_data_esco_multilot["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_data_esco_multilot["minimalStepPercentage"] = 0.02712
test_tender_data_esco_multilot["fundingKind"] = "other"
test_tender_data_esco_multilot["yearlyPaymentsPercentageRange"] = 0.80000

test_lots_esco = deepcopy(test_lots)
for lot in test_lots_esco:
    del lot["value"]
    del lot["minimalStep"]
    lot["minimalStepPercentage"] = 0.02514
    lot["fundingKind"] = "other"
    lot["yearlyPaymentsPercentageRange"] = 0.80000

test_tender_data_esco_multilot["lots"] = test_lots_esco


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

    async def __aexit__(self, *_):
        pass

    async def __aenter__(self):
        return self
