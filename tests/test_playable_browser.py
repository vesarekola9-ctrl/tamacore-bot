"""Regression checks for the standalone TamaCore browser game export."""
import json
import re
import shutil
import subprocess
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

    @unittest.skipUnless(shutil.which("node"), "Node.js required for browser logic checks")
    def test_boutique_save_normalization_and_javascript_syntax(self):
        html = self.build({"name": "TamaCore"})
        scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
        self.assertTrue(scripts)
        js = "\n".join(scripts)
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "game.js"
            script.write_text(js, encoding="utf-8")
            subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, text=True)
        start = js.index("function normalizeBoutique(")
        end = js.index("let boutiqueSave=", start)
        logic = js[start:end]
        config = re.search(r'<script id="config" type="application/json">(.*?)</script>', html, re.S)
        catalog = json.loads(config.group(1))["collectibles"]
        furniture = [item["id"] for item in catalog if item["category"] == "furniture"][:4]
        fixture = {"owned": {**dict.fromkeys(furniture, True), "invalid": True},
                   "equipped": {"furniture": furniture[0], "toy": furniture[0]},
                   "displayed": furniture + furniture,
                   "positions": {furniture[0]: {"x": -500, "y": 999}},
                   "layouts": {"1": {"equipped": {"furniture": furniture[0]}, "roomTheme": "loft", "roomRug": "woven", "roomClock": True}},
                   "wishlist": [furniture[0], "invalid", "wallpaper_sky", "wallpaper_sky"],
                   "roomTheme": "observatory", "roomLighting": "invalid",
                   "roomRug": "stars", "roomPlant": "fern", "roomArt": "moon",
                   "roomWindow": "round", "roomClock": True,
                   "roomFloor": "oak", "roomCurtain": "blue", "roomLamp": "gold",
                   "extraOutfits": [furniture[0], "invalid"],
                   "roomAwards": {"firstItem": True, "invalid": True}}
        code = "const cfg=" + json.dumps({"collectibles": catalog}) + ";\n" + logic
        code += "\nconsole.log(JSON.stringify(normalizeBoutique(" + json.dumps(fixture) + ")));"
        result = json.loads(subprocess.check_output(["node", "-e", code], text=True))
        self.assertEqual(result["wishlist"], ["wallpaper_sky"])
        self.assertEqual(result["roomTheme"], "observatory")
        self.assertEqual(result["roomLighting"], "auto")
        self.assertEqual(result["roomRug"], "stars")
        self.assertEqual(result["roomPlant"], "fern")
        self.assertEqual(result["roomArt"], "moon")
        self.assertEqual(result["roomWindow"], "round")
        self.assertTrue(result["roomClock"])
        self.assertEqual(result["roomFloor"], "oak")
        self.assertEqual(result["roomCurtain"], "blue")
        self.assertEqual(result["roomLamp"], "gold")
        self.assertEqual(result["extraOutfits"], [])
        self.assertEqual(result["roomAwards"], {"firstItem": True})
        self.assertNotIn("invalid", result["owned"])
        self.assertNotIn("toy", result["equipped"])
        self.assertEqual(len(result["displayed"]), 3)
        self.assertEqual(result["positions"][furniture[0]], {"x": 130, "y": 495})
        self.assertEqual(result["layouts"]["1"]["equipped"]["furniture"], furniture[0])
        self.assertEqual(result["layouts"]["1"]["roomTheme"], "loft")
        self.assertEqual(result["layouts"]["1"]["roomRug"], "woven")
        self.assertTrue(result["layouts"]["1"]["roomClock"])

    def test_boutique_discovery_controls(self):
        html = self.build({"name": "TamaCore"})
        for element in ("boutiqueSearch", "boutiqueTheme", "boutiqueOwnedOnly",
                        "boutiqueWishlist", "boutiqueSort"):
            self.assertIn('id="' + element + '"', html)
        self.assertIn("Try preview", html)
        self.assertIn("more coins needed", html)

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
