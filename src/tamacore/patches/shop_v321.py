from __future__ import annotations
from typing import Any, Dict, List, Optional

Json = Dict[str, Any]


def apply_shop_v321(project: Json, scene_name: str = "Main") -> bool:
    layout = _find_layout(project, scene_name)
    if layout is None:
        return False

    changed = False

    _ensure_ui_layer(layout)

    # project globals
    changed |= _ensure_global(project, "Coins", 250)
    changed |= _ensure_global(project, "Speed", 200)
    changed |= _ensure_global(project, "ShopOpen", 0)

    # IMPORTANT: your template uses layout-local objects
    changed |= _ensure_layout_object(layout, _obj_text("ShopButton", "SHOP", 36))
    changed |= _ensure_layout_object(layout, _obj_panel("ShopPanel", 520, 420))
    changed |= _ensure_layout_object(layout, _obj_text("ShopItem", "BUY: SPEED +50 (100c)", 28))

    changed |= _ensure_instance(layout, "ShopButton", 820, 24, "UI", 2000)
    changed |= _ensure_instance(layout, "ShopPanel", 450, 110, "UI", 2100)
    changed |= _ensure_instance(layout, "ShopItem", 490, 200, "UI", 2200)

    changed |= _ensure_shop_events(layout)

    return changed


# ---------------- helpers ----------------

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
            ly.setdefault("followBaseLayerCamera", True)
            return
    layers.append({"name": "UI", "visibility": True, "effects": [], "followBaseLayerCamera": True})


def _ensure_global(project: Json, name: str, value: float) -> bool:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_
    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            return False
    vars_.append({"name": name, "type": "number", "value": value, "children": []})
    return True


def _ensure_layout_object(layout: Json, obj: Json) -> bool:
    objs = layout.get("objects")
    if not isinstance(objs, list):
        objs = []
        layout["objects"] = objs
    name = obj.get("name")
    for o in objs:
        if isinstance(o, dict) and o.get("name") == name:
            return False
    objs.append(obj)
    return True


def _ensure_instance(layout: Json, name: str, x: float, y: float, layer: str, z: int) -> bool:
    inst = layout.get("instances")
    if not isinstance(inst, list):
        inst = []
        layout["instances"] = inst
    for i in inst:
        if isinstance(i, dict) and (i.get("name") == name or i.get("objectName") == name):
            # ensure UI
            changed = False
            if i.get("layer") != layer:
                i["layer"] = layer
                changed = True
            if int(i.get("zOrder", 0) or 0) < z:
                i["zOrder"] = z
                changed = True
            return changed

    inst.append({
        "name": name,
        "objectName": name,
        "x": x,
        "y": y,
        "angle": 0,
        "layer": layer,
        "zOrder": z,
        "locked": False,
        "persistentUuid": "",
        "customSize": False,
        "width": 0,
        "height": 0,
    })
    return True


def _obj_text(name: str, text: str, size: int) -> Json:
    return {
        "name": name,
        "type": "TextObject::Text",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {
            "font": "",
            "size": size,
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


# -------- events: IMPORTANT: use "instruction" field (NOT type=instruction) --------

def _ensure_shop_events(layout: Json) -> bool:
    events = layout.get("events")
    if not isinstance(events, list):
        events = []
        layout["events"] = events

    marker = "TAMACORE_AUTOGEN_SHOP_V3_2_1"
    for e in events:
        if isinstance(e, dict) and e.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(e.get("comment", "")):
                return False

    events.append({"type": "BuiltinCommonInstructions::Comment", "comment": marker, "comment2": ""})

    # Init
    events.append(_std(
        cond=[_c("AtTheBeginningOfTheScene", [])],
        act=[
            _a("Hide", ["ShopPanel"]),
            _a("Hide", ["ShopItem"]),
            _a("SetNumberVariable", ["ShopOpen", "=", "0"]),
        ],
        name="Shop Init",
    ))

    # Toggle ON
    events.append(_std(
        cond=[
            _c("CursorOnObject", ["ShopButton", "", ""]),
            _c("MouseButtonReleased", ["Left"]),
            _c("CompareNumbers", ["Variable(ShopOpen)", "=", "0"]),
        ],
        act=[
            _a("Show", ["ShopPanel"]),
            _a("Show", ["ShopItem"]),
            _a("SetNumberVariable", ["ShopOpen", "=", "1"]),
        ],
        name="Shop ON",
    ))

    # Toggle OFF
    events.append(_std(
        cond=[
            _c("CursorOnObject", ["ShopButton", "", ""]),
            _c("MouseButtonReleased", ["Left"]),
            _c("CompareNumbers", ["Variable(ShopOpen)", "=", "1"]),
        ],
        act=[
            _a("Hide", ["ShopPanel"]),
            _a("Hide", ["ShopItem"]),
            _a("SetNumberVariable", ["ShopOpen", "=", "0"]),
        ],
        name="Shop OFF",
    ))

    # Purchase
    events.append(_std(
        cond=[
            _c("CursorOnObject", ["ShopItem", "", ""]),
            _c("MouseButtonReleased", ["Left"]),
            _c("CompareNumbers", ["Variable(Coins)", ">=", "100"]),
        ],
        act=[
            _a("SubFromNumberVariable", ["Coins", "100"]),
            _a("AddToNumberVariable", ["Speed", "50"]),
        ],
        name="Buy Speed",
    ))

    return True


def _std(cond: List[Json], act: List[Json], name: str) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": cond,
        "actions": act,
        "events": [],
        "disabled": False,
        "folded": False,
        "infiniteLoopWarning": False,
        "name": name,
    }


def _c(instruction: str, params: List[str]) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "inverted": False,
        "parameters": params,
        "subInstructions": [],
        "instructionType": "condition",
        "instruction": instruction,
    }


def _a(instruction: str, params: List[str]) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "parameters": params,
        "subInstructions": [],
        "instructionType": "action",
        "instruction": instruction,
    }
