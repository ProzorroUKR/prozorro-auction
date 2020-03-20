from prozorro_auction.chronograph.model import build_audit_document
import unittest


class AuditTestCase(unittest.TestCase):

    def test_build_audit_doc(self):
        auction = {
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
      label:
        en: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        ru: ТОВ "ТЕХНО-БУД-ЦЕНТР"
        uk: ТОВ "ТЕХНО-БУД-ЦЕНТР"
      time: '2019-08-08T15:55:24.790505+03:00'
    - amount: 1460500
      bidder: d9018f974341493e9d6b379295438499
      label:
        en: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        ru: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
        uk: ТОВАРИСТВО З ОБМЕЖЕНОЮ ВІДПОВІДАЛЬНІСТЮ "ГЛОБАЛ БІЛД ІНЖИНІРИНГ"
      time: '2019-08-07T16:22:32.545240+03:00'
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
