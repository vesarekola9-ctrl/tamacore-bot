from pathlib import Path
import shutil

def main():
    raw = Path("output") / "assets_raw"
    for p in ["ui", "cosmetics", "effects", "backgrounds", "pet", "_drop_all"]:
        (raw / p).mkdir(parents=True, exist_ok=True)

    extracted = Path("output") / "extracted"
    drop = raw / "_drop_all"

    for folder in ["pages", "embedded"]:
        src = extracted / folder
        if not src.exists():
            continue
        for f in src.glob("*.*"):
            shutil.copy2(f, drop / f.name)

    print("[✓] Created output/assets_raw/* and copied files to _drop_all")

if __name__ == "__main__":
    main()
