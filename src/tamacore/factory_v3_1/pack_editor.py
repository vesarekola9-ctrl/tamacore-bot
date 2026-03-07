from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import read_json, write_json


def load_pack(pack_dir: Path) -> Dict[str, Any]:
    path = pack_dir / "pack.json"
    if not path.exists():
        return {}

    data = read_json(path)
    if not isinstance(data, dict):
        return {}

    return data


def save_pack(pack_dir: Path, data: Dict[str, Any]) -> None:
    path = pack_dir / "pack.json"
    write_json(path, data)


def create_default_pack(name: str) -> Dict[str, Any]:
    return {
        "name": name,
        "version": 1,
        "scene": "Main",
        "display": {
            "mode": "portrait",
            "virtualWidth": 720,
            "virtualHeight": 1280,
        },
        "worldBounds": {
            "xMin": 0,
            "yMin": 0,
            "xMax": 720,
            "yMax": 1280,
        },
        "levels": {
            "count": 3,
            "seed": 1337,
        },
        "coinSpawn": {
            "objectName": "Coin",
            "count": 5,
            "enabled": True,
        },
        "enemySpawn": {
            "objectName": "Enemy",
            "count": 2,
            "enabled": True,
        },
        "shop": {
            "upgrades": [
                {
                    "id": "speed1",
                    "name": "Speed +50",
                    "cost": 100,
                    "effect": {
                        "type": "speed",
                        "value": 50,
                    },
                    "ownedVariable": "owned_speed1",
                    "uiText": "BUY SPEED +50 (100c)",
                }
            ]
        },
    }
