from __future__ import annotations
from pathlib import Path
import re

from tools.config import PATHS, ILLEGAL_CHARS, MAX_STEM_LEN, RENAME_FORMAT, DEFAULT_VERSION, CATEGORY_ORDER

def safe_stem(s: str) -> str:
    s = s.strip()
    for ch in ILLEGAL_CHARS:
        s = s.replace(ch, "_")
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)  # keep safe
    s = re.sub(r"_+", "_", s)
    s = s.lower()
    return s[:MAX_STEM_LEN]

def rename_in_dir(category: str, d: Path, version: int = DEFAULT_VERSION) -> int:
    if not d.exists():
        return 0
    renamed = 0
    for f in sorted(d.iterdir()):
        if not f.is_file():
            continue
        stem = safe_stem(f.stem)
        new_stem = RENAME_FORMAT.format(category=category, name=stem, version=str(version).zfill(3))
        new_path = f.with_name(new_stem + f.suffix.lower())

        if new_path.name == f.name:
            continue

        # avoid collisions
        i = 2
        cand = new_path
        while cand.exists():
            cand = f.with_name(f"{new_stem}_{i}{f.suffix.lower()}")
            i += 1

        f.rename(cand)
        renamed += 1

    return renamed

def main():
    total = 0
    cat_dirs = {
        "ui": PATHS.ui,
        "cosmetics": PATHS.cosmetics,
        "effects": PATHS.effects,
        "backgrounds": PATHS.backgrounds,
        "pet": PATHS.pet,
        "_unmapped": PATHS.unmapped,
    }
    for cat in CATEGORY_ORDER:
        d = cat_dirs[cat]
        total += rename_in_dir(cat, d, DEFAULT_VERSION)

    print(f"[✓] Naming PRO done. Renamed files: {total}")

if __name__ == "__main__":
    main()
