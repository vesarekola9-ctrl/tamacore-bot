from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..utils import write_json
from .schema import PackCfg


def generate_levels(pack: PackCfg, out_dir: Path) -> List[Dict[str, Any]]:
    """
    Writes levels into out_dir/levels/*.json
    Returns a list of level dicts for manifest usage.
    """
    levels_dir = out_dir / "levels"
    levels_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(pack.levels.seed)

    levels: List[Dict[str, Any]] = []
    for i in range(1, pack.levels.count + 1):
        level_id = f"level_{i:03d}"
        # Very simple procedural: pick random coin/enemy spawn rectangles inside world bounds
        b = pack.worldBounds
        level = {
            "id": level_id,
            "worldBounds": {"xMin": b.xMin, "yMin": b.yMin, "xMax": b.xMax, "yMax": b.yMax},
            "coinSpawnArea": _rand_rect(rng, b, margin=100),
            "enemySpawnArea": _rand_rect(rng, b, margin=150),
        }
        write_json(levels_dir / f"{level_id}.json", level)
        levels.append(level)

    # manifest
    write_json(levels_dir / "manifest.json", {"levels": [l["id"] for l in levels]})
    return levels


def _rand_rect(rng: random.Random, b, margin: int) -> Dict[str, int]:
    x1 = rng.randint(b.xMin + margin, max(b.xMin + margin, b.xMax - margin - 300))
    y1 = rng.randint(b.yMin + margin, max(b.yMin + margin, b.yMax - margin - 200))
    w = rng.randint(240, 520)
    h = rng.randint(180, 420)
    x2 = min(b.xMax - margin, x1 + w)
    y2 = min(b.yMax - margin, y1 + h)
    return {"x": x1, "y": y1, "w": max(50, x2 - x1), "h": max(50, y2 - y1)}
