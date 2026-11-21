"""Regression tests for cosmetic and furniture shop catalog."""
import unittest

from tamacore.factory_v3_1.collectibles_catalog import collectible_catalog


class CollectiblesCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_and_fair(self):
        catalog = collectible_catalog()
        items = catalog["items"]
        self.assertGreaterEqual(len(items), 20)
        self.assertEqual(len({item["id"] for item in items}), len(items))
        self.assertEqual({item["category"] for item in items},
                         {"outfit", "furniture", "wallpaper", "toy"})
        for item in items:
            self.assertGreater(item["coinPrice"], 0)
            self.assertFalse(item["premiumOnly"])
            self.assertIsNone(item["cashPrice"])
        self.assertTrue(catalog["rules"]["freeCoinsCanPurchaseAll"])
        self.assertFalse(catalog["rules"]["randomPaidRewards"])
        self.assertFalse(catalog["rules"]["realMoneyPurchasesImplemented"])


if __name__ == "__main__":
    unittest.main()
