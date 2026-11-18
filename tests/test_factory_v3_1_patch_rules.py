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

    def test_small_landscape_display_keeps_shop_controls_inside(self):
        small_cfg = cfg()
        small_cfg.display.virtualWidth = 320
        small_cfg.display.virtualHeight = 240
        project = {"variables": []}
        scene = {"objects": [], "instances": [], "layers": []}
        apply_v3_1_rules(project, scene, small_cfg)
        instances = {item["objectName"]: item for item in scene["instances"]}
        for name in ("ShopButton", "ShopPanel"):
            with self.subTest(name=name):
                self.assertGreaterEqual(instances[name]["x"], 0)
                self.assertLess(instances[name]["x"], 320)
                self.assertGreaterEqual(instances[name]["y"], 0)
                self.assertLess(instances[name]["y"], 240)

    def test_tiny_display_keeps_ui_anchors_inside_viewport(self):
        tiny = cfg()
        tiny.display.virtualWidth = 20
        tiny.display.virtualHeight = 20
        tiny.ui.joystick.marginX = 36
        tiny.ui.joystick.marginY = 36
        project = {"variables": []}
        scene = {"objects": [], "instances": [], "layers": []}
        apply_v3_1_rules(project, scene, tiny)
        names = {"ShopButton", "ShopPanel", "TouchJoystick",
                 "CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel"}
        for instance in scene["instances"]:
            if instance["objectName"] not in names:
                continue
            with self.subTest(name=instance["objectName"]):
                self.assertGreaterEqual(instance["x"], 0)
                self.assertLess(instance["x"], 20)
                self.assertGreaterEqual(instance["y"], 0)
                self.assertLess(instance["y"], 20)

    def test_one_pixel_viewport_keeps_hud_coordinates_in_bounds(self):
        tiny = cfg()
        tiny.display.virtualWidth = 1
        tiny.display.virtualHeight = 1
        project = {"variables": []}
        scene = {"objects": [], "instances": [], "layers": []}
        apply_v3_1_rules(project, scene, tiny)
        labels = {"CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel"}
        for instance in scene["instances"]:
            if instance["objectName"] in labels:
                with self.subTest(name=instance["objectName"]):
                    self.assertEqual(instance["x"], 0)
                    self.assertEqual(instance["y"], 0)

    def test_normal_viewport_keeps_original_hud_spacing(self):
        positions = {instance["objectName"]: instance["y"]
                     for instance in self.scene["instances"]}
        self.assertEqual([positions[name] for name in
                          ("CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel")],
                         [24, 60, 96, 132])

    def test_level_defaults_match_pack_configuration(self):
        variables = {item["name"]: item["value"]
                     for item in self.project["variables"]}
        self.assertEqual(variables["LevelCount"], 3)
        self.assertEqual(variables["CoinTarget"], 5)
        self.assertEqual(variables["EnemyTarget"], 2)

    def test_patching_twice_does_not_duplicate_objects_or_variables(self):
        apply_v3_1_rules(self.project, self.scene, cfg())
        for collection, key in ((self.scene["objects"], "name"),
                                (self.scene["instances"], "objectName"),
                                (self.project["variables"], "name")):
            names = [item[key] for item in collection]
            self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
