from __future__ import annotations

import shutil
from pathlib import Path

from ..utils import write_text


def bundle_release(game_dir: Path, export_dir: Path, bundle_dir: Path) -> None:
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)

    bundle_dir.mkdir(parents=True, exist_ok=True)

    game_dst = bundle_dir / "game"
    exports_dst = bundle_dir / "exports"

    if game_dir.exists():
        shutil.copytree(game_dir, game_dst)
    else:
        game_dst.mkdir(parents=True, exist_ok=True)

    if export_dir.exists():
        shutil.copytree(export_dir, exports_dst)
    else:
        exports_dst.mkdir(parents=True, exist_ok=True)

    write_text(
        bundle_dir / "README_RELEASE.txt",
        "\n".join(
            [
                "TamaCore Release Bundle",
                "======================",
                "",
                f"Game dir: {game_dir}",
                f"Export dir: {export_dir}",
                "",
                "Contents:",
                "- game/",
                "- exports/",
            ]
        ),
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
