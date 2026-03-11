from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import read_json, write_json


def write_save_runtime(game_dir: Path) -> Dict[str, Any]:
    save_path = game_dir / "save.json"
    data = read_json(save_path) if save_path.exists() else {}

    defaults = data.get("defaults", {}) if isinstance(data, dict) else {}
    if not isinstance(defaults, dict):
        defaults = {}

    runtime = {
        "storageKey": str(data.get("storageKey", "tamacore_save")) if isinstance(data, dict) else "tamacore_save",
        "defaults": {
            "Coins": _int(defaults.get("Coins"), 250),
            "Speed": _int(defaults.get("Speed"), 200),
            "PlayerMaxSpeed": _int(defaults.get("PlayerMaxSpeed"), 200),
            "LevelIndex": _int(defaults.get("LevelIndex"), 0),
            "LevelCount": _int(defaults.get("LevelCount"), 1),
            "CoinTarget": _int(defaults.get("CoinTarget"), 0),
            "EnemyTarget": _int(defaults.get("EnemyTarget"), 0),
            "CoinsCollected": _int(defaults.get("CoinsCollected"), 0),
            "EnemiesHit": _int(defaults.get("EnemiesHit"), 0),
            "LevelComplete": _int(defaults.get("LevelComplete"), 0),
            "GameComplete": _int(defaults.get("GameComplete"), 0),
            "SaveLoaded": _int(defaults.get("SaveLoaded"), 0),
            "PetHunger": _int(defaults.get("PetHunger"), 60),
            "PetEnergy": _int(defaults.get("PetEnergy"), 60),
            "PetMood": _int(defaults.get("PetMood"), 60),
            "PetCleanliness": _int(defaults.get("PetCleanliness"), 60),
            "PetState": _int(defaults.get("PetState"), 0),
            "ownedUpgrades": defaults.get("ownedUpgrades", {}) if isinstance(defaults.get("ownedUpgrades", {}), dict) else {},
        },
    }

    write_json(game_dir / "save_runtime.json", runtime)
    return runtime


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default
