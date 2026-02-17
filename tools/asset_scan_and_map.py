import json
import shutil
from pathlib import Path
from datetime import datetime

from PIL import Image

DROP = Path("output") / "assets_raw" / "_drop_all"
OUT_ROOT = Path("output") / "assets_raw"

CATS = {
    "ui": OUT_ROOT / "ui",
    "cosmetics": OUT_ROOT / "cosmetics",
    "effects": OUT_ROOT / "effects",
    "backgrounds": OUT_ROOT / "backgrounds",
    "pet": OUT_ROOT / "pet",
    "_unmapped": OUT_ROOT / "_unmapped",
}

def ensure_dirs():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for p in CATS.values():
        p.mkdir(parents=True, exist_ok=True)

def img_meta(path: Path):
    try:
        with Image.open(path) as im:
            return {"w": im.size[0], "h": im.size[1], "mode": im.mode}
    except Exception as e:
        return {"w": None, "h": None, "mode": None, "error": str(e)}

def guess_category(path: Path) -> str:
    name = path.name.lower()

    # Strong heuristic for your extracted PDF page renders
    if "page_02" in name or name.startswith("p02_"):
        return "ui"
    if "page_03" in name or name.startswith("p03_"):
        # mixed cosmetics/effects page -> store as cosmetics pack first
        return "cosmetics"

    # Fallback heuristics
    if any(k in name for k in ["button", "btn", "ui", "icon", "hud"]):
        return "ui"
    if any(k in name for k in ["hat", "glasses", "skin", "cosmetic", "clothes"]):
        return "cosmetics"
    if any(k in name for k in ["spark", "effect", "splash", "heart", "shine"]):
        return "effects"
    if any(k in name for k in ["bg", "background", "room", "scene"]):
        return "backgrounds"
    if any(k in name for k in ["pet", "fluff", "egg", "chonk", "skinny"]):
        return "pet"

    return "_unmapped"

def copy_file(src: Path, dest_dir: Path):
    dest = dest_dir / src.name
    if dest.exists():
        stem = src.stem
        suf = src.suffix
        i = 2
        while True:
            candidate = dest_dir / f"{stem}_{i}{suf}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1
    shutil.copy2(src, dest)
    return dest

def main():
    ensure_dirs()
    if not DROP.exists():
        raise SystemExit(f"Missing drop folder: {DROP} (aja ensin extract + make_folders)")

    files = [p for p in DROP.iterdir() if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]]
    if not files:
        raise SystemExit(f"_drop_all on tyhjä: {DROP}")

    mapping = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "drop_folder": str(DROP),
        "items": [],
        "summary": {k: 0 for k in CATS.keys()},
    }

    for f in sorted(files):
        meta = img_meta(f)
        cat = guess_category(f)
        out_path = copy_file(f, CATS[cat])

        mapping["items"].append({
            "source": str(f),
            "category": cat,
            "copied_to": str(out_path),
            "meta": meta,
            "note": "Likely a pack image; slicing later" if ("page_" in f.name.lower() or f.name.lower().startswith("p0")) else ""
        })
        mapping["summary"][cat] += 1

    out_json = OUT_ROOT / "mapping.json"
    out_json.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[✓] Asset scan complete")
    for k, v in mapping["summary"].items():
        print(f"  {k}: {v}")
    print(f"mapping -> {out_json}")

if __name__ == "__main__":
    main()
