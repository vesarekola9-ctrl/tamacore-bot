"""Level configuration validation regression tests."""
import unittest

from tamacore.factory_v3_1.pack_inspector import _validate_levels


def levels(**overrides):
    data = {"count": 5, "coinBase": 8, "coinStep": 2,
            "enemyBase": 1, "enemyStep": 1, "seed": 1337}
    data.update(overrides)
    return data


class LevelValidationTests(unittest.TestCase):
    def test_valid_levels(self):
        self.assertEqual(_validate_levels(levels()), [])

    def test_fractional_count_rejected(self):
        self.assertTrue(any("integer" in error
                            for error in _validate_levels(levels(count=2.5))))

    def test_boolean_count_rejected(self):
        self.assertTrue(any("integer" in error
                            for error in _validate_levels(levels(count=True))))

    def test_numeric_string_count_rejected(self):
        self.assertTrue(any("integer" in error
                            for error in _validate_levels(levels(count="5"))))

    def test_zero_count_rejected(self):
        self.assertTrue(any("count must be > 0" in error
                            for error in _validate_levels(levels(count=0))))

    def test_negative_spawn_count_rejected(self):
        self.assertTrue(any("coinBase must be >= 0" in error
                            for error in _validate_levels(levels(coinBase=-1))))

    def test_negative_seed_allowed(self):
        self.assertEqual(_validate_levels(levels(seed=-10)), [])


if __name__ == "__main__":
    unittest.main()
