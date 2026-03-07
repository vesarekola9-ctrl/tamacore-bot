from __future__ import annotations

from pathlib import Path
from typing import Dict

from .patch_gdevelop import copy_assets_into_game, patch_project


def run_pipeline(assets_dir: Path, template_dir: Path, game_dir: Path) -> None:
    game_json = game_dir / "game.json"

    if not template_dir.exists():
        raise FileNotFoundError(f"Template dir not found: {template_dir}")

    if not game_dir.exists():
        raise FileNotFoundError(f"Game dir not found: {game_dir}")

    if not game_json.exists():
        raise FileNotFoundError(f"game.json not found: {game_json}")

    image_map: Dict[str, str] = copy_assets_into_game(assets_dir=assets_dir, game_dir=game_dir)
    patch_project(
        game_json_path=game_json,
        image_map=image_map,
        scene_name="Main",
    )

    print("[OK] Pipeline patched:", game_json)
