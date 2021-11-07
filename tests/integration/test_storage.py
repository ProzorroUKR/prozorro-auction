from prozorro_auction.storage import get_mongodb_collection
from tests.integration.base import BaseTestCase
from decimal import Decimal


class TestProfileActions(BaseTestCase):

    async def tearDownAsync(self):
        await get_mongodb_collection().delete_many({})

    async def test_types(self):

        collection = get_mongodb_collection()
        await collection.insert_one({
            "_id": 1,
            "set": {"a", "b", "c"},
            "decimal": Decimal("0.3"),
            "long": 9223372036854775807,
        })

        result = await collection.find_one({})
        self.assertIsInstance(result["set"], list)
        self.assertEqual(set(result["set"]), {"a", "b", "c"})

        self.assertIsInstance(result["decimal"], Decimal)
        self.assertEqual(result["decimal"],  Decimal("0.3"))

        self.assertIsInstance(result["long"], int)
        self.assertEqual(result["long"],  9223372036854775807)

