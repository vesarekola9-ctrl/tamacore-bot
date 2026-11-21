"""Regression test: malformed shop data must yield errors, not crash."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tamacore.factory_v3_1 import validate


class BuildShopValidationTests(unittest.TestCase):
    def test_non_list_upgrades_do_not_crash_build_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for filename in (
                "game.json", "catalog.json", "levels.json", "shop.json",
                "save.json", "pet_runtime.json", "save_runtime.json",
                "cosmetics_runtime.json", "foods_runtime.json",
                "FACTORY_MANIFEST.json",
            ):
                data = {"variables": []} if filename == "game.json" else {}
                if filename == "shop.json":
                    data = {"upgrades": None}
                if filename == "levels.json":
                    data = []
                (root / filename).write_text(json.dumps(data), encoding="utf-8")
            # Other sections are not the subject of this regression.
            with patch.object(validate, "_validate_game"), \
                 patch.object(validate, "_validate_catalog"), \
                 patch.object(validate, "_validate_levels"), \
                 patch.object(validate, "_validate_save"), \
                 patch.object(validate, "_validate_pet_runtime"), \
                 patch.object(validate, "_validate_save_runtime"), \
                 patch.object(validate, "_validate_cosmetics_runtime"), \
                 patch.object(validate, "_validate_foods_runtime"), \
                 patch.object(validate, "_validate_manifest"):
                errors = validate.validate_build_output(root)
            self.assertTrue(any("shop.json: upgrades missing" in e for e in errors))


    def test_duplicate_shop_ownership_variable_is_reported(self):
        self._assert_invalid_ownership([
            {"name": "Owned_speed", "type": "number", "value": 0},
            {"name": "Owned_speed", "type": "number", "value": 0},
        ], "duplicate shop ownership variable")

    def test_string_shop_ownership_variable_is_reported(self):
        self._assert_invalid_ownership([
            {"name": "Owned_speed", "type": "string", "value": "0"},
        ], "must be numeric")

    def _assert_invalid_ownership(self, variables, expected):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for filename in (
                "game.json", "catalog.json", "levels.json", "shop.json",
                "save.json", "pet_runtime.json", "save_runtime.json",
                "cosmetics_runtime.json", "foods_runtime.json",
                "FACTORY_MANIFEST.json",
            ):
                data = {}
                if filename == "game.json":
                    data = {"variables": variables}
                elif filename == "shop.json":
                    data = {"upgrades": [{"id": "speed",
                                         "ownedVariable": "Owned_speed"}]}
                elif filename == "levels.json":
                    data = []
                (root / filename).write_text(json.dumps(data), encoding="utf-8")
            with patch.object(validate, "_validate_game"), \
                 patch.object(validate, "_validate_catalog"), \
                 patch.object(validate, "_validate_levels"), \
                 patch.object(validate, "_validate_shop"), \
                 patch.object(validate, "_validate_save"), \
                 patch.object(validate, "_validate_pet_runtime"), \
                 patch.object(validate, "_validate_save_runtime"), \
                 patch.object(validate, "_validate_cosmetics_runtime"), \
                 patch.object(validate, "_validate_foods_runtime"), \
                 patch.object(validate, "_validate_manifest"):
                errors = validate.validate_build_output(root)
            self.assertTrue(any(expected in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
