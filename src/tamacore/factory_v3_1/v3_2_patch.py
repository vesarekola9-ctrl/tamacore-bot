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
    _ensure_global_var(project, "LevelComplete", 0)
    _ensure_global_var(project, "GameComplete", 0)
    _ensure_global_var(project, "SaveLoaded", 0)
    _ensure_global_var(project, "SaveDirty", 0)

    pet_runtime = _load_pet_runtime(game_dir)
    _ensure_pet_vars(project, pet_runtime)

    _ensure_ui_layer(scene)
    _ensure_runtime_labels(scene)

    levels = _load_levels(game_dir)
    level_count = len(levels)
    first_level = levels[0] if levels else {}

    _spawn_level_instances(scene, first_level)
    _inject_runtime_events(
        scene=scene,
        cfg=cfg,
        level_count=level_count,
        coin_target=_safe_int(first_level.get("coinCount"), 0),
        enemy_target=_safe_int(first_level.get("enemyCount"), 0),
        pet_runtime=pet_runtime,
    )


def _load_levels(game_dir: Path) -> List[Json]:
    path = game_dir / "levels.json"
    if not path.exists():
        return []

    data = read_json(path)
    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _load_pet_runtime(game_dir: Path) -> Json:
    path = game_dir / "pet_runtime.json"
    if not path.exists():
        return {
            "stats": {"hunger": 60, "energy": 60, "mood": 60, "cleanliness": 60},
            "actions": {
                "feed": {"hungerAdd": 18, "moodAdd": 4, "coinsCost": 8},
                "play": {"moodAdd": 12, "energyAdd": -8, "hungerAdd": -5},
                "sleep": {"energyAdd": 20, "moodAdd": 3, "cleanlinessAdd": -4},
                "clean": {"cleanlinessAdd": 20, "moodAdd": 2, "coinsCost": 5},
            },
        }

    data = read_json(path)
    return data if isinstance(data, dict) else {}


def _ensure_pet_vars(project: Json, pet_runtime: Json) -> None:
    stats = pet_runtime.get("stats", {})
    if not isinstance(stats, dict):
        stats = {}

    _ensure_global_var(project, "PetHunger", _safe_int(stats.get("hunger"), 60))
    _ensure_global_var(project, "PetEnergy", _safe_int(stats.get("energy"), 60))
    _ensure_global_var(project, "PetMood", _safe_int(stats.get("mood"), 60))
    _ensure_global_var(project, "PetCleanliness", _safe_int(stats.get("cleanliness"), 60))
    _ensure_global_var(project, "PetState", 0)
    _ensure_global_var(project, "FeedCost", _safe_int(pet_runtime.get("actions", {}).get("feed", {}).get("coinsCost"), 8))
    _ensure_global_var(project, "CleanCost", _safe_int(pet_runtime.get("actions", {}).get("clean", {}).get("coinsCost"), 5))


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
            _ensure_unique_instance(scene, coin_name, x=x, y=y, layer="", z=20)

    if enemy_count > 0:
        for x, y in _random_points(rng, x_min, y_min, x_max, y_max, enemy_count, margin=140):
            _ensure_unique_instance(scene, enemy_name, x=x, y=y, layer="", z=20)


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


def _inject_runtime_events(
    scene: Json,
    cfg: Any,
    level_count: int,
    coin_target: int,
    enemy_target: int,
    pet_runtime: Json,
) -> None:
    events = scene.get("events")
    if not isinstance(events, list):
        events = []
        scene["events"] = events

    marker = "TAMACORE_AUTOGEN_RUNTIME_V3_6"
    for event in events:
        if isinstance(event, dict) and event.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(event.get("comment", "")):
                return

    player_name = str(getattr(getattr(cfg, "camera", None), "followObject", "Player") or "Player")
    x_min = str(getattr(getattr(cfg, "worldBounds", None), "xMin", 0))
    y_min = str(getattr(getattr(cfg, "worldBounds", None), "yMin", 0))
    x_max = str(getattr(getattr(cfg, "worldBounds", None), "xMax", 720))
    y_max = str(getattr(getattr(cfg, "worldBounds", None), "yMax", 1280))

    feed = pet_runtime.get("actions", {}).get("feed", {})
    play = pet_runtime.get("actions", {}).get("play", {})
    sleep = pet_runtime.get("actions", {}).get("sleep", {})
    clean = pet_runtime.get("actions", {}).get("clean", {})

    events.append({"type": "BuiltinCommonInstructions::Comment", "comment": marker, "comment2": ""})

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", [])],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["LevelCount", str(max(1, level_count))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["CoinTarget", str(max(0, coin_target))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["EnemyTarget", str(max(0, enemy_target))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["RuntimeReady", "1"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PlayerMaxSpeed", "Variable(Speed)"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "TamaCore Runtime Init",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(SaveLoaded)", "=", "0"])],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveLoaded", "1"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "0"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Save Load Init Stub",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PlayerMaxSpeed", "Variable(Speed)"]),
                _act("TextObject::SetString", ["CoinsLabel", "\"Coins: \" + ToString(Variable(Coins))"]),
                _act("TextObject::SetString", ["SpeedLabel", "\"H:\" + ToString(Variable(PetHunger)) + \" E:\" + ToString(Variable(PetEnergy)) + \" M:\" + ToString(Variable(PetMood)) + \" C:\" + ToString(Variable(PetCleanliness))"]),
                _act("TextObject::SetString", ["LevelLabel", "\"Level: \" + ToString(Variable(LevelIndex)+1) + \"/\" + ToString(Variable(LevelCount))"]),
                _act("TextObject::SetString", ["GoalLabel", "\"Coins: \" + ToString(Variable(CoinsCollected)) + \"/\" + ToString(Variable(CoinTarget)) + \" | Enemies: \" + ToString(Variable(EnemiesHit)) + \"/\" + ToString(Variable(EnemyTarget))"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "TamaCore HUD Refresh",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::RepeatEveryXSeconds", ["5"])],
            "actions": [
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["PetHunger", "1"]),
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["PetEnergy", "1"]),
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["PetMood", "1"]),
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["PetCleanliness", "1"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Pet Decay Tick",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(Coins)", ">=", str(_safe_int(feed.get("coinsCost"), 8))]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(LevelComplete)", "=", "0"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["Coins", str(_safe_int(feed.get("coinsCost"), 8))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetHunger", str(_safe_int(feed.get("hungerAdd"), 18))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetMood", str(_safe_int(feed.get("moodAdd"), 4))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PetState", "1"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Pet Feed",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::KeyPressed", ["p"])],
            "actions": [
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetMood", str(_safe_int(play.get("moodAdd"), 12))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetEnergy", str(_safe_int(play.get("energyAdd"), -8))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetHunger", str(_safe_int(play.get("hungerAdd"), -5))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PetState", "2"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Pet Play",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::KeyPressed", ["s"])],
            "actions": [
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetEnergy", str(_safe_int(sleep.get("energyAdd"), 20))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetMood", str(_safe_int(sleep.get("moodAdd"), 3))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetCleanliness", str(_safe_int(sleep.get("cleanlinessAdd"), -4))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PetState", "3"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Pet Sleep",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::KeyPressed", ["c"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(Coins)", ">=", str(_safe_int(clean.get("coinsCost"), 5))]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["Coins", str(_safe_int(clean.get("coinsCost"), 5))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetCleanliness", str(_safe_int(clean.get("cleanlinessAdd"), 20))]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PetMood", str(_safe_int(clean.get("moodAdd"), 2))]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["PetState", "4"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Pet Clean",
        }
    )

    for var_name in ["PetHunger", "PetEnergy", "PetMood", "PetCleanliness"]:
        events.append(
            {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({var_name})", "<", "0"])],
                "actions": [_act("BuiltinCommonInstructions::SetNumberVariable", [var_name, "0"])],
                "events": [],
                "disabled": False,
                "folded": False,
                "name": f"Clamp {var_name} Min",
            }
        )
        events.append(
            {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({var_name})", ">", "100"])],
                "actions": [_act("BuiltinCommonInstructions::SetNumberVariable", [var_name, "100"])],
                "events": [],
                "disabled": False,
                "folded": False,
                "name": f"Clamp {var_name} Max",
            }
        )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(SaveDirty)", "=", "1"]),
                _cond("BuiltinCommonInstructions::RepeatEveryXSeconds", ["10"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "0"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Save Write Stub",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"{player_name}.X()", "<", x_min])],
            "actions": [_act("BuiltinCommonInstructions::ModVarObjet", [player_name, "=", x_min, "X"])],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Clamp Player Left",
        }
    )
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"{player_name}.Y()", "<", y_min])],
            "actions": [_act("BuiltinCommonInstructions::ModVarObjet", [player_name, "=", y_min, "Y"])],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Clamp Player Top",
        }
    )
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"{player_name}.X()", ">", x_max])],
            "actions": [_act("BuiltinCommonInstructions::ModVarObjet", [player_name, "=", x_max, "X"])],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Clamp Player Right",
        }
    )
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::CompareNumbers", [f"{player_name}.Y()", ">", y_max])],
            "actions": [_act("BuiltinCommonInstructions::ModVarObjet", [player_name, "=", y_max, "Y"])],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Clamp Player Bottom",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::Collision", [player_name, "Coin", "", ""])],
            "actions": [
                _act("BuiltinCommonInstructions::Delete", ["Coin"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["Coins", "10"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["CoinsCollected", "1"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Collect Coin",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::Collision", [player_name, "Enemy", "", ""])],
            "actions": [
                _act("BuiltinCommonInstructions::Delete", ["Enemy"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["EnemiesHit", "1"]),
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["PetMood", "3"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Hit Enemy",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(LevelComplete)", "=", "0"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(CoinsCollected)", ">=", "Variable(CoinTarget)"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(EnemiesHit)", ">=", "Variable(EnemyTarget)"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SetNumberVariable", ["LevelComplete", "1"]),
                _act("TextObject::SetString", ["GoalLabel", "\"LEVEL COMPLETE - TAP SHOP TO CONTINUE\""]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["SaveDirty", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "name": "Level Complete",
        }
    )


def _ensure_runtime_labels(scene: Json) -> None:
    _ensure_layout_object(scene, _obj_text("CoinsLabel", "Coins: 0", 26))
    _ensure_layout_object(scene, _obj_text("SpeedLabel", "H:0 E:0 M:0 C:0", 22))
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

    vars_.append({"name": name, "type": "number", "value": number_value, "children": []})


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
        if inst.get("objectName") == object_name and inst.get("x") == x and inst.get("y") == y and inst.get("layer", "") == layer:
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


def _ensure_unique_instance(scene: Json, object_name: str, x: float, y: float, layer: str, z: int) -> None:
    _ensure_instance(scene, object_name, x, y, layer, z)


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
