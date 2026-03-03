import argparse
from pathlib import Path

from src.tamacore.pipeline import run_pipeline


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets-dir", default="assets", help="Input assets folder (png/jpg/webp)")
    ap.add_argument("--template-dir", default="templates/gdevelop_template", help="GDevelop template project folder")
    ap.add_argument("--game-dir", required=True, help="Output game folder (will be created/overwritten)")
    args = ap.parse_args()

    run_pipeline(
        assets_dir=Path(args.assets_dir),
        template_dir=Path(args.template_dir),
        game_dir=Path(args.game_dir),
    )


if __name__ == "__main__":
    main()
