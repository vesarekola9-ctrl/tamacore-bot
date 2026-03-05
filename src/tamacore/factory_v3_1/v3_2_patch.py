from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import read_json


def apply_v3_2_runtime(project: Dict[str, Any], scene: Dict[str, Any], cfg: Any, game_dir: Path) -> None:
    """
    V3.2: inject level spawn areas into scene vars + add shop/upgrade runtime events.

    V3.2.1:
      - Adds a UI text button "ShopBtn" that works on mobile (touch/click).
      - Clicking ShopBtn purchases speed_1 (cost 10) once and applies +20 PlayerMaxSpeed.
    """
    level = _load_first_level(game_dir)
    if isinstance(level, dict):
        _inject_level_areas(scene, level)

    # Ensure UI layer exists
    _ensure_ui_layer(scene, "UI")

    # Ensure shop button object exists + instance exists
    _ensure_shop_button(scene)

    events = scene.get("events")
    if not isinstance(events, list):
        return

    # Prevent duplicates for v3.2.1
    if any(isinstance(e, dict) and e.get("comment") == "FACTORY_V3_2_1_SHOPBTN" for e in events):
        return

    # Add variables
    _ensure_global_var(project, "PlayerMaxSpeed", "number", "240")
    _ensure_global_var(project, "Owned_speed_1", "number", "0")
    _ensure_global_var(project, "Owned_speed_2", "number", "0")

    # Update movement speed continuously from PlayerMaxSpeed
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

    # Keyboard fallback buy (PC)
    events.append(
        {
            "comment": "FACTORY_V3_2_SHOP_KEY_1",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::KeyPressed", "parameters": ["1"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_1", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Coins", ">=", "10"]},
            ],
            "actions": _actions_buy_speed1(),
            "events": [],
        }
    )

    # V3.2.1: Touch/click ShopBtn (mobile + desktop)
    events.append(
        {
            "comment": "FACTORY_V3_2_1_SHOPBTN",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::ObjectClicked", "parameters": ["ShopBtn"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_1", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Coins", ">=", "10"]},
            ],
            "actions": _actions_buy_speed1(),
            "events": [],
        }
    )

    # If not enough coins, show hint when clicking ShopBtn
    events.append(
        {
            "comment": "FACTORY_V3_2_1_SHOPBTN_NOCOINS",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::ObjectClicked", "parameters": ["ShopBtn"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_1", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Coins", "<", "10"]},
            ],
            "actions": [
                {
                    "type": "TextObject::SetString",
                    "parameters": [
                        "ShopBtn",
                        "\"BUY SPEED +20 (10 coins)  —  NEED \" + ToString(10-Variable(Coins)) + \" MORE\"",
                    ],
                }
            ],
            "events": [],
        }
    )

    # If already owned, show owned label
    events.append(
        {
            "comment": "FACTORY_V3_2_1_SHOPBTN_OWNED",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::ObjectClicked", "parameters": ["ShopBtn"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Owned_speed_1", "=", "1"]},
            ],
            "actions": [{"type": "TextObject::SetString", "parameters": ["ShopBtn", "\"SPEED +20  —  OWNED\""]}],
            "events": [],
        }
    )


def _actions_buy_speed1() -> list[dict]:
    return [
        {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Coins", "=", "Variable(Coins)-10"]},
        {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Owned_speed_1", "=", "1"]},
        {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["PlayerMaxSpeed", "=", "Variable(PlayerMaxSpeed)+20"]},
        {"type": "TextObject::SetString", "parameters": ["ShopBtn", "\"SPEED +20  —  OWNED\""]},
        {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP)) + \"  SPD: \" + ToString(Variable(PlayerMaxSpeed))"]},
    ]


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


def _ensure_ui_layer(scene: Dict[str, Any], layer_name: str) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers
    if not any(isinstance(l, dict) and l.get("name") == layer_name for l in layers):
        layers.append({"name": layer_name, "visibility": True, "effects": []})


def _ensure_shop_button(scene: Dict[str, Any]) -> None:
    # Objects list in a layout is "objects": [ {name,type,...} ]
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    if not any(isinstance(o, dict) and o.get("name") == "ShopBtn" for o in objects):
        objects.append(
            {
                "name": "ShopBtn",
                "type": "Text",
                "string": "BUY SPEED +20 (10 coins)",
                "fontSize": 28,
                "bold": True,
                "italic": False,
                "underlined": False,
                "smoothed": True,
                "font": "",
                "color": {"r": 245, "g": 245, "b": 250},
                "behaviors": [],
                "effects": [],
            }
        )

    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    if not any(isinstance(i, dict) and (i.get("objectName") == "ShopBtn" or i.get("name") == "ShopBtn") for i in instances):
        # place on UI layer; anchoring is handled by v3.1 camera-ui anchoring if present
        instances.append(
            {
                "objectName": "ShopBtn",
                "name": "ShopBtn",
                "x": 20,
                "y": 70,
                "angle": 0,
                "layer": "UI",
                "zOrder": 1000,
            }
        )


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
