from pathlib import Path
from datetime import datetime
import json
import shutil

try:
    from PIL import Image
except Exception:
    Image = None

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
    for d in CATS.values():
        d.mkdir(parents=True, exist_ok=True)

def img_meta(path: Path):
    if Image is None:
        return {"w": None, "h": None, "mode": None}
    try:
        with Image.open(path) as im:
            return {"w": im.size[0], "h": im.size[1], "mode": im.mode}
    except Exception as e:
        return {"w": None, "h": None, "mode": None, "error": str(e)}

def guess_category(name_lower: str) -> str:
    n = name_lower
    if any(k in n for k in ["button", "btn", "ui", "icon", "panel", "popup", "badge"]):
        return "ui"
    if any(k in n for k in ["hat", "glasses", "skin", "outfit", "cosmetic", "clothes"]):
        return "cosmetics"
    if any(k in n for k in ["effect", "spark", "heart", "splash", "rare", "wow", "burst"]):
        return "effects"
    if any(k in n for k in ["bg", "background", "scene", "room"]):
        return "backgrounds"
    if any(k in n for k in ["pet", "egg", "chonk", "fluff", "tama", "face", "reaction"]):
        return "pet"
    return "_unmapped"

def copy_file(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / src.name
    if dest.exists():
        i = 2
        while True:
            cand = dest_dir / f"{src.stem}_{i}{src.suffix}"
            if not cand.exists():
                dest = cand
                break
            i += 1
    shutil.copy2(src, dest)
    return dest

def main():
    ensure_dirs()

    if not DROP.exists():
        raise SystemExit(f"_drop_all missing: {DROP}")
    files = [p for p in DROP.iterdir() if p.is_file()]
    if not files:
        raise SystemExit(f"_drop_all on tyhjä: {DROP}")

    mapping = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {k: 0 for k in CATS},
        "items": [],
    }

    for f in sorted(files):
        cat = guess_category(f.name.lower())
        out_path = copy_file(f, CATS[cat])
        meta = img_meta(f)

        mapping["summary"][cat] += 1
        mapping["items"].append({
            "filename": f.name,
            "category": cat,
            "copied_to": str(out_path).replace("\\", "/"),
            "meta": meta,
        })

    out_json = OUT_ROOT / "mapping.json"
    out_json.write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    print("[✓] Asset scan complete")
    print(mapping["summary"])
    print("[✓] Wrote:", out_json)

if __name__ == "__main__":
    main()
