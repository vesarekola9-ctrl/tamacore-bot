from __future__ import annotations
from pathlib import Path
from datetime import datetime

from tools.config import PATHS, ILLEGAL_CHARS, MAX_STEM_LEN, ALLOWED_EXT, MAX_FILE_MB, CATEGORY_ORDER

def validate_dir(d: Path, problems: list[str]):
    for f in sorted(d.iterdir()):
        if not f.is_file():
            continue

        # ext
        if f.suffix.lower() not in ALLOWED_EXT:
            problems.append(f"BAD_EXT: {f} (ext={f.suffix})")

        # illegal chars
        if any(ch in f.name for ch in ILLEGAL_CHARS):
            problems.append(f"ILLEGAL_CHAR: {f.name}")

        # stem length
        if len(f.stem) > MAX_STEM_LEN:
            problems.append(f"NAME_TOO_LONG: {f.name} (len={len(f.stem)})")

        # size
        size_mb = f.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_MB:
            problems.append(f"FILE_TOO_BIG: {f} ({size_mb:.2f} MB)")

def main():
    PATHS.reports_dir.mkdir(parents=True, exist_ok=True)

    problems: list[str] = []
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
        if d.exists():
            validate_dir(d, problems)

    report = PATHS.reports_dir / "soft_validation.txt"
    header = f"Soft validation report | {datetime.utcnow().isoformat()}Z\n"
    body = "OK\n" if not problems else "\n".join(problems) + "\n"
    report.write_text(header + body, encoding="utf-8")

    if problems:
        print("[!] Soft validation found issues. See:", report)
    else:
        print("[✓] Soft validation OK. Report:", report)

if __name__ == "__main__":
    main()
