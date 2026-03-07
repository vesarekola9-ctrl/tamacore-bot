from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json

Json = Dict[str, Any]


def apply_v3_2_runtime(project: Dict[str, Any], scene: Dict[str, Any], cfg: Any, game_dir: Path) -> None:
    _ensure_global_var(project, "LevelIndex", 0)
    _ensure_global_var(project, "LevelCount", 1)
    _ensure_global_var(project, "CoinTarget", 0)
    _ensure_global_var(project, "EnemyTarget", 0)
    _ensure_global_var(project, "RuntimeReady", 0)

    _ensure_ui_layer(scene)
    _ensure_runtime_labels(scene)

    levels = _load_levels(game_dir)
    level_count = len(levels)
    first_level = levels[0] if levels else {}

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

    out: List[Json] = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
    return out


def _inject_runtime_events(
    scene: Json,
    level_count: int,
    coin_target: int,
    enemy_target: int,
) -> None:
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
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "TamaCore HUD Refresh",
        }
    )


def _ensure_runtime_labels(scene: Json) -> None:
    _ensure_layout_object(scene, _obj_text("CoinsLabel", "Coins: 0", 26))
    _ensure_layout_object(scene, _obj_text("SpeedLabel", "Speed: 0", 26))
    _ensure_layout_object(scene, _obj_text("LevelLabel", "Level: 1/1", 26))

    _ensure_instance(scene, "CoinsLabel", x=24, y=24, layer="UI", z=2500)
    _ensure_instance(scene, "SpeedLabel", x=24, y=58, layer="UI", z=2501)
    _ensure_instance(scene, "LevelLabel", x=24, y=92, layer="UI", z=2502)


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

    for inst in instances:
        if not isinstance(inst, dict):
            continue
        if inst.get("objectName") == object_name or inst.get("name") == object_name:
            inst["x"] = x
            inst["y"] = y
            inst["layer"] = layer
            inst["zOrder"] = max(int(inst.get("zOrder", 0) or 0), z)
            return

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
