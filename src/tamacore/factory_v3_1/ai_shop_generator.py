from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json, write_json


SHOP_EFFECTS = [
    ("speed", "playerMaxSpeedAdd", [25, 50, 75, 100]),
    ("coins", "coinsAdd", [50, 100, 150, 250]),
    ("mood", "moodAdd", [5, 10, 15, 20]),
    ("energy", "energyAdd", [5, 10, 15, 20]),
    ("clean", "cleanlinessAdd", [5, 10, 15, 20]),
]

SHOP_NAMES = {
    "playerMaxSpeedAdd": "Speed",
    "coinsAdd": "Coins",
    "moodAdd": "Mood",
    "energyAdd": "Energy",
    "cleanlinessAdd": "Clean",
}


def generate_ai_shop(pack_dir: Path, upgrade_count: int = 4) -> Dict[str, Any]:
    pack_path = pack_dir / "pack.json"
    if not pack_path.exists():
        raise FileNotFoundError(f"Missing file: {pack_path}")

    data = read_json(pack_path)
    if not isinstance(data, dict):
        raise ValueError("pack.json must be an object")

    upgrades: List[Dict[str, Any]] = []
    used_ids: set[str] = set()

    for i in range(max(1, upgrade_count)):
        label, effect_key, values = random.choice(SHOP_EFFECTS)
        value = random.choice(values)
        cost = max(10, int(value * random.uniform(1.5, 3.5)))

        uid = f"{label}_{i+1}"
        while uid in used_ids:
            uid = f"{label}_{i+1}_{random.randint(1, 99)}"
        used_ids.add(uid)

        pretty = SHOP_NAMES.get(effect_key, label.title())
        upgrades.append(
            {
                "id": uid,
                "name": f"{pretty} +{value}",
                "cost": cost,
                "effect": {
                    effect_key: value,
                },
                "ownedVariable": f"Owned_{uid}",
                "uiText": f"BUY: {pretty} +{value} ({cost}c)",
            }
        )

    shop = {
        "currencyVariable": "Coins",
        "upgrades": upgrades,
    }

    data["shop"] = shop
    write_json(pack_path, data)
    write_json(pack_dir / "shop.ai.json", shop)
    return shop
