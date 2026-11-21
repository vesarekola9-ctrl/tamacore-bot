"""Regression tests for pet runtime GDevelop compatibility."""
import unittest
from tamacore.factory_v3_1.pet_runtime import apply_pet_runtime


class PetRuntimeTests(unittest.TestCase):
    def test_adds_state_without_nonexistent_sprite_files(self):
        project = {"layouts": [{"name": "MainScene", "objects": [], "events": []}]}
        apply_pet_runtime(project)
        self.assertEqual(project["layouts"][0]["objects"], [])
        self.assertEqual(project["layouts"][0]["events"], [])
        self.assertEqual(next(v for v in project["variables"] if v["name"] == "Pet_State")["value"], "Idle")
        self.assertEqual(next(v for v in project["globalVariables"] if v["name"] == "Pet_State")["value"], "Idle")

    def test_repeated_application_does_not_duplicate_variables(self):
        project = {"variables": [{"name": "Pet_State", "type": "string", "value": "Sleep", "children": []}]}
        apply_pet_runtime(project)
        apply_pet_runtime(project)
        self.assertEqual(sum(v["name"] == "Pet_State" for v in project["variables"]), 1)
        self.assertEqual(next(v for v in project["variables"] if v["name"] == "Pet_State")["value"], "Sleep")
        self.assertEqual(sum(v["name"] == "Pet_State" for v in project["globalVariables"]), 1)


if __name__ == "__main__":
    unittest.main()
