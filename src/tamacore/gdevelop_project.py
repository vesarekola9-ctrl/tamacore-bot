from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .utils import read_json, write_json


def load_or_create_project(game_json: Path) -> Dict[str, Any]:
    """
    Create a GDevelop 5 compatible project JSON structure.
    This matches the schema used by real exported examples:
    - gdVersion is an object
    - firstLayout exists
    - properties include required fields
    - resources contain resourceFolders
    - layouts contain uiSettings, layers.cameras, etc.
    """
    if game_json.exists():
        # If it's already a project, load and then we will patch/ensure required keys.
        data = read_json(game_json)
        return data

    return {
        "firstLayout": "Main",
        "gdVersion": {"build": 0, "major": 5, "minor": 0, "revision": 0},
        "properties": {
            "folderProject": False,
            "useExternalSourceFiles": False,
            "projectFile": str(game_json).replace("\\", "\\\\"),
            "name": "TamaCore",
            "author": "",
            "packageName": "com.yourcompany.tamacore",
            "version": "0.1.0",
            "windowWidth": 960,
            "windowHeight": 540,
            "latestCompilationDirectory": "",
            "maxFPS": 60,
            "minFPS": 10,
            "verticalSync": False,
            "linuxExecutableFilename": "",
            "macExecutableFilename": "",
            "winExecutableFilename": "",
            "winExecutableIconFile": "",
            "extensions": [
                {"name": "BuiltinObject"},
                {"name": "BuiltinVariables"},
                {"name": "BuiltinTime"},
                {"name": "BuiltinMouse"},
                {"name": "BuiltinKeyboard"},
                {"name": "BuiltinJoystick"},
                {"name": "BuiltinCamera"},
                {"name": "BuiltinWindow"},
                {"name": "BuiltinFile"},
                {"name": "BuiltinNetwork"},
                {"name": "BuiltinScene"},
                {"name": "BuiltinAdvanced"},
                {"name": "Sprite"},
                {"name": "BuiltinCommonInstructions"},
                {"name": "BuiltinCommonConversions"},
                {"name": "BuiltinStringInstructions"},
                {"name": "BuiltinMathematicalTools"},
                {"name": "BuiltinExternalLayouts"},
                {"name": "TextObject"},
            ],
            "platforms": [{"name": "GDevelop JS platform"}],
            "currentPlatform": "GDevelop JS platform",
        },
        "resources": {"resources": [], "resourceFolders": []},
        "objects": [],
        "objectsGroups": [],
        "variables": [],
        "layouts": [],
        "externalEvents": [],
        "externalLayouts": [],
        "externalSourceFiles": [],
    }


def _resources(project: Dict[str, Any]) -> list[dict]:
    project.setdefault("resources", {"resources": [], "resourceFolders": []})
    project["resources"].setdefault("resources", [])
    project["resources"].setdefault("resourceFolders", [])
    return project["resources"]["resources"]


def ensure_resource(project: Dict[str, Any], name: str, kind: str, file_path: str) -> None:
    res = _resources(project)
    for r in res:
        if isinstance(r, dict) and r.get("name") == name:
            r["kind"] = kind
            r["file"] = file_path
            r.setdefault("metadata", "")
            r.setdefault("userAdded", True)
            r.setdefault("alwaysLoaded", False)
            # GDevelop expects this for images
            if kind == "image":
                r.setdefault("smoothed", True)
            return

    entry = {
        "alwaysLoaded": False,
        "file": file_path,
        "kind": kind,
        "metadata": "",
        "name": name,
        "userAdded": True,
    }
    if kind == "image":
        entry["smoothed"] = True
    res.append(entry)


def get_or_create_layout(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    project.setdefault("layouts", [])
    for l in project["layouts"]:
        if isinstance(l, dict) and l.get("name") == name:
            return l

    layout = {
        # Required-ish layout keys (seen in official examples)
        "name": name,
        "title": "",
        "mangledName": name.replace(" ", "_"),
        "r": 255,
        "g": 255,
        "b": 255,
        "v": 255,
        "oglFOV": 90,
        "oglZNear": 1,
        "oglZFar": 500,
        "standardSortMethod": True,
        "stopSoundsOnStartup": True,
        "disableInputWhenNotFocused": True,
        "uiSettings": {
            "grid": False,
            "gridWidth": 32,
            "gridHeight": 32,
            "gridOffsetX": 0,
            "gridOffsetY": 0,
            "snap": True,
            "zoomFactor": 1,
            "gridR": 158,
            "gridG": 180,
            "gridB": 255,
            "windowMask": False,
        },
        "objectsGroups": [],
        "variables": [],
        "instances": [],
        "objects": [],
        "events": [],
        "layers": [
            {
                "name": "",
                "visibility": True,
                "cameras": [
                    {
                        "defaultSize": True,
                        "defaultViewport": True,
                        "height": 0,
                        "width": 0,
                        "viewportTop": 0,
                        "viewportLeft": 0,
                        "viewportRight": 1,
                        "viewportBottom": 1,
                    }
                ],
                "effects": [],
            }
        ],
        "behaviorsSharedData": [],
    }
    project["layouts"].append(layout)
    return layout


def _ensure_layout_object(layout: Dict[str, Any], obj: Dict[str, Any]) -> None:
    layout.setdefault("objects", [])
    for existing in layout["objects"]:
        if isinstance(existing, dict) and existing.get("name") == obj.get("name"):
            existing.clear()
            existing.update(obj)
            return
    layout["objects"].append(obj)


def _ensure_instance(layout: Dict[str, Any], inst: Dict[str, Any]) -> None:
    layout.setdefault("instances", [])
    for existing in layout["instances"]:
        if isinstance(existing, dict) and existing.get("name") == inst.get("name"):
            existing.clear()
            existing.update(inst)
            return
    layout["instances"].append(inst)


def make_sprite_object(name: str, image_resource_name: str) -> Dict[str, Any]:
    """
    Sprite object schema matching GDevelop examples.
    """
    return {
        "name": name,
        "type": "Sprite",
        "updateIfNotVisible": True,
        "variables": [],
        "behaviors": [],
        "animations": [
            {
                "name": "",
                "useMultipleDirections": False,
                "directions": [
                    {
                        "looping": True,
                        "timeBetweenFrames": 0.1,
                        "sprites": [
                            {
                                "hasCustomCollisionMask": False,
                                "image": image_resource_name,
                                "points": [],
                                "originPoint": {"name": "origine", "x": 0, "y": 0},
                                "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0},
                                "customCollisionMask": [],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def make_text_object(name: str, initial_text: str) -> Dict[str, Any]:
    """
    Text object schema matching GDevelop examples.
    """
    return {
        "name": name,
        "type": "TextObject::Text",
        "variables": [],
        "behaviors": [],
        "string": initial_text,
        "font": "",
        "characterSize": 28,
        "bold": True,
        "italic": False,
        "underlined": False,
        "smoothed": True,
        "color": {"r": 245, "g": 245, "b": 250},
    }


def produce_game(game_dir: Path, image_map: Dict[str, str]) -> Path:
    game_json = game_dir / "game.json"
    project = load_or_create_project(game_json)

    # Ensure top-level required keys exist even if we loaded an older/invalid file
    project.setdefault("firstLayout", "Main")
    if not isinstance(project.get("gdVersion"), dict):
        project["gdVersion"] = {"build": 0, "major": 5, "minor": 0, "revision": 0}
    project.setdefault("resources", {"resources": [], "resourceFolders": []})
    project.setdefault("layouts", [])
    project.setdefault("externalEvents", [])
    project.setdefault("externalLayouts", [])
    project.setdefault("externalSourceFiles", [])
    project.setdefault("objects", [])
    project.setdefault("objectsGroups", [])
    project.setdefault("variables", [])

    # Resources
    for logical, rel_file in image_map.items():
        ensure_resource(project, name=logical, kind="image", file_path=rel_file)

    layout = get_or_create_layout(project, "Main")
    project["firstLayout"] = "Main"

    # Choose resources
    player_res = "player" if "player" in image_map else next(iter(image_map.keys()))
    coin_res = "coin" if "coin" in image_map else player_res
    bg_res = "bg" if "bg" in image_map else None

    # Objects
    if bg_res:
        _ensure_layout_object(layout, make_sprite_object("Background", bg_res))
    _ensure_layout_object(layout, make_sprite_object("Player", player_res))
    _ensure_layout_object(layout, make_sprite_object("Coin", coin_res))
    _ensure_layout_object(layout, make_text_object("HUD", "Score: 0"))

    # Instances (note: field is "name" in GDevelop examples)
    if bg_res:
        _ensure_instance(
            layout,
            {
                "name": "Background",
                "x": 0,
                "y": 0,
                "angle": 0,
                "layer": "",
                "zOrder": 0,
                "locked": True,
                "customSize": False,
                "width": 0,
                "height": 0,
                "numberProperties": [],
                "stringProperties": [],
                "initialVariables": [],
            },
        )

    _ensure_instance(
        layout,
        {
            "name": "Player",
            "x": 200,
            "y": 240,
            "angle": 0,
            "layer": "",
            "zOrder": 1,
            "locked": False,
            "customSize": False,
            "width": 0,
            "height": 0,
            "numberProperties": [],
            "stringProperties": [],
            "initialVariables": [],
        },
    )
    _ensure_instance(
        layout,
        {
            "name": "Coin",
            "x": 520,
            "y": 280,
            "angle": 0,
            "layer": "",
            "zOrder": 2,
            "locked": False,
            "customSize": False,
            "width": 0,
            "height": 0,
            "numberProperties": [],
            "stringProperties": [],
            "initialVariables": [],
        },
    )
    _ensure_instance(
        layout,
        {
            "name": "HUD",
            "x": 20,
            "y": 20,
            "angle": 0,
            "layer": "",
            "zOrder": 99,
            "locked": False,
            "customSize": False,
            "width": 0,
            "height": 0,
            "numberProperties": [],
            "stringProperties": [],
            "initialVariables": [],
        },
    )

    # Start with no events to guarantee project opens.
    # We'll add events via a compatible schema after you confirm it opens.
    layout["events"] = []

    write_json(game_json, project)
    return game_json
