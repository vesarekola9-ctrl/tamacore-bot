from __future__ import annotations

import base64
from pathlib import Path

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# Tiny valid 1x1 PNGs (different colors) base64-encoded.
# These are enough for GDevelop to load as image resources.
_PNG_PLAYER = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)  # black-ish
_PNG_COIN = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)  # light-ish
_PNG_BG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGP4DwQACfsD/QYJ7qQAAAAASUVORK5CYII="
)  # gray-ish


def ensure_assets_exist(assets_dir: Path) -> None:
    """
    If assets folder has no images, create placeholders (player/coin/bg).
    No external deps required.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)

    for p in assets_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            return

    _write_png(assets_dir / "player.png", _PNG_PLAYER)
    _write_png(assets_dir / "coin.png", _PNG_COIN)
    _write_png(assets_dir / "bg.png", _PNG_BG)


def _write_png(path: Path, b64: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64))
