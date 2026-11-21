"""Smoke-test the real AI pack generation pipeline."""
import random
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.ai_full_pack_generator import generate_ai_full_pack
from tamacore.factory_v3_1.pack_inspector import inspect_pack
from tamacore.utils import read_json


class FullPackSmokeTests(unittest.TestCase):
    def test_generated_pack_is_complete_and_valid(self):
        random.seed(20261121)
        with tempfile.TemporaryDirectory() as temp:
            pack_dir = Path(temp) / "generated_pack"
            result = generate_ai_full_pack(
                pack_dir, shop_count=4, foods_count=4, cosmetics_count=4
            )
            self.assertEqual(inspect_pack(pack_dir), [])
            pack = read_json(pack_dir / "pack.json")
            self.assertEqual(result["shopUpgrades"], 4)
            self.assertEqual(result["foodCount"], 4)
            self.assertEqual(result["cosmeticCount"], 4)
            self.assertEqual(len(pack["shop"]["upgrades"]), 4)
            self.assertTrue((pack_dir / "assets" / "player").is_dir())
            self.assertTrue((pack_dir / "assets" / "background").is_dir())


if __name__ == "__main__":
    unittest.main()
