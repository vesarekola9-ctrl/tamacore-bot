from __future__ import annotations

from typing import Any, Dict


def patch_project(project: Dict[str, Any], scene_name: str = "Main") -> Dict[str, Any]:
    layouts = project.get("layouts", [])
    if not isinstance(layouts, list) or not layouts:
        return project

    # Find scene
    scene = None
    for layout in layouts:
        if isinstance(layout, dict) and layout.get("name") == scene_name:
            scene = layout
            break
    if scene is None and isinstance(layouts[0], dict):
        scene = layouts[0]
    if scene is None:
        return project

    # Ensure lists
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers

    # Ensure UI layer exists
    if not any(isinstance(l, dict) and l.get("name") == "UI" for l in layers):
        layers.append({"name": "UI", "visibility": True, "effects": []})

    # Add joystick object
    if not any(isinstance(o, dict) and o.get("name") == "TouchJoystick" for o in objects):
        objects.append(
            {
                "name": "TouchJoystick",
                "type": "SpriteMultitouchJoystick::SpriteMultitouchJoystick",
                "updateIfNotVisible": True,
                "behaviors": [],
                "effects": [],
            }
        )

    # Add joystick instance
    if not any(isinstance(i, dict) and (i.get("objectName") == "TouchJoystick" or i.get("name") == "TouchJoystick") for i in instances):
        instances.append(
            {
                "objectName": "TouchJoystick",
                "name": "TouchJoystick",
                "x": 140,
                "y": 500,
                "angle": 0,
                "layer": "UI",
                "zOrder": 999,
            }
        )

    return project