from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json

Json = Dict[str, Any]


def validate_build_output(game_dir: Path) -> List[str]:
    errors: List[str] = []

    required_files = [
        game_dir / "game.json",
        game_dir / "catalog.json",
        game_dir / "levels.json",
        game_dir / "shop.json",
        game_dir / "save.json",
        game_dir / "pet_runtime.json",
        game_dir / "save_runtime.json",
        game_dir / "FACTORY_MANIFEST.json",
    ]

    for path in required_files:
        if not path.exists():
            errors.append(f"Missing file: {path.name}")

    if errors:
        return errors

    game = _load_json(game_dir / "game.json", errors, "game.json")
    catalog = _load_json(game_dir / "catalog.json", errors, "catalog.json")
    levels = _load_json(game_dir / "levels.json", errors, "levels.json")
    shop = _load_json(game_dir / "shop.json", errors, "shop.json")
    save_data = _load_json(game_dir / "save.json", errors, "save.json")
    pet_runtime = _load_json(game_dir / "pet_runtime.json", errors, "pet_runtime.json")
    save_runtime = _load_json(game_dir / "save_runtime.json", errors, "save_runtime.json")
    manifest = _load_json(game_dir / "FACTORY_MANIFEST.json", errors, "FACTORY_MANIFEST.json")

    if isinstance(game, dict):
        _validate_game(game, errors)
    if isinstance(catalog, dict):
        _validate_catalog(catalog, errors)
    if isinstance(levels, list):
        _validate_levels(levels, errors)
    else:
        errors.append("levels.json: must be a list")
    if isinstance(shop, dict):
        _validate_shop(shop, errors)
    if isinstance(save_data, dict):
        _validate_save(save_data, shop if isinstance(shop, dict) else {}, errors)
    if isinstance(pet_runtime, dict):
        _validate_pet_runtime(pet_runtime, errors)
    if isinstance(save_runtime, dict):
        _validate_save_runtime(save_runtime, errors)
    if isinstance(manifest, dict):
        _validate_manifest(manifest, errors)

    build_report = game_dir / "BUILD_REPORT.txt"
    if build_report.exists():
        text = build_report.read_text(encoding="utf-8")
        if "TamaCore Build Report" not in text:
            errors.append("BUILD_REPORT.txt: invalid header")
    else:
        errors.append("Missing file: BUILD_REPORT.txt")

    return errors


def _validate_game(game: Json, errors: List[str]) -> None:
    layouts = game.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        errors.append("game.json: layouts missing")
        return

    main = None
    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == "Main":
            main = layout
            break

    if not isinstance(main, dict):
        main = layouts[0] if layouts and isinstance(layouts[0], dict) else None

    if not isinstance(main, dict):
        errors.append("game.json: main scene missing")
        return

    objects = main.get("objects")
    instances = main.get("instances")
    events = main.get("events")

    if not isinstance(objects, list):
        errors.append("game.json: scene objects missing")
        return
    if not isinstance(instances, list):
        errors.append("game.json: scene instances missing")
        return
    if not isinstance(events, list):
        errors.append("game.json: scene events missing")
        return

    object_names = {obj.get("name") for obj in objects if isinstance(obj, dict)}
    instance_names = {(inst.get("objectName") or inst.get("name")) for inst in instances if isinstance(inst, dict)}

    for name in {"Player", "Coin", "Enemy", "TouchJoystick", "ShopButton", "ShopPanel", "CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel"}:
        if name not in object_names:
            errors.append(f"game.json: missing object '{name}'")

    for name in {"Player", "TouchJoystick", "ShopButton", "ShopPanel", "CoinsLabel", "SpeedLabel", "LevelLabel", "GoalLabel"}:
        if name not in instance_names:
            errors.append(f"game.json: missing instance '{name}'")

    markers = set()
    for event in events:
        if isinstance(event, dict) and event.get("type") == "BuiltinCommonInstructions::Comment":
            comment = str(event.get("comment", ""))
            if comment:
                markers.add(comment)

    if not any("TAMACORE_AUTOGEN_PACK_SHOP_V3_3" in marker for marker in markers):
        errors.append("game.json: pack shop events marker missing")
    if not any("TAMACORE_AUTOGEN_RUNTIME_V3_6" in marker for marker in markers):
        errors.append("game.json: runtime v3.6 marker missing")

    variables = game.get("variables")
    if not isinstance(variables, list):
        errors.append("game.json: global variables missing")
        return

    variable_names = {var.get("name") for var in variables if isinstance(var, dict)}
    for name in [
        "Coins", "Speed", "PlayerMaxSpeed", "ShopOpen", "LevelIndex", "LevelCount", "CoinTarget", "EnemyTarget",
        "CoinsCollected", "EnemiesHit", "LevelComplete", "GameComplete", "SaveLoaded", "SaveDirty",
        "PetHunger", "PetEnergy", "PetMood", "PetCleanliness", "PetState", "FeedCost", "CleanCost",
    ]:
        if name not in variable_names:
            errors.append(f"game.json: missing global variable '{name}'")


def _validate_catalog(catalog: Json, errors: List[str]) -> None:
    assets = catalog.get("assets")
    objects = catalog.get("objects")
    instances = catalog.get("instances")

    if not isinstance(assets, dict):
        errors.append("catalog.json: assets missing")
    if not isinstance(objects, list):
        errors.append("catalog.json: objects missing")
    if not isinstance(instances, list):
        errors.append("catalog.json: instances missing")

    if isinstance(assets, dict) and len(assets) == 0:
        errors.append("catalog.json: assets empty")

    if isinstance(objects, list):
        names = {obj.get("name") for obj in objects if isinstance(obj, dict)}
        for name in ["Player", "Coin", "Enemy", "TouchJoystick"]:
            if name not in names:
                errors.append(f"catalog.json: missing object '{name}'")


def _validate_levels(levels: List[Json], errors: List[str]) -> None:
    if not levels:
        errors.append("levels.json: empty")
        return
    for index, item in enumerate(levels):
        if not isinstance(item, dict):
            errors.append(f"levels.json: level {index} invalid")
            continue
        for key in ["id", "coinCount", "enemyCount", "coinObjectName", "enemyObjectName", "worldBounds", "seed"]:
            if key not in item:
                errors.append(f"levels.json: level {index} missing '{key}'")


def _validate_shop(shop: Json, errors: List[str]) -> None:
    upgrades = shop.get("upgrades")
    if not isinstance(upgrades, list):
        errors.append("shop.json: upgrades missing")
        return
    if not upgrades:
        errors.append("shop.json: upgrades empty")
        return

    for index, item in enumerate(upgrades):
        if not isinstance(item, dict):
            errors.append(f"shop.json: upgrade {index} invalid")
            continue
        for key in ["id", "name", "cost", "effect", "ownedVariable", "uiText"]:
            if key not in item:
                errors.append(f"shop.json: upgrade {index} missing '{key}'")


def _validate_save(save_data: Json, shop: Json, errors: List[str]) -> None:
    for key in ["version", "storageKey", "defaults"]:
        if key not in save_data:
            errors.append(f"save.json: missing '{key}'")

    defaults = save_data.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("save.json: defaults missing")
        return

    for key in ["Coins", "Speed", "PlayerMaxSpeed", "LevelIndex", "LevelCount", "CoinTarget", "EnemyTarget", "CoinsCollected", "EnemiesHit", "LevelComplete", "GameComplete", "SaveLoaded", "ownedUpgrades"]:
        if key not in defaults:
            errors.append(f"save.json: defaults missing '{key}'")

    owned_upgrades = defaults.get("ownedUpgrades")
    if not isinstance(owned_upgrades, dict):
        errors.append("save.json: ownedUpgrades missing")
        return

    upgrades = shop.get("upgrades", [])
    if isinstance(upgrades, list):
        for item in upgrades:
            if not isinstance(item, dict):
                continue
            owned_var = str(item.get("ownedVariable", "")).strip()
            if owned_var and owned_var not in owned_upgrades:
                errors.append(f"save.json: ownedUpgrades missing '{owned_var}'")


def _validate_pet_runtime(pet_runtime: Json, errors: List[str]) -> None:
    for key in ["name", "species", "temperament", "stats", "behavior", "actions", "decay"]:
        if key not in pet_runtime:
            errors.append(f"pet_runtime.json: missing '{key}'")


def _validate_save_runtime(save_runtime: Json, errors: List[str]) -> None:
    for key in ["storageKey", "defaults"]:
        if key not in save_runtime:
            errors.append(f"save_runtime.json: missing '{key}'")

    defaults = save_runtime.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("save_runtime.json: defaults missing")
        return

    for key in [
        "Coins", "Speed", "PlayerMaxSpeed", "LevelIndex", "LevelCount", "CoinTarget", "EnemyTarget",
        "CoinsCollected", "EnemiesHit", "LevelComplete", "GameComplete", "SaveLoaded",
        "PetHunger", "PetEnergy", "PetMood", "PetCleanliness", "PetState", "ownedUpgrades",
    ]:
        if key not in defaults:
            errors.append(f"save_runtime.json: defaults missing '{key}'")


def _validate_manifest(manifest: Json, errors: List[str]) -> None:
    for key in ["factory", "pack", "display", "worldBounds", "camera", "ui", "spawns", "levels", "shopUpgrades", "catalogSummary", "save", "petRuntime", "saveRuntime"]:
        if key not in manifest:
            errors.append(f"FACTORY_MANIFEST.json: missing '{key}'")


def _load_json(path: Path, errors: List[str], label: str) -> Any:
    try:
        return read_json(path)
    except Exception as exc:
        errors.append(f"{label}: invalid json ({exc})")
        return None
