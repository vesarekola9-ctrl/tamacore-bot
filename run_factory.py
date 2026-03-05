from __future__ import annotations

import argparse
from pathlib import Path

from src.tamacore.factory import generate_game


def main() -> None:
    p = argparse.ArgumentParser(description="TamaCore AI Game Factory (v1)")

    p.add_argument(
        "--spec",
        default="specs/my_game.json",
        help="Path to game spec JSON (default: specs/my_game.json)",
    )
    p.add_argument(
        "--out",
        default="../tamacore-game",
        help="Output folder for generated game (default: ../tamacore-game)",
    )
    p.add_argument(
        "--template-dir",
        default="templates/gdevelop_template",
        help="GDevelop template folder (default: templates/gdevelop_template)",
    )
    p.add_argument(
        "--assets-dir",
        default="assets",
        help="Seed assets folder (default: assets) - if missing, factory will use template assets/generated if present",
    )

    args = p.parse_args()

    generate_game(
        spec_path=Path(args.spec),
        out_dir=Path(args.out),
        template_dir=Path(args.template_dir),
        seed_assets_dir=Path(args.assets_dir),
    )


if __name__ == "__main__":
    main()
