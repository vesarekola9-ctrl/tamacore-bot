from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from ..utils import is_image_file, read_json


def inspect_pack(pack_dir: Path) -> List[str]:
    errors: List[str] = []

    pack_json = pack_dir / "pack.json"
    assets_dir = pack_dir / "assets"

    if not pack_json.exists():
        return [f"Missing file: {pack_json}"]

    if not assets_dir.exists():
        return [f"Missing directory: {assets_dir}"]

    data = read_json(pack_json)
    if not isinstance(data, dict):
        return ["pack.json must be a JSON object"]

    errors.extend(_validate_root(data))
    errors.extend(_validate_assets(assets_dir))
    errors.extend(_validate_shop(data.get("shop")))
    errors.extend(_validate_levels(data.get("levels")))
    errors.extend(_validate_bounds(data.get("worldBounds"), data.get("display")))
    errors.extend(_validate_spawns(data))

    return errors


def _validate_root(data: Dict[str, object]) -> List[str]:
    errors: List[str] = []

    for key in ["name", "version", "scene", "display", "worldBounds", "camera", "ui", "levels", "shop"]:
        if key not in data:
            errors.append(f"pack.json: missing '{key}'")

    display = data.get("display")
    if not isinstance(display, dict):
        errors.append("pack.json: display must be an object")
    else:
        for key in ["mode", "virtualWidth", "virtualHeight"]:
            if key not in display:
                errors.append(f"pack.json: display missing '{key}'")

        mode = str(display.get("mode", "")).strip().lower()
        if mode not in {"portrait", "landscape"}:
            errors.append("pack.json: display.mode must be 'portrait' or 'landscape'")

        try:
            if int(display.get("virtualWidth", 0)) <= 0:
                errors.append("pack.json: display.virtualWidth must be > 0")
        except Exception:
            errors.append("pack.json: display.virtualWidth invalid")

        try:
            if int(display.get("virtualHeight", 0)) <= 0:
                errors.append("pack.json: display.virtualHeight must be > 0")
        except Exception:
            errors.append("pack.json: display.virtualHeight invalid")

    camera = data.get("camera")
    if not isinstance(camera, dict):
        errors.append("pack.json: camera must be an object")
    else:
        if not str(camera.get("followObject", "")).strip():
            errors.append("pack.json: camera.followObject missing")
        try:
            float(camera.get("lerp", 0.12))
        except Exception:
            errors.append("pack.json: camera.lerp invalid")

    ui = data.get("ui")
    if not isinstance(ui, dict):
        errors.append("pack.json: ui must be an object")
    else:
        if not str(ui.get("layer", "")).strip():
            errors.append("pack.json: ui.layer missing")

    return errors


def _validate_assets(assets_dir: Path) -> List[str]:
    errors: List[str] = []

    required_asset_groups = ["background", "player", "coin", "enemy", "ui"]
    for group in required_asset_groups:
        group_dir = assets_dir / group
        if not group_dir.exists():
            errors.append(f"Missing asset directory: assets/{group}")
            continue

        images = [p for p in group_dir.rglob("*") if p.is_file() and is_image_file(p)]
        if not images:
            errors.append(f"No images in: assets/{group}")

    return errors


def _validate_shop(shop: object) -> List[str]:
    errors: List[str] = []

    if not isinstance(shop, dict):
        return ["pack.json: shop must be an object"]

    currency_variable = str(shop.get("currencyVariable", "")).strip()
    if not currency_variable:
        errors.append("pack.json: shop.currencyVariable missing")

    upgrades = shop.get("upgrades", [])
    if not isinstance(upgrades, list) or not upgrades:
        errors.append("pack.json: shop.upgrades missing or empty")
        return errors

    seen_ids: Dict[str, int] = {}
    for i, item in enumerate(upgrades):
        if not isinstance(item, dict):
            errors.append(f"pack.json: upgrade {i} must be object")
            continue

        uid = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        cost = item.get("cost")
        effect = item.get("effect")

        if not uid:
            errors.append(f"pack.json: upgrade {i} missing id")
        else:
            seen_ids[uid] = seen_ids.get(uid, 0) + 1

        if not name:
            errors.append(f"pack.json: upgrade {i} missing name")

        try:
            if int(cost) < 0:
                errors.append(f"pack.json: upgrade {i} cost must be >= 0")
        except Exception:
            errors.append(f"pack.json: upgrade {i} invalid cost")

        if not isinstance(effect, dict) or not effect:
            errors.append(f"pack.json: upgrade {i} missing effect")
        else:
            for key, value in effect.items():
                if not str(key).strip():
                    errors.append(f"pack.json: upgrade {i} effect key invalid")
                if not isinstance(value, (int, float, str, bool)):
                    errors.append(f"pack.json: upgrade {i} effect '{key}' invalid type")

    for uid, count in seen_ids.items():
        if count > 1:
            errors.append(f"pack.json: duplicate upgrade id '{uid}'")

    return errors


def _validate_levels(levels: object) -> List[str]:
    errors: List[str] = []

    if not isinstance(levels, dict):
        return ["pack.json: levels must be an object"]

    required = ["count", "coinBase", "coinStep", "enemyBase", "enemyStep", "seed"]
    for key in required:
        if key not in levels:
            errors.append(f"pack.json: levels missing '{key}'")

    for key in ["count", "coinBase", "coinStep", "enemyBase", "enemyStep", "seed"]:
        try:
            value = int(levels.get(key, 0))
            if key != "seed" and value < 0:
                errors.append(f"pack.json: levels.{key} must be >= 0")
            if key == "count" and value <= 0:
                errors.append("pack.json: levels.count must be > 0")
        except Exception:
            errors.append(f"pack.json: levels.{key} invalid")

    return errors


def _validate_bounds(world_bounds: object, display: object) -> List[str]:
    errors: List[str] = []

    if not isinstance(world_bounds, dict):
        return ["pack.json: worldBounds must be an object"]
    if not isinstance(display, dict):
        return errors

    try:
        x_min = int(world_bounds.get("xMin", 0))
        y_min = int(world_bounds.get("yMin", 0))
        x_max = int(world_bounds.get("xMax", 0))
        y_max = int(world_bounds.get("yMax", 0))
    except Exception:
        return ["pack.json: worldBounds values invalid"]

    if x_max <= x_min:
        errors.append("pack.json: worldBounds xMax must be > xMin")
    if y_max <= y_min:
        errors.append("pack.json: worldBounds yMax must be > yMin")

    try:
        width = int(display.get("virtualWidth", 0))
        height = int(display.get("virtualHeight", 0))
        if x_max - x_min < width:
            errors.append("pack.json: worldBounds width smaller than display.virtualWidth")
        if y_max - y_min < height:
            errors.append("pack.json: worldBounds height smaller than display.virtualHeight")
    except Exception:
        pass

    return errors


def _validate_spawns(data: Dict[str, object]) -> List[str]:
    errors: List[str] = []

    for key in ["coinSpawn", "enemySpawn"]:
        spawn = data.get(key)
        if not isinstance(spawn, dict):
            errors.append(f"pack.json: {key} must be an object")
            continue

        if not str(spawn.get("objectName", "")).strip():
            errors.append(f"pack.json: {key}.objectName missing")

        for field in ["count", "minDistanceFromPlayer"]:
            try:
                if int(spawn.get(field, 0)) < 0:
                    errors.append(f"pack.json: {key}.{field} must be >= 0")
            except Exception:
                errors.append(f"pack.json: {key}.{field} invalid")

    return errors
