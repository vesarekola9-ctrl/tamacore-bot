from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, Any, List

from ..utils import write_json, ensure_dir


NAMES = [
    "Fluffy",
    "Zappy",
    "Mochi",
    "Pixel",
    "Bobo",
    "Luna",
    "Rex",
    "Neko",
    "Choco",
    "Nova",
]

FOODS = [
    "apple",
    "burger",
    "cake",
    "fish",
    "pizza",
    "carrot",
]

COSMETICS = [
    "hat",
    "glasses",
    "bow",
    "cape",
    "mask",
]


def _rand_name() -> str:
    return random.choice(NAMES) + str(random.randint(1, 999))


def _rand_foods() -> List[Dict[str, Any]]:
    count = random.randint(2, 5)
    result = []
    for i in range(count):
        f = random.choice(FOODS)
        result.append(
            {
                "id": f"{f}{i}",
                "name": f.title(),
                "hunger": random.randint(5, 20),
                "price": random.randint(5, 30),
            }
        )
    return result


def _rand_cosmetics() -> List[Dict[str, Any]]:
    count = random.randint(2, 5)
    result = []
    for i in range(count):
        c = random.choice(COSMETICS)
        result.append(
            {
                "id": f"{c}{i}",
                "name": c.title(),
                "price": random.randint(10, 50),
            }
        )
    return result


def generate_ai_pack(pack_dir: Path) -> None:
    ensure_dir(pack_dir)

    pack: Dict[str, Any] = {
        "name": _rand_name(),
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
            "count": random.randint(1, 5),
            "seed": random.randint(1, 9999),
        },
        "foods": _rand_foods(),
        "cosmetics": _rand_cosmetics(),
        "coinSpawn": {
            "objectName": "Coin",
            "count": random.randint(3, 10),
            "enabled": True,
        },
        "enemySpawn": {
            "objectName": "Enemy",
            "count": random.randint(0, 3),
            "enabled": True,
        },
    }

    write_json(pack_dir / "pack.json", pack)
