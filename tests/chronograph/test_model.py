import unittest

from copy import deepcopy

from prozorro_auction.chronograph.model import build_audit_document

from tests.chronograph.base import (
    test_auction,
    test_auction_with_stages,
    test_auction_with_stages_meat,
    test_auction_with_stages_lcc,
    test_audit,
    test_audit_with_stages,
    test_audit_with_stages_meat,
    test_audit_with_stages_lcc,
    test_bids_meat,
    test_bids_lcc,
)


class AuditTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.auction = test_auction

    def test_build_audit_doc(self):
        name, content = build_audit_document(self.auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(content.decode(), test_audit)

    def test_build_audit_doc_with_stages(self):
        auction = deepcopy(self.auction)
        auction["features"] = False
        auction["stages"].extend(test_auction_with_stages)

        name, content = build_audit_document(auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(content.decode(), test_audit_with_stages)

    def test_build_audit_doc_with_stages_meat(self):
        auction = deepcopy(self.auction)
        auction["auction_type"] = "meat"
        auction["stages"].extend(test_auction_with_stages_meat)
        auction["bids"] = test_bids_meat

        name, content = build_audit_document(auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(content.decode(), test_audit_with_stages_meat)

    def test_build_audit_doc_with_stages_lcc(self):
        auction = deepcopy(self.auction)
        auction["auction_type"] = "lcc"
        auction["stages"].extend(test_auction_with_stages_lcc)
        auction["bids"] = test_bids_lcc

        name, content = build_audit_document(auction)
        self.assertEqual(name, "audit_123.yaml")
        self.assertEqual(content.decode(), test_audit_with_stages_lcc)
