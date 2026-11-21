"""Spawn configuration regression tests."""
import unittest

from tamacore.factory_v3_1.pack_inspector import _validate_spawns


def config(**overrides):
    data = {
        "coinSpawn": {"objectName": "Coin", "count": 8,
                      "minDistanceFromPlayer": 120},
        "enemySpawn": {"objectName": "Enemy", "count": 2,
                       "minDistanceFromPlayer": 180},
    }
    for key, value in overrides.items():
        group, field = key.split("__", 1)
        data[group][field] = value
    return data


class SpawnValidationTests(unittest.TestCase):
    def test_valid_spawn_settings(self):
        self.assertEqual(_validate_spawns(config()), [])

    def test_fractional_coin_count_rejected(self):
        errors = _validate_spawns(config(coinSpawn__count=2.5))
        self.assertTrue(any("coinSpawn.count must be an integer" in e for e in errors))

    def test_boolean_enemy_count_rejected(self):
        errors = _validate_spawns(config(enemySpawn__count=True))
        self.assertTrue(any("enemySpawn.count must be an integer" in e for e in errors))

    def test_numeric_string_distance_rejected(self):
        errors = _validate_spawns(config(coinSpawn__minDistanceFromPlayer="120"))
        self.assertTrue(any("must be an integer" in e for e in errors))

    def test_negative_distance_rejected(self):
        errors = _validate_spawns(config(enemySpawn__minDistanceFromPlayer=-1))
        self.assertTrue(any("must be >= 0" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
