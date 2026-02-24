from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Paths:
    root: Path = Path(".")
    input_dir: Path = Path("input")
    output_dir: Path = Path("output")

    assets_raw: Path = Path("output/assets_raw")
    drop_all: Path = Path("output/assets_raw/_drop_all")
    mapping_json: Path = Path("output/assets_raw/mapping.json")

    atlas_dir: Path = Path("output/atlas")
    gdevelop_pack: Path = Path("output/gdevelop_pack")

    reports_dir: Path = Path("output/reports")
    scaffold_dir: Path = Path("output/scaffold")

    # categorized dirs
    ui: Path = Path("output/assets_raw/ui")
    cosmetics: Path = Path("output/assets_raw/cosmetics")
    effects: Path = Path("output/assets_raw/effects")
    backgrounds: Path = Path("output/assets_raw/backgrounds")
    pet: Path = Path("output/assets_raw/pet")
    unmapped: Path = Path("output/assets_raw/_unmapped")


PATHS = Paths()

# --- Naming system (PRO-safe) ---
ILLEGAL_CHARS = ['<','>','"',':','/','\\','|','?','*']
MAX_STEM_LEN = 64

RENAME_FORMAT = "{category}__{name}__v{version}"
DEFAULT_VERSION = 1

CATEGORY_ORDER = ["ui", "cosmetics", "effects", "backgrounds", "pet", "_unmapped"]

# --- Soft validation rules ---
ALLOWED_EXT = {".png", ".webp", ".jpg", ".jpeg"}
MAX_FILE_MB = 15
