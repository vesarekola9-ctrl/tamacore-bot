"""Verify GDevelop event-sheet wiring for pet animations."""
import unittest
from tamacore.factory_v3_1.character_builder import apply_pet_animation_events, apply_pet_keyboard_controls


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

    def test_keyboard_controls_set_pet_state_without_duplicates(self):
        scene = {"objects": [{"name": "Player", "animations": [{"name": "Idle"}]}], "events": []}
        apply_pet_keyboard_controls(scene)
        apply_pet_keyboard_controls(scene)
        self.assertEqual(len(scene["events"]), 5)
        for event, (key, state) in zip(scene["events"],
                                       (("f", "Eat"), ("p", "Play"), ("s", "Sleep"), ("w", "Walk"), ("i", "Idle"))):
            self.assertEqual(event["conditions"][0]["parameters"], [key])
            self.assertEqual(event["actions"][0]["parameters"], ["Pet_State", "=", f'"{state}"'])



if __name__ == "__main__":
    unittest.main()
