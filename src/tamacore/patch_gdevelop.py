from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import is_image_file, read_json, write_json


def _find_scene(project: Dict[str, Any], scene_name: str = "Main") -> Dict[str, Any] | None:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None
    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == scene_name:
            return layout
    # fallback: first layout if Main not found
    first = layouts[0]
    return first if isinstance(first, dict) else None


def _ensure_layer(scene: Dict[str, Any], layer_name: str) -> None:
    layers = scene.setdefault("layers", [])
    if not isinstance(layers, list):
        scene["layers"] = []
        layers = scene["layers"]

    if any(isinstance(l, dict) and l.get("name") == layer_name for l in layers):
        return

    layers.append(
        {
            "name": layer_name,
            "visibility": True,
            "effects": [],
        }
    )


def _ensure_object(scene: Dict[str, Any], obj: Dict[str, Any]) -> None:
    objects = scene.setdefault("objects", [])
    if not isinstance(objects, list):
        scene["objects"] = []
        objects = scene["objects"]

    name = obj.get("name")
    if name and any(isinstance(o, dict) and o.get("name") == name for o in objects):
        return

    objects.append(obj)


def _ensure_instance(scene: Dict[str, Any], inst: Dict[str, Any]) -> None:
    instances = scene.setdefault("instances", [])
    if not isinstance(instances, list):
        scene["instances"] = []
        instances = scene["instances"]

    want = inst.get("objectName") or inst.get("name")
    if want and any(
        isinstance(i, dict) and ((i.get("objectName") == want) or (i.get("name") == want))
        for i in instances
    ):
        return

    instances.append(inst)


def _ensure_global_variable(project: Dict[str, Any], name: str, vtype: str, value: str) -> None:
    vars_ = project.setdefault("variables", [])
    if not isinstance(vars_, list):
        project["variables"] = []
        vars_ = project["variables"]

    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            v["type"] = vtype
            v["value"] = value
            v.setdefault("children", [])
            return

    vars_.append({"name": name, "type": vtype, "value": value, "children": []})


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copy images from assets_dir into game_dir/assets/generated.
    Returns: resourceName (stem) -> relativePathInGame
    """
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}
    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not is_image_file(p):
            continue

        name = p.stem
        dst = out_dir / p.name
        shutil.copy2(p, dst)

        image_map[name] = str(Path("assets") / "generated" / p.name).replace("\\", "/")

    return image_map


def _patch_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    resources_block = project.setdefault("resources", {})
    if not isinstance(resources_block, dict):
        project["resources"] = {}
        resources_block = project["resources"]

    inner = resources_block.setdefault("resources", [])
    if not isinstance(inner, list):
        resources_block["resources"] = []
        inner = resources_block["resources"]

    existing_by_name: Dict[str, Dict[str, Any]] = {}
    for r in inner:
        if isinstance(r, dict) and isinstance(r.get("name"), str):
            existing_by_name[r["name"]] = r

    for name, relpath in image_map.items():
        if name in existing_by_name:
            existing_by_name[name]["file"] = relpath
            existing_by_name[name]["kind"] = "image"
            continue

        inner.append(
            {
                "name": name,
                "kind": "image",
                "file": relpath,
                "metadata": "",
                "userAdded": True,
            }
        )


def _inject_touch_joystick(scene: Dict[str, Any]) -> None:
    """
    Ensure TouchJoystick object + instance exists.
    Requires SpriteMultitouchJoystick extension to be present in template.
    """
    _ensure_layer(scene, "UI")

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

    _ensure_instance(
        scene,
        {
            "objectName": "TouchJoystick",
            "name": "TouchJoystick",
            "x": 140,
            "y": 500,
            "angle": 0,
            "layer": "UI",
            "zOrder": 999,
        },
    )


def _inject_shop_ui(scene: Dict[str, Any]) -> None:
    """
    Create basic Shop button + panel as Text objects.
    v3.2.1 events + vars are injected separately.
    """
    _ensure_layer(scene, "UI")

    # Button
    _ensure_object(
        scene,
        {
            "name": "ShopButton",
            "type": "Text",
            "string": "SHOP",
            "fontSize": 28,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        },
    )

    _ensure_instance(
        scene,
        {
            "objectName": "ShopButton",
            "name": "ShopButton",
            "x": 860,
            "y": 20,
            "angle": 0,
            "layer": "UI",
            "zOrder": 1000,
        },
    )

    # Panel
    _ensure_object(
        scene,
        {
            "name": "ShopPanel",
            "type": "Text",
            "string": "SHOP\\n\\nSPEED +50 (100 coins)",
            "fontSize": 24,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        },
    )

    _ensure_instance(
        scene,
        {
            "objectName": "ShopPanel",
            "name": "ShopPanel",
            "x": 520,
            "y": 120,
            "angle": 0,
            "layer": "UI",
            "zOrder": 1100,
        },
    )

    # Clickable "ShopItem" line
    _ensure_object(
        scene,
        {
            "name": "ShopItem",
            "type": "Text",
            "string": "BUY: SPEED +50 (100c)",
            "fontSize": 22,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        },
    )

    _ensure_instance(
        scene,
        {
            "objectName": "ShopItem",
            "name": "ShopItem",
            "x": 560,
            "y": 220,
            "angle": 0,
            "layer": "UI",
            "zOrder": 1110,
        },
    )


def _has_shop_marker(events: List[Any]) -> bool:
    marker = "TAMACORE_AUTOGEN_SHOP_V3_2_1"
    for e in events:
        if isinstance(e, dict) and e.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(e.get("comment", "")):
                return True
    return False


def _ensure_shop_events(scene: Dict[str, Any]) -> None:
    """
    Adds:
    - On scene start: hide panel + item, ShopOpen=0
    - Toggle on/off by clicking ShopButton
    - Purchase by clicking ShopItem if Coins >= 100 (Coins -= 100, Speed += 50)
    Uses the same event JSON style already present in repo (type + parameters).
    """
    events = scene.setdefault("events", [])
    if not isinstance(events, list):
        scene["events"] = []
        events = scene["events"]

    if _has_shop_marker(events):
        return

    events.append(
        {
            "type": "BuiltinCommonInstructions::Comment",
            "comment": "TAMACORE_AUTOGEN_SHOP_V3_2_1",
            "comment2": "",
        }
    )

    # Init (Once)
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["ShopOpen", "=", "0"]},
                {"type": "BuiltinCommonInstructions::Hide", "parameters": ["ShopPanel"]},
                {"type": "BuiltinCommonInstructions::Hide", "parameters": ["ShopItem"]},
            ],
            "events": [],
        }
    )

    # Toggle ON
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ShopButton", "", ""]},
                {"type": "BuiltinCommonInstructions::MouseButtonReleased", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CompareNumbers", "parameters": ["Variable(ShopOpen)", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::Show", "parameters": ["ShopPanel"]},
                {"type": "BuiltinCommonInstructions::Show", "parameters": ["ShopItem"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["ShopOpen", "=", "1"]},
            ],
            "events": [],
        }
    )

    # Toggle OFF
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ShopButton", "", ""]},
                {"type": "BuiltinCommonInstructions::MouseButtonReleased", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CompareNumbers", "parameters": ["Variable(ShopOpen)", "=", "1"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::Hide", "parameters": ["ShopPanel"]},
                {"type": "BuiltinCommonInstructions::Hide", "parameters": ["ShopItem"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["ShopOpen", "=", "0"]},
            ],
            "events": [],
        }
    )

    # Purchase
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ShopItem", "", ""]},
                {"type": "BuiltinCommonInstructions::MouseButtonReleased", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CompareNumbers", "parameters": ["Variable(Coins)", ">=", "100"]},
            ],
            "actions": [
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Coins", "=", "Variable(Coins) - 100"],
                },
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Speed", "=", "Variable(Speed) + 50"],
                },
            ],
            "events": [],
        }
    )


def patch_project(game_json: Path, image_map: Dict[str, str], scene_name: str = "Main") -> None:
    """
    Patch a GDevelop game.json in-place:
    - update resources for generated assets
    - ensure UI layer exists
    - inject TouchJoystick + basic shop UI objects
    - v3.2.1: add Coins/Speed/ShopOpen globals + toggle/purchase events
    """
    project = read_json(game_json)
    if not isinstance(project, dict):
        raise ValueError(f"Invalid game.json (expected object): {game_json}")

    if image_map:
        _patch_resources(project, image_map)

    # Globals for shop / upgrades (v3.2.1)
    _ensure_global_variable(project, "Coins", "number", "250")
    _ensure_global_variable(project, "Speed", "number", "200")
    _ensure_global_variable(project, "ShopOpen", "number", "0")

    scene = _find_scene(project, scene_name=scene_name)
    if scene is not None:
        _ensure_layer(scene, "UI")
        _inject_touch_joystick(scene)
        _inject_shop_ui(scene)
        _ensure_shop_events(scene)

    write_json(game_json, project)
