from __future__ import annotations

import argparse
from pathlib import Path

from src.tamacore.factory import generate_game
from src.tamacore.utils import read_json, write_json


def main() -> None:
    p = argparse.ArgumentParser(description="TamaCore AI Game Factory (v3)")
    p.add_argument("--spec", default="specs/my_game.json", help="Spec JSON path")
    p.add_argument("--out", default="../tamacore-game", help="Generated game output folder")
    p.add_argument("--template-dir", default="templates/gdevelop_template", help="GDevelop template folder")
    p.add_argument("--assets-dir", default="assets", help="Seed assets folder (optional)")
    p.add_argument("--provider", default="", help="Override provider (rules-v2)")
    p.add_argument("--seed", default="", help="Override seed")
    p.add_argument("--theme", default="", help="Override theme")
    p.add_argument("--difficulty", default="", help="Override difficulty")
    p.add_argument("--prompt", default="", help="Override prompt")

    args = p.parse_args()

    spec_path = Path(args.spec)

    # optional spec overrides
    if spec_path.exists():
        spec = read_json(spec_path)
        if isinstance(spec, dict):
            if args.provider:
                spec["provider"] = args.provider
            if args.seed:
                spec["seed"] = int(args.seed)
            if args.theme:
                spec["theme"] = args.theme
            if args.difficulty:
                spec["difficulty"] = args.difficulty
            if args.prompt:
                spec["prompt"] = args.prompt
            write_json(spec_path, spec)

    generate_game(
        spec_path=spec_path,
        out_dir=Path(args.out),
        template_dir=Path(args.template_dir),
        seed_assets_dir=Path(args.assets_dir),
    )


if __name__ == "__main__":
    main()
