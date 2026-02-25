from pathlib import Path
import shutil

def main():
    # Base dirs
    inp = Path("input")
    out = Path("output")
    inp.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    # NEW: template project folder for analyzer
    (inp / "template_project").mkdir(parents=True, exist_ok=True)

    # NEW: analyzer outputs
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "scaffold").mkdir(parents=True, exist_ok=True)

    # Raw asset structure (existing + _unmapped)
    raw = out / "assets_raw"
    for p in ["ui", "cosmetics", "effects", "backgrounds", "pet", "_drop_all", "_unmapped"]:
        (raw / p).mkdir(parents=True, exist_ok=True)

    # Existing: copy extracted images into _drop_all
    extracted = out / "extracted"
    drop = raw / "_drop_all"

    for folder in ["pages", "embedded"]:
        src = extracted / folder
        if not src.exists():
            continue
        for f in src.glob("*.*"):
            shutil.copy2(f, drop / f.name)

    print("[✓] Folders ready")
    print(f"  - {inp/'template_project'}  (put your reference GDevelop project here)")
    print(f"  - {out/'reports'}          (analyzer outputs)")
    print(f"  - {out/'scaffold'}         (conventions + scaffold)")
    print("[✓] output/assets_raw/* created and extracted files copied to _drop_all (if any)")

if __name__ == "__main__":
    main()
