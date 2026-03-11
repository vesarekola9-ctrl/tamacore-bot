from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..factory_v3.catalog import build_catalog
from ..patch_gdevelop import factory_apply_catalog
from ..template_ops import copy_template, ensure_template_exists
from ..utils import read_json, write_json
from .build_report import write_build_report
from .character_builder import apply_character_animations
from .cosmetics_runtime import write_cosmetics_runtime
from .foods_runtime import write_foods_runtime
from .levels import generate_levels
from .patch_rules import apply_v3_1_rules
from .pet_runtime import write_pet_runtime
from .save_runtime import write_save_runtime
from .save_system import write_save_schema
from .schema import PackCfg, load_pack_cfg
from .shop import write_shop
from .v3_2_patch import apply_v3_2_runtime
from .validate import validate_build_output


def run_factory_v3_1(
    pack_dir: Path,
    template_dir: Path,
    game_dir: Path,
    with_demo_layout: bool = True,
    enable_v3_2: bool = False,
) -> None:
    cfg = load_pack_cfg(pack_dir)

    ensure_template_exists(template_dir)
    copy_template(template_dir, game_dir)

    catalog = build_catalog(pack_dir=pack_dir, game_dir=game_dir)

    game_json = game_dir / "game.json"

    factory_apply_catalog(
        game_json_path=game_json,
        catalog=catalog,
        scene_name=cfg.scene,
        seed=cfg.levels.seed,
        with_demo_layout=with_demo_layout,
    )

    levels = generate_levels(cfg, game_dir)
    shop = write_shop(cfg, game_dir)
    save_data = write_save_schema(game_dir, shop)
    pet_runtime = write_pet_runtime(pack_dir, game_dir)
    save_runtime = write_save_runtime(game_dir)
    cosmetics_runtime = write_cosmetics_runtime(pack_dir, game_dir)
    foods_runtime = write_foods_runtime(pack_dir, game_dir)

    project = read_json(game_json)
    if not isinstance(project, dict):
        raise ValueError("game.json must be a JSON object after catalog patching")

    scene = _find_scene(project, cfg.scene)
    if not isinstance(scene, dict):
        raise ValueError(f"Scene '{cfg.scene}' was not found from game.json")

    apply_v3_1_rules(project, scene, cfg)
    _ensure_shop_owned_vars(project, shop)
    apply_character_animations(project, scene, game_dir)

    if enable_v3_2:
        apply_v3_2_runtime(project, scene, cfg, game_dir)

    write_json(game_json, project)

    manifest = _build_manifest(
        cfg,
        levels,
        shop,
        catalog,
        save_data,
        pet_runtime,
        save_runtime,
        cosmetics_runtime,
        foods_runtime,
        enable_v3_2,
    )
    write_json(game_dir / "FACTORY_MANIFEST.json", manifest)

    errors = validate_build_output(game_dir)
    if errors:
        raise RuntimeError("Build validation failed:\n" + "\n".join(f"- {item}" for item in errors))

    write_build_report(
        game_dir=game_dir,
        pack_name=cfg.name,
        factory_version="v3.2" if enable_v3_2 else "v3.1",
        manifest=manifest,
        catalog=catalog,
        levels=levels,
        shop=shop,
    )

    print("[OK] Factory generated:", game_dir)
    print("[NEXT] Open in GDevelop:", game_json)


def _find_scene(project: Dict[str, Any], name: str) -> Dict[str, Any] | None:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None

    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == name:
            return layout

    first = layouts[0]
    return first if isinstance(first, dict) else None


def _ensure_global_var(project: Dict[str, Any], name: str, value: float) -> None:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    for item in vars_:
        if isinstance(item, dict) and item.get("name") == name:
            item.setdefault("type", "number")
            item.setdefault("children", [])
            if "value" not in item:
                item["value"] = value
            return

    vars_.append({"name": name, "type": "number", "value": value, "children": []})


def _ensure_shop_owned_vars(project: Dict[str, Any], shop: Dict[str, Any]) -> None:
    upgrades = shop.get("upgrades", [])
    if not isinstance(upgrades, list):
        return

    for item in upgrades:
        if not isinstance(item, dict):
            continue
        owned_var = str(item.get("ownedVariable", "")).strip()
        if owned_var:
            _ensure_global_var(project, owned_var, 0)


def _build_manifest(
    cfg: PackCfg,
    levels: List[Dict[str, Any]],
    shop: Dict[str, Any],
    catalog: Dict[str, Any],
    save_data: Dict[str, Any],
    pet_runtime: Dict[str, Any],
    save_runtime: Dict[str, Any],
    cosmetics_runtime: Dict[str, Any],
    foods_runtime: Dict[str, Any],
    enable_v3_2: bool,
) -> Dict[str, Any]:
    return {
        "factory": "v3.2" if enable_v3_2 else "v3.1",
        "pack": {
            "name": cfg.name,
            "version": cfg.version,
            "scene": cfg.scene,
        },
        "display": {
            "mode": cfg.display.mode,
            "virtualWidth": cfg.display.virtualWidth,
            "virtualHeight": cfg.display.virtualHeight,
        },
        "worldBounds": {
            "xMin": cfg.worldBounds.xMin,
            "yMin": cfg.worldBounds.yMin,
            "xMax": cfg.worldBounds.xMax,
            "yMax": cfg.worldBounds.yMax,
        },
        "camera": {
            "followObject": cfg.camera.followObject,
            "lerp": cfg.camera.lerp,
        },
        "ui": {
            "layer": cfg.ui.layer,
            "hud": {
                "objectName": cfg.ui.hud.objectName,
                "anchor": cfg.ui.hud.anchor,
                "marginX": cfg.ui.hud.marginX,
                "marginY": cfg.ui.hud.marginY,
            },
            "joystick": {
                "objectName": cfg.ui.joystick.objectName,
                "anchor": cfg.ui.joystick.anchor,
                "marginX": cfg.ui.joystick.marginX,
                "marginY": cfg.ui.joystick.marginY,
            },
        },
        "spawns": {
            "coin": {
                "objectName": cfg.coinSpawn.objectName,
                "count": cfg.coinSpawn.count,
                "enabled": cfg.coinSpawn.enabled,
                "respawnOnCollect": cfg.coinSpawn.respawnOnCollect,
                "minDistanceFromPlayer": cfg.coinSpawn.minDistanceFromPlayer,
            },
            "enemy": {
                "objectName": cfg.enemySpawn.objectName,
                "count": cfg.enemySpawn.count,
                "enabled": cfg.enemySpawn.enabled,
                "respawnOnCollect": cfg.enemySpawn.respawnOnCollect,
                "minDistanceFromPlayer": cfg.enemySpawn.minDistanceFromPlayer,
            },
        },
        "levels": [level.get("id", f"level_{i + 1}") for i, level in enumerate(levels)],
        "shopUpgrades": [u.get("id", f"upgrade_{i + 1}") for i, u in enumerate(shop.get("upgrades", []))],
        "catalogSummary": _catalog_summary(catalog),
        "save": save_data,
        "petRuntime": pet_runtime,
        "saveRuntime": save_runtime,
        "cosmeticsRuntime": cosmetics_runtime,
        "foodsRuntime": foods_runtime,
    }


def _catalog_summary(catalog: Dict[str, Any]) -> Dict[str, Any]:
    assets = catalog.get("assets", {})
    objects = catalog.get("objects", [])
    instances = catalog.get("instances", [])

    return {
        "assetCount": len(assets) if isinstance(assets, dict) else 0,
        "objectCount": len(objects) if isinstance(objects, list) else 0,
        "instanceCount": len(instances) if isinstance(instances, list) else 0,
    }
