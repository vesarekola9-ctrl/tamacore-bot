from __future__ import annotations

import argparse
from pathlib import Path

from tamacore.factory_v3.generator import run_factory_v3
from tamacore.factory_v3_1.generator import run_factory_v3_1


def main() -> None:
    parser = argparse.ArgumentParser(description="TamaCore Factory Runner")
    parser.add_argument("--pack", required=True, help="Pack directory")
    parser.add_argument("--template-dir", default="templates/gdevelop_template", help="Template directory")
    parser.add_argument("--game-dir", required=True, help="Output game directory")
    parser.add_argument("--with-demo-layout", action="store_true")
    parser.add_argument("--v31", action="store_true")
    parser.add_argument("--v32", action="store_true")
    parser.add_argument("--scene", default="Main")
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    if args.v31 or args.v32:
        run_factory_v3_1(
            pack_dir=Path(args.pack),
            template_dir=Path(args.template_dir),
            game_dir=Path(args.game_dir),
            with_demo_layout=bool(args.with_demo_layout),
            enable_v3_2=bool(args.v32),
        )
        return

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
