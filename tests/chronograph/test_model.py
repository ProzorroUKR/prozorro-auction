from copy import deepcopy
import datetime

from prozorro_auction.chronograph.model import build_audit_document
import unittest


class AuditTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.auction = {
            "_id": "123",
            "tender_id": "123",
            "tenderID": "UA-123",
            "lot_id": None,
            "start_at": "2019-08-12T14:53:52+03:00",
            "bids": [
                {
                    "id": "a",
                    "hash": "1",
                    "date":  "2019-08-12T14:53:52+03:00",
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

    def test_build_audit_doc(self):

        name, content = build_audit_document(self.auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(
            content.decode(),
            """id: '123'
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
        )

    def test_build_audit_doc_with_stages(self):
        auction = deepcopy(self.auction)
        auction["features"] = False
        auction["stages"].extend([
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
            {'start': datetime.datetime(2020, 7, 8, 10, 57, 1, 173000), 'type': 'pause'},
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
            {'start': '2019-08-12T15:02:52+03:00', 'type': 'announcement'}]
        )

        name, content = build_audit_document(auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(
            content.decode(),
            """id: '123'
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
        )


