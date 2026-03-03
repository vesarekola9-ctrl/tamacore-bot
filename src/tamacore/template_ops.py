from __future__ import annotations

import shutil
from pathlib import Path


def ensure_template_exists(template_dir: Path) -> Path:
    """
    Validate template directory contains game.json
    Returns path to template game.json.
    """
    game_json = template_dir / "game.json"
    if not game_json.exists():
        raise FileNotFoundError(
            f"Template missing: {game_json}\n"
            "Create it in GDevelop:\n"
            "  New project → Empty → Save As into templates/gdevelop_template\n"
            "Then commit templates/gdevelop_template to GitHub."
        )
    return game_json


def copy_template(template_dir: Path, out_game_dir: Path) -> None:
    """
    Copy whole template folder into out_game_dir (overwrite).
    """
    if out_game_dir.exists():
        shutil.rmtree(out_game_dir)
    shutil.copytree(template_dir, out_game_dir)
