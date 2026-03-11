from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json, write_json


def write_cosmetics_runtime(pack_dir: Path, game_dir: Path) -> Dict[str, Any]:
    pack_path = pack_dir / "pack.json"
    cosmetics: List[Dict[str, Any]] = []

    if pack_path.exists():
        data = read_json(pack_path)
        if isinstance(data, dict):
            raw = data.get("cosmetics", [])
            if isinstance(raw, list):
                for item in raw:
                    if not isinstance(item, dict):
                        continue
                    cosmetics.append(
                        {
                            "id": str(item.get("id", "")),
                            "name": str(item.get("name", "")),
                            "price": _int(item.get("price"), 0),
                            "styleBonus": _int(item.get("styleBonus"), 0),
                        }
                    )

    runtime: Dict[str, Any] = {
        "selectedCosmeticId": cosmetics[0]["id"] if cosmetics else "",
        "cosmetics": cosmetics,
    }

    write_json(game_dir / "cosmetics_runtime.json", runtime)
    return runtime


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default
