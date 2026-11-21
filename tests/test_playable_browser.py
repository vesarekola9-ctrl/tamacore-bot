"""Regression checks for the standalone TamaCore browser game export."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.playable_browser import write_playable_browser_game


class PlayableBrowserTests(unittest.TestCase):
    def build(self, pack):
        with tempfile.TemporaryDirectory() as directory:
            output = write_playable_browser_game(
                Path(directory), pack, [{"coinCount": 10}], {"upgrades": []}
            )
            return output.read_text(encoding="utf-8")

    def test_export_contains_html_canvas_and_embedded_config(self):
        html = self.build({"name": "TamaCore Test", "foods": [], "cosmetics": [], "pet": {}})
        self.assertIn('<canvas id="game"', html)
        self.assertIn('id="config" type="application/json"', html)
        self.assertNotIn("__GAME_CONFIG__", html)
        match = re.search(r'<script id="config" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1))["name"], "TamaCore Test")

    def test_collectible_boutique_has_visual_preview_and_catalog(self):
        html = self.build({"name": "TamaCore", "foods": [], "cosmetics": []})
        match = re.search(r'<script id="config" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        catalog = json.loads(match.group(1))["collectibles"]
        self.assertGreaterEqual(len(catalog), 20)
        for element_id in ("boutiquePreview", "boutiquePreviewOutfit",
                           "boutiquePreviewFurniture", "boutiquePreviewWallpaper",
                           "boutiquePreviewToy"):
            self.assertIn('id="' + element_id + '"', html)
        self.assertIn('boutiqueSave.owned', html)

    def test_boutique_items_are_rendered_in_live_game(self):
        html = self.build({"name": "TamaCore"})
        for category in ("outfit", "furniture", "wallpaper", "toy"):
            self.assertIn('boutiqueSelected("' + category + '")', html)
        self.assertIn("ctx.fillText(outfit.emoji", html)
        self.assertIn("ctx.fillText(boutiqueFurniture.emoji", html)
        self.assertIn("ctx.fillText(boutiqueToy.emoji", html)
        self.assertIn("state.coins-=item.coinPrice", html)

    def test_legacy_food_cost_is_normalized(self):
        html = self.build({"foods": [{"id": "apple", "cost": 7, "energy": 2}]})
        match = re.search(r'<script id="config" type="application/json">(.*?)</script>', html, re.S)
        food = json.loads(match.group(1))["foods"][0]
        self.assertEqual(food["price"], 7)
        self.assertEqual(food["energy"], 2)

    def test_config_cannot_close_script_tag(self):
        malicious = '</script><script>alert("unsafe")</script>'
        html = self.build({"name": malicious, "foods": []})
        self.assertNotIn(malicious, html)
        match = re.search(r'<script id="config" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1))["name"], malicious)


if __name__ == "__main__":
    unittest.main()
