from __future__ import annotations

import shutil
from pathlib import Path


def export_zip(game_dir: Path, zip_path: Path) -> None:
    """Package a generated GDevelop project, not an HTML5 build."""
    game_dir = Path(game_dir)
    zip_path = Path(zip_path)

    if not game_dir.is_dir():
        raise FileNotFoundError(f"Game directory not found: {game_dir}")
    if not (game_dir / "game.json").is_file():
        raise FileNotFoundError(f"GDevelop project not found: {game_dir / 'game.json'}")
    if zip_path.suffix.lower() != ".zip":
        raise ValueError("ZIP output path must end with .zip")
    if zip_path.resolve().is_relative_to(game_dir.resolve()):
        raise ValueError("ZIP output must be outside the game directory")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    archive_base = zip_path.with_suffix("")
    generated = Path(
        shutil.make_archive(
            base_name=str(archive_base),
            format="zip",
            root_dir=str(game_dir),
        )
    )
    if generated.resolve() != zip_path.resolve():
        raise RuntimeError(f"Unexpected archive path: {generated}")
