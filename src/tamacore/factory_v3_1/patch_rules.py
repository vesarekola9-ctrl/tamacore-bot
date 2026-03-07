from __future__ import annotations

from typing import Any, Dict, List

Json = Dict[str, Any]


def apply_v3_1_rules(project: Dict[str, Any], scene: Dict[str, Any], cfg: Any) -> None:
    _ensure_project_var(project, "Coins", 250)
    _ensure_project_var(project, "Speed", 200)
    _ensure_project_var(project, "PlayerMaxSpeed", 200)
    _ensure_project_var(project, "ShopOpen", 0)

    _ensure_ui_layer(scene)
    _ensure_scene_property(scene, "standardSortMethod", False)

    _ensure_player_object(scene)
    _ensure_coin_enemy_objects(scene, cfg)
    _ensure_camera_marker(scene, cfg)
    _ensure_hud_objects(scene, cfg)
    _ensure_joystick_instance(scene, cfg)
    _ensure_shop_shell(scene)


def _ensure_project_var(project: Json, name: str, value: float) -> None:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    for item in vars_:
        if isinstance(item, dict) and item.get("name") == name:
            item.setdefault("type", "number")
            item.setdefault("children", [])
            if "value" not in item:
                item["value"] = value
            return

    vars_.append(
        {
            "name": name,
            "type": "number",
            "value": value,
            "children": [],
        }
    )


def _ensure_scene_property(scene: Json, key: str, value: Any) -> None:
    if key not in scene:
        scene[key] = value


def _ensure_ui_layer(scene: Json) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers

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


def _ensure_layout_object(scene: Json, obj_def: Json) -> None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        objects = []
        scene["objects"] = objects

    name = obj_def.get("name")
    if not name:
        return

    for existing in objects:
        if isinstance(existing, dict) and existing.get("name") == name:
            return

    objects.append(obj_def)


def _find_layout_object(scene: Json, name: str) -> Json | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None

    for existing in objects:
        if isinstance(existing, dict) and existing.get("name") == name:
            return existing
    return None


def _ensure_instance(scene: Json, object_name: str, x: float, y: float, layer: str, z: int) -> None:
    instances = scene.get("instances")
    if not isinstance(instances, list):
        instances = []
        scene["instances"] = instances

    for inst in instances:
        if not isinstance(inst, dict):
            continue
        if inst.get("objectName") == object_name or inst.get("name") == object_name:
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


def _obj_text(name: str, text: str, size: int, align: str = "left") -> Json:
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
            "alignment": align,
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


def _ensure_behavior(obj: Json, behavior_type: str, behavior_name: str) -> None:
    behaviors = obj.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        obj["behaviors"] = behaviors

    for behavior in behaviors:
        if not isinstance(behavior, dict):
            continue
        if behavior.get("name") == behavior_name or behavior.get("type") == behavior_type:
            behavior.setdefault("name", behavior_name)
            behavior.setdefault("type", behavior_type)
            return

    behaviors.append(
        {
            "name": behavior_name,
            "type": behavior_type,
        }
    )


def _ensure_player_object(scene: Json) -> None:
    player = _find_layout_object(scene, "Player")
    if not isinstance(player, dict):
        _ensure_layout_object(
            scene,
            {
                "name": "Player",
                "type": "Sprite",
                "assetStoreId": "",
                "tags": "",
                "variables": [],
                "behaviors": [],
                "animations": [
                    {
                        "name": "Idle",
                        "useMultipleDirections": False,
                        "directions": [
                            {
                                "timeBetweenFrames": 0.12,
                                "sprites": [],
                            }
                        ],
                    }
                ],
                "effects": [],
            },
        )
        player = _find_layout_object(scene, "Player")

    if isinstance(player, dict):
        player["type"] = "Sprite"
        _ensure_behavior(player, "TopDownMovementBehavior::TopDownMovementBehavior", "TopDownMovement")
        _ensure_behavior(player, "PathfindingBehavior::PathfindingBehavior", "Pathfinding")


def _ensure_coin_enemy_objects(scene: Json, cfg: Any) -> None:
    for object_name in {
        getattr(cfg.coinSpawn, "objectName", "Coin"),
        getattr(cfg.enemySpawn, "objectName", "Enemy"),
    }:
        obj = _find_layout_object(scene, object_name)
        if not isinstance(obj, dict):
            _ensure_layout_object(
                scene,
                {
                    "name": object_name,
                    "type": "Sprite",
                    "assetStoreId": "",
                    "tags": "",
                    "variables": [],
                    "behaviors": [],
                    "animations": [
                        {
                            "name": "Idle",
                            "useMultipleDirections": False,
                            "directions": [
                                {
                                    "timeBetweenFrames": 0.12,
                                    "sprites": [],
                                }
                            ],
                        }
                    ],
                    "effects": [],
                },
            )


def _ensure_camera_marker(scene: Json, cfg: Any) -> None:
    marker_name = "CameraTarget"
    follow_object = getattr(cfg.camera, "followObject", "Player")

    _ensure_layout_object(scene, _obj_text(marker_name, f"FOLLOW: {follow_object}", 18))
    _ensure_instance(scene, marker_name, x=-9999, y=-9999, layer="UI", z=10)


def _ensure_hud_objects(scene: Json, cfg: Any) -> None:
    hud_name = getattr(cfg.ui.hud, "objectName", "HUD")
    _ensure_layout_object(scene, _obj_text(hud_name, "HUD", 28))
    _ensure_instance(
        scene,
        hud_name,
        x=max(0, int(getattr(cfg.ui.hud, "marginX", 24))),
        y=max(0, int(getattr(cfg.ui.hud, "marginY", 24))),
        layer="UI",
        z=2400,
    )


def _ensure_joystick_instance(scene: Json, cfg: Any) -> None:
    object_name = getattr(cfg.ui.joystick, "objectName", "TouchJoystick")
    margin_x = max(0, int(getattr(cfg.ui.joystick, "marginX", 36)))
    margin_y = max(0, int(getattr(cfg.ui.joystick, "marginY", 36)))

    _ensure_instance(
        scene,
        object_name,
        x=margin_x,
        y=900 + margin_y,
        layer="UI",
        z=2300,
    )


def _ensure_shop_shell(scene: Json) -> None:
    _ensure_layout_object(scene, _obj_text("ShopButton", "SHOP", 36, align="center"))
    _ensure_layout_object(scene, _obj_panel("ShopPanel", 520, 420))

    _ensure_instance(scene, "ShopButton", x=820, y=24, layer="UI", z=2000)
    _ensure_instance(scene, "ShopPanel", x=450, y=110, layer="UI", z=2100)
