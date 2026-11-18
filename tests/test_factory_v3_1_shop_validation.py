"""Shop pack validation regression coverage.

Run: PYTHONPATH=src python -m unittest discover -s tests -v
"""
import unittest

from tamacore.factory_v3_1.pack_inspector import _validate_shop


def shop(*upgrades):
    return {"currencyVariable": "Coins", "upgrades": list(upgrades)}


def upgrade(identifier, **extra):
    item = {"id": identifier, "name": "Speed boost", "cost": 25,
            "effect": {"speed": 10}}
    item.update(extra)
    return item


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

    def test_null_upgrade_id_is_rejected(self):
        errors = _validate_shop(shop(upgrade(None)))
        self.assertTrue(any("missing id" in e for e in errors))

    def test_numeric_upgrade_id_is_rejected(self):
        errors = _validate_shop(shop(upgrade(42)))
        self.assertTrue(any("missing id" in e for e in errors))

    def test_null_upgrade_name_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", name=None)))
        self.assertTrue(any("missing name" in e for e in errors))

    def test_fractional_price_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", cost=1.5)))
        self.assertTrue(any("cost must be an integer" in e for e in errors))

    def test_boolean_price_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", cost=True)))
        self.assertTrue(any("cost must be an integer" in e for e in errors))

    def test_negative_price_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", cost=-1)))
        self.assertTrue(any("cost must be >= 0" in e for e in errors))

    def test_zero_price_is_allowed(self):
        self.assertEqual(_validate_shop(shop(upgrade("speed", cost=0))), [])

    def test_nonfinite_effect_is_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                errors = _validate_shop(shop(upgrade("speed", effect={"speed": value})))
                self.assertTrue(any("must be finite" in e for e in errors))

    def test_missing_effect_is_rejected(self):
        errors = _validate_shop(shop(upgrade("speed", effect={})))
        self.assertTrue(any("missing effect" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
