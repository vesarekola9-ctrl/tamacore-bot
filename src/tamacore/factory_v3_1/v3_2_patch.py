from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import read_json


def apply_v3_2_runtime(project: Dict[str, Any], scene: Dict[str, Any], cfg: Any, game_dir: Path) -> None:
    """
    V3.2: inject level spawn areas into scene vars + add shop/upgrade runtime events.

    - Reads game_dir/levels/level_001.json (or first from manifest)
    - Writes CoinAreaX/Y/W/H and EnemyAreaX/Y/W/H scene variables initial values
    - Adds keybind purchase events (1/2) that apply speed upgrades
    """
    level = _load_first_level(game_dir)
    if isinstance(level, dict):
        _inject_level_areas(scene, level)

    events = scene.get("events")
    if not isinstance(events, list):
        return

    # Prevent duplicates
    if any(isinstance(e, dict) and e.get("comment") == "FACTORY_V3_2_SHOP" for e in events):
        return

    # Add PlayerMaxSpeed variable (used for upgrades)
    _ensure_global_var(project, "PlayerMaxSpeed", "number", "240")
    _ensure_global_var(project, "Owned_speed_1", "number", "0")
    _ensure_global_var(project, "Owned_speed_2", "number", "0")

    # Update TopDownMovement max speed every frame from PlayerMaxSpeed
    # (Action name may vary by GDevelop version; this is the common one.)
    events.append(
        {
            "comment": "FACTORY_V3_2_STATS",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {
                    "type": "TopDownMovement::SetMaxSpeed",
                    "parameters": ["Player", "TopDownMovement", "Variable(PlayerMaxSpeed)"],
                }
            ],
            "events": [],
        }
    )

    # Simple shop buy with keyboard:
    # Press 1 => buy speed_1 (cost 10) => +20 max speed
    events.append(
        {
            "comment": "FACTORY_V3_2_SHOP",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::KeyPressed", "parameters": ["1"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_1", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Coins", ">=", "10"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Coins", "=", "Variable(Coins)-10"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Owned_speed_1", "=", "1"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["PlayerMaxSpeed", "=", "Variable(PlayerMaxSpeed)+20"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP)) + \"  SPD: \" + ToString(Variable(PlayerMaxSpeed))"]},
            ],
            "events": [],
        }
    )

    # Press 2 => buy speed_2 (cost 25) => +40 max speed
    events.append(
        {
            "comment": "FACTORY_V3_2_SHOP_SPEED2",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::KeyPressed", "parameters": ["2"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_2", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Coins", ">=", "25"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Coins", "=", "Variable(Coins)-25"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Owned_speed_2", "=", "1"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["PlayerMaxSpeed", "=", "Variable(PlayerMaxSpeed)+40"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP)) + \"  SPD: \" + ToString(Variable(PlayerMaxSpeed))"]},
            ],
            "events": [],
        }
    )


def _load_first_level(game_dir: Path) -> Dict[str, Any] | None:
    manifest = game_dir / "levels" / "manifest.json"
    if manifest.exists():
        m = read_json(manifest)
        if isinstance(m, dict) and isinstance(m.get("levels"), list) and m["levels"]:
            first_id = str(m["levels"][0])
            p = game_dir / "levels" / f"{first_id}.json"
            if p.exists():
                d = read_json(p)
                return d if isinstance(d, dict) else None

    # fallback
    p = game_dir / "levels" / "level_001.json"
    if p.exists():
        d = read_json(p)
        return d if isinstance(d, dict) else None
    return None


def _inject_level_areas(scene: Dict[str, Any], level: Dict[str, Any]) -> None:
    coin = level.get("coinSpawnArea") if isinstance(level.get("coinSpawnArea"), dict) else {}
    enemy = level.get("enemySpawnArea") if isinstance(level.get("enemySpawnArea"), dict) else {}

    _ensure_scene_var(scene, "CoinAreaX", "number", str(int(coin.get("x", 200))))
    _ensure_scene_var(scene, "CoinAreaY", "number", str(int(coin.get("y", 200))))
    _ensure_scene_var(scene, "CoinAreaW", "number", str(int(coin.get("w", 800))))
    _ensure_scene_var(scene, "CoinAreaH", "number", str(int(coin.get("h", 500))))

    _ensure_scene_var(scene, "EnemyAreaX", "number", str(int(enemy.get("x", 300))))
    _ensure_scene_var(scene, "EnemyAreaY", "number", str(int(enemy.get("y", 300))))
    _ensure_scene_var(scene, "EnemyAreaW", "number", str(int(enemy.get("w", 900))))
    _ensure_scene_var(scene, "EnemyAreaH", "number", str(int(enemy.get("h", 650))))


def _ensure_global_var(project: Dict[str, Any], name: str, vtype: str, value: str) -> None:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_
    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            v["type"] = vtype
            v["value"] = value
            v.setdefault("children", [])
            return
    vars_.append({"name": name, "type": vtype, "value": value, "children": []})


def _ensure_scene_var(scene: Dict[str, Any], name: str, vtype: str, value: str) -> None:
    vars_ = scene.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        scene["variables"] = vars_
    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            v["type"] = vtype
            v["value"] = value
            v.setdefault("children", [])
            return
    vars_.append({"name": name, "type": vtype, "value": value, "children": []})
