from __future__ import annotations

from pathlib import Path

from .assets_seed import ensure_assets_exist
from .game_files import copy_images_into_game
from .gdevelop_project import produce_game


def run_pipeline(assets_dir: Path, game_dir: Path) -> None:
    ensure_assets_exist(assets_dir)
    game_dir.mkdir(parents=True, exist_ok=True)

    image_map = copy_images_into_game(assets_dir=assets_dir, game_dir=game_dir, target_rel_dir="assets/generated")
    game_json = produce_game(game_dir, image_map)

    print("[OK] Copied images to:", (game_dir / "assets/generated"))
    print("[OK] Produced/updated GDevelop project:", game_json)
    print("[NEXT] Open in GDevelop:", game_json)
