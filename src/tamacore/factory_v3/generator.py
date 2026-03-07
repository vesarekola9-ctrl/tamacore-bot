from __future__ import annotations

from pathlib import Path

from ..patch_gdevelop import factory_apply_catalog
from ..template_ops import copy_template, ensure_template_exists
from ..utils import read_json, write_json
from .catalog import build_catalog


def run_factory_v3(
    pack_dir: Path,
    template_dir: Path,
    game_dir: Path,
    scene_name: str = "Main",
    seed: int = 1337,
    with_demo_layout: bool = True,
) -> None:
    ensure_template_exists(template_dir)
    copy_template(template_dir, game_dir)

    catalog = build_catalog(pack_dir=pack_dir, game_dir=game_dir)

    game_json = game_dir / "game.json"

    factory_apply_catalog(
        game_json_path=game_json,
        catalog=catalog,
        scene_name=scene_name,
        seed=seed,
        with_demo_layout=with_demo_layout,
    )

    manifest = {
        "factory": "v3",
        "scene": scene_name,
        "seed": seed,
        "withDemoLayout": with_demo_layout,
        "catalogSummary": {
            "assetCount": len(catalog.get("assets", {})) if isinstance(catalog.get("assets"), dict) else 0,
            "objectCount": len(catalog.get("objects", [])) if isinstance(catalog.get("objects"), list) else 0,
            "instanceCount": len(catalog.get("instances", [])) if isinstance(catalog.get("instances"), list) else 0,
        },
    }

    write_json(game_dir / "FACTORY_MANIFEST.json", manifest)

    project = read_json(game_json)
    if not isinstance(project, dict):
        raise ValueError("game.json must remain a JSON object")

    write_json(game_json, project)

    print("[OK] Factory v3 generated:", game_dir)
