import argparse
from pathlib import Path

from src.tamacore.pipeline import run_pipeline


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets-dir", default="assets", help="Input assets folder")
    ap.add_argument("--game-dir", required=True, help="Path to tamacore-game folder (create/update game.json inside)")
    args = ap.parse_args()

    run_pipeline(
        assets_dir=Path(args.assets_dir),
        game_dir=Path(args.game_dir),
    )


if __name__ == "__main__":
    main()
