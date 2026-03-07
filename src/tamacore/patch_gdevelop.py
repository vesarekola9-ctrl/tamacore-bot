from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import is_image_file, read_json, write_json

Json = Dict[str, Any]


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}

    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not p.is_file():
            continue
        if not is_image_file(p):
            continue

        rel_name = p.name
        dst = out_dir / rel_name
        shutil.copy2(p, dst)
        image_map[p.stem] = str(Path("assets") / "generated" / rel_name).replace("\\", "/")

    return image_map


def patch_project(
    game_json_path: Path,
    image_map: Optional[Dict[str, str]] = None,
    scene_name: str = "Main",
) -> None:
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json is not a JSON object")

    if image_map:
        _patch_resources(project, image_map)

    _ensure_global_var(project, "Coins", 250)
    _ensure_global_var(project, "Speed", 200)
    _ensure_global_var(project, "PlayerMaxSpeed", 200)
    _ensure_global_var(project, "ShopOpen", 0)

    layout = _find_layout(project, scene_name)
    if not isinstance(layout, dict):
        write_json(game_json_path, project)
        return

    _ensure_ui_layer(layout)
    _ensure_layout_object(layout, _obj_text("ShopButton", "SHOP", 36))
    _ensure_layout_object(layout, _obj_panel("ShopPanel", 520, 420))

    _ensure_instance(layout, "ShopButton", x=820, y=24, layer="UI", z=2000)
    _ensure_instance(layout, "ShopPanel", x=450, y=110, layer="UI", z=2100)

    shop = _load_shop_json(game_json_path.parent)
    if isinstance(shop, dict):
        _ensure_pack_shop(project, layout, shop)
    else:
        _ensure_layout_object(layout, _obj_text("ShopItem", "BUY: SPEED +50 (100c)", 28))
        _ensure_instance(layout, "ShopItem", x=490, y=200, layer="UI", z=2200)
        _ensure_legacy_shop_events(layout)

    write_json(game_json_path, project)


def factory_apply_catalog(
    game_json_path: Path,
    catalog: Dict[str, Any],
    scene_name: str = "Main",
    seed: int = 1337,
    with_demo_layout: bool = True,
) -> None:
    project = read_json(game_json_path)
    if not isinstance(project, dict):
        raise ValueError("game.json is not a JSON object")

    assets = catalog.get("assets", {})
    if isinstance(assets, dict):
        _patch_resources(project, assets)

    _ensure_global_var(project, "Coins", 250)
    _ensure_global_var(project, "Speed", 200)
    _ensure_global_var(project, "PlayerMaxSpeed", 200)
    _ensure_global_var(project, "ShopOpen", 0)
    _ensure_global_var(project, "FactorySeed", seed)

    layout = _find_layout(project, scene_name)
    if not isinstance(layout, dict):
        write_json(game_json_path, project)
        return

    _ensure_ui_layer(layout)

    objects = catalog.get("objects", [])
    if isinstance(objects, list):
        for obj in objects:
            if isinstance(obj, dict):
                _ensure_layout_object(layout, obj)

    if with_demo_layout:
        instances = catalog.get("instances", [])
        if isinstance(instances, list):
            for inst in instances:
                if isinstance(inst, dict):
                    _ensure_catalog_instance(layout, inst)

    _ensure_layout_object(layout, _obj_text("ShopButton", "SHOP", 36))
    _ensure_layout_object(layout, _obj_panel("ShopPanel", 520, 420))

    _ensure_instance(layout, "ShopButton", x=820, y=24, layer="UI", z=2000)
    _ensure_instance(layout, "ShopPanel", x=450, y=110, layer="UI", z=2100)

    shop = _load_shop_json(game_json_path.parent)
    if isinstance(shop, dict):
        _ensure_pack_shop(project, layout, shop)

    write_json(game_json_path, project)


def _load_shop_json(game_dir: Path) -> Optional[Json]:
    path = game_dir / "shop.json"
    if not path.exists():
        return None
    data = read_json(path)
    return data if isinstance(data, dict) else None


def _find_layout(project: Json, scene_name: str) -> Optional[Json]:
    layouts = project.get("layouts")
    if not isinstance(layouts, list) or not layouts:
        return None

    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == scene_name:
            return layout

    first = layouts[0]
    return first if isinstance(first, dict) else None


def _ensure_ui_layer(layout: Json) -> None:
    layers = layout.get("layers")
    if not isinstance(layers, list):
        layers = []
        layout["layers"] = layers

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

    vars_.append(
        {
            "name": name,
            "type": "number",
            "value": number_value,
            "children": [],
        }
    )


def _patch_resources(project: Json, image_map: Dict[str, str]) -> None:
    resources = project.get("resources")
    if not isinstance(resources, dict):
        resources = {}
        project["resources"] = resources

    inner = resources.get("resources")
    if not isinstance(inner, list):
        inner = []
        resources["resources"] = inner

    by_name: Dict[str, Json] = {}
    for item in inner:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            by_name[item["name"]] = item

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

    for obj in objects:
        if isinstance(obj, dict) and obj.get("name") == name:
            return

    objects.append(obj_def)


def _ensure_instance(layout: Json, object_name: str, x: float, y: float, layer: str, z: int) -> None:
    instances = layout.get("instances")
    if not isinstance(instances, list):
        instances = []
        layout["instances"] = instances

    for inst in instances:
        if not isinstance(inst, dict):
            continue
        if inst.get("name") == object_name or inst.get("objectName") == object_name:
            inst["x"] = x
            inst["y"] = y
            inst["layer"] = layer
            inst["zOrder"] = max(int(inst.get("zOrder", 0) or 0), z)
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


def _ensure_catalog_instance(layout: Json, inst: Json) -> None:
    object_name = str(inst.get("objectName") or inst.get("name") or "").strip()
    if not object_name:
        return

    _ensure_instance(
        layout,
        object_name=object_name,
        x=_safe_float(inst.get("x"), 0),
        y=_safe_float(inst.get("y"), 0),
        layer=str(inst.get("layer", "")),
        z=_safe_int(inst.get("zOrder"), 0),
    )


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


def _ensure_pack_shop(project: Json, layout: Json, shop: Json) -> None:
    upgrades = shop.get("upgrades")
    if not isinstance(upgrades, list):
        upgrades = []

    currency_var = str(shop.get("currencyVariable", "Coins") or "Coins")
    marker = "TAMACORE_AUTOGEN_PACK_SHOP_V3_3"

    events = layout.get("events")
    if not isinstance(events, list):
        events = []
        layout["events"] = events

    if any(isinstance(e, dict) and e.get("type") == "BuiltinCommonInstructions::Comment" and marker in str(e.get("comment", "")) for e in events):
        return

    normalized: List[Json] = []
    for idx, raw in enumerate(upgrades):
        if not isinstance(raw, dict):
            continue

        upgrade_id = str(raw.get("id", f"upgrade_{idx + 1}")).strip() or f"upgrade_{idx + 1}"
        name = str(raw.get("name", upgrade_id)).strip() or upgrade_id
        cost = _safe_int(raw.get("cost"), 0)
        effect = raw.get("effect", {})
        if not isinstance(effect, dict):
            effect = {}

        owned_var = str(raw.get("ownedVariable", f"Owned_{_safe_identifier(upgrade_id)}"))
        ui_text = str(raw.get("uiText", f"BUY: {name} ({cost}c)"))

        normalized.append(
            {
                "id": upgrade_id,
                "name": name,
                "cost": cost,
                "effect": effect,
                "ownedVariable": owned_var,
                "uiText": ui_text,
                "objectName": f"ShopItem_{idx + 1}",
            }
        )

    for item in normalized:
        _ensure_global_var(project, item["ownedVariable"], 0)

    start_x = 490
    start_y = 180
    step_y = 56

    for idx, item in enumerate(normalized):
        _ensure_layout_object(layout, _obj_text(item["objectName"], item["uiText"], 28))
        _ensure_instance(
            layout,
            item["objectName"],
            x=start_x,
            y=start_y + idx * step_y,
            layer="UI",
            z=2200 + idx,
        )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Comment",
            "comment": marker,
            "comment2": "",
        }
    )

    hide_actions = [
        _act("BuiltinCommonInstructions::Hide", ["ShopPanel"]),
        _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "0"]),
    ]
    show_actions = [
        _act("BuiltinCommonInstructions::Show", ["ShopPanel"]),
        _act("BuiltinCommonInstructions::SetNumberVariable", ["ShopOpen", "1"]),
    ]

    for item in normalized:
        hide_actions.append(_act("BuiltinCommonInstructions::Hide", [item["objectName"]]))
        show_actions.append(_act("BuiltinCommonInstructions::Show", [item["objectName"]]))

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", [])],
            "actions": hide_actions,
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Init",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "0"]),
            ],
            "actions": show_actions,
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Toggle ON",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                _cond("BuiltinCommonInstructions::CursorOnObject", ["ShopButton", "", ""]),
                _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
                _cond("BuiltinCommonInstructions::CompareNumbers", ["Variable(ShopOpen)", "=", "1"]),
            ],
            "actions": hide_actions,
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Shop Toggle OFF",
        }
    )

    for item in normalized:
        events.append(_purchase_event(item, currency_var))
        events.append(_purchase_no_coins_event(item, currency_var))
        events.append(_purchase_owned_event(item))


def _purchase_event(item: Json, currency_var: str) -> Json:
    actions: List[Json] = [
        _act("BuiltinCommonInstructions::SubFromNumberVariable", [currency_var, str(item["cost"])]),
        _act("BuiltinCommonInstructions::SetNumberVariable", [item["ownedVariable"], "1"]),
    ]

    actions.extend(_effect_actions(item["effect"]))
    actions.append(
        _act(
            "TextObject::SetString",
            [
                item["objectName"],
                f"\"{_escape_gd_string(str(item['name']))} — OWNED\"",
            ],
        )
    )

    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            _cond("BuiltinCommonInstructions::CursorOnObject", [item["objectName"], "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({item['ownedVariable']})", "=", "0"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({currency_var})", ">=", str(item["cost"])]),
        ],
        "actions": actions,
        "events": [],
        "disabled": False,
        "folded": False,
        "infiniteLoopWarning": False,
        "name": f"Buy {item['id']}",
    }


def _purchase_no_coins_event(item: Json, currency_var: str) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            _cond("BuiltinCommonInstructions::CursorOnObject", [item["objectName"], "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({item['ownedVariable']})", "=", "0"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({currency_var})", "<", str(item["cost"])]),
        ],
        "actions": [
            _act(
                "TextObject::SetString",
                [
                    item["objectName"],
                    (
                        f"\"{_escape_gd_string(str(item['name']))} "
                        f"({item['cost']}c) — NEED \" + "
                        f"ToString({item['cost']}-Variable({currency_var})) + \" MORE\""
                    ),
                ],
            )
        ],
        "events": [],
        "disabled": False,
        "folded": False,
        "infiniteLoopWarning": False,
        "name": f"Buy {item['id']} No Coins",
    }


def _purchase_owned_event(item: Json) -> Json:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            _cond("BuiltinCommonInstructions::CursorOnObject", [item["objectName"], "", ""]),
            _cond("BuiltinCommonInstructions::MouseButtonReleased", ["Left"]),
            _cond("BuiltinCommonInstructions::CompareNumbers", [f"Variable({item['ownedVariable']})", "=", "1"]),
        ],
        "actions": [
            _act(
                "TextObject::SetString",
                [
                    item["objectName"],
                    f"\"{_escape_gd_string(str(item['name']))} — OWNED\"",
                ],
            )
        ],
        "events": [],
        "disabled": False,
        "folded": False,
        "infiniteLoopWarning": False,
        "name": f"Buy {item['id']} Owned",
    }


def _effect_actions(effect: Json) -> List[Json]:
    actions: List[Json] = []
    if not isinstance(effect, dict):
        return actions

    for key, value in effect.items():
        amount = _safe_int(value, 0)

        if key == "playerMaxSpeedAdd":
            actions.append(_act("BuiltinCommonInstructions::AddToNumberVariable", ["PlayerMaxSpeed", str(amount)]))
            actions.append(_act("BuiltinCommonInstructions::AddToNumberVariable", ["Speed", str(amount)]))
        elif key == "speedAdd":
            actions.append(_act("BuiltinCommonInstructions::AddToNumberVariable", ["Speed", str(amount)]))
        elif key == "coinsAdd":
            actions.append(_act("BuiltinCommonInstructions::AddToNumberVariable", ["Coins", str(amount)]))
        else:
            if _is_reasonable_variable_name(str(key)):
                actions.append(_act("BuiltinCommonInstructions::AddToNumberVariable", [str(key), str(amount)]))

    return actions


def _ensure_legacy_shop_events(layout: Json) -> None:
    events = layout.get("events")
    if not isinstance(events, list):
        events = []
        layout["events"] = events

    marker = "TAMACORE_AUTOGEN_SHOP_V3_2_1"
    for event in events:
        if isinstance(event, dict) and event.get("type") == "BuiltinCommonInstructions::Comment":
            if marker in str(event.get("comment", "")):
                return

    events.append(
        {
            "type": "BuiltinCommonInstructions::Comment",
            "comment": marker,
            "comment2": "",
        }
    )

    events.append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [_cond("BuiltinCommonInstructions::AtTheBeginningOfTheScene", [])],
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
                _act("BuiltinCommonInstructions::AddToNumberVariable", ["PlayerMaxSpeed", "50"]),
            ],
            "events": [],
            "disabled": False,
            "folded": False,
            "infiniteLoopWarning": False,
            "name": "Buy Speed",
        }
    )


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_identifier(value: str) -> str:
    s = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in value)
    return s or "upgrade"


def _is_reasonable_variable_name(value: str) -> bool:
    if not value:
        return False
    return all(ch.isalnum() or ch == "_" for ch in value)


def _escape_gd_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


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
