from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List

from .utils import read_json, write_json

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping: Dict[str, str] = {}
    for p in sorted(assets_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMG_EXTS:
            continue
        dst = out_dir / p.name
        shutil.copy2(p, dst)
        mapping[p.stem.lower()] = "assets/generated/" + dst.name
    return mapping


def patch_project(game_json_path: Path, image_map: Dict[str, str]) -> None:
    project = read_json(game_json_path)

    _upsert_resources(project, image_map)

    scene = _get_scene(project, preferred_name="Main")
    if scene is not None:
        _ensure_ui_layer(scene)
        _inject_touch_joystick(scene)        # <-- now injects into scene["objects"] + instances
        _ensure_player_touch_mapper(scene)

    write_json(game_json_path, project)


# ---------------- internal helpers ----------------

def _get_scene(project: Dict[str, Any], preferred_name: str) -> Dict[str, Any] | None:
    layouts = project.get("layouts", [])
    if not isinstance(layouts, list) or not layouts:
        return None
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == preferred_name:
            return l
    return layouts[0] if isinstance(layouts[0], dict) else None


def _upsert_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    project.setdefault("resources", {})
    res_root = project["resources"]
    if not isinstance(res_root, dict):
        project["resources"] = {}
        res_root = project["resources"]

    res_list = res_root.get("resources")
    if not isinstance(res_list, list):
        res_list = []
        res_root["resources"] = res_list

    res_root.setdefault("resourceFolders", [])
    res_root.setdefault("resourcesFolderStructure", {"folderName": "__ROOT"})

    for name, rel in image_map.items():
        _upsert_image_resource(res_list, name=name, rel_path=rel)


def _upsert_image_resource(res_list: List[Dict[str, Any]], name: str, rel_path: str) -> None:
    for r in res_list:
        if isinstance(r, dict) and r.get("name") == name:
            r["kind"] = "image"
            r["file"] = rel_path
            r.setdefault("metadata", "")
            r.setdefault("userAdded", True)
            r.setdefault("alwaysLoaded", False)
            r.setdefault("smoothed", True)
            return
    res_list.append(
        {
            "name": name,
            "kind": "image",
            "file": rel_path,
            "metadata": "",
            "userAdded": True,
            "alwaysLoaded": False,
            "smoothed": True,
        }
    )


def _ensure_ui_layer(scene: Dict[str, Any]) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers
    if not any(isinstance(l, dict) and l.get("name") == "UI" for l in layers):
        layers.append({"name": "UI", "visibility": True, "effects": []})


def _find_object_in_scene_objects(scene_objects: List[Dict[str, Any]], name: str) -> Dict[str, Any] | None:
    for o in scene_objects:
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None


def _ensure_instance(scene: Dict[str, Any], obj_name: str, x: int, y: int, layer: str, z: int) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    if any(isinstance(i, dict) and (i.get("objectName") == obj_name or i.get("name") == obj_name) for i in instances):
        return

    instances.append(
        {
            "objectName": obj_name,
            "name": obj_name,
            "x": x,
            "y": y,
            "angle": 0,
            "layer": layer,
            "zOrder": z,
        }
    )


def _inject_touch_joystick(scene: Dict[str, Any]) -> None:
    """
    IMPORTANT: put it into scene["objects"] so it shows in GDevelop UI "Scene Objects".
    """
    scene_objects = scene.get("objects")
    if not isinstance(scene_objects, list):
        scene_objects = []
        scene["objects"] = scene_objects

    if _find_object_in_scene_objects(scene_objects, "TouchJoystick") is None:
        scene_objects.append(
            {
                "name": "TouchJoystick",
                "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
                "updateIfNotVisible": True,
                "behaviors": [],
                "effects": [],
            }
        )

    _ensure_instance(scene, "TouchJoystick", x=140, y=500, layer="UI", z=999)


def _ensure_player_touch_mapper(scene: Dict[str, Any]) -> None:
    scene_objects = scene.get("objects")
    if not isinstance(scene_objects, list):
        return

    player = _find_object_in_scene_objects(scene_objects, "Player")
    if player is None:
        return

    behaviors = player.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        player["behaviors"] = behaviors

    def has(name: str) -> bool:
        return any(isinstance(b, dict) and b.get("name") == name for b in behaviors)

    if not has("TopDownMovement"):
        behaviors.append(
            {
                "name": "TopDownMovement",
                "type": "TopDownMovementBehavior::TopDownMovementBehavior",
                "allowDiagonals": True,
                "acceleration": 700,
                "deceleration": 900,
                "maxSpeed": 240,
                "angularMaxSpeed": 0,
                "rotateObject": False,
                "ignoreDefaultControls": False,
                "defaultControls": True,
            }
        )

    if not has("TouchMapper"):
        behaviors.append(
            {
                "name": "TouchMapper",
                "type": "SpriteMultitouchJoystick::TopDownMultitouchMapper",
                "ControllerIdentifier": 1,
                "JoystickIdentifier": "Primary",
                "StickMode": "Analog",
                "TopDownMovement": "TopDownMovement",
            }
        )
