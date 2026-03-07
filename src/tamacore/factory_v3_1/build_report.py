from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import write_text
from .validate import validate_build_output


def write_build_report(
    game_dir: Path,
    pack_name: str,
    factory_version: str,
    manifest: Dict[str, Any],
    catalog: Dict[str, Any],
    levels: List[Dict[str, Any]],
    shop: Dict[str, Any],
) -> None:
    errors = validate_build_output(game_dir)

    asset_count = len(catalog.get("assets", {})) if isinstance(catalog.get("assets"), dict) else 0
    object_count = len(catalog.get("objects", [])) if isinstance(catalog.get("objects"), list) else 0
    instance_count = len(catalog.get("instances", [])) if isinstance(catalog.get("instances"), list) else 0
    upgrade_count = len(shop.get("upgrades", [])) if isinstance(shop.get("upgrades"), list) else 0

    save_defaults = {}
    if isinstance(manifest.get("save"), dict):
        save_defaults = manifest["save"].get("defaults", {})
        if not isinstance(save_defaults, dict):
            save_defaults = {}

    lines = [
        "TamaCore Build Report",
        "====================",
        "",
        f"Pack: {pack_name}",
        f"Factory: {factory_version}",
        f"Output: {game_dir}",
        "",
        "Summary",
        "-------",
        f"Assets: {asset_count}",
        f"Objects: {object_count}",
        f"Instances: {instance_count}",
        f"Levels: {len(levels)}",
        f"Shop upgrades: {upgrade_count}",
        "",
        "Levels",
        "------",
    ]

    for level in levels:
        level_id = str(level.get("id", "unknown"))
        coin_count = level.get("coinCount", 0)
        enemy_count = level.get("enemyCount", 0)
        lines.append(f"- {level_id}: coins={coin_count}, enemies={enemy_count}")

    lines.extend(["", "Shop", "----"])
    for upgrade in shop.get("upgrades", []) if isinstance(shop.get("upgrades"), list) else []:
        if not isinstance(upgrade, dict):
            continue
        uid = str(upgrade.get("id", "unknown"))
        name = str(upgrade.get("name", uid))
        cost = upgrade.get("cost", 0)
        owned = str(upgrade.get("ownedVariable", ""))
        lines.append(f"- {uid}: {name} ({cost}c) [{owned}]")

    lines.extend(["", "Save Defaults", "-------------"])
    for key in ["Coins", "Speed", "PlayerMaxSpeed", "LevelIndex", "CoinsCollected", "EnemiesHit", "LevelComplete", "GameComplete", "SaveLoaded"]:
        if key in save_defaults:
            lines.append(f"- {key}: {save_defaults[key]}")
    owned_upgrades = save_defaults.get("ownedUpgrades", {})
    if isinstance(owned_upgrades, dict):
        lines.append(f"- ownedUpgrades: {len(owned_upgrades)}")

    lines.extend(["", "Manifest", "--------"])
    for key in ["factory", "pack", "display", "worldBounds", "camera", "ui", "spawns", "save"]:
        if key in manifest:
            lines.append(f"- {key}: OK")

    lines.extend(["", "Validation", "----------"])
    if errors:
        for err in errors:
            lines.append(f"- ERROR: {err}")
    else:
        lines.append("- OK")

    lines.append("")
    write_text(game_dir / "BUILD_REPORT.txt", "\n".join(lines))
