from __future__ import annotations

from typing import Any, Dict, List


def _get_scene(project: Dict[str, Any], scene_name: str) -> Dict[str, Any] | None:
    layouts = project.get("layouts", [])
    if not isinstance(layouts, list) or not layouts:
        return None
    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == scene_name:
            return layout
    if isinstance(layouts[0], dict):
        return layouts[0]
    return None


def _ensure_ui_layer(scene: Dict[str, Any]) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers
    if not any(isinstance(l, dict) and l.get("name") == "UI" for l in layers):
        layers.append({"name": "UI", "visibility": True, "effects": []})


def _get_or_create_group(scene: Dict[str, Any], group_name: str) -> Dict[str, Any]:
    groups = scene.get("objectsGroups")
    if not isinstance(groups, list):
        groups = []
        scene["objectsGroups"] = groups

    for g in groups:
        if isinstance(g, dict) and g.get("name") == group_name:
            g.setdefault("objects", [])
            return g

    new_g = {"name": group_name, "objects": []}
    groups.append(new_g)
    return new_g


def _has_object(group: Dict[str, Any], obj_name: str) -> bool:
    objs = group.get("objects", [])
    return any(isinstance(o, dict) and o.get("name") == obj_name for o in objs)


def _add_object(group: Dict[str, Any], obj: Dict[str, Any]) -> None:
    group.setdefault("objects", [])
    if not isinstance(group["objects"], list):
        group["objects"] = []
    group["objects"].append(obj)


def _ensure_instance(scene: Dict[str, Any], obj_name: str, x: int, y: int, layer: str, z: int) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    if any(isinstance(i, dict) and (i.get("objectName") == obj_name or i.get("name") == obj_name) for i in instances):
        return

    instances.append(
        {
            "objectName": obj_name,
            "name": obj_name,
            "x": x,
            "y": y,
            "angle": 0,
            "layer": layer,
            "zOrder": z,
        }
    )


def patch_project(project: Dict[str, Any], scene_name: str = "Main") -> Dict[str, Any]:
    scene = _get_scene(project, scene_name)
    if scene is None:
        return project

    _ensure_ui_layer(scene)

    # Put our injected objects into a dedicated group that GDevelop DOES use:
    group = _get_or_create_group(scene, "Injected")

    # Add TouchJoystick
    if not _has_object(group, "TouchJoystick"):
        _add_object(
            group,
            {
                "name": "TouchJoystick",
                "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
                "updateIfNotVisible": True,
                "behaviors": [],
                "effects": [],
            },
        )

    # Add instance on UI layer
    _ensure_instance(scene, "TouchJoystick", x=140, y=500, layer="UI", z=999)

    return project
