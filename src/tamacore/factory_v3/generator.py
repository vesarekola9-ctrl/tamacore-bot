from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..template_ops import ensure_template_exists, copy_template
from ..utils import write_json, read_json
from ..patch_gdevelop import factory_apply_catalog
from .catalog import build_catalog, load_pack_meta
from .rules import factory_rules_patch


def run_factory_v3(
    pack_dir: Path,
    template_dir: Path,
    game_dir: Path,
    scene_name: str = "Main",
    seed: int = 1337,
    with_demo_layout: bool = False,
) -> None:
    if not pack_dir.exists():
        raise FileNotFoundError(f"Pack folder not found: {pack_dir}")

    ensure_template_exists(template_dir)

    # Copy template into output game
    copy_template(template_dir, game_dir)

    # Build catalog (copies images into game/assets/generated)
    catalog = build_catalog(pack_dir=pack_dir, game_dir=game_dir)

    # Patch game.json with catalog (objects + animations + instances + joystick + HUD + mobile control)
    game_json = game_dir / "game.json"
    factory_apply_catalog(
        game_json_path=game_json,
        catalog=catalog,
        scene_name=scene_name,
        seed=seed,
        with_demo_layout=with_demo_layout,
    )

    # Apply factory rules (enemy AI etc.)
    project = read_json(game_json)
    if isinstance(project, dict):
        scene = _find_scene(project, catalog)
        if isinstance(scene, dict):
            factory_rules_patch(project, scene)
            write_json(game_json, project)

    # Write factory manifest for debugging
    write_json(game_dir / "FACTORY_CATALOG.json", catalog)

    print("[OK] V3 Factory generated:", game_dir)
    print("[OK] Pack:", pack_dir)
    print("[NEXT] Open in GDevelop:", game_json)


def _find_scene(project: Dict[str, Any], catalog: Dict[str, Any]) -> Dict[str, Any] | None:
    target = "Main"
    pack = catalog.get("pack")
    if isinstance(pack, dict) and isinstance(pack.get("scene"), str):
        target = pack["scene"]

    layouts = project.get("layouts")
    if not isinstance(layouts, list):
        return None

    for l in layouts:
        if isinstance(l, dict) and l.get("name") == target:
            return l

    return layouts[0] if layouts and isinstance(layouts[0], dict) else None
