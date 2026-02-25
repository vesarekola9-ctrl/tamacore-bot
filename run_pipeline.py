from __future__ import annotations

import os
import sys
import shutil
import runpy
from pathlib import Path
from datetime import datetime


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def exe_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def tools_dir(base: Path) -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS")) / "tools"
    return base / "tools"


def ensure_dirs(base: Path):
    (base / "input").mkdir(parents=True, exist_ok=True)
    (base / "output").mkdir(parents=True, exist_ok=True)
    (base / "output" / "reports").mkdir(parents=True, exist_ok=True)


def log_path(base: Path) -> Path:
    return base / "output" / "reports" / "run_log.txt"


def log(base: Path, msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)

    lp = log_path(base)
    lp.parent.mkdir(parents=True, exist_ok=True)
    prev = ""
    if lp.exists():
        prev = lp.read_text(encoding="utf-8", errors="ignore")
    lp.write_text(prev + line + "\n", encoding="utf-8")


def normalize_pdf_name(src: Path) -> str:
    # Keep stable name for tools that expect this filename.
    return "TamaCore_Game_Design_WITH_IMAGES.pdf"


def accept_drag_drop_inputs(base: Path):
    args = [Path(a) for a in sys.argv[1:] if str(a).strip()]
    if not args:
        return

    pdf = None
    for a in args:
        try:
            if a.exists() and a.is_file() and a.suffix.lower() == ".pdf":
                pdf = a
                break
        except Exception:
            pass

    if not pdf:
        log(base, f"No PDF drag-drop detected in args: {sys.argv[1:]}")
        return

    dst = base / "input" / normalize_pdf_name(pdf)
    try:
        shutil.copy2(pdf, dst)
        log(base, f"Drag-drop PDF copied -> {dst}")
    except Exception as e:
        log(base, f"FAILED to copy drag-drop PDF: {e}")


def run_script(base: Path, script: Path):
    if not script.exists():
        log(base, f"[skip] Missing tool: {script.name}")
        return

    log(base, f"> Running: {script.name}")
    runpy.run_path(str(script), run_name="__main__")
    log(base, f"[ok] {script.name}")


def main():
    base = exe_dir()

    # Portable: always resolve relative paths next to EXE
    os.chdir(base)
    ensure_dirs(base)

    accept_drag_drop_inputs(base)

    tdir = tools_dir(base)

    pipeline = [
        "make_folders.py",
        "extract_from_pdf.py",
        "asset_scan_and_map.py",
        "template_analyzer.py",
        "atlas_pack.py",
        "gdevelop_pack_generate.py",
        "game_scaffold_generate.py",
    ]

    log(base, f"Base dir: {base}")
    log(base, f"Tools dir: {tdir}")
    log(base, f"Frozen: {is_frozen()}")

    for name in pipeline:
        run_script(base, tdir / name)

    log(base, "DONE ✅  Check output/ folder")


if __name__ == "__main__":
    main()
