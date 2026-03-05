from __future__ import annotations

import argparse
from pathlib import Path

from src.tamacore.factory_v3.generator import run_factory_v3


def main() -> None:
    p = argparse.ArgumentParser(description="TamaCore V3 Factory Mode (assets pack -> full GDevelop game)")
    p.add_argument("--pack", required=True, help="Path to asset pack folder (assets/packs/<pack>)")
    p.add_argument("--template-dir", default="templates/gdevelop_template", help="GDevelop template directory")
    p.add_argument("--game-dir", required=True, help="Output game directory (e.g. ..\\tamacore-game)")

    # Optional overrides
    p.add_argument("--scene", default="Main", help="Scene name to patch (default Main)")
    p.add_argument("--seed", type=int, default=1337, help="Deterministic random seed for layout/spawns")
    p.add_argument("--with-demo-layout", action="store_true", help="Force a demo layout with objects placed")

    args = p.parse_args()

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
