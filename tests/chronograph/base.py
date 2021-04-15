from datetime import datetime

test_auction = {
    "_id": "123",
    "tender_id": "123",
    "tenderID": "UA-123",
    "lot_id": None,
    "start_at": "2019-08-12T14:53:52+03:00",
    "auction_type": "default",
    "bids": [
        {
            "id": "a",
            "hash": "1",
            "date": "2019-08-12T14:53:52+03:00",
            "value": {
                "amount": 200
            }
        },
        {
            "id": "b",
            "hash": "22",
            "date": "2019-08-12T14:53:52+03:00",
            "value": {
                "amount": 300
            }
        },
    ],
    "initial_bids": [
        {
            "amount": 1439783,
            "bidder_id": "c1aacdd8b6574e668824fca035b5f65f",
            "time": "2019-08-08T15:55:24.790505+03:00",
            "label": {
                "ru": "ТОВ \"ТЕХНО-БУД-ЦЕНТР\"",
                "en": "ТОВ \"ТЕХНО-БУД-ЦЕНТР\"",
                "uk": "ТОВ \"ТЕХНО-БУД-ЦЕНТР\""
            }
        },
        {
            "amount": 1460500,
            "bidder_id": "d9018f974341493e9d6b379295438499",
            "time": "2019-08-07T16:22:32.545240+03:00",
            "label": {
                "ru": "ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ \"ГЛОБАЛ БІЛД ІНЖИНІРИНГ\"",
                "en": "ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ \"ГЛОБАЛ БІЛД ІНЖИНІРИНГ\"",
                "uk": "ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ \"ГЛОБАЛ БІЛД ІНЖИНІРИНГ\""
            }
        }
    ],
    "stages": [
        {
            "start": "2019-08-12T14:53:52+03:00",
            "type": "pause",
            "stage": "pause"
        },
    ]
}

test_auction_with_stages = [
    {
        'amount': 200,
        'bidder_id': 'a',
        'start': '2019-08-12T14:54:52+03:00',
        'time': '2019-08-12T14:54:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:55:00+03:00',
    },
    {
        'amount': 300,
        'bidder_id': 'b',
        'start': '2019-08-12T14:55:52+03:00',
        'time': '2019-08-12T14:55:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:56:00+03:00',
    },
    {'start': '2019-08-12T14:56:52+03:00', 'type': 'pause'},
    {
        'amount': 200,
        'bidder_id': 'a',
        'start': '2019-08-12T14:57:52+03:00',
        'time': '2019-08-12T14:57:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:58:00+03:00',
    },
    {
        'amount': 300,
        'bidder_id': 'b',
        'start': '2019-08-12T14:58:52+03:00',
        'time': '2019-08-12T14:58:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:59:00+03:00',
    },
    {'start': datetime(2020, 7, 8, 10, 57, 1, 173000), 'type': 'pause'},
    {
        'amount': 200,
        'bidder_id': 'a',
        'start': '2019-08-12T14:59:52+03:00',
        'time': '2019-08-12T14:59:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:00:00+03:00',
    },
    {
        'amount': 300,
        'bidder_id': 'b',
        'start': '2019-08-12T15:00:52+03:00',
        'time': '2019-08-12T15:00:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:01:00+03:00',
    },
    {'start': '2019-08-12T15:01:52+03:00', 'type': 'pre_announcement'},
    {'start': '2019-08-12T15:02:52+03:00', 'type': 'announcement'}
]

test_auction_with_stages_meat = [
    {
        'amount': 200,
        'amount_features': '400',
        'coeficient': '2',
        'bidder_id': 'a',
        'start': '2019-08-12T14:54:52+03:00',
        'time': '2019-08-12T14:54:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:55:00+03:00',
    },
    {
        'amount': 300,
        'amount_features': '600',
        'coeficient': '2',
        'bidder_id': 'b',
        'start': '2019-08-12T14:55:52+03:00',
        'time': '2019-08-12T14:55:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:56:00+03:00',
    },
    {'start': '2019-08-12T14:56:52+03:00', 'type': 'pause'},
    {
        'amount': 200,
        'amount_features': '400',
        'coeficient': '2',
        'bidder_id': 'a',
        'start': '2019-08-12T14:57:52+03:00',
        'time': '2019-08-12T14:57:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:58:00+03:00',
    },
    {
        'amount': 300,
        'amount_features': '600',
        'coeficient': '2',
        'bidder_id': 'b',
        'start': '2019-08-12T14:58:52+03:00',
        'time': '2019-08-12T14:58:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:59:00+03:00',
    },
    {'start': datetime(2020, 7, 8, 10, 57, 1, 173000), 'type': 'pause'},
    {
        'amount': 200,
        'amount_features': '400',
        'coeficient': '2',
        'bidder_id': 'a',
        'start': '2019-08-12T14:59:52+03:00',
        'time': '2019-08-12T14:59:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:00:00+03:00',
    },
    {
        'amount': 300,
        'amount_features': '600',
        'coeficient': '2',
        'bidder_id': 'b',
        'start': '2019-08-12T15:00:52+03:00',
        'time': '2019-08-12T15:00:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:01:00+03:00',
    },
    {'start': '2019-08-12T15:01:52+03:00', 'type': 'pre_announcement'},
    {'start': '2019-08-12T15:02:52+03:00', 'type': 'announcement'}
]

test_auction_with_stages_lcc = [
    {
        'amount': 200,
        'amount_weighted': 300,
        'non_price_cost': 100,
        'bidder_id': 'a',
        'start': '2019-08-12T14:54:52+03:00',
        'time': '2019-08-12T14:54:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:55:00+03:00',
    },
    {
        'amount': 300,
        'amount_weighted': 400,
        'non_price_cost': 100,
        'bidder_id': 'b',
        'start': '2019-08-12T14:55:52+03:00',
        'time': '2019-08-12T14:55:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:56:00+03:00',
    },
    {'start': '2019-08-12T14:56:52+03:00', 'type': 'pause'},
    {
        'amount': 200,
        'amount_weighted': 300,
        'non_price_cost': 100,
        'bidder_id': 'a',
        'start': '2019-08-12T14:57:52+03:00',
        'time': '2019-08-12T14:57:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:58:00+03:00',
    },
    {
        'amount': 300,
        'amount_weighted': 400,
        'non_price_cost': 100,
        'bidder_id': 'b',
        'start': '2019-08-12T14:58:52+03:00',
        'time': '2019-08-12T14:58:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T14:59:00+03:00',
    },
    {'start': datetime(2020, 7, 8, 10, 57, 1, 173000), 'type': 'pause'},
    {
        'amount': 200,
        'amount_weighted': 300,
        'non_price_cost': 100,
        'bidder_id': 'a',
        'start': '2019-08-12T14:59:52+03:00',
        'time': '2019-08-12T14:59:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:00:00+03:00',
    },
    {
        'amount': 300,
        'amount_weighted': 400,
        'non_price_cost': 100,
        'bidder_id': 'b',
        'start': '2019-08-12T15:00:52+03:00',
        'time': '2019-08-12T15:00:00+03:00',
        'type': 'bids',
        'publish_time': '2019-08-12T15:01:00+03:00',
    },
    {'start': '2019-08-12T15:01:52+03:00', 'type': 'pre_announcement'},
    {'start': '2019-08-12T15:02:52+03:00', 'type': 'announcement'}
]

test_bids_meat = [
    {
        "id": "a",
        "hash": "1",
        "date": "2019-08-12T14:53:52+03:00",
        "value": {
            "amount": 200
        },
        "amount_features": "400",
        "coeficient": "2"
    },
    {
        "id": "b",
        "hash": "22",
        "date": "2019-08-12T14:53:52+03:00",
        "value": {
            "amount": 300
        },
        "amount_features": "600",
        "coeficient": "2"
    }
]

test_bids_lcc = [
    {
        "id": "a",
        "hash": "1",
        "date": "2019-08-12T14:53:52+03:00",
        "value": {
            "amount": 200
        },
        "amount_weighted": 300,
        "non_price_cost": 100,
    },
    {
        "id": "b",
        "hash": "22",
        "date": "2019-08-12T14:53:52+03:00",
        "value": {
            "amount": 300
        },
        "amount_weighted": 400,
        "non_price_cost": 100,
    }
]

test_audit = """id: '123'
tenderId: UA-123
tender_id: '123'
timeline:
  auction_start:
    initial_bids:
    - amount: 1439783
      bidder: c1aacdd8b6574e668824fca035b5f65f
      date: '2019-08-08T15:55:24.790505+03:00'
      label:
        en: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        ru: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        uk: ТОВ "ТЕХНО-БУД-ЦЕНТР"
    - amount: 1460500
      bidder: d9018f974341493e9d6b379295438499
      date: '2019-08-07T16:22:32.545240+03:00'
      label:
        en: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        ru: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        uk: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
    time: '2019-08-12T14:53:52+03:00'
  results:
    bids:
    - amount: 200
      bidder: a
      time: '2019-08-12T14:53:52+03:00'
    - amount: 300
      bidder: b
      time: '2019-08-12T14:53:52+03:00'
    time: '2019-08-12T14:53:52+03:00'
"""

test_audit_with_stages = """id: '123'
tenderId: UA-123
tender_id: '123'
timeline:
  auction_start:
    initial_bids:
    - amount: 1439783
      bidder: c1aacdd8b6574e668824fca035b5f65f
      date: '2019-08-08T15:55:24.790505+03:00'
      label:
        en: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        ru: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        uk: ТОВ "ТЕХНО-БУД-ЦЕНТР"
    - amount: 1460500
      bidder: d9018f974341493e9d6b379295438499
      date: '2019-08-07T16:22:32.545240+03:00'
      label:
        en: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        ru: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        uk: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
    time: '2019-08-12T14:53:52+03:00'
  results:
    bids:
    - amount: 200
      bidder: a
      time: '2019-08-12T14:53:52+03:00'
    - amount: 300
      bidder: b
      time: '2019-08-12T14:53:52+03:00'
    time: '2019-08-12T15:02:52+03:00'
  round_1:
    turn_1:
      amount: 200
      bidder: a
      time: '2019-08-12T14:55:00+03:00'
    turn_2:
      amount: 300
      bidder: b
      time: '2019-08-12T14:56:00+03:00'
  round_2:
    turn_1:
      amount: 200
      bidder: a
      time: '2019-08-12T14:58:00+03:00'
    turn_2:
      amount: 300
      bidder: b
      time: '2019-08-12T14:59:00+03:00'
  round_3:
    turn_1:
      amount: 200
      bidder: a
      time: '2019-08-12T15:00:00+03:00'
    turn_2:
      amount: 300
      bidder: b
      time: '2019-08-12T15:01:00+03:00'
"""

test_audit_with_stages_meat = """id: '123'
tenderId: UA-123
tender_id: '123'
timeline:
  auction_start:
    initial_bids:
    - amount: 1439783
      bidder: c1aacdd8b6574e668824fca035b5f65f
      date: '2019-08-08T15:55:24.790505+03:00'
      label:
        en: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        ru: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        uk: ТОВ "ТЕХНО-БУД-ЦЕНТР"
    - amount: 1460500
      bidder: d9018f974341493e9d6b379295438499
      date: '2019-08-07T16:22:32.545240+03:00'
      label:
        en: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        ru: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        uk: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
    time: '2019-08-12T14:53:52+03:00'
  results:
    bids:
    - amount: 200
      amount_features: '400'
      bidder: a
      coeficient: '2'
      time: '2019-08-12T14:53:52+03:00'
    - amount: 300
      amount_features: '600'
      bidder: b
      coeficient: '2'
      time: '2019-08-12T14:53:52+03:00'
    time: '2019-08-12T15:02:52+03:00'
  round_1:
    turn_1:
      amount: 200
      amount_features: '400'
      bidder: a
      coeficient: '2'
      time: '2019-08-12T14:55:00+03:00'
    turn_2:
      amount: 300
      amount_features: '600'
      bidder: b
      coeficient: '2'
      time: '2019-08-12T14:56:00+03:00'
  round_2:
    turn_1:
      amount: 200
      amount_features: '400'
      bidder: a
      coeficient: '2'
      time: '2019-08-12T14:58:00+03:00'
    turn_2:
      amount: 300
      amount_features: '600'
      bidder: b
      coeficient: '2'
      time: '2019-08-12T14:59:00+03:00'
  round_3:
    turn_1:
      amount: 200
      amount_features: '400'
      bidder: a
      coeficient: '2'
      time: '2019-08-12T15:00:00+03:00'
    turn_2:
      amount: 300
      amount_features: '600'
      bidder: b
      coeficient: '2'
      time: '2019-08-12T15:01:00+03:00'
"""

test_audit_with_stages_lcc = """id: '123'
tenderId: UA-123
tender_id: '123'
timeline:
  auction_start:
    initial_bids:
    - amount: 1439783
      bidder: c1aacdd8b6574e668824fca035b5f65f
      date: '2019-08-08T15:55:24.790505+03:00'
      label:
        en: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        ru: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        uk: ТОВ "ТЕХНО-БУД-ЦЕНТР"
    - amount: 1460500
      bidder: d9018f974341493e9d6b379295438499
      date: '2019-08-07T16:22:32.545240+03:00'
      label:
        en: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        ru: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        uk: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
    time: '2019-08-12T14:53:52+03:00'
  results:
    bids:
    - amount: 200
      amount_weighted: 300
      bidder: a
      non_price_cost: 100
      time: '2019-08-12T14:53:52+03:00'
    - amount: 300
      amount_weighted: 400
      bidder: b
      non_price_cost: 100
      time: '2019-08-12T14:53:52+03:00'
    time: '2019-08-12T15:02:52+03:00'
  round_1:
    turn_1:
      amount: 200
      amount_weighted: 300
      bidder: a
      non_price_cost: 100
      time: '2019-08-12T14:55:00+03:00'
    turn_2:
      amount: 300
      amount_weighted: 400
      bidder: b
      non_price_cost: 100
      time: '2019-08-12T14:56:00+03:00'
  round_2:
    turn_1:
      amount: 200
      amount_weighted: 300
      bidder: a
      non_price_cost: 100
      time: '2019-08-12T14:58:00+03:00'
    turn_2:
      amount: 300
      amount_weighted: 400
      bidder: b
      non_price_cost: 100
      time: '2019-08-12T14:59:00+03:00'
  round_3:
    turn_1:
      amount: 200
      amount_weighted: 300
      bidder: a
      non_price_cost: 100
      time: '2019-08-12T15:00:00+03:00'
    turn_2:
      amount: 300
      amount_weighted: 400
      bidder: b
      non_price_cost: 100
      time: '2019-08-12T15:01:00+03:00'
"""
