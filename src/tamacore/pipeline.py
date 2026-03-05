from __future__ import annotations

from pathlib import Path

from .assets_seed import ensure_assets_exist
from .template_ops import ensure_template_exists, copy_template
from .patch_gdevelop import copy_assets_into_game, patch_project


def run_pipeline(assets_dir: Path, template_dir: Path, game_dir: Path) -> None:
    ensure_assets_exist(assets_dir)
    ensure_template_exists(template_dir)

    # Copy template to game folder
    copy_template(template_dir, game_dir)

    # Copy assets into game folder and patch game.json
    image_map = copy_assets_into_game(assets_dir, game_dir)

    game_json = game_dir / "game.json"
    patch_project(game_json, image_map)

    print("[OK] Template copied to:", game_dir)
    print("[OK] Assets copied to:", game_dir / "assets" / "generated")
    print("[OK] Patched:", game_json)
    print("[NEXT] Open in GDevelop:", game_json)
