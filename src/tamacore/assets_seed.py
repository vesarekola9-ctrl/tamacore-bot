from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_assets_exist(assets_dir: Path) -> None:
    """
    If assets folder has no images, create placeholder player/coin/bg so pipeline always produces a game.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)

    for p in assets_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            return

    _make_placeholder(assets_dir / "player.png", "PLAYER", (256, 256))
    _make_placeholder(assets_dir / "coin.png", "COIN", (128, 128))
    _make_placeholder(assets_dir / "bg.png", "TAMACORE", (1024, 576))


def _make_placeholder(path: Path, label: str, size: tuple[int, int]) -> None:
    img = Image.new("RGBA", size, (16, 16, 20, 255))
    d = ImageDraw.Draw(img)

    # Border
    d.rectangle([6, 6, size[0] - 6, size[1] - 6], outline=(220, 220, 235, 255), width=4)

    # Diagonals
    d.line([0, 0, size[0], size[1]], fill=(80, 80, 95, 255), width=3)
    d.line([0, size[1], size[0], 0], fill=(80, 80, 95, 255), width=3)

    # Text
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    bbox = d.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size[0] - tw) // 2, (size[1] - th) // 2), label, fill=(245, 245, 250, 255), font=font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")
