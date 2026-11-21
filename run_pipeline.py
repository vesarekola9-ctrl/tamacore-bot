from __future__ import annotations

import argparse
from pathlib import Path

from tamacore.factory_v3_1.ai_pack_generator import generate_ai_pack
from tamacore.factory_v3_1.generator import run_factory_v3_1


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a complete TamaCore GDevelop game")
    parser.add_argument("--assets-dir", default="assets")
    parser.add_argument("--template-dir", default="templates/gdevelop_template")
    parser.add_argument("--game-dir", required=True)
    args = parser.parse_args()

    game_dir = Path(args.game_dir)
    pack_dir = game_dir.parent / (game_dir.name + "_pack")
    generate_ai_pack(pack_dir)
    run_factory_v3_1(
        pack_dir=pack_dir,
        template_dir=Path(args.template_dir),
        game_dir=game_dir,
        with_demo_layout=True,
    )
    print(f"[OK] TamaCore GDevelop game generated: {game_dir}")


if __name__ == "__main__":
    main()
