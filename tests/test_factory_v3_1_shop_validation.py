"""Shop pack validation regression coverage.

Run: PYTHONPATH=src python -m unittest discover -s tests -v
"""
import unittest

from tamacore.factory_v3_1.pack_inspector import _validate_shop


def shop(*upgrades):
    return {"currencyVariable": "Coins", "upgrades": list(upgrades)}


def upgrade(identifier, **extra):
    return {"id": identifier, "name": "Speed boost", "cost": 25,
            "effect": {"speed": 10}, **extra}


class ShopValidationTests(unittest.TestCase):
    def test_legacy_upgrade_without_owned_variable(self):
        self.assertEqual(_validate_shop(shop(upgrade("speed"))), [])

    def test_empty_owned_variable_uses_generator_fallback(self):
        self.assertEqual(_validate_shop(shop(upgrade("speed", ownedVariable=""))), [])

    def test_explicit_owned_variable_is_supported(self):
        self.assertEqual(
            _validate_shop(shop(upgrade("speed", ownedVariable="OwnSpeed"))), []
        )

    def test_duplicate_explicit_owned_variables_are_rejected(self):
        errors = _validate_shop(shop(
            upgrade("speed", ownedVariable="OwnedSame"),
            upgrade("power", ownedVariable="OwnedSame"),
        ))
        self.assertTrue(any("duplicate upgrade ownedVariable" in e for e in errors))

    def test_explicit_and_fallback_owned_variables_cannot_collide(self):
        errors = _validate_shop(shop(
            upgrade("speed"),
            upgrade("power", ownedVariable="Owned_speed"),
        ))
        self.assertTrue(any("duplicate upgrade ownedVariable" in e for e in errors))

    def test_duplicate_upgrade_ids_are_rejected(self):
        errors = _validate_shop(shop(upgrade("speed"), upgrade("speed")))
        self.assertTrue(any("duplicate upgrade id" in e for e in errors))

    def test_missing_effect_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", effect={})))
        self.assertTrue(any("missing effect" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
