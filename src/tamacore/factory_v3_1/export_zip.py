from __future__ import annotations

import shutil
from pathlib import Path


def export_zip(game_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(
        base_name=str(zip_path.with_suffix("")),
        format="zip",
        root_dir=str(game_dir),
    )
