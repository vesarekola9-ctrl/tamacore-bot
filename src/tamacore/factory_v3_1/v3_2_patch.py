from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json

Json = Dict[str, Any]


def apply_v3_2_runtime(project: Dict[str, Any], scene: Dict[str, Any], cfg: Any, game_dir: Path) -> None:
    _ensure_global_var(project, "LevelIndex", 0)
    _ensure_global_var(project, "LevelCount", 1)
    _ensure_global_var(project, "CoinTarget", 0)
    _ensure_global_var(project, "EnemyTarget", 0)
    _ensure_global_var(project, "CoinsCollected", 0)
    _ensure_global_var(project, "EnemiesHit", 0)
    _ensure_global_var(project, "RuntimeReady", 0)

    _ensure_ui_layer(scene)
    _ensure_runtime_labels(scene)

    levels = _load_levels(game_dir)
    level_count = len(levels)
    first_level = levels[0] if levels else {}

    _spawn_level_instances(scene, first_level)

    _inject_runtime_events(
        scene=scene,
        level_count=level_count,
        coin_target=_safe_int(first_level.get("coinCount"), 0),
        enemy_target=_safe_int(first_level.get("enemyCount"), 0),
    )


def _load_levels(game_dir: Path) -> List[Json]:
    path = game_dir / "levels.json"
    if not path.exists():
        return []

    data = read_json(path)
    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _spawn_level_instances(scene: Json, level: Json) -> None:
    bounds = level.get("worldBounds", {})
    if not isinstance(bounds, dict):
        bounds = {}

    x_min = _safe_int(bounds.get("xMin"), 0)
    y_min = _safe_int(bounds.get("yMin"), 0)
    x_max = _safe_int(bounds.get("xMax"), 720)
    y_max = _safe_int(bounds.get("yMax"), 1280)

    coin_count = max(0, _safe_int(level.get("coinCount"), 0))
    enemy_count = max(0, _safe_int(level.get("enemyCount"), 0))
    coin_name = str(level.get("coinObjectName", "Coin") or "Coin")
    enemy_name = str(level.get("enemyObjectName", "Enemy") or "Enemy")
    seed = _safe_int(level.get("seed"), 1337)

    rng = random.Random(seed)

    if coin_count > 0:
        for x, y in _random_points(rng, x_min, y_min, x_max, y_max, coin_count, margin=96):
            _ensure_instance(scene, coin_name, x=x, y=y, layer="", z=20)

    if enemy_count > 0:
        for x, y in _random_points(rng, x_min, y_min, x_max, y_max, enemy_count, margin=140):
            _ensure_instance(scene, enemy_name, x=x, y=y, layer="", z=20)


def _random_points(
    rng: random.Random,
    x_min: int,
    y_min: int,
    x_max: int,
    y_max: int,
    count: int,
    margin: int,
) -> List[tuple[int, int]]:
    out: List[tuple[int, int]] = []
    left = x_min + margin
    top = y_min + margin
    right = max(left + 1, x_max - margin)
    bottom = max(top + 1, y_max - margin)

    for _ in range(count):
        out.append((rng.randint(left, right), rng.randint(top, bottom)))
    return out


def _inject_runtime_events(scene: Json, level_count: int, coin_target: int, enemy_target: int) -> None:
    events = scene.get("events")
    if not isinstance(events, list):
        events = []
        scene["events"] = events

    marker = "TAMACORE_AUTOGEN_RUNTIME_V3_2"
    for event in events:
        if isinstance(event, dict) and event.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(event.get("comment", "")):
                return

    events.append(
        {
            "type": "BuiltinCommonInstructions::Comment",
            "comment": marker,
            "comment2": "",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", []),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["LevelIndex", "0"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["LevelCount", str(max(1, level_count))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["CoinTarget", str(max(0, coin_target))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["EnemyTarget", str(max(0, enemy_target))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["CoinsCollected", "0"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["EnemiesHit", "0"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["RuntimeReady", "1"]),
                _act("TextObject::SetString", ["CoinsLabel", "\"Coins: \" + ToString(Variable(Coins))"]),
                _act("TextObject::SetString", ["SpeedLabel", "\"Speed: \" + ToString(Variable(PlayerMaxSpeed))"]),
                _act(
                    "TextObject::SetString",
                    [
                        "LevelLabel",
                        "\"Level: \" + ToString(Variable(LevelIndex)+1) + \"/\" + ToString(Variable(LevelCount))",
                    ],
                ),
                _act(
                    "TextObject::SetString",
                    [
                        "GoalLabel",
                        "\"Coins: \" + ToString(Variable(CoinsCollected)) + \"/\" + ToString(Variable(CoinTarget)) + \" | Enemies: \" + ToString(Variable(EnemiesHit)) + \"/\" + ToString(Variable(EnemyTarget))",
                    ],
                ),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "TamaCore Runtime Init",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                _act("TextObject::SetString", ["CoinsLabel", "\"Coins: \" + ToString(Variable(Coins))"]),
                _act("TextObject::SetString", ["SpeedLabel", "\"Speed: \" + ToString(Variable(PlayerMaxSpeed))"]),
                _act(
                    "TextObject::SetString",
                    [
                        "LevelLabel",
                        "\"Level: \" + ToString(Variable(LevelIndex)+1) + \"/\" + ToString(Variable(LevelCount))",
                    ],
                ),
                _act(
                    "TextObject::SetString",
                    [
                        "GoalLabel",
                        "\"Coins: \" + ToString(Variable(CoinsCollected)) + \"/\" + ToString(Variable(CoinTarget)) + \" | Enemies: \" + ToString(Variable(EnemiesHit)) + \"/\" + ToString(Variable(EnemyTarget))",
                    ],
                ),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "TamaCore HUD Refresh",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::Collision", ["Player", "Coin", "", ""]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::Delete", ["Coin"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["Coins", "10"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["CoinsCollected", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Collect Coin",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::Collision", ["Player", "Enemy", "", ""]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::Delete", ["Enemy"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["EnemiesHit", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Hit Enemy",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(CoinTarget)", ">", "0"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(CoinsCollected)", ">=", "Variable(CoinTarget)"]),
            ],
            "actions": [
                _act(
                    "TextObject::SetString",
                    [
                        "GoalLabel",
                        "\"LEVEL COMPLETE\"",
                    ],
                )
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Level Complete",
        }
    )


def _ensure_runtime_labels(scene: Json) -> None:
    _ensure_layout_object(scene, _obj_text("CoinsLabel", "Coins: 0", 26))
    _ensure_layout_object(scene, _obj_text("SpeedLabel", "Speed: 0", 26))
    _ensure_layout_object(scene, _obj_text("LevelLabel", "Level: 1/1", 26))
    _ensure_layout_object(scene, _obj_text("GoalLabel", "Coins: 0/0 | Enemies: 0/0", 24))

    _ensure_instance(scene, "CoinsLabel", x=24, y=24, layer="UI", z=2500)
    _ensure_instance(scene, "SpeedLabel", x=24, y=58, layer="UI", z=2501)
    _ensure_instance(scene, "LevelLabel", x=24, y=92, layer="UI", z=2502)
    _ensure_instance(scene, "GoalLabel", x=24, y=126, layer="UI", z=2503)


def _ensure_ui_layer(scene: Json) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers

    for layer in layers:
        if isinstance(layer, dict) and layer.get("name") == "UI":
            layer.setdefault("followBaseLayerCamera", True)
            return

    layers.append(
        {
            "name": "UI",
            "visibility": True,
            "effects": [],
            "isLightingLayer": False,
            "followBaseLayerCamera": True,
        }
    )


def _ensure_global_var(project: Json, name: str, number_value: float) -> None:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    for var in vars_:
        if isinstance(var, dict) and var.get("name") == name:
            var.setdefault("type", "number")
            var.setdefault("children", [])
            if "value" not in var:
                var["value"] = number_value
            return

    vars_.append(
        {
            "name": name,
            "type": "number",
            "value": number_value,
            "children": [],
        }
    )


def _ensure_layout_object(scene: Json, obj_def: Json) -> None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    obj_name = obj_def.get("name")
    if not obj_name:
        return

    for existing in objects:
        if isinstance(existing, dict) and existing.get("name") == obj_name:
            return

    objects.append(obj_def)


def _ensure_instance(scene: Json, object_name: str, x: float, y: float, layer: str, z: int) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    instances.append(
        {
            "name": object_name,
            "objectName": object_name,
            "layer": layer,
            "x": x,
            "y": y,
            "angle": 0,
            "zOrder": z,
            "locked": False,
            "persistentUuid": "",
            "customSize": False,
            "width": 0,
            "height": 0,
        }
    )


def _obj_text(name: str, text: str, font_size: int) -> Json:
    return {
        "name": name,
        "type": "TextObject::Text",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {
            "font": "",
            "size": font_size,
            "bold": True,
            "italic": False,
            "underlined": False,
            "color": "255;255;255",
            "string": text,
            "alignment": "left",
            "verticalAlignment": "center",
            "wrapping": False,
        },
        "effects": [],
    }


def _cond(instruction: str, parameters: List[str]) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "inverted": False,
        "parameters": parameters,
        "subInstructions": [],
        "instructionType": "condition",
        "instruction": instruction,
    }


def _act(instruction: str, parameters: List[str]) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "parameters": parameters,
        "subInstructions": [],
        "instructionType": "action",
        "instruction": instruction,
    }


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
