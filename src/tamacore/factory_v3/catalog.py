from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import read_json, write_json, is_image_file


FRAME_RE = re.compile(r"^(?P<obj>[a-zA-Z0-9]+)_(?P<anim>[a-zA-Z0-9]+)_(?P<frame>\d+)$")


@dataclass
class PackMeta:
    name: str
    version: str
    scene: str


def load_pack_meta(pack_dir: Path) -> PackMeta:
    meta_path = pack_dir / "pack.json"
    if meta_path.exists():
        data = read_json(meta_path)
        if isinstance(data, dict):
            return PackMeta(
                name=str(data.get("name", pack_dir.name)),
                version=str(data.get("version", "0.0.0")),
                scene=str(data.get("scene", "Main")),
            )
    # default if missing
    return PackMeta(name=pack_dir.name, version="0.0.0", scene="Main")


def copy_pack_images_into_game(pack_dir: Path, game_dir: Path) -> Dict[str, str]:
    """
    Copies pack images into game_dir/assets/generated.
    Returns resource map: resource_name -> relative path ("assets/generated/file.png").
    Resource name is filename stem.
    """
    out_assets = game_dir / "assets" / "generated"
    out_assets.mkdir(parents=True, exist_ok=True)

    res: Dict[str, str] = {}
    for p in sorted(pack_dir.rglob("*")):
        if not is_image_file(p):
            continue
        dst = out_assets / p.name
        shutil.copy2(p, dst)
        res_name = dst.stem
        res[res_name] = str(Path("assets") / "generated" / dst.name).replace("\\", "/")
    return res


def build_catalog(pack_dir: Path, game_dir: Path) -> Dict[str, Any]:
    """
    Build a catalog dict used by patch_gdevelop.factory_apply_catalog.
    """
    meta = load_pack_meta(pack_dir)
    resources = copy_pack_images_into_game(pack_dir, game_dir)

    # group frames by (obj, anim)
    groups: Dict[Tuple[str, str], List[Tuple[int, str]]] = {}

    singles: Dict[str, str] = {}  # res_name -> res_name
    for res_name in resources.keys():
        m = FRAME_RE.match(res_name)
        if m:
            obj = m.group("obj")
            anim = m.group("anim")
            frame = int(m.group("frame"))
            groups.setdefault((obj, anim), []).append((frame, res_name))
        else:
            singles[res_name] = res_name

    objects: List[Dict[str, Any]] = []

    # Background: use bg if exists
    if "bg" in resources:
        objects.append(sprite_single("Background", "bg", instance={"x": 0, "y": 0, "layer": "", "zOrder": 0}))
    elif "background" in resources:
        objects.append(sprite_single("Background", "background", instance={"x": 0, "y": 0, "layer": "", "zOrder": 0}))

    # Standard game objects if their frames exist
    # Player
    player_anims = animations_for_object("player", groups)
    if player_anims:
        objects.append(sprite_multi("Player", player_anims, instance={"x": 200, "y": 240, "layer": "", "zOrder": 2}))
    elif "player" in resources:
        objects.append(sprite_single("Player", "player", instance={"x": 200, "y": 240, "layer": "", "zOrder": 2}))

    # Coin
    coin_anims = animations_for_object("coin", groups)
    if coin_anims:
        objects.append(sprite_multi("Coin", coin_anims, instance={"x": 520, "y": 280, "layer": "", "zOrder": 3}))
    elif "coin" in resources:
        objects.append(sprite_single("Coin", "coin", instance={"x": 520, "y": 280, "layer": "", "zOrder": 3}))

    # Enemy (optional)
    enemy_anims = animations_for_object("enemy", groups)
    if enemy_anims:
        objects.append(sprite_multi("Enemy", enemy_anims, instance={"x": 700, "y": 260, "layer": "", "zOrder": 4}))
    elif "enemy" in resources:
        objects.append(sprite_single("Enemy", "enemy", instance={"x": 700, "y": 260, "layer": "", "zOrder": 4}))

    # UI button (optional)
    btn_anims = animations_for_object("ui", groups) or animations_for_object("button", groups)
    if btn_anims:
        objects.append(sprite_multi("UIButton", btn_anims, instance={"x": 820, "y": 40, "layer": "UI", "zOrder": 997}))
    elif "ui_button" in resources:
        objects.append(sprite_single("UIButton", "ui_button", instance={"x": 820, "y": 40, "layer": "UI", "zOrder": 997}))

    catalog = {
        "pack": {"name": meta.name, "version": meta.version, "scene": meta.scene},
        "resources": resources,
        "objects": objects,
    }
    return catalog


def animations_for_object(obj_prefix: str, groups: Dict[Tuple[str, str], List[Tuple[int, str]]]) -> List[Dict[str, Any]]:
    anims: List[Dict[str, Any]] = []
    for (obj, anim), frames in groups.items():
        if obj.lower() != obj_prefix.lower():
            continue
        frames_sorted = sorted(frames, key=lambda t: t[0])
        sprite_entries = [make_sprite_frame(res_name) for _, res_name in frames_sorted]
        anims.append(make_animation(anim_name=anim, sprite_entries=sprite_entries))
    # stable order
    anims.sort(key=lambda a: str(a.get("name", "")))
    # ensure at least one animation called Idle
    if anims and not any(str(a.get("name", "")).lower() == "idle" for a in anims):
        anims[0]["name"] = "Idle"
    return anims


def sprite_single(obj_name: str, resource_name: str, instance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "name": obj_name,
        "type": "Sprite",
        "animations": [make_animation("Idle", [make_sprite_frame(resource_name)])],
        "behaviors": [],
        "instances": [instance] if isinstance(instance, dict) else [],
    }


def sprite_multi(obj_name: str, animations: List[Dict[str, Any]], instance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "name": obj_name,
        "type": "Sprite",
        "animations": animations,
        "behaviors": [],
        "instances": [instance] if isinstance(instance, dict) else [],
    }


def make_animation(anim_name: str, sprite_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "name": anim_name if anim_name else "Idle",
        "directionType": "LeftRight",
        "useMultipleDirections": False,
        "loop": True,
        "speed": 10,
        "directions": [{"sprites": sprite_entries}],
    }


def make_sprite_frame(resource_name: str) -> Dict[str, Any]:
    return {
        "image": resource_name,
        "originPoint": {"x": 0, "y": 0},
        "centerPoint": {"x": 0, "y": 0},
        "points": [],
        "hasCustomCollisionMask": False,
        "customCollisionMask": [],
    }
