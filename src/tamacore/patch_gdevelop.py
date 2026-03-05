from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import is_image_file, read_json, write_json

Json = Dict[str, Any]


# ----------------------------
# Public API (pipeline uses these)
# ----------------------------

def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copies images from repo assets/ into game/assets/generated/.
    Returns map: resourceName -> relative path in game folder.
    """
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}
    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not is_image_file(p):
            continue
        dst = out_dir / p.name
        shutil.copy2(p, dst)

        # resource name = file stem (without extension)
        image_map[p.stem] = str(Path("assets") / "generated" / p.name).replace("\\", "/")

    return image_map


def patch_project(game_json_path: Path, image_map: Optional[Dict[str, str]] = None, scene_name: str = "Main") -> None:
    """
    Patch game.json in-place:
    - register resources for generated assets
    - add v3.2.1 shop (objects + instances + events) to the FIRST layout (or scene_name if found)
    - ensure UI layer exists
    - ensure globals Coins/Speed/ShopOpen exist
    """
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json is not a JSON object")

    if image_map:
        _patch_resources(project, image_map)

    # globals (project-level)
    _ensure_global_var(project, "Coins", 250)
    _ensure_global_var(project, "Speed", 200)
    _ensure_global_var(project, "ShopOpen", 0)

    layout = _find_layout(project, scene_name)
    if layout is None:
        write_json(game_json_path, project)
        return

    _ensure_ui_layer(layout)

    # v3.2.1 shop objects must go INSIDE layout["objects"] (your template uses layout-local objects)
    _ensure_layout_object(layout, _obj_text("ShopButton", "SHOP", 36))
    _ensure_layout_object(layout, _obj_panel("ShopPanel", w=520, h=420))
    _ensure_layout_object(layout, _obj_text("ShopItem", "BUY: SPEED +50 (100c)", 28))

    # instances (safe: include both name + objectName so it works across schemas)
    _ensure_instance(layout, "ShopButton", x=820, y=24, layer="UI", z=2000)
    _ensure_instance(layout, "ShopPanel",  x=450, y=110, layer="UI", z=2100)
    _ensure_instance(layout, "ShopItem",   x=490, y=200, layer="UI", z=2200)

    _ensure_shop_events(layout)

    write_json(game_json_path, project)


# ----------------------------
# Core JSON ops
# ----------------------------

def _find_layout(project: Json, scene_name: str) -> Optional[Json]:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None

    for l in layouts:
        if isinstance(l, dict) and l.get("name") == scene_name:
            return l

    first = layouts[0]
    return first if isinstance(first, dict) else None


def _ensure_ui_layer(layout: Json) -> None:
    layers = layout.get("layers")
    if not isinstance(layers, list):
        layers = []
        layout["layers"] = layers

    for ly in layers:
        if isinstance(ly, dict) and ly.get("name") == "UI":
            # ensure follows base camera so it behaves like UI
            ly.setdefault("followBaseLayerCamera", True)
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

    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            # keep existing, but ensure structure
            v.setdefault("type", "number")
            v.setdefault("children", [])
            if "value" not in v:
                v["value"] = number_value
            return

    vars_.append({"name": name, "type": "number", "value": number_value, "children": []})


def _patch_resources(project: Json, image_map: Dict[str, str]) -> None:
    res = project.get("resources")
    if not isinstance(res, dict):
        res = {}
        project["resources"] = res

    inner = res.get("resources")
    if not isinstance(inner, list):
        inner = []
        res["resources"] = inner

    by_name: Dict[str, Json] = {}
    for r in inner:
        if isinstance(r, dict) and isinstance(r.get("name"), str):
            by_name[r["name"]] = r

    for name, relpath in image_map.items():
        if name in by_name:
            by_name[name]["kind"] = "image"
            by_name[name]["file"] = relpath
            by_name[name]["userAdded"] = True
        else:
            inner.append(
                {
                    "name": name,
                    "kind": "image",
                    "file": relpath,
                    "metadata": "",
                    "userAdded": True,
                }
            )


def _ensure_layout_object(layout: Json, obj_def: Json) -> None:
    objects = layout.get("objects")
    if not isinstance(objects, list):
        objects = []
        layout["objects"] = objects

    name = obj_def.get("name")
    if not name:
        return

    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            return

    objects.append(obj_def)


def _ensure_instance(layout: Json, object_name: str, x: float, y: float, layer: str, z: int) -> None:
    inst = layout.get("instances")
    if not isinstance(inst, list):
        inst = []
        layout["instances"] = inst

    for it in inst:
        if not isinstance(it, dict):
            continue
        if it.get("name") == object_name or it.get("objectName") == object_name:
            # ensure on UI layer + z
            it["layer"] = layer
            it["zOrder"] = max(int(it.get("zOrder", 0) or 0), z)
            return

    inst.append(
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


# ----------------------------
# Object defs (template-safe)
# ----------------------------

def _obj_text(name: str, text: str, font_size: int) -> Json:
    # Use canonical TextObject::Text format (works in exported JSON)
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
            "alignment": "center",
            "verticalAlignment": "center",
            "wrapping": False,
        },
        "effects": [],
    }


def _obj_panel(name: str, w: int, h: int) -> Json:
    # PanelSprite is present in many templates; even if not, it won't delete anything.
    return {
        "name": name,
        "type": "PanelSpriteObject::PanelSprite",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {"width": w, "height": h},
        "effects": [],
    }


# ----------------------------
# Events (v3.2.1)
# ----------------------------

def _ensure_shop_events(layout: Json) -> None:
    events = layout.get("events")
    if not isinstance(events, list):
        events = []
        layout["events"] = events

    marker = "TAMACORE_AUTOGEN_SHOP_V3_2_1"
    for e in events:
        if isinstance(e, dict) and e.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(e.get("comment", "")):
                return

    events.append(
        {
            "type": "BuiltinCommonInstructions::Comment",
            "comment": marker,
            "comment2": "",
        }
    )

    # Init: hide panel+item and set ShopOpen=0 once at start
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", [])
            ],
            "actions": [
                _act("BuiltinCommonInstructions::Hide", ["ShopPanel"]),
                _act("BuiltinCommonInstructions::Hide", ["ShopItem"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "0"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Init",
        }
    )

    # Toggle ON
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "0"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::Show", ["ShopPanel"]),
                _act("BuiltinCommonInstructions::Show", ["ShopItem"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "1"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Toggle ON",
        }
    )

    # Toggle OFF
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "1"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::Hide", ["ShopPanel"]),
                _act("BuiltinCommonInstructions::Hide", ["ShopItem"]),
                _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "0"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Toggle OFF",
        }
    )

    # Purchase: Speed +50 for 100 coins
    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopItem", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(Coins)", ">=", "100"]),
            ],
            "actions": [
                _act("BuiltinCommonInstructions::SubFromNumberVariable", ["Coins", "100"]),
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["Speed", "50"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Buy Speed",
        }
    )


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
