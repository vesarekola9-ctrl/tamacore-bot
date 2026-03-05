from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copies png assets from assets_dir into <game_dir>/assets/generated
    Returns image_map: { logical_name: relative_path_from_game_root }
    """
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}

    # Take png files in assets_dir root (simple by design)
    for p in sorted(assets_dir.glob("*.png")):
        logical = p.stem
        dst = out_dir / p.name
        shutil.copy2(p, dst)
        image_map[logical] = str(Path("assets/generated") / p.name).replace("\\", "/")

    return image_map


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _find_layout(project: Dict[str, Any], scene_name: str) -> Dict[str, Any] | None:
    layouts = _ensure_list(project.get("layouts", []))
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == scene_name:
            return l
    if layouts and isinstance(layouts[0], dict):
        return layouts[0]
    return None


def _ensure_layer(scene: Dict[str, Any], layer_name: str) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers

    for l in layers:
        if isinstance(l, dict) and l.get("name") == layer_name:
            return

    # Minimal layer object (GDevelop fills extra internally)
    layers.append(
        {
            "name": layer_name,
            "visibility": True,
            "effects": [],
        }
    )


def _ensure_resource(project: Dict[str, Any], name: str, kind: str, file_path: str) -> None:
    resources = project.get("resources", {})
    if not isinstance(resources, dict):
        resources = {}
        project["resources"] = resources

    res_list = resources.get("resources")
    if not isinstance(res_list, list):
        res_list = []
        resources["resources"] = res_list

    for r in res_list:
        if isinstance(r, dict) and r.get("name") == name:
            # Update file path if changed
            r["kind"] = kind
            r["file"] = file_path
            r["userAdded"] = True
            return

    res_list.append(
        {
            "name": name,
            "kind": kind,
            "file": file_path,
            "metadata": "",
            "userAdded": True,
        }
    )


def _ensure_object(scene: Dict[str, Any], obj_def: Dict[str, Any]) -> None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    name = obj_def.get("name")
    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            # Merge-ish: keep existing but ensure required keys
            for k, v in obj_def.items():
                if k not in o:
                    o[k] = v
            return

    objects.append(obj_def)


def _ensure_instance(scene: Dict[str, Any], inst_def: Dict[str, Any]) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    target_name = inst_def.get("objectName") or inst_def.get("name")
    for i in instances:
        if not isinstance(i, dict):
            continue
        if i.get("objectName") == target_name or i.get("name") == target_name:
            # Update placement/layer/zOrder if missing
            for k, v in inst_def.items():
                if k not in i:
                    i[k] = v
            return

    instances.append(inst_def)


def _ensure_behavior_on_object(obj: Dict[str, Any], behavior_def: Dict[str, Any]) -> None:
    behaviors = obj.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        obj["behaviors"] = behaviors

    bname = behavior_def.get("name")
    for b in behaviors:
        if isinstance(b, dict) and b.get("name") == bname:
            # Update keys
            for k, v in behavior_def.items():
                b[k] = v
            return

    behaviors.append(behavior_def)


def _get_object(scene: Dict[str, Any], name: str) -> Dict[str, Any] | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None
    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None


def _make_sprite_object(name: str, resource_name: str) -> Dict[str, Any]:
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
        ],
        "behaviors": [],
        "effects": [],
    }


def _make_text_object(name: str, text: str) -> Dict[str, Any]:
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


def patch_project(game_json_path: Path, image_map: Dict[str, str], scene_name: str = "Main") -> None:
    """
    Patches a GDevelop project (game.json):
    - ensures resources exist for images
    - ensures Background/Player/Coin/HUD exist (if not present)
    - ensures UI layer exists, and HUD + TouchJoystick instances are on UI layer
    - ensures TouchJoystick object exists (SpriteMultitouchJoystick::SpriteMultitouchJoystick)
    - ensures Player has TopDownMovement + TopDownMultitouchMapper behaviors
      so the joystick controls the player on mobile automatically. :contentReference[oaicite:1]{index=1}
    """
    project = _load_json(game_json_path)
    scene = _find_layout(project, scene_name)
    if scene is None:
        _save_json(game_json_path, project)
        return

    # Ensure UI layer exists
    _ensure_layer(scene, "UI")

    # Resources for images
    for logical, rel_path in image_map.items():
        _ensure_resource(project, logical, "image", rel_path)

    # Ensure core objects exist if missing (only if matching resource exists)
    if "bg" in image_map:
        _ensure_object(scene, _make_sprite_object("Background", "bg"))
    if "player" in image_map:
        _ensure_object(scene, _make_sprite_object("Player", "player"))
    if "coin" in image_map:
        _ensure_object(scene, _make_sprite_object("Coin", "coin"))

    _ensure_object(scene, _make_text_object("HUD", "Score: 0"))

    # Touch joystick object (virtual joystick)
    _ensure_object(
        scene,
        {
            "name": "TouchJoystick",
            "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
            "updateIfNotVisible": True,
            "behaviors": [],
            "effects": [],
        },
    )

    # Ensure instances
    _ensure_instance(scene, {"objectName": "Background", "x": 0, "y": 0, "angle": 0, "layer": "", "zOrder": 0})
    _ensure_instance(scene, {"objectName": "Player", "x": 200, "y": 240, "angle": 0, "layer": "", "zOrder": 1})
    _ensure_instance(scene, {"objectName": "Coin", "x": 520, "y": 280, "angle": 0, "layer": "", "zOrder": 2})

    # HUD anchored via UI layer (stays fixed when camera moves)
    _ensure_instance(scene, {"objectName": "HUD", "x": 20, "y": 20, "angle": 0, "layer": "UI", "zOrder": 999})

    # Joystick anchored bottom-left (UI layer)
    _ensure_instance(
        scene,
        {"objectName": "TouchJoystick", "x": 140, "y": 500, "angle": 0, "layer": "UI", "zOrder": 998},
    )

    # Ensure player behaviors: TopDownMovement + TopDown multitouch mapper
    player = _get_object(scene, "Player")
    if isinstance(player, dict):
        # Make sure TopDownMovement exists and disables keyboard defaults (mobile-first)
        _ensure_behavior_on_object(
            player,
            {
                "name": "TopDownMovement",
                "type": "TopDownMovement::TopDownMovementBehavior",
                "allowDiagonals": True,
                "acceleration": 700,
                "deceleration": 900,
                "maxSpeed": 240,
                "angularMaxSpeed": 0,
                "rotateObject": False,
                # For mobile: don't rely on keyboard defaults
                "ignoreDefaultControls": True,
                "defaultControls": False,
            },
        )

        # Add the mapper behavior that reads TouchJoystick state and simulates controls automatically. :contentReference[oaicite:2]{index=2}
        # Internal JSON type name is not explicitly shown in the docs, but follows the extension naming convention.
        _ensure_behavior_on_object(
            player,
            {
                "name": "TopDownMultitouchMapper",
                "type": "SpriteMultitouchJoystick::TopDownMultitouchMapper",
                "ControllerIdentifier": 1,
                "JoystickIdentifier": "Primary",
                "StickMode": "Analog",
                # Link to TopDownMovement behavior name on the same object:
                "TopDownMovement": "TopDownMovement",
            },
        )

    _save_json(game_json_path, project)
