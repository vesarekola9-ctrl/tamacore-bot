from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json, write_json


def write_foods_runtime(pack_dir: Path, game_dir: Path) -> Dict[str, Any]:
    pack_path = pack_dir / "pack.json"
    foods: List[Dict[str, Any]] = []

    if pack_path.exists():
        data = read_json(pack_path)
        if isinstance(data, dict):
            raw = data.get("foods", [])
            if isinstance(raw, list):
                for item in raw:
                    if not isinstance(item, dict):
                        continue
                    foods.append(
                        {
                            "id": str(item.get("id", "")),
                            "name": str(item.get("name", "")),
                            "hunger": _int(item.get("hunger"), 0),
                            "energy": _int(item.get("energy"), 0),
                            "mood": _int(item.get("mood"), 0),
                            "price": _int(item.get("price"), 0),
                        }
                    )

    runtime: Dict[str, Any] = {
        "selectedFoodIndex": 0,
        "foods": foods,
        "activeFood": foods[0] if foods else {
            "id": "",
            "name": "",
            "hunger": 18,
            "energy": 0,
            "mood": 4,
            "price": 8,
        },
    }

    write_json(game_dir / "foods_runtime.json", runtime)
    return runtime


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default
