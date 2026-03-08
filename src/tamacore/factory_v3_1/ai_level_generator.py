from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict

from ..utils import read_json, write_json


def generate_ai_levels(pack_dir: Path) -> Dict[str, Any]:
    pack_path = pack_dir / "pack.json"
    if not pack_path.exists():
        raise FileNotFoundError(f"Missing file: {pack_path}")

    data = read_json(pack_path)
    if not isinstance(data, dict):
        raise ValueError("pack.json must be an object")

    level_count = random.randint(3, 8)
    coin_base = random.randint(4, 8)
    coin_step = random.randint(1, 3)
    enemy_base = random.randint(0, 2)
    enemy_step = random.randint(0, 2)
    seed = random.randint(1, 999999)

    levels = {
        "count": level_count,
        "coinBase": coin_base,
        "coinStep": coin_step,
        "enemyBase": enemy_base,
        "enemyStep": enemy_step,
        "seed": seed,
    }

    data["levels"] = levels
    write_json(pack_path, data)
    write_json(pack_dir / "levels.ai.json", levels)
    return levels
