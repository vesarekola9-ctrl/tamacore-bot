from __future__ import annotations

import shutil
from pathlib import Path


def ensure_template_exists(template_dir: Path) -> None:
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    game_json = template_dir / "game.json"
    if not game_json.exists():
        raise FileNotFoundError(f"Template game.json not found: {game_json}")


def copy_template(template_dir: Path, game_dir: Path) -> None:
    ensure_template_exists(template_dir)

    if game_dir.exists():
        shutil.rmtree(game_dir)

    shutil.copytree(template_dir, game_dir)
