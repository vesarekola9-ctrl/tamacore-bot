"""Regression tests for cosmetic and furniture shop catalog."""
import unittest

from tamacore.factory_v3_1.collectibles_catalog import collectible_catalog


class CollectiblesCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_and_fair(self):
        catalog = collectible_catalog()
        items = catalog["items"]
        self.assertGreaterEqual(len(items), 200)
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

    def test_theme_variants_reference_existing_base_items(self):
        items = {item["id"]: item for item in collectible_catalog()["items"]}
        themes = {"pastel", "royal", "winter", "garden"}
        for item in items.values():
            if "theme" in item:
                self.assertIn(item["theme"], themes)
                suffix = "_" + item["theme"]
                self.assertTrue(item["id"].endswith(suffix))
                base = items[item["id"][:-len(suffix)]]
                self.assertEqual(item["category"], base["category"])
                self.assertGreater(item["coinPrice"], base["coinPrice"])
        for item in items.values():
            if "theme" not in item and item["category"] != "wallpaper":
                for theme in themes:
                    self.assertIn(item["id"] + "_" + theme, items)


if __name__ == "__main__":
    unittest.main()
