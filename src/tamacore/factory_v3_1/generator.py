from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..template_ops import ensure_template_exists, copy_template
from ..utils import write_json, read_json
from ..patch_gdevelop import factory_apply_catalog
from ..factory_v3.catalog import build_catalog
from .schema import load_pack_cfg
from .levels import generate_levels
from .shop import write_shop
from .patch_rules import apply_v3_1_rules


def run_factory_v3_1(pack_dir: Path, template_dir: Path, game_dir: Path, with_demo_layout: bool = True) -> None:
    cfg = load_pack_cfg(pack_dir)

    ensure_template_exists(template_dir)
    copy_template(template_dir, game_dir)

    # Build catalog (copies images into game/assets/generated)
    catalog = build_catalog(pack_dir=pack_dir, game_dir=game_dir)

    # Patch objects/resources + joystick + base score loop
    game_json = game_dir / "game.json"
    factory_apply_catalog(
        game_json_path=game_json,
        catalog=catalog,
        scene_name=cfg.scene,
        seed=cfg.levels.seed,
        with_demo_layout=with_demo_layout,
    )

    # Generate levels + shop outputs into game_dir
    levels = generate_levels(cfg, game_dir)
    shop = write_shop(cfg, game_dir)

    # Apply v3.1 rules into events (camera follow, UI anchor, spawns, coins/hp)
    project = read_json(game_json)
    if isinstance(project, dict):
        scene = _find_scene(project, cfg.scene)
        if isinstance(scene, dict):
            apply_v3_1_rules(project, scene, cfg)
            write_json(game_json, project)

    # Write manifest for debugging / future automation
    write_json(
        game_dir / "FACTORY_MANIFEST.json",
        {
            "factory": "v3.1",
            "pack": {"name": cfg.name, "version": cfg.version, "scene": cfg.scene},
            "display": {"mode": cfg.display.mode, "virtualWidth": cfg.display.virtualWidth, "virtualHeight": cfg.display.virtualHeight},
            "worldBounds": {"xMin": cfg.worldBounds.xMin, "yMin": cfg.worldBounds.yMin, "xMax": cfg.worldBounds.xMax, "yMax": cfg.worldBounds.yMax},
            "levels": [l["id"] for l in levels],
            "shopUpgrades": [u["id"] for u in shop.get("upgrades", [])] if isinstance(shop, dict) else [],
        },
    )

    print("[OK] V3.1 Factory generated:", game_dir)
    print("[OK] Wrote levels:", game_dir / "levels")
    print("[OK] Wrote shop:", game_dir / "shop.json")
    print("[NEXT] Open in GDevelop:", game_json)


def _find_scene(project: Dict[str, Any], name: str) -> Dict[str, Any] | None:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == name:
            return l
    return layouts[0] if isinstance(layouts[0], dict) else None
