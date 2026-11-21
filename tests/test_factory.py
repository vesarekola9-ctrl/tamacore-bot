"""Master factory smoke test compatible with unittest and pytest."""
import unittest

from tamacore.factory_v3_1.generator import build_game_json


class FactoryTests(unittest.TestCase):
    def test_build_game_json(self):
        base_data = {
            "properties": {"name": "Test Game"},
            "layouts": [{"name": "MainScene", "objects": [], "instances": [], "events": []}],
            "globalVariables": [],
            "resources": {"resources": []},
        }
        result = build_game_json(base_data)
        self.assertIn("globalVariables", result)
        names = {variable["name"] for variable in result["globalVariables"]}
        self.assertIn("Pet_CurrentEmote", names)
        self.assertIn("Seasonal_ActiveEvent", names)


if __name__ == "__main__":
    unittest.main()
