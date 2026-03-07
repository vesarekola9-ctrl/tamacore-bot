from __future__ import annotations

import shutil
from pathlib import Path


def export_web(game_dir: Path, export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)

    src = game_dir
    dst = export_dir / "web"

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

    index = dst / "index.html"

    if not index.exists():
        index.write_text(
            """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TamaCore Game</title>
</head>
<body>
<h1>TamaCore export</h1>
<p>Open this folder in GDevelop to run the game.</p>
</body>
</html>
"""
        )
