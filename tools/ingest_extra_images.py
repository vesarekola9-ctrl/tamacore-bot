from pathlib import Path
import shutil

EXTRA = Path("input") / "extra_images"
DROP = Path("output") / "assets_raw" / "_drop_all"
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

def main():
    DROP.mkdir(parents=True, exist_ok=True)

    if not EXTRA.exists():
        print("[i] input/extra_images not found (ok).")
        return

    copied = 0
    for p in EXTRA.rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED:
            dest = DROP / p.name
            if dest.exists():
                i = 2
                while True:
                    cand = DROP / f"{p.stem}_{i}{p.suffix.lower()}"
                    if not cand.exists():
                        dest = cand
                        break
                    i += 1
            shutil.copy2(p, dest)
            copied += 1

    print(f"[✓] Ingested {copied} extra images -> {DROP}")

if __name__ == "__main__":
    main()
