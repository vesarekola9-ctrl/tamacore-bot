from __future__ import annotations

import argparse
from pathlib import Path

from src.tamacore.factory_v3.generator import run_factory_v3
from src.tamacore.factory_v3_1.generator import run_factory_v3_1


def main() -> None:
    p = argparse.ArgumentParser(description="TamaCore Factory Mode")
    p.add_argument("--pack", required=True, help="Path to asset pack folder (assets/packs/<pack>)")
    p.add_argument("--template-dir", default="templates/gdevelop_template", help="GDevelop template directory")
    p.add_argument("--game-dir", required=True, help="Output game directory (e.g. ..\\tamacore-game)")

    p.add_argument("--v31", action="store_true", help="Use v3.1 pro pack schema (levels/shop/ui/camera)")
    p.add_argument("--with-demo-layout", action="store_true", help="Place demo instances in scene")

    # v3 options
    p.add_argument("--scene", default="Main", help="Scene name to patch (v3 fallback)")
    p.add_argument("--seed", type=int, default=1337, help="Seed (v3 fallback)")

    args = p.parse_args()

    if args.v31:
        run_factory_v3_1(
            pack_dir=Path(args.pack),
            template_dir=Path(args.template_dir),
            game_dir=Path(args.game_dir),
            with_demo_layout=bool(args.with_demo_layout),
        )
    else:
        run_factory_v3(
            pack_dir=Path(args.pack),
            template_dir=Path(args.template_dir),
            game_dir=Path(args.game_dir),
            scene_name=str(args.scene),
            seed=int(args.seed),
            with_demo_layout=bool(args.with_demo_layout),
        )


if __name__ == "__main__":
    main()
