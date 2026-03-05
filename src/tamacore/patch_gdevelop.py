from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Tuple

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

    # Some GDevelop exports use "objectName", some also include "name"
    want = inst.get("objectName") or inst.get("name")
    if want and any(
        isinstance(i, dict)
        and ((i.get("objectName") == want) or (i.get("name") == want))
        for i in instances
    ):
        return

    instances.append(inst)


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copy images from assets_dir into game_dir/assets/generated.
    Returns a mapping: resourceName -> relativePathInGame
    """
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    image_map: Dict[str, str] = {}

    if not assets_dir.exists():
        return image_map

    for p in sorted(assets_dir.rglob("*")):
        if not is_image_file(p):
            continue

        # resource name: filename without extension
        name = p.stem
        dst = out_dir / p.name

        # overwrite to keep deterministic builds
        shutil.copy2(p, dst)

        # path stored in game.json should be relative to game root
        image_map[name] = str(Path("assets") / "generated" / p.name).replace("\\", "/")

    return image_map


def _patch_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    """
    Update/Create resources entries for images we copied.
    """
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
    Requires the SpriteMultitouchJoystick extension to be present in template.
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
    You can later replace with sprites if desired.
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
            "x": 860,
            "y": 20,
            "angle": 0,
            "layer": "UI",
            "zOrder": 1000,
        },
    )

    # Panel (hidden by default; we store state in variable, panel text used as placeholder)
    _ensure_object(
        scene,
        {
            "name": "ShopPanel",
            "type": "Text",
            "string": "SHOP\\n- Item 1\\n- Item 2\\n\\n(TODO: shop UI)",
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
            "x": 520,
            "y": 120,
            "angle": 0,
            "layer": "UI",
            "zOrder": 1100,
        },
    )


def patch_project(game_json: Path, image_map: Dict[str, str], scene_name: str = "Main") -> None:
    """
    Patch a GDevelop game.json in-place:
    - update resources for generated assets
    - ensure UI layer exists
    - inject TouchJoystick + basic shop UI objects
    """
    project = read_json(game_json)
    if not isinstance(project, dict):
        raise ValueError(f"Invalid game.json (expected object): {game_json}")

    # resources
    if image_map:
        _patch_resources(project, image_map)

    # scene changes
    scene = _find_scene(project, scene_name=scene_name)
    if scene is not None:
        _ensure_layer(scene, "UI")
        _inject_touch_joystick(scene)
        _inject_shop_ui(scene)

    write_json(game_json, project)
