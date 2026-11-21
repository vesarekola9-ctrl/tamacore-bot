"""Verify GDevelop event-sheet wiring for pet animations."""
import unittest
from tamacore.factory_v3_1.character_builder import apply_pet_animation_events


class PetAnimationEventTests(unittest.TestCase):
    def test_all_available_states_have_named_animation_actions(self):
        names = ("Idle", "Walk", "Sleep", "Eat", "Play")
        scene = {"objects": [{"name": "Player", "animations": [{"name": n} for n in names]}], "events": []}
        apply_pet_animation_events(scene)
        self.assertEqual(len(scene["events"]), 5)
        for index, (event, name) in enumerate(zip(scene["events"], names)):
            self.assertEqual(event["conditions"][0]["parameters"], ["Pet_State", "=", name])
            self.assertEqual(event["actions"][0]["type"]["value"], "SetAnimation")
            self.assertEqual(event["actions"][0]["parameters"], ["Player", str(index)])
        apply_pet_animation_events(scene)
        self.assertEqual(len(scene["events"]), 5)

    def test_missing_states_do_not_generate_invalid_actions(self):
        scene = {"objects": [{"name": "Player", "animations": [{"name": "Idle"}]}]}
        apply_pet_animation_events(scene)
        self.assertEqual(len(scene["events"]), 1)
        self.assertEqual(scene["events"][0]["name"], "TamaCorePetAnimation_Idle")

    def test_missing_player_leaves_scene_unchanged(self):
        scene = {"objects": [], "events": []}
        apply_pet_animation_events(scene)
        self.assertEqual(scene["events"], [])


if __name__ == "__main__":
    unittest.main()
