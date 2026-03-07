from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import write_json
from .schema import PackCfg


def generate_levels(cfg: PackCfg, game_dir: Path) -> List[Dict[str, Any]]:
    levels: List[Dict[str, Any]] = []

    for index in range(cfg.levels.count):
        level_id = f"level_{index + 1}"
        coin_count = max(0, cfg.levels.coinBase + index * cfg.levels.coinStep)
        enemy_count = max(0, cfg.levels.enemyBase + index * cfg.levels.enemyStep)

        levels.append(
            {
                "id": level_id,
                "index": index,
                "coinCount": coin_count if cfg.coinSpawn.enabled else 0,
                "enemyCount": enemy_count if cfg.enemySpawn.enabled else 0,
                "coinObjectName": cfg.coinSpawn.objectName,
                "enemyObjectName": cfg.enemySpawn.objectName,
                "worldBounds": {
                    "xMin": cfg.worldBounds.xMin,
                    "yMin": cfg.worldBounds.yMin,
                    "xMax": cfg.worldBounds.xMax,
                    "yMax": cfg.worldBounds.yMax,
                },
                "seed": cfg.levels.seed + index,
            }
        )

    write_json(game_dir / "levels.json", levels)
    return levels
