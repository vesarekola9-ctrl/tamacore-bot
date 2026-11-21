"""Structural regression tests for GDevelop care controls and needs decay."""
import unittest

from tamacore.factory_v3_1.pet_care_events import apply_pet_care_events


class PetCareEventsTests(unittest.TestCase):
    def test_buttons_stats_decay_and_hud_are_created_once(self):
        scene = {
            "objects": [{"name": "Player", "animations": [{"name": "Idle"}]}],
            "instances": [],
            "events": [],
        }
        apply_pet_care_events(scene, width=720, height=1280)
        counts = tuple(len(scene[key]) for key in ("objects", "instances", "events"))
        self.assertEqual(counts, (9, 8, 9))
        apply_pet_care_events(scene, width=720, height=1280)
        self.assertEqual(tuple(len(scene[key]) for key in ("objects", "instances", "events")), counts)
        by_name = {event["name"]: event for event in scene["events"]}
        self.assertEqual(by_name["TamaCorePetClick_Feed"]["actions"][1]["parameters"][0], "Pet_Hunger")
        self.assertEqual(by_name["TamaCorePetClick_Play"]["actions"][1]["parameters"][0], "Pet_Happiness")
        self.assertEqual(by_name["TamaCorePetClick_Sleep"]["actions"][1]["parameters"][0], "Pet_Energy")
        self.assertEqual(len(by_name["TamaCorePetNeedsDecay"]["actions"]), 4)
        self.assertEqual(by_name["TamaCorePetNeedsDecay"]["actions"][-1]["type"]["value"], "ResetTimer")
        self.assertEqual(len(by_name["TamaCorePetClick_Idle"]["actions"]), 1)

    def test_no_player_means_no_pet_controls(self):
        scene = {"objects": [], "instances": [], "events": []}
        apply_pet_care_events(scene)
        self.assertEqual(scene, {"objects": [], "instances": [], "events": []})


if __name__ == "__main__":
    unittest.main()
