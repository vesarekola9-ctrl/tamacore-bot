from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Tuple

from .utils import read_json, write_json

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copy images from assets_dir into game_dir/assets/generated.
    Return mapping: resource_name -> relative path (posix).
    resource_name is filename stem lowercased.
    """
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


def patch_project(game_json: Path, image_map: Dict[str, str]) -> None:
    """
    Patch a REAL GDevelop template game.json.
    We only modify resources + create/update a scene with objects & instances.

    This avoids schema guessing: we keep all template metadata.
    """
    project = read_json(game_json)

    # Locate resources list
    resources = _get_resources_list(project)

    # Upsert image resources
    for name, rel in image_map.items():
        _upsert_image_resource(resources, name=name, rel_path=rel)

    # Ensure a layout exists (use firstLayout or create Main)
    layout_name = project.get("firstLayout") or "Main"
    layout = _get_or_create_layout(project, layout_name)

    # Create objects in the layout (compatible with template style)
    # We keep schema minimal by cloning from template if possible.
    player_res = "player" if "player" in image_map else next(iter(image_map.keys()))
    coin_res = "coin" if "coin" in image_map else player_res
    bg_res = "bg" if "bg" in image_map else None

    _ensure_object_sprite(layout, "Player", player_res)
    _ensure_object_sprite(layout, "Coin", coin_res)
    if bg_res:
        _ensure_object_sprite(layout, "Background", bg_res)
    _ensure_object_text(layout, "HUD", "Score: 0")

    # Instances: template uses either "name" or "objectName" based on version.
    # We'll set both to be safe.
    _ensure_instance(layout, "Player", x=200, y=240, z=1)
    _ensure_instance(layout, "Coin", x=520, y=280, z=2)
    if bg_res:
        _ensure_instance(layout, "Background", x=0, y=0, z=0, locked=True)
    _ensure_instance(layout, "HUD", x=20, y=20, z=99)

    write_json(game_json, project)


def _get_resources_list(project: Dict[str, Any]) -> list[Dict[str, Any]]:
    if "resources" not in project or not isinstance(project["resources"], dict):
        project["resources"] = {}
    r = project["resources"]
    # Different templates may use "resources" or nested structures
    if "resources" not in r or not isinstance(r["resources"], list):
        r["resources"] = []
    # ensure resourceFolders exists if template uses it
    r.setdefault("resourceFolders", [])
    return r["resources"]


def _upsert_image_resource(resources: list[Dict[str, Any]], name: str, rel_path: str) -> None:
    for res in resources:
        if isinstance(res, dict) and res.get("name") == name:
            res["kind"] = "image"
            res["file"] = rel_path
            res.setdefault("metadata", "")
            res.setdefault("userAdded", True)
            res.setdefault("alwaysLoaded", False)
            res.setdefault("smoothed", True)
            return
    resources.append(
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


def _get_or_create_layout(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    project.setdefault("layouts", [])
    for l in project["layouts"]:
        if isinstance(l, dict) and l.get("name") == name:
            return l

    # If template has at least one layout, clone it structure to stay compatible.
    if project["layouts"]:
        base = project["layouts"][0]
        clone = _shallow_clone_layout(base, name)
        project["layouts"].append(clone)
        project["firstLayout"] = name
        return clone

    # Fallback minimal (rare)
    layout = {"name": name, "objects": [], "instances": [], "events": [], "layers": [{"name": "", "visibility": True}]}
    project["layouts"].append(layout)
    project["firstLayout"] = name
    return layout


def _shallow_clone_layout(base: Dict[str, Any], new_name: str) -> Dict[str, Any]:
    clone = dict(base)
    clone["name"] = new_name
    if "title" in clone:
        clone["title"] = new_name
    clone["objects"] = []
    clone["instances"] = []
    clone["events"] = []
    clone.setdefault("variables", [])
    return clone


def _layout_objects(layout: Dict[str, Any]) -> list[Dict[str, Any]]:
    layout.setdefault("objects", [])
    return layout["objects"]


def _layout_instances(layout: Dict[str, Any]) -> list[Dict[str, Any]]:
    layout.setdefault("instances", [])
    return layout["instances"]


def _ensure_object_sprite(layout: Dict[str, Any], obj_name: str, image_resource: str) -> None:
    objs = _layout_objects(layout)
    for o in objs:
        if isinstance(o, dict) and o.get("name") == obj_name:
            # try update image in a broad way
            if "animations" in o and isinstance(o["animations"], list) and o["animations"]:
                try:
                    o["animations"][0]["directions"][0]["sprites"][0]["image"] = image_resource
                except Exception:
                    pass
            return

    # Create a generic sprite object (common schema)
    objs.append(
        {
            "name": obj_name,
            "type": "Sprite",
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
                                    "image": image_resource,
                                    "originPoint": {"x": 0, "y": 0, "name": "origine"},
                                    "centerPoint": {"x": 0, "y": 0, "name": "centre", "automatic": True},
                                    "points": [],
                                    "hasCustomCollisionMask": False,
                                    "customCollisionMask": [],
                                }
                            ],
                        }
                    ],
                }
            ],
            "behaviors": [],
            "variables": [],
        }
    )


def _ensure_object_text(layout: Dict[str, Any], obj_name: str, text: str) -> None:
    objs = _layout_objects(layout)
    for o in objs:
        if isinstance(o, dict) and o.get("name") == obj_name:
            o["string"] = text
            return

    # Text object schema varies; template should have Text extension.
    objs.append(
        {
            "name": obj_name,
            "type": "TextObject::Text",
            "string": text,
            "characterSize": 28,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "variables": [],
        }
    )


def _ensure_instance(layout: Dict[str, Any], obj_name: str, x: int, y: int, z: int, locked: bool = False) -> None:
    insts = _layout_instances(layout)

    # find by either "name" or "objectName"
    for inst in insts:
        if not isinstance(inst, dict):
            continue
        if inst.get("name") == obj_name or inst.get("objectName") == obj_name:
            inst["x"] = x
            inst["y"] = y
            inst["zOrder"] = z
            inst.setdefault("layer", "")
            inst.setdefault("angle", 0)
            inst.setdefault("locked", locked)
            inst["name"] = obj_name
            inst["objectName"] = obj_name
            return

    # create instance with both fields to handle template differences
    insts.append(
        {
            "name": obj_name,
            "objectName": obj_name,
            "x": x,
            "y": y,
            "angle": 0,
            "layer": "",
            "zOrder": z,
            "locked": locked,
            "customSize": False,
            "width": 0,
            "height": 0,
            "numberProperties": [],
            "stringProperties": [],
            "initialVariables": [],
        }
    )
