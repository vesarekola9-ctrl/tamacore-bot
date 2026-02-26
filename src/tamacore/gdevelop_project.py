from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .utils import read_json, write_json


def load_or_create_project(game_json: Path) -> Dict[str, Any]:
    if game_json.exists():
        return read_json(game_json)

    return {
        "gdVersion": "5",
        "properties": {
            "name": "TamaCore",
            "packageName": "com.yourcompany.tamacore",
            "version": "0.1.0",
        },
        "resources": {"resources": []},
        "layouts": [],
        "externalLayouts": [],
        "eventsFunctionsExtensions": [],
        "variables": [],
    }


def _resources(project: Dict[str, Any]) -> list[dict]:
    if "resources" not in project or not isinstance(project["resources"], dict):
        project["resources"] = {"resources": []}
    if "resources" not in project["resources"] or not isinstance(project["resources"]["resources"], list):
        project["resources"]["resources"] = []
    return project["resources"]["resources"]


def ensure_resource(project: Dict[str, Any], name: str, kind: str, file_path: str) -> None:
    res = _resources(project)
    for r in res:
        if isinstance(r, dict) and r.get("name") == name:
            r["kind"] = kind
            r["file"] = file_path
            r.setdefault("metadata", "")
            r.setdefault("userAdded", True)
            return
    res.append({"name": name, "kind": kind, "file": file_path, "metadata": "", "userAdded": True})


def get_or_create_layout(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    if "layouts" not in project or not isinstance(project["layouts"], list):
        project["layouts"] = []
    for l in project["layouts"]:
        if isinstance(l, dict) and l.get("name") == name:
            return l

    layout = {
        "name": name,
        "title": name,
        "layers": [{"name": "", "visibility": True, "effects": []}],
        "objects": [],
        "instances": [],
        "events": [],
        "variables": [],
    }
    project["layouts"].append(layout)
    return layout


def _ensure_layout_object(layout: Dict[str, Any], obj: Dict[str, Any]) -> None:
    if "objects" not in layout or not isinstance(layout["objects"], list):
        layout["objects"] = []
    for existing in layout["objects"]:
        if isinstance(existing, dict) and existing.get("name") == obj.get("name"):
            existing.clear()
            existing.update(obj)
            return
    layout["objects"].append(obj)


def _ensure_instance(layout: Dict[str, Any], inst: Dict[str, Any]) -> None:
    if "instances" not in layout or not isinstance(layout["instances"], list):
        layout["instances"] = []
    for existing in layout["instances"]:
        if isinstance(existing, dict) and existing.get("objectName") == inst.get("objectName"):
            existing.clear()
            existing.update(inst)
            return
    layout["instances"].append(inst)


def make_sprite_object(name: str, image_resource_name: str, topdown: bool = False) -> Dict[str, Any]:
    obj: Dict[str, Any] = {
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
                                "image": image_resource_name,
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

    if topdown:
        obj["behaviors"].append(
            {
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
        )

    return obj


def make_text_object(name: str, initial_text: str) -> Dict[str, Any]:
    return {
        "name": name,
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


def _ensure_scene_variable(layout: Dict[str, Any], var_name: str, initial_value: int = 0) -> None:
    if "variables" not in layout or not isinstance(layout["variables"], list):
        layout["variables"] = []
    for v in layout["variables"]:
        if isinstance(v, dict) and v.get("name") == var_name:
            v.setdefault("type", "number")
            v.setdefault("value", str(initial_value))
            return
    layout["variables"].append({"name": var_name, "type": "number", "value": str(initial_value), "children": []})


def set_events(layout: Dict[str, Any]) -> None:
    # Best-effort. If your GDevelop rejects these IDs, paste the error and we’ll adapt.
    layout["events"] = [
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: 0\""]},
            ],
            "events": [],
        },
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Coin"]}],
            "actions": [
                {
                    "type": "BuiltinCommonInstructions::SetNumberVariable",
                    "parameters": ["Score", "=", "Variable(Score) + 1"],
                },
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(50, 900)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(80, 500)"]},
            ],
            "events": [],
        },
    ]


def produce_game(game_dir: Path, image_map: Dict[str, str]) -> Path:
    game_json = game_dir / "game.json"
    project = load_or_create_project(game_json)

    for logical, rel_file in image_map.items():
        ensure_resource(project, name=logical, kind="image", file_path=rel_file)

    layout = get_or_create_layout(project, "Main")
    _ensure_scene_variable(layout, "Score", 0)

    player_res = "player" if "player" in image_map else next(iter(image_map.keys()))
    coin_res = "coin" if "coin" in image_map else player_res
    bg_res = "bg" if "bg" in image_map else None

    if bg_res:
        _ensure_layout_object(layout, make_sprite_object("Background", bg_res, topdown=False))
    _ensure_layout_object(layout, make_sprite_object("Player", player_res, topdown=True))
    _ensure_layout_object(layout, make_sprite_object("Coin", coin_res, topdown=False))
    _ensure_layout_object(layout, make_text_object("HUD", "Score: 0"))

    if bg_res:
        _ensure_instance(layout, {"objectName": "Background", "x": 0, "y": 0, "angle": 0, "layer": "", "zOrder": 0})
    _ensure_instance(layout, {"objectName": "Player", "x": 200, "y": 240, "angle": 0, "layer": "", "zOrder": 1})
    _ensure_instance(layout, {"objectName": "Coin", "x": 520, "y": 280, "angle": 0, "layer": "", "zOrder": 2})
    _ensure_instance(layout, {"objectName": "HUD", "x": 20, "y": 20, "angle": 0, "layer": "", "zOrder": 99})

    set_events(layout)
    write_json(game_json, project)
    return game_json
