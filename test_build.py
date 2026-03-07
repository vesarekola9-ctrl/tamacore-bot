from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from tamacore.factory_v3_1.export_validate import validate_exports
from tamacore.factory_v3_1.validate import validate_build_output


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_test_build_output"
EXPORTS = ROOT / "_test_exports"


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if EXPORTS.exists():
        shutil.rmtree(EXPORTS)

    cmd = [
        sys.executable,
        "-m",
        "tamacore.cli",
        "make-game",
        "--v31",
        "--v32",
        "--pack",
        str(ROOT / "assets" / "packs" / "demo_pack"),
        "--template",
        str(ROOT / "templates" / "gdevelop_template"),
        "--out",
        str(OUT),
        "--with-demo-layout",
        "--export-out",
        str(EXPORTS),
        "--export-web",
        "--export-zip",
    ]

    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise SystemExit(result.returncode)

    build_errors = validate_build_output(OUT)
    if build_errors:
        for err in build_errors:
            print(err)
        raise SystemExit(1)

    export_errors = validate_exports(EXPORTS)
    if export_errors:
        for err in export_errors:
            print(err)
        raise SystemExit(1)

    required = [
        OUT / "game.json",
        OUT / "catalog.json",
        OUT / "levels.json",
        OUT / "shop.json",
        OUT / "save.json",
        OUT / "FACTORY_MANIFEST.json",
        OUT / "BUILD_REPORT.txt",
        EXPORTS / "web" / "index.html",
        EXPORTS / "game.zip",
        EXPORTS / "EXPORT_REPORT.txt",
        EXPORTS / "export_manifest.json",
    ]

    missing = [str(p) for p in required if not p.exists()]
    if missing:
        for item in missing:
            print(f"Missing: {item}")
        raise SystemExit(1)

    print("[OK] test_build passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
