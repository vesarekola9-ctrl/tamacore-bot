from __future__ import annotations

import shutil
from pathlib import Path

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def collect_images(assets_dir: Path) -> list[Path]:
    imgs: list[Path] = []
    for p in assets_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            imgs.append(p)
    return sorted(imgs)


def copy_images_into_game(
    assets_dir: Path,
    game_dir: Path,
    target_rel_dir: str = "assets/generated",
) -> dict[str, str]:
    """
    Copies images into game_dir/target_rel_dir.
    Returns mapping: logical_name -> relative posix path.
    """
    out_dir = game_dir / target_rel_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    for src in collect_images(assets_dir):
        dst = out_dir / src.name
        shutil.copy2(src, dst)
        logical = src.stem.lower()
        mapping[logical] = str(Path(target_rel_dir) / dst.name).replace("\\", "/")

    return mapping
