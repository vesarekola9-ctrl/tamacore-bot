from pathlib import Path
import shutil

def main():
    inp = Path("input")
    out = Path("output")

    inp.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    # Analyzer folders
    (inp / "template_project").mkdir(parents=True, exist_ok=True)
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "scaffold").mkdir(parents=True, exist_ok=True)

    raw = out / "assets_raw"

    for p in ["ui", "cosmetics", "effects", "backgrounds", "pet", "_drop_all", "_unmapped"]:
        (raw / p).mkdir(parents=True, exist_ok=True)

    extracted = out / "extracted"
    drop = raw / "_drop_all"

    for folder in ["pages", "embedded"]:
        src = extracted / folder
        if not src.exists():
            continue

        for f in src.glob("*.*"):
            shutil.copy2(f, drop / f.name)

    print("[✓] Folder structure ready")

if __name__ == "__main__":
    main()
