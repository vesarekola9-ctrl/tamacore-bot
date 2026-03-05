from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    if scene is None:
        write_json(game_json_path, project)
        return

    _ensure_ui_layer(scene)

    # Make sure instances are placed on correct layers
    _force_instance_to_ui(scene, "HUD")
    _force_instance_to_ui(scene, "TouchJoystick")  # if present in template/previous runs

    # Ensure HUD is anchored top-left
    _ensure_hud_anchor(scene, project)

    # Ensure Player controls for mobile + optional keyboard
    _ensure_player_controls(scene)

    # Ensure core gameplay events exist (score + coin collection)
    _ensure_core_events(scene)

    # Ensure camera follows Player
    _ensure_camera_follow(scene)

    write_json(game_json_path, project)


# ---------------- internal helpers ----------------

def _get_scene(project: Dict[str, Any], preferred_name: str) -> Optional[Dict[str, Any]]:
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


def _instances(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    inst = scene.get("instances")
    if not isinstance(inst, list):
        inst = []
        scene["instances"] = inst
    return inst


def _find_instance(scene: Dict[str, Any], object_name: str) -> Optional[Dict[str, Any]]:
    for i in _instances(scene):
        if not isinstance(i, dict):
            continue
        if i.get("objectName") == object_name or i.get("name") == object_name:
            return i
    return None


def _force_instance_to_ui(scene: Dict[str, Any], object_name: str) -> None:
    inst = _find_instance(scene, object_name)
    if inst is None:
        return
    inst["layer"] = "UI"
    inst["zOrder"] = int(inst.get("zOrder", 999))
    # Keep HUD in safe zone
    if object_name == "HUD":
        inst["x"] = 20
        inst["y"] = 20
        inst["zOrder"] = 2000


def _scene_objects(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    objs = scene.get("objects")
    if not isinstance(objs, list):
        objs = []
        scene["objects"] = objs
    return objs


def _find_object(scene: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    for o in _scene_objects(scene):
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None


def _detect_anchor_behavior_type(project: Dict[str, Any]) -> str:
    # Try to reuse if present
    layouts = project.get("layouts", [])
    if isinstance(layouts, list):
        for l in layouts:
            if not isinstance(l, dict):
                continue
            objs = l.get("objects")
            if not isinstance(objs, list):
                continue
            for o in objs:
                if not isinstance(o, dict):
                    continue
                beh = o.get("behaviors")
                if not isinstance(beh, list):
                    continue
                for b in beh:
                    if isinstance(b, dict) and "Anchor" in str(b.get("type", "")):
                        t = b.get("type")
                        if isinstance(t, str) and t.strip():
                            return t
    return "AnchorBehavior::AnchorBehavior"


def _ensure_hud_anchor(scene: Dict[str, Any], project: Dict[str, Any]) -> None:
    hud_obj = _find_object(scene, "HUD")
    if hud_obj is None:
        return

    behaviors = hud_obj.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        hud_obj["behaviors"] = behaviors

    if any(isinstance(b, dict) and b.get("name") == "AnchorHUD" for b in behaviors):
        return

    anchor_type = _detect_anchor_behavior_type(project)

    behaviors.append(
        {
            "name": "AnchorHUD",
            "type": anchor_type,
            "topEdgeAnchor": "WindowTop",
            "leftEdgeAnchor": "WindowLeft",
            "rightEdgeAnchor": "None",
            "bottomEdgeAnchor": "None",
            "relativeToOriginalWindowSize": True,
            "useLegacyBottomAndRightAnchors": False,
        }
    )


def _ensure_player_controls(scene: Dict[str, Any]) -> None:
    player = _find_object(scene, "Player")
    if player is None:
        return

    behaviors = player.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        player["behaviors"] = behaviors

    def has(name: str) -> bool:
        return any(isinstance(b, dict) and b.get("name") == name for b in behaviors)

    # TopDownMovement (keep keyboard ON by default; you can disable later if you want mobile-only)
    if not has("TopDownMovement"):
        behaviors.append(
            {
                "name": "TopDownMovement",
                "type": "TopDownMovementBehavior::TopDownMovementBehavior",
                "allowDiagonals": True,
                "acceleration": 1000,
                "deceleration": 1200,
                "maxSpeed": 300,
                "angularMaxSpeed": 0,
                "rotateObject": False,
                "ignoreDefaultControls": False,
                "defaultControls": True,
            }
        )

    # Touch mapper (SpriteMultitouchJoystick extension)
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


def _events(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    ev = scene.get("events")
    if not isinstance(ev, list):
        ev = []
        scene["events"] = ev
    return ev


def _ensure_core_events(scene: Dict[str, Any]) -> None:
    evs = _events(scene)

    # Detect if our "TAMACORE_AUTOGEN" exists
    if any(isinstance(e, dict) and e.get("name") == "TAMACORE_AUTOGEN" for e in evs):
        return

    # Create a grouped event block
    block: Dict[str, Any] = {
        "type": "BuiltinCommonInstructions::Group",
        "name": "TAMACORE_AUTOGEN",
        "events": [],
    }

    # 1) Init score once
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Score", "=", "0"],
                },
                {
                    "type": "TextObject::SetString",
                    "parameters": ["HUD", "\"Score: 0\""],
                },
            ],
            "events": [],
        }
    )

    # 2) Collision Player/Coin => score++ + update HUD + move coin random
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {
                    "type": "BuiltinCommonInstructions::Collision",
                    "parameters": ["Player", "Coin"],
                }
            ],
            "actions": [
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Score", "=", "Variable(Score) + 1"],
                },
                {
                    "type": "TextObject::SetString",
                    "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score))"],
                },
                {
                    "type": "BuiltinCommonInstructions::SetObjectX",
                    "parameters": ["Coin", "RandomInRange(80, 900)"],
                },
                {
                    "type": "BuiltinCommonInstructions::SetObjectY",
                    "parameters": ["Coin", "RandomInRange(120, 520)"],
                },
            ],
            "events": [],
        }
    )

    evs.append(block)

    # Ensure scene variable Score exists
    vars_ = scene.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        scene["variables"] = vars_

    if not any(isinstance(v, dict) and v.get("name") == "Score" for v in vars_):
        vars_.append({"name": "Score", "type": "number", "value": "0", "children": []})


def _ensure_camera_follow(scene: Dict[str, Any]) -> None:
    # Safe minimal camera follow: center camera on Player each frame
    evs = _events(scene)

    # avoid duplicates
    if any(isinstance(e, dict) and e.get("name") == "TAMACORE_CAMERA" for e in evs):
        return

    evs.append(
        {
            "type": "BuiltinCommonInstructions::Group",
            "name": "TAMACORE_CAMERA",
            "events": [
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [],
                    "actions": [
                        {
                            "type": "Scene::CenterCameraOnObject",
                            "parameters": ["Player", "", "0", "0"],
                        }
                    ],
                    "events": [],
                }
            ],
        }
    )
