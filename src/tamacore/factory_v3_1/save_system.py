from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import write_json


def write_save_schema(game_dir: Path, shop: Dict[str, Any] | None = None) -> Dict[str, Any]:
    owned_upgrades: Dict[str, int] = {}

    upgrades = []
    if isinstance(shop, dict):
        raw = shop.get("upgrades", [])
        if isinstance(raw, list):
            upgrades = raw

    for item in upgrades:
        if not isinstance(item, dict):
            continue
        owned_var = str(item.get("ownedVariable", "")).strip()
        if owned_var:
            owned_upgrades[owned_var] = 0

    data: Dict[str, Any] = {
        "version": 2,
        "storageKey": "tamacore_save",
        "defaults": {
            "Coins": 250,
            "Speed": 200,
            "PlayerMaxSpeed": 200,
            "LevelIndex": 0,
            "LevelCount": 1,
            "CoinTarget": 0,
            "EnemyTarget": 0,
            "CoinsCollected": 0,
            "EnemiesHit": 0,
            "LevelComplete": 0,
            "GameComplete": 0,
            "SaveLoaded": 0,
            "ownedUpgrades": owned_upgrades,
        },
    }

    write_json(game_dir / "save.json", data)
    return data
