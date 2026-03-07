from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import write_json


def write_save_schema(game_dir: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "version": 1,
        "storageKey": "tamacore_save",
        "defaults": {
            "Coins": 250,
            "Speed": 200,
            "PlayerMaxSpeed": 200,
            "LevelIndex": 0,
            "CoinsCollected": 0,
            "EnemiesHit": 0,
            "LevelComplete": 0,
            "GameComplete": 0,
            "ownedUpgrades": {},
        },
    }
    write_json(game_dir / "save.json", data)
    return data
