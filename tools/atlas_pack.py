from pathlib import Path
import json
from PIL import Image

SRC_DIRS = [
    Path("output/assets_raw/ui"),
    Path("output/assets_raw/cosmetics"),
    Path("output/assets_raw/effects"),
    Path("output/assets_raw/backgrounds"),
    Path("output/assets_raw/pet"),
]

OUT_DIR = Path("output/atlas")
OUT_PNG = OUT_DIR / "atlas.png"
OUT_JSON = OUT_DIR / "atlas.json"

PADDING = 4
MAX_ATLAS_W = 2048  # jos tulee liikaa, nosta 4096:een

def collect_images():
    items = []
    for d in SRC_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.png")):
            items.append(p)
        for p in sorted(d.glob("*.webp")):
            items.append(p)
        for p in sorted(d.glob("*.jpg")):
            items.append(p)
        for p in sorted(d.glob("*.jpeg")):
            items.append(p)
    return items

def shelf_pack(sizes, max_w):
    x = PADDING
    y = PADDING
    shelf_h = 0

    placements = []
    used_w = 0
    used_h = 0

    for (w, h) in sizes:
        if x + w + PADDING > max_w:
            x = PADDING
            y += shelf_h + PADDING
            shelf_h = 0

        placements.append((x, y))
        x += w + PADDING
        shelf_h = max(shelf_h, h)

        used_w = max(used_w, x)
        used_h = max(used_h, y + shelf_h + PADDING)

    atlas_w = min(max_w, max(256, ((used_w + 31) // 32) * 32))
    atlas_h = max(256, ((used_h + 31) // 32) * 32)
    return placements, atlas_w, atlas_h

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    paths = collect_images()
    if not paths:
        raise SystemExit("Ei kuvia atlasointiin. Aja ensin: extract -> scan_and_map")

    # load & normalize to RGBA
    loaded = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        loaded.append((p, im))

    # sort big first helps packing
    loaded.sort(key=lambda t: (t[1].size[1] * t[1].size[0]), reverse=True)

    sizes = [im.size for _, im in loaded]
    placements, atlas_w, atlas_h = shelf_pack(sizes, MAX_ATLAS_W)

    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))

    frames = {}
    for (p, im), (x, y) in zip(loaded, placements):
        atlas.alpha_composite(im, (x, y))
        name = p.stem  # frame-name
        frames[f"{name}.png"] = {
            "frame": {"x": x, "y": y, "w": im.size[0], "h": im.size[1]},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": im.size[0], "h": im.size[1]},
            "sourceSize": {"w": im.size[0], "h": im.size[1]},
        }

    atlas.save(OUT_PNG)

    data = {
        "frames": frames,
        "meta": {
            "app": "tamacore-bot",
            "version": "1.0",
            "image": OUT_PNG.name,
            "size": {"w": atlas_w, "h": atlas_h},
            "scale": "1",
        }
    }
    OUT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print("[✓] Atlas ready:")
    print("   ", OUT_PNG)
    print("   ", OUT_JSON)
    print(f"[i] Frames: {len(frames)}")

if __name__ == "__main__":
    main()
