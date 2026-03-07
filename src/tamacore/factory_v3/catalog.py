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

    assets: Dict[str, str] = {}

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

            asset_name = _asset_name_from_rel(rel)
            rel_game_path = ("assets/generated/" + rel.as_posix()).replace("\\", "/")
            assets[asset_name] = rel_game_path

    objects = _build_object_defs(assets)
    instances = _build_default_instances(objects)

    catalog: Json = {
        "assets": assets,
        "objects": objects,
        "instances": instances,
    }

    write_json(game_dir / "catalog.json", catalog)
    return catalog


def _asset_name_from_rel(rel: Path) -> str:
    parts = list(rel.parts)
    stem = rel.stem
    if len(parts) >= 2:
        prefix = parts[0]
        return f"{prefix}_{stem}"
    return stem


def _guess_object_type(asset_name: str) -> str:
    name = asset_name.lower()
    if "background" in name or name.startswith("bg_"):
        return "TiledSpriteObject::TiledSprite"
    return "Sprite"


def _pretty_object_name(asset_name: str) -> str:
    raw = asset_name.replace("-", "_")
    return "".join(part.capitalize() for part in raw.split("_") if part)


def _build_object_defs(assets: Dict[str, str]) -> List[Json]:
    objects: List[Json] = []

    for asset_name, asset_path in assets.items():
        object_name = _pretty_object_name(asset_name)
        obj_type = _guess_object_type(asset_name)

        if obj_type == "TiledSpriteObject::TiledSprite":
            objects.append(
                {
                    "name": object_name,
                    "type": obj_type,
                    "assetStoreId": "",
                    "tags": "",
                    "variables": [],
                    "behaviors": [],
                    "content": {
                        "texture": asset_path,
                        "width": 720,
                        "height": 1280,
                    },
                    "effects": [],
                }
            )
        else:
            objects.append(
                {
                    "name": object_name,
                    "type": obj_type,
                    "assetStoreId": "",
                    "tags": "",
                    "variables": [],
                    "behaviors": [],
                    "animations": [
                        {
                            "name": "",
                            "useMultipleDirections": False,
                            "directions": [
                                {
                                    "timeBetweenFrames": 0.08,
                                    "sprites": [
                                        {
                                            "image": asset_path,
                                            "originPoint": {"name": "Origin", "x": 0, "y": 0},
                                            "centerPoint": {"name": "Center", "x": 64, "y": 64},
                                            "points": [],
                                            "hasCustomCollisionMask": False,
                                            "customCollisionMask": [],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                    "effects": [],
                }
            )

    _ensure_core_placeholders(objects)
    return objects


def _ensure_core_placeholders(objects: List[Json]) -> None:
    existing = {obj.get("name") for obj in objects if isinstance(obj, dict)}

    if "Player" not in existing:
        objects.append(
            {
                "name": "Player",
                "type": "Sprite",
                "assetStoreId": "",
                "tags": "",
                "variables": [],
                "behaviors": [],
                "animations": [
                    {
                        "name": "",
                        "useMultipleDirections": False,
                        "directions": [
                            {
                                "timeBetweenFrames": 0.08,
                                "sprites": [],
                            }
                        ],
                    }
                ],
                "effects": [],
            }
        )

    if "Coin" not in existing:
        objects.append(
            {
                "name": "Coin",
                "type": "Sprite",
                "assetStoreId": "",
                "tags": "",
                "variables": [],
                "behaviors": [],
                "animations": [
                    {
                        "name": "",
                        "useMultipleDirections": False,
                        "directions": [
                            {
                                "timeBetweenFrames": 0.08,
                                "sprites": [],
                            }
                        ],
                    }
                ],
                "effects": [],
            }
        )

    if "Enemy" not in existing:
        objects.append(
            {
                "name": "Enemy",
                "type": "Sprite",
                "assetStoreId": "",
                "tags": "",
                "variables": [],
                "behaviors": [],
                "animations": [
                    {
                        "name": "",
                        "useMultipleDirections": False,
                        "directions": [
                            {
                                "timeBetweenFrames": 0.08,
                                "sprites": [],
                            }
                        ],
                    }
                ],
                "effects": [],
            }
        )


def _build_default_instances(objects: List[Json]) -> List[Json]:
    names = {obj.get("name") for obj in objects if isinstance(obj, dict)}
    instances: List[Json] = []

    if "Background" in names:
        instances.append(_instance("Background", 0, 0, "", 0))
    if "Player" in names:
        instances.append(_instance("Player", 360, 640, "", 10))
    if "Coin" in names:
        instances.append(_instance("Coin", 240, 420, "", 20))
    if "Enemy" in names:
        instances.append(_instance("Enemy", 520, 360, "", 20))

    return instances


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
