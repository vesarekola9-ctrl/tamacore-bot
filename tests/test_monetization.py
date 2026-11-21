"""Monetization economy invariants and generated configuration."""
import unittest

from tamacore.factory_v3_1.monetization import (
    COINS_PER_GEM, MAX_REWARDED_ADS_PER_DAY,
    exchange_gems_for_coins, monetization_manifest, rewarded_coins,
)


class MonetizationTests(unittest.TestCase):
    def test_exchange_is_one_way_and_cannot_overdraw(self):
        self.assertEqual(exchange_gems_for_coins(2, 5), (3, 2 * COINS_PER_GEM))
        for gems, balance in ((0, 5), (-1, 5), (6, 5), (True, 5)):
            with self.assertRaises(ValueError):
                exchange_gems_for_coins(gems, balance)

    def test_rewarded_ads_are_opt_in_verified_and_capped(self):
        self.assertEqual(rewarded_coins(0, verified_reward=False), 0)
        self.assertEqual(rewarded_coins(0, verified_reward=True), 40)
        self.assertEqual(rewarded_coins(MAX_REWARDED_ADS_PER_DAY, verified_reward=True), 0)

    def test_no_cashout_and_no_local_purchase_fulfillment(self):
        manifest = monetization_manifest()
        self.assertFalse(manifest["currency"]["cashOut"])
        self.assertFalse(manifest["currency"]["coinsToRealMoney"])
        self.assertEqual(manifest["purchaseFulfillment"], "trusted_backend_only")
        self.assertTrue(manifest["rewardedAds"]["optInOnly"])
        self.assertEqual(len({item["id"] for item in manifest["products"]}), len(manifest["products"]))


if __name__ == "__main__":
    unittest.main()
