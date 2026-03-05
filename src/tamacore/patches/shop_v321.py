from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

Json = Dict[str, Any]


def apply_shop_v321(project: Json) -> bool:
    """
    Adds ShopButton/ShopPanel/ShopItem + globals + UI layer + instances.
    Tries to add events in the common GDevelop-export JSON format.
    SAFE: if events schema doesn't match, it will still add objects/instances/vars
    (so nothing breaks) and you can inspect schema with inspect script.
    """
    changed = False

    layout = _get_first_layout(project)
    if layout is None:
        return False

    changed |= _ensure_ui_layer(layout)

    changed |= _ensure_global_var(project, "Coins", 250)
    changed |= _ensure_global_var(project, "Speed", 200)
    changed |= _ensure_global_var(project, "ShopOpen", 0)

    changed |= _ensure_object(project, _obj_text("ShopButton", "SHOP", 36))
    changed |= _ensure_object(project, _obj_panel("ShopPanel"))
    changed |= _ensure_object(project, _obj_text("ShopItem", "SPEED +50 (100c)", 28))

    changed |= _ensure_instance(layout, "ShopButton", 40, 40, "UI")
    changed |= _ensure_instance(layout, "ShopPanel", 30, 120, "UI")
    changed |= _ensure_instance(layout, "ShopItem", 60, 170, "UI")

    # Try add events (best-effort, safe)
    changed |= _try_add_shop_events(layout)

    return changed


# ----------------------------
# Layout + project helpers
# ----------------------------

def _get_first_layout(project: Json) -> Optional[Json]:
    layouts = project.get("layouts")
    if isinstance(layouts, list) and layouts and isinstance(layouts[0], dict):
        return layouts[0]
    return None


def _ensure_ui_layer(layout: Json) -> bool:
    layers = layout.get("layers")
    if not isinstance(layers, list):
        layers = []
        layout["layers"] = layers

    for ly in layers:
        if isinstance(ly, dict) and ly.get("name") == "UI":
            return False

    layers.append({
        "name": "UI",
        "visibility": True,
        "effects": [],
        "isLightingLayer": False,
        "followBaseLayerCamera": True,
    })
    return True


def _ensure_global_var(project: Json, name: str, number_value: float) -> bool:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            return False

    vars_.append({"name": name, "type": "number", "value": number_value, "children": []})
    return True


def _ensure_object(project: Json, obj_def: Json) -> bool:
    objects = project.get("objects")
    if not isinstance(objects, list):
        objects = []
        project["objects"] = objects

    for o in objects:
        if isinstance(o, dict) and o.get("name") == obj_def.get("name"):
            return False

    objects.append(obj_def)
    return True


def _ensure_instance(layout: Json, object_name: str, x: float, y: float, layer: str) -> bool:
    inst = layout.get("instances")
    if not isinstance(inst, list):
        inst = []
        layout["instances"] = inst

    for it in inst:
        if isinstance(it, dict) and it.get("name") == object_name:
            if it.get("layer") != layer:
                it["layer"] = layer
                return True
            return False

    inst.append({
        "name": object_name,
        "layer": layer,
        "x": x,
        "y": y,
        "angle": 0,
        "zOrder": 0,
        "locked": False,
        "persistentUuid": "",
        "customSize": False,
        "width": 0,
        "height": 0,
    })
    return True


# ----------------------------
# Object templates
# ----------------------------

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
            "bold": False,
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


def _obj_panel(name: str) -> Json:
    return {
        "name": name,
        "type": "PanelSpriteObject::PanelSprite",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {"width": 520, "height": 420},
        "effects": [],
    }


# ----------------------------
# Events (best-effort)
# ----------------------------

def _try_add_shop_events(layout: Json) -> bool:
    events = layout.get("events")
    if not isinstance(events, list):
        # Unknown schema, skip safely
        return False

    marker = "TAMACORE_AUTOGEN_SHOP_V3_2_1"
    for e in events:
        if isinstance(e, dict) and e.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(e.get("comment", "")):
                return False

    changed = True
    events.append({
        "type": "BuiltinCommonInstructions::Comment",
        "comment": f"{marker}",
        "comment2": "",
    })

    # Init hide
    events.append(_event(
        conditions=[_cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", [])],
        actions=[
            _act("BuiltinCommonInstructions::Hide", ["ShopPanel"]),
            _act("BuiltinCommonInstructions::Hide", ["ShopItem"]),
            _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "0"]),
        ],
        name="Init Shop",
    ))

    # Toggle ON
    events.append(_event(
        conditions=[
            _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "0"]),
        ],
        actions=[
            _act("BuiltinCommonInstructions::Show", ["ShopPanel"]),
            _act("BuiltinCommonInstructions::Show", ["ShopItem"]),
            _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "1"]),
        ],
        name="Shop ON",
    ))

    # Toggle OFF
    events.append(_event(
        conditions=[
            _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "1"]),
        ],
        actions=[
            _act("BuiltinCommonInstructions::Hide", ["ShopPanel"]),
            _act("BuiltinCommonInstructions::Hide", ["ShopItem"]),
            _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "0"]),
        ],
        name="Shop OFF",
    ))

    # Purchase
    events.append(_event(
        conditions=[
            _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopItem", "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(Coins)", ">=", "100"]),
        ],
        actions=[
            _act("BuiltinCommonInstructions::SubFromNumberVariable", ["Coins", "100"]),
            _act("BuiltinCommonInstructions::AddToNumberVariable", ["Speed", "50"]),
        ],
        name="Buy Speed",
    ))

    return changed


def _event(conditions: List[Json], actions: List[Json], name: str) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": conditions,
        "actions": actions,
        "events": [],
        "disabled": False,
        "folded": False,
        "infiniteLoopWarning": False,
        "name": name,
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
