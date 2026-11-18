"""Regression tests for the v3.1 scene patcher.

Run with: PYTHONPATH=src python -m unittest discover -s tests
"""
import unittest
from types import SimpleNamespace

from tamacore.factory_v3_1.patch_rules import apply_v3_1_rules


def cfg():
    ns = SimpleNamespace
    return ns(
        display=ns(virtualWidth=720, virtualHeight=1280),
        levels=ns(count=3, coinBase=5, enemyBase=2),
        coinSpawn=ns(objectName="Coin"),
        enemySpawn=ns(objectName="Enemy"),
        camera=ns(followObject="Player"),
        ui=ns(
            hud=ns(objectName="HUD", marginX=24, marginY=24),
            joystick=ns(objectName="TouchJoystick", marginX=36, marginY=36),
        ),
    )


class ScenePatchTests(unittest.TestCase):
    def setUp(self):
        self.project = {"variables": []}
        self.scene = {"objects": [], "instances": [], "layers": []}
        apply_v3_1_rules(self.project, self.scene, cfg())

    def test_required_hud_and_joystick_objects_have_instances(self):
        objects = {item["name"] for item in self.scene["objects"]}
        instances = {item["objectName"] for item in self.scene["instances"]}
        for name in ("TouchJoystick", "ShopButton", "ShopPanel",
                     "CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel"):
            with self.subTest(name=name):
                self.assertIn(name, objects)
                self.assertIn(name, instances)

    def test_shop_button_is_on_screen(self):
        button = next(item for item in self.scene["instances"]
                      if item["objectName"] == "ShopButton")
        self.assertGreaterEqual(button["x"], 0)
        self.assertLess(button["x"], 720)

    def test_joystick_uses_display_height(self):
        joystick = next(item for item in self.scene["instances"]
                        if item["objectName"] == "TouchJoystick")
        self.assertEqual(joystick["y"], 1280 - 36 - 160)

    def test_patching_twice_does_not_duplicate_objects_or_variables(self):
        apply_v3_1_rules(self.project, self.scene, cfg())
        for collection, key in ((self.scene["objects"], "name"),
                                (self.scene["instances"], "objectName"),
                                (self.project["variables"], "name")):
            names = [item[key] for item in collection]
            self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
