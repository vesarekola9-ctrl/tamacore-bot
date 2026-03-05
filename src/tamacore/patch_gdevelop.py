from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import read_json, write_json, is_image_file


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copies images into game_dir/assets/generated.
    Returns a map: resource_name -> file_relative_path (from game root).
    """
    out_assets = game_dir / "assets" / "generated"
    out_assets.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}

    # If assets_dir doesn't exist, do not fail; rely on template's own images
    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not is_image_file(p):
            continue
        dst = out_assets / p.name
        shutil.copy2(p, dst)

        # resource name = stem (bg.png -> bg)
        resource_name = dst.stem
        rel = Path("assets") / "generated" / dst.name
        image_map[resource_name] = str(rel).replace("\\", "/")

    return image_map


def patch_project(game_json_path: Path, image_map: Dict[str, str]) -> None:
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json root is not an object/dict")

    ensure_resources(project, image_map)
    ensure_main_scene_basics(project, image_map)

    write_json(game_json_path, project)


# -------------------------
# Resources
# -------------------------
def ensure_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    """
    Supports both shapes:
      resources: { resources: [ ... ] }
      resources: [ ... ]  (rare)
    """
    resources_root = project.get("resources")
    if isinstance(resources_root, dict):
        res_list = resources_root.get("resources")
        if not isinstance(res_list, list):
            res_list = []
            resources_root["resources"] = res_list
    elif isinstance(resources_root, list):
        res_list = resources_root
    else:
        resources_root = {"resources": []}
        project["resources"] = resources_root
        res_list = resources_root["resources"]

    # Index existing by name
    existing = {}
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


# -------------------------
# Scene patching
# -------------------------
def ensure_main_scene_basics(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return

    scene = find_scene(layouts, "Main") or (layouts[0] if isinstance(layouts[0], dict) else None)
    if not isinstance(scene, dict):
        return

    # GDevelop scene has top-level keys: objects, instances, layers, events
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = [{"name": "", "visibility": True, "effects": []}]
        scene["layers"] = layers

    ensure_layer(layers, "UI")

    # canonical resource keys (if not in image_map, still keep names for template assets)
    bg_res = "bg"
    player_res = "player"
    coin_res = "coin"

    # If our map contains these exact keys, good. If not, keep them anyway (template may have them).
    ensure_sprite_object(objects, "Background", bg_res)
    ensure_sprite_object(objects, "Player", player_res, behaviors=[topdown_behavior()])
    ensure_sprite_object(objects, "Coin", coin_res)
    ensure_text_object(objects, "HUD", "Score: 0")

    # Joystick object (only if template has extension installed; safe to add anyway)
    ensure_joystick_object(objects, "TouchJoystick")

    ensure_instance(instances, "Background", x=0, y=0, layer="", z=0)
    ensure_instance(instances, "Player", x=200, y=240, layer="", z=1)
    ensure_instance(instances, "Coin", x=520, y=280, layer="", z=2)
    ensure_instance(instances, "HUD", x=20, y=20, layer="UI", z=999)
    ensure_instance(instances, "TouchJoystick", x=140, y=500, layer="UI", z=998)

    # Ensure minimal variables/events if scene has events list
    events = scene.get("events")
    if isinstance(events, list):
        ensure_scene_variable(scene, "Score", "number", "0")
        ensure_score_events(events)


def find_scene(layouts: List[Any], name: str) -> Optional[Dict[str, Any]]:
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == name:
            return l
    return None


def ensure_layer(layers: List[Any], name: str) -> None:
    for l in layers:
        if isinstance(l, dict) and l.get("name") == name:
            return
    layers.append({"name": name, "visibility": True, "effects": []})


def ensure_sprite_object(objects: List[Any], obj_name: str, resource_name: str, behaviors: Optional[List[Dict[str, Any]]] = None) -> None:
    if any(isinstance(o, dict) and o.get("name") == obj_name for o in objects):
        return

    anim = {
        "name": "Idle",
        "directionType": "LeftRight",
        "useMultipleDirections": False,
        "loop": True,
        "speed": 5,
        "directions": [
            {
                "sprites": [
                    {
                        "image": resource_name,
                        "originPoint": {"x": 0, "y": 0},
                        "centerPoint": {"x": 0, "y": 0},
                        "points": [],
                        "hasCustomCollisionMask": False,
                        "customCollisionMask": [],
                    }
                ]
            }
        ],
    }

    objects.append(
        {
            "name": obj_name,
            "type": "Sprite",
            "updateIfNotVisible": False,
            "animations": [anim],
            "behaviors": behaviors or [],
            "effects": [],
        }
    )


def ensure_text_object(objects: List[Any], obj_name: str, initial_text: str) -> None:
    if any(isinstance(o, dict) and o.get("name") == obj_name for o in objects):
        return
    objects.append(
        {
            "name": obj_name,
            "type": "Text",
            "string": initial_text,
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
    )


def ensure_joystick_object(objects: List[Any], obj_name: str) -> None:
    if any(isinstance(o, dict) and o.get("name") == obj_name for o in objects):
        return
    # Object type used by the Multitouch Joystick extension
    objects.append(
        {
            "name": obj_name,
            "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
            "updateIfNotVisible": True,
            "behaviors": [],
            "effects": [],
        }
    )


def ensure_instance(instances: List[Any], object_name: str, x: int, y: int, layer: str, z: int) -> None:
    for inst in instances:
        if not isinstance(inst, dict):
            continue
        if inst.get("objectName") == object_name or inst.get("name") == object_name:
            return
    instances.append(
        {
            "objectName": object_name,
            "name": object_name,
            "x": x,
            "y": y,
            "angle": 0,
            "layer": layer,
            "zOrder": z,
        }
    )


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


def topdown_behavior() -> Dict[str, Any]:
    return {
        "name": "TopDownMovement",
        "type": "TopDownMovement::TopDownMovementBehavior",
        "allowDiagonals": True,
        "acceleration": 700,
        "deceleration": 900,
        "maxSpeed": 240,
        "angularMaxSpeed": 0,
        "rotateObject": False,
        "ignoreDefaultControls": False,
        "defaultControls": True,
    }


def ensure_score_events(events: List[Any]) -> None:
    """
    Adds two basic event blocks if they don't exist:
      - Once: Score=0 and HUD set
      - Collision(Player,Coin): Score++ + HUD set + randomize coin
    We detect by searching for SetNumberVariable Score in actions.
    """
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
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Score", "=", "Variable(Score) + 1"],
                },
                {
                    "type": "TextObject::SetString",
                    "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score))"],
                },
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
