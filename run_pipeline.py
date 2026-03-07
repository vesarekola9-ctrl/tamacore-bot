from __future__ import annotations

import argparse
from pathlib import Path

from tamacore.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="TamaCore pipeline patcher")
    parser.add_argument("--assets-dir", default="assets")
    parser.add_argument("--template-dir", default="templates/gdevelop_template")
    parser.add_argument("--game-dir", required=True)
    args = parser.parse_args()

    run_pipeline(
        assets_dir=Path(args.assets_dir),
        template_dir=Path(args.template_dir),
        game_dir=Path(args.game_dir),
    )


if __name__ == "__main__":
    main()
