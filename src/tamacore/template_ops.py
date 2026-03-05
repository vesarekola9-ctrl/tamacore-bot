from __future__ import annotations

import shutil
from pathlib import Path


def ensure_template_exists(template_dir: Path) -> None:
    game_json = template_dir / "game.json"
    if not game_json.exists():
        raise FileNotFoundError(
            f"Template missing: {game_json}\n"
            "Fix:\n"
            "  GDevelop -> New project -> Empty -> Save As into templates/gdevelop_template\n"
            "  Ensure templates/gdevelop_template/game.json exists and commit it."
        )


def copy_template(template_dir: Path, out_dir: Path) -> None:
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_dir, out_dir, dirs_exist_ok=True)
