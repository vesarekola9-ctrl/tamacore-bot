from __future__ import annotations

import shutil
from pathlib import Path


def export_web(game_dir: Path, export_dir: Path) -> None:
    """Copy an already compiled GDevelop HTML5 export.

    A GDevelop project JSON is not a playable web export. Never create a
    placeholder index.html that incorrectly suggests a successful export.
    """
    game_dir = Path(game_dir)
    export_dir = Path(export_dir)

    index = game_dir / "index.html"
    if not index.is_file():
        raise RuntimeError(
            "Web export requires compiled GDevelop HTML5 output "
            "(index.html and runtime files). The source game.json is "
            "not a playable web export. Export with GDevelop first."
        )

    if not (game_dir / "game.json").is_file() and not any(
        game_dir.glob("*.js")
    ):
        raise RuntimeError(
            "Compiled web runtime files are missing from the source directory."
        )

    destination = export_dir / "web"
    if game_dir.resolve() == destination.resolve():
        raise ValueError("Source and destination must be different directories")

    export_dir.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(game_dir, destination)
