from __future__ import annotations
from pathlib import Path
import hashlib

from tools.config import PATHS, CATEGORY_ORDER

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    cat_dirs = {
        "ui": PATHS.ui,
        "cosmetics": PATHS.cosmetics,
        "effects": PATHS.effects,
        "backgrounds": PATHS.backgrounds,
        "pet": PATHS.pet,
        "_unmapped": PATHS.unmapped,
    }

    seen: dict[str, Path] = {}
    removed = 0

    for cat in CATEGORY_ORDER:
        d = cat_dirs[cat]
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if not f.is_file():
                continue
            key = sha256(f)
            if key in seen:
                f.unlink()
                removed += 1
            else:
                seen[key] = f

    print(f"[✓] Dedupe done. Removed duplicates: {removed}")

if __name__ == "__main__":
    main()
