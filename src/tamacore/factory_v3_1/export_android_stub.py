from __future__ import annotations

from pathlib import Path


def export_android_stub(game_dir: Path, export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)

    readme = export_dir / "ANDROID_EXPORT.txt"

    readme.write_text(
        f"""
TamaCore Android export stub

Game directory:
{game_dir}

Open this project in GDevelop
Export -> Android
"""
    )
