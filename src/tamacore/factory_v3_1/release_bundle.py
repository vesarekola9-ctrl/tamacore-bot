from __future__ import annotations

import shutil
from pathlib import Path

from ..utils import write_text


def bundle_release(game_dir: Path, export_dir: Path, bundle_dir: Path) -> None:
    """Create a source-project release bundle without pretending it is playable."""
    game_dir = Path(game_dir).resolve()
    export_dir = Path(export_dir).resolve()
    bundle_dir = Path(bundle_dir).resolve()

    if not (game_dir / "game.json").is_file():
        raise FileNotFoundError(f"GDevelop game.json not found: {game_dir}")
    if bundle_dir == game_dir or bundle_dir.is_relative_to(game_dir):
        raise ValueError("Bundle directory must be outside the game directory")
    if bundle_dir == export_dir or bundle_dir.is_relative_to(export_dir):
        raise ValueError("Bundle directory must be outside the export directory")
    if game_dir.is_relative_to(bundle_dir) or (
        export_dir.exists() and export_dir.is_relative_to(bundle_dir)
    ):
        raise ValueError("Bundle directory must not contain source directories")

    bundle_dir.parent.mkdir(parents=True, exist_ok=True)
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    shutil.copytree(game_dir, bundle_dir / "game")
    if export_dir.is_dir():
        shutil.copytree(export_dir, bundle_dir / "exports")
    else:
        (bundle_dir / "exports").mkdir()

    compiled_web = (bundle_dir / "exports" / "web" / "index.html").is_file()
    write_text(
        bundle_dir / "README_RELEASE.txt",
        "\n".join([
            "TamaCore Release Bundle",
            "======================",
            "",
            "Contents:",
            "- game/: GDevelop source project",
            "- exports/: generated export artifacts",
            "",
            "Compiled HTML5 game: " + ("present" if compiled_web else "not included"),
            "Open game/game.json in GDevelop to edit the project.",
            "A ZIP containing only the source project is not a playable web build.",
            "",
        ]),
    )

    archive_base = bundle_dir.parent / bundle_dir.name
    zip_path = archive_base.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(bundle_dir),
    )
