from pathlib import Path

OUT = Path("output")
ASSETS = OUT / "assets_raw"
DROP = ASSETS / "_drop_all"

CATS = ["ui", "cosmetics", "effects", "backgrounds", "pet", "_unmapped"]

def main():
    DROP.mkdir(parents=True, exist_ok=True)
    for c in CATS:
        (ASSETS / c).mkdir(parents=True, exist_ok=True)

    (OUT / "atlas").mkdir(parents=True, exist_ok=True)

    print("[✓] Folders ready")
    print("    input/  (place PDF here)")
    print(f"    {DROP}")

if __name__ == "__main__":
    main()
