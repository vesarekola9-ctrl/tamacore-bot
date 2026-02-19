from pathlib import Path

OUT = Path("output") / "assets_raw"
DROP = OUT / "_drop_all"

CATS = ["ui", "cosmetics", "effects", "backgrounds", "pet", "_unmapped"]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DROP.mkdir(parents=True, exist_ok=True)
    for c in CATS:
        (OUT / c).mkdir(parents=True, exist_ok=True)
    print("[✓] Folders ready:", OUT)

if __name__ == "__main__":
    main()
