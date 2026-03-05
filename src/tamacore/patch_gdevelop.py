from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import read_json, write_json, is_image_file


# -------------------------
# Simple pipeline (old)
# -------------------------
def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    out_assets = game_dir / "assets" / "generated"
    out_assets.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}
    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not is_image_file(p):
            continue
        dst = out_assets / p.name
        shutil.copy2(p, dst)
        res_name = dst.stem
        rel = Path("assets") / "generated" / dst.name
        image_map[res_name] = str(rel).replace("\\", "/")

    return image_map


def patch_project(game_json_path: Path, image_map: Dict[str, str]) -> None:
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json root is not an object/dict")

    ensure_resources(project, image_map)
    ensure_minimal_scene(project, image_map)

    write_json(game_json_path, project)


# -------------------------
# Shared helpers
# -------------------------
def ensure_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    resources_root = project.get("resources")
    if isinstance(resources_root, dict):
        res_list = resources_root.get("resources")
        if not isinstance(res_list, list):
            res_list = []
            resources_root["resources"] = res_list
    else:
        resources_root = {"resources": []}
        project["resources"] = resources_root
        res_list = resources_root["resources"]

    existing: Dict[str, Dict[str, Any]] = {}
    for r in res_list:
        if isinstance(r, dict) and isinstance(r.get("name"), str):
            existing[r["name"]] = r

    for name, file_path in image_map.items():
        if name in existing:
            existing[name]["file"] = file_path
            existing[name]["kind"] = "image"
            existing[name]["userAdded"] = True
        else:
            res_list.append(
                {
                    "name": name,
                    "kind": "image",
                    "file": file_path,
                    "metadata": "",
                    "userAdded": True,
                }
            )


def find_scene(project: Dict[str, Any], scene_name: str) -> Optional[Dict[str, Any]]:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == scene_name:
            return l
    return layouts[0] if isinstance(layouts[0], dict) else None


def ensure_layer(scene: Dict[str, Any], layer_name: str) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = [{"name": "", "visibility": True, "effects": []}]
        scene["layers"] = layers

    for l in layers:
        if isinstance(l, dict) and l.get("name") == layer_name:
            return
    layers.append({"name": layer_name, "visibility": True, "effects": []})


def ensure_scene_variable(scene: Dict[str, Any], name: str, vtype: str, value: str) -> None:
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


def ensure_global_variable(project: Dict[str, Any], name: str, vtype: str, value: str) -> None:
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


def ensure_object(scene: Dict[str, Any], obj_def: Dict[str, Any]) -> None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    name = obj_def.get("name")
    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            # minimal merge
            for k, v in obj_def.items():
                if k not in o:
                    o[k] = v
            return
    objects.append(obj_def)


def ensure_instance(scene: Dict[str, Any], inst_def: Dict[str, Any]) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    target = inst_def.get("objectName") or inst_def.get("name")
    for i in instances:
        if not isinstance(i, dict):
            continue
        if i.get("objectName") == target or i.get("name") == target:
            for k, v in inst_def.items():
                if k not in i:
                    i[k] = v
            return
    instances.append(inst_def)


def get_object(scene: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None
    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None


def ensure_behavior(obj: Dict[str, Any], behavior_def: Dict[str, Any]) -> None:
    behaviors = obj.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        obj["behaviors"] = behaviors

    bname = behavior_def.get("name")
    for b in behaviors:
        if isinstance(b, dict) and b.get("name") == bname:
            for k, v in behavior_def.items():
                b[k] = v
            return
    behaviors.append(behavior_def)


# -------------------------
# Minimal scene (old default)
# -------------------------
def ensure_minimal_scene(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    scene = find_scene(project, "Main")
    if not isinstance(scene, dict):
        return

    ensure_layer(scene, "UI")

    # Basic objects if map has keys
    if "bg" in image_map:
        ensure_object(scene, make_sprite_object("Background", "bg", {"x": 0, "y": 0}))
        ensure_instance(scene, {"objectName": "Background", "name": "Background", "x": 0, "y": 0, "angle": 0, "layer": "", "zOrder": 0})

    if "player" in image_map:
        ensure_object(scene, make_sprite_object("Player", "player"))
        ensure_instance(scene, {"objectName": "Player", "name": "Player", "x": 200, "y": 240, "angle": 0, "layer": "", "zOrder": 2})

    if "coin" in image_map:
        ensure_object(scene, make_sprite_object("Coin", "coin"))
        ensure_instance(scene, {"objectName": "Coin", "name": "Coin", "x": 520, "y": 280, "angle": 0, "layer": "", "zOrder": 3})

    ensure_object(scene, make_text_object("HUD", "Score: 0"))
    ensure_instance(scene, {"objectName": "HUD", "name": "HUD", "x": 20, "y": 20, "angle": 0, "layer": "UI", "zOrder": 999})

    # Joystick object + instance
    ensure_object(scene, make_joystick_object("TouchJoystick"))
    ensure_instance(scene, {"objectName": "TouchJoystick", "name": "TouchJoystick", "x": 140, "y": 500, "angle": 0, "layer": "UI", "zOrder": 998})

    # Player behaviors: movement + multitouch mapper
    player = get_object(scene, "Player")
    if isinstance(player, dict):
        ensure_behavior(player, topdown_movement_behavior(mobile_first=True))
        ensure_behavior(player, topdown_multitouch_mapper_behavior())

    # Score variable + events
    events = scene.get("events")
    if isinstance(events, list):
        ensure_scene_variable(scene, "Score", "number", "0")
        ensure_score_events(events)


def ensure_score_events(events: List[Any]) -> None:
    if has_action_setting_score(events):
        return

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: 0\""]},
            ],
            "events": [],
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Coin"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "Variable(Score) + 1"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(50, 900)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(80, 500)"]},
            ],
            "events": [],
        }
    )


def has_action_setting_score(events: List[Any]) -> bool:
    for e in events:
        if not isinstance(e, dict):
            continue
        actions = e.get("actions")
        if not isinstance(actions, list):
            continue
        for a in actions:
            if isinstance(a, dict) and a.get("type") == "BuiltinCommonInstructions::SetNumberVariable":
                params = a.get("parameters")
                if isinstance(params, list) and params and params[0] == "Score":
                    return True
    return False


# -------------------------
# Object factories
# -------------------------
def make_sprite_object(name: str, resource_name: str, origin: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    origin = origin or {"x": 0, "y": 0}
    return {
        "name": name,
        "type": "Sprite",
        "updateIfNotVisible": False,
        "animations": [
            {
                "name": "Idle",
                "directionType": "LeftRight",
                "useMultipleDirections": False,
                "loop": True,
                "speed": 8,
                "directions": [
                    {
                        "sprites": [
                            {
                                "image": resource_name,
                                "originPoint": {"x": origin["x"], "y": origin["y"]},
                                "centerPoint": {"x": 0, "y": 0},
                                "points": [],
                                "hasCustomCollisionMask": False,
                                "customCollisionMask": [],
                            }
                        ]
                    }
                ],
            }
        ],
        "behaviors": [],
        "effects": [],
    }


def make_sprite_object_with_animations(name: str, animations: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "name": name,
        "type": "Sprite",
        "updateIfNotVisible": False,
        "animations": animations,
        "behaviors": [],
        "effects": [],
    }


def make_text_object(name: str, text: str) -> Dict[str, Any]:
    return {
        "name": name,
        "type": "Text",
        "string": text,
        "fontSize": 32,
        "bold": True,
        "italic": False,
        "underlined": False,
        "smoothed": True,
        "font": "",
        "color": {"r": 245, "g": 245, "b": 250},
        "behaviors": [],
        "effects": [],
    }


def make_joystick_object(name: str) -> Dict[str, Any]:
    return {
        "name": name,
        "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
        "updateIfNotVisible": True,
        "behaviors": [],
        "effects": [],
    }


def topdown_movement_behavior(mobile_first: bool) -> Dict[str, Any]:
    return {
        "name": "TopDownMovement",
        "type": "TopDownMovement::TopDownMovementBehavior",
        "allowDiagonals": True,
        "acceleration": 700,
        "deceleration": 900,
        "maxSpeed": 240,
        "angularMaxSpeed": 0,
        "rotateObject": False,
        "ignoreDefaultControls": True if mobile_first else False,
        "defaultControls": False if mobile_first else True,
    }


def topdown_multitouch_mapper_behavior() -> Dict[str, Any]:
    # This behavior is provided by the SpriteMultitouchJoystick extension.
    return {
        "name": "TopDownMultitouchMapper",
        "type": "SpriteMultitouchJoystick::TopDownMultitouchMapper",
        "ControllerIdentifier": 1,
        "JoystickIdentifier": "Primary",
        "StickMode": "Analog",
        "TopDownMovement": "TopDownMovement",
    }


# -------------------------
# V3 FACTORY PATCH
# -------------------------
def factory_apply_catalog(
    game_json_path: Path,
    catalog: Dict[str, Any],
    scene_name: str = "Main",
    seed: int = 1337,
    with_demo_layout: bool = False,
) -> None:
    """
    Catalog format (dict) produced by factory_v3/catalog.py:
      {
        "pack": {...},
        "resources": {resName: "assets/generated/file.png", ...},
        "objects": [
          {
            "name": "Player",
            "type": "Sprite",
            "animations": [...],
            "behaviors": [...],
            "instances": [{"x":..,"y":..,"layer":"", "zOrder":..}, ...]  (optional)
          },
          ...
        ]
      }
    """
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json root is not an object/dict")

    # globals: store pack meta so future engine can read it
    pack = catalog.get("pack") if isinstance(catalog.get("pack"), dict) else {}
    ensure_global_variable(project, "FactoryV3", "string", "1")
    ensure_global_variable(project, "FactoryPackName", "string", str(pack.get("name", "pack")))
    ensure_global_variable(project, "FactoryPackVersion", "string", str(pack.get("version", "0.0.0")))
    ensure_global_variable(project, "FactorySeed", "number", str(float(seed)))

    # resources
    res_map = catalog.get("resources")
    if isinstance(res_map, dict):
        ensure_resources(project, {str(k): str(v) for k, v in res_map.items()})

    scene = find_scene(project, scene_name)
    if not isinstance(scene, dict):
        write_json(game_json_path, project)
        return

    ensure_layer(scene, "UI")

    # Always ensure joystick + HUD exist (factory standard)
    ensure_object(scene, make_joystick_object("TouchJoystick"))
    ensure_instance(scene, {"objectName": "TouchJoystick", "name": "TouchJoystick", "x": 140, "y": 500, "angle": 0, "layer": "UI", "zOrder": 998})
    ensure_object(scene, make_text_object("HUD", "Score: 0"))
    ensure_instance(scene, {"objectName": "HUD", "name": "HUD", "x": 20, "y": 20, "angle": 0, "layer": "UI", "zOrder": 999})

    # objects from catalog
    obj_list = catalog.get("objects")
    if isinstance(obj_list, list):
        for entry in obj_list:
            if not isinstance(entry, dict):
                continue

            name = str(entry.get("name", "")).strip()
            otype = entry.get("type", "Sprite")
            animations = entry.get("animations")
            behaviors = entry.get("behaviors")

            if not name:
                continue

            if otype == "Sprite" and isinstance(animations, list):
                ensure_object(scene, make_sprite_object_with_animations(name, animations))
            elif otype == "Text":
                ensure_object(scene, make_text_object(name, str(entry.get("string", ""))))
            else:
                # fallback sprite single-frame if resource named like name.lower()
                fallback_res = str(entry.get("fallbackResource", "")).strip()
                if fallback_res:
                    ensure_object(scene, make_sprite_object(name, fallback_res))

            obj = get_object(scene, name)
            if isinstance(obj, dict) and isinstance(behaviors, list):
                for b in behaviors:
                    if isinstance(b, dict):
                        ensure_behavior(obj, b)

            # demo instances
            if with_demo_layout:
                insts = entry.get("instances")
                if isinstance(insts, list) and insts:
                    for inst in insts:
                        if not isinstance(inst, dict):
                            continue
                        ensure_instance(
                            scene,
                            {
                                "objectName": name,
                                "name": name,
                                "x": int(inst.get("x", 0)),
                                "y": int(inst.get("y", 0)),
                                "angle": 0,
                                "layer": str(inst.get("layer", "")),
                                "zOrder": int(inst.get("zOrder", 1)),
                            },
                        )

    # Player standard behaviors if Player exists
    player = get_object(scene, "Player")
    if isinstance(player, dict):
        ensure_behavior(player, topdown_movement_behavior(mobile_first=True))
        ensure_behavior(player, topdown_multitouch_mapper_behavior())

    # minimal score loop if Coin exists
    events = scene.get("events")
    if isinstance(events, list):
        ensure_scene_variable(scene, "Score", "number", "0")
        ensure_score_events(events)

    write_json(game_json_path, project)
