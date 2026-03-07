from __future__ import annotations

import argparse
from pathlib import Path

from tamacore.patch_gdevelop import patch_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch shop + UI into an existing GDevelop game.json")
    parser.add_argument("--game-dir", required=True, help="Existing game directory")
    parser.add_argument("--scene", default="Main", help="Scene/layout name")
    args = parser.parse_args()

    game_dir = Path(args.game_dir)
    game_json = game_dir / "game.json"

    patch_project(
        game_json_path=game_json,
        image_map=None,
        scene_name=str(args.scene),
    )

    print("[OK] Shop patched:", game_json)


if __name__ == "__main__":
    main()
