from __future__ import annotations

import shutil
from pathlib import Path

from tamacore.factory_v3_1.validate import validate_build_output


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_test_build_output"


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)

    import subprocess
    import sys

    cmd = [
        sys.executable,
        "-m",
        "tamacore.cli",
        "build",
        "--v31",
        "--v32",
        "--pack",
        str(ROOT / "assets" / "packs" / "demo_pack"),
        "--template",
        str(ROOT / "templates" / "gdevelop_template"),
        "--out",
        str(OUT),
        "--with-demo-layout",
    ]

    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise SystemExit(result.returncode)

    errors = validate_build_output(OUT)
    if errors:
        for err in errors:
            print(err)
        raise SystemExit(1)

    print("[OK] test_build passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
