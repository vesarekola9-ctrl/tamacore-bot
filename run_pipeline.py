from __future__ import annotations

import argparse
from pathlib import Path

from src.tamacore.pipeline import run_pipeline


def main() -> None:
    p = argparse.ArgumentParser(description="TamaCore pipeline (template + assets + patch)")
    p.add_argument("--assets-dir", default="assets", help="Seed assets folder (default: assets)")
    p.add_argument("--template-dir", default="templates/gdevelop_template", help="Template dir")
    p.add_argument("--game-dir", default="../tamacore-game", help="Output game folder")

    args = p.parse_args()

    run_pipeline(
        assets_dir=Path(args.assets_dir),
        template_dir=Path(args.template_dir),
        game_dir=Path(args.game_dir),
    )


if __name__ == "__main__":
    main()
