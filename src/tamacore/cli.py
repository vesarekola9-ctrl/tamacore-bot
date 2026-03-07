from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .factory_v3_1.generator import run_factory_v3_1


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    p = argparse.ArgumentParser(prog="tamacore", description="TamaCore AI Game Factory")
    sub = p.add_subparsers(dest="cmd", required=True)

    # tamacore build ...
    b = sub.add_parser("build", help="Build a GDevelop game from a pack + template")
    b.add_argument("--pack", required=True, help="Pack dir (e.g. assets/packs/demo_pack)")
    b.add_argument("--template", default="templates/gdevelop_template", help="Template dir")
    b.add_argument("--out", required=True, help="Output game dir (e.g. ../tamacore-game)")
    b.add_argument(
        "--with-demo-layout",
        action="store_true",
        help="Place demo instances into scene",
    )
    b.add_argument(
        "--v31",
        action="store_true",
        help="Use v3.1 schema (recommended)",
    )
    b.add_argument(
        "--v32",
        action="store_true",
        help="Enable v3.2 runtime features (shop/upgrades/level injection)",
    )

    args = p.parse_args(argv)

    if args.cmd == "build":
        pack_dir = Path(args.pack)
        template_dir = Path(args.template)
        out_dir = Path(args.out)

        # v3.2 = v3.1 + extra patching (implemented inside generator if enabled)
        run_factory_v3_1(
            pack_dir=pack_dir,
            template_dir=template_dir,
            game_dir=out_dir,
            with_demo_layout=bool(args.with_demo_layout),
            enable_v3_2=bool(args.v32),
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
