from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List

from ..utils import ensure_dir, is_image_file, write_json

Json = Dict[str, Any]


def build_catalog(pack_dir: Path, game_dir: Path) -> Json:
    src_assets = pack_dir / "assets"
    dst_assets = game_dir / "assets" / "generated"
    ensure_dir(dst_assets)

    copied_assets: Dict[str, str] = {}

    if src_assets.exists():
        for file_path in sorted(src_assets.rglob("*")):
            if not file_path.is_file():
                continue
            if not is_image_file(file_path):
                continue

            rel = file_path.relative_to(src_assets)
            dst = dst_assets / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dst)

            rel_game_path = ("assets/generated/" + rel.as_posix()).replace("\\", "/")
            copied_assets[rel.as_posix()] = rel_game_path

    catalog: Json = {
        "assets": _build_resource_map(copied_assets),
        "objects": _build_objects(copied_assets),
        "instances": _build_instances(copied_assets),
    }

    write_json(game_dir / "catalog.json", catalog)
    return catalog


def _build_resource_map(copied_assets: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rel, game_path in copied_assets.items():
        key = rel.replace("/", "_").rsplit(".", 1)[0]
        out[key] = game_path
    return out


def _build_objects(copied_assets: Dict[str, str]) -> List[Json]:
    groups = _group_assets(copied_assets)
    objects: List[Json] = []

    background_path = _first(groups.get("background", []))
    if background_path:
        objects.append(_background_object("Background", background_path))

    player_frames = groups.get("player", [])
    if player_frames:
        objects.append(_sprite_object("Player", _frames(player_frames)))

    coin_frames = groups.get("coin", [])
    if coin_frames:
        objects.append(_sprite_object("Coin", _frames(coin_frames)))

    enemy_frames = groups.get("enemy", [])
    if enemy_frames:
        objects.append(_sprite_object("Enemy", _frames(enemy_frames)))

    joystick_frames = groups.get("ui_touch_joystick", [])
    if joystick_frames:
        objects.append(_sprite_object("TouchJoystick", _frames(joystick_frames)))

    hud_label_frames = groups.get("ui_hud_label", [])
    if hud_label_frames:
        objects.append(_sprite_object("HUDSprite", _frames(hud_label_frames)))

    _ensure_core_placeholders(objects)
    return objects


def _build_instances(copied_assets: Dict[str, str]) -> List[Json]:
    groups = _group_assets(copied_assets)
    instances: List[Json] = []

    if groups.get("background"):
        instances.append(_instance("Background", 0, 0, "", 0))

    instances.append(_instance("Player", 360, 640, "", 10))

    if groups.get("coin"):
        instances.append(_instance("Coin", 240, 420, "", 20))

    if groups.get("enemy"):
        instances.append(_instance("Enemy", 520, 360, "", 20))

    if groups.get("ui_touch_joystick"):
        instances.append(_instance("TouchJoystick", 36, 936, "UI", 2300))

    if groups.get("ui_hud_label"):
        instances.append(_instance("HUDSprite", 20, 18, "UI", 2390))

    return instances


def _group_assets(copied_assets: Dict[str, str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {
        "background": [],
        "player": [],
        "coin": [],
        "enemy": [],
        "ui_touch_joystick": [],
        "ui_hud_label": [],
    }

    for rel, game_path in copied_assets.items():
        rel_l = rel.lower()

        if rel_l.startswith("background/"):
            groups["background"].append(game_path)
        elif rel_l.startswith("player/"):
            groups["player"].append(game_path)
        elif rel_l.startswith("coin/"):
            groups["coin"].append(game_path)
        elif rel_l.startswith("enemy/"):
            groups["enemy"].append(game_path)
        elif rel_l.startswith("ui/"):
            stem = Path(rel_l).stem
            if "touch_joystick" in stem or "joystick" in stem:
                groups["ui_touch_joystick"].append(game_path)
            elif "hud_label" in stem or "hud" in stem:
                groups["ui_hud_label"].append(game_path)

    for key in groups:
        groups[key] = sorted(groups[key])

    return groups


def _ensure_core_placeholders(objects: List[Json]) -> None:
    existing = {obj.get("name") for obj in objects if isinstance(obj, dict)}

    if "Player" not in existing:
        objects.append(_sprite_object("Player", []))

    if "Coin" not in existing:
        objects.append(_sprite_object("Coin", []))

    if "Enemy" not in existing:
        objects.append(_sprite_object("Enemy", []))

    if "TouchJoystick" not in existing:
        objects.append(_sprite_object("TouchJoystick", []))


def _background_object(name: str, image_path: str) -> Json:
    return {
        "name": name,
        "type": "TiledSpriteObject::TiledSprite",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {
            "texture": image_path,
            "width": 720,
            "height": 1280,
        },
        "effects": [],
    }


def _sprite_object(name: str, sprites: List[Json]) -> Json:
    return {
        "name": name,
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
                        "timeBetweenFrames": 0.08,
                        "sprites": sprites,
                    }
                ],
            }
        ],
        "effects": [],
    }


def _frames(paths: List[str]) -> List[Json]:
    return [_sprite_frame(path) for path in paths[:8]]


def _sprite_frame(image_path: str) -> Json:
    return {
        "image": image_path,
        "originPoint": {"name": "Origin", "x": 0, "y": 0},
        "centerPoint": {"name": "Center", "x": 64, "y": 64},
        "points": [],
        "hasCustomCollisionMask": False,
        "customCollisionMask": [],
    }


def _first(values: List[str]) -> str | None:
    return values[0] if values else None


def _instance(object_name: str, x: float, y: float, layer: str, z: int) -> Json:
    return {
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
