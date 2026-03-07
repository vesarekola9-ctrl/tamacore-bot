from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json

Json = Dict[str, Any]


def validate_build_output(game_dir: Path) -> List[str]:
    errors: List[str] = []

    required_files = [
        game_dir / "game.json",
        game_dir / "catalog.json",
        game_dir / "levels.json",
        game_dir / "shop.json",
        game_dir / "FACTORY_MANIFEST.json",
    ]

    for path in required_files:
        if not path.exists():
            errors.append(f"Missing file: {path.name}")

    if errors:
        return errors

    game = _load_json(game_dir / "game.json", errors, "game.json")
    catalog = _load_json(game_dir / "catalog.json", errors, "catalog.json")
    levels = _load_json(game_dir / "levels.json", errors, "levels.json")
    shop = _load_json(game_dir / "shop.json", errors, "shop.json")
    manifest = _load_json(game_dir / "FACTORY_MANIFEST.json", errors, "FACTORY_MANIFEST.json")

    if isinstance(game, dict):
        layouts = game.get("layouts")
        if not isinstance(layouts, list) or not layouts:
            errors.append("game.json: layouts missing")

    if isinstance(catalog, dict):
        if not isinstance(catalog.get("assets"), dict):
            errors.append("catalog.json: assets missing")
        if not isinstance(catalog.get("objects"), list):
            errors.append("catalog.json: objects missing")
        if not isinstance(catalog.get("instances"), list):
            errors.append("catalog.json: instances missing")

    if not isinstance(levels, list):
        errors.append("levels.json: must be a list")

    if isinstance(shop, dict):
        if not isinstance(shop.get("upgrades"), list):
            errors.append("shop.json: upgrades missing")

    if isinstance(manifest, dict):
        if "factory" not in manifest:
            errors.append("FACTORY_MANIFEST.json: factory missing")

    return errors


def _load_json(path: Path, errors: List[str], label: str) -> Any:
    try:
        return read_json(path)
    except Exception as exc:
        errors.append(f"{label}: invalid json ({exc})")
        return None
