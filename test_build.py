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
BUNDLE = ROOT / "_test_release_bundle"


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if EXPORTS.exists():
        shutil.rmtree(EXPORTS)
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)

    bundle_zip = ROOT / "_test_release_bundle.zip"
    if bundle_zip.exists():
        bundle_zip.unlink()

    cmd = [
        sys.executable,
        "-m",
        "tamacore.cli",
        "ai-make-game",
        "--out-pack",
        str(ROOT / "assets" / "packs" / "ai_test_pack"),
        "--template",
        str(ROOT / "templates" / "gdevelop_template"),
        "--out-game",
        str(OUT),
        "--export-out",
        str(EXPORTS),
        "--bundle-out",
        str(BUNDLE),
        "--shop-count",
        "5",
        "--foods",
        "5",
        "--cosmetics",
        "5",
        "--with-demo-layout",
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
        OUT / "pet_runtime.json",
        OUT / "FACTORY_MANIFEST.json",
        OUT / "BUILD_REPORT.txt",
        EXPORTS / "web" / "index.html",
        EXPORTS / "game.zip",
        EXPORTS / "EXPORT_REPORT.txt",
        EXPORTS / "export_manifest.json",
        BUNDLE / "README_RELEASE.txt",
        BUNDLE / "game" / "game.json",
        BUNDLE / "exports" / "EXPORT_REPORT.txt",
        ROOT / "_test_release_bundle.zip",
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
