from __future__ import annotations

import os
import sys
import runpy
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_tools_dir(base: Path) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "tools"
    return base / "tools"


def run_script(script: Path):
    if not script.exists():
        print(f"[skip] Missing: {script.name}")
        return

    print(f"> Running: {script.name}")
    runpy.run_path(str(script), run_name="__main__")


def main():
    base = get_base_dir()
    tools = get_tools_dir(base)

    os.chdir(base)

    (base / "input").mkdir(exist_ok=True)
    (base / "output").mkdir(exist_ok=True)

    pipeline = [
        "make_folders.py",
        "extract_from_pdf.py",
        "asset_scan_and_map.py",
        "template_analyzer.py",
        "atlas_pack.py",
        "gdevelop_pack_generate.py",
        "game_scaffold_generate.py",
    ]

    for name in pipeline:
        run_script(tools / name)

    print("\nDONE ✅")


if __name__ == "__main__":
    main()
