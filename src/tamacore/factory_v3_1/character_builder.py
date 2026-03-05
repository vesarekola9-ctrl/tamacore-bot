from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


_PLAYER_RE = re.compile(r"^player_(?P<anim>[a-zA-Z0-9]+)_(?P<frame>\d+)$")


def apply_character_animations(project: Dict[str, Any], scene: Dict[str, Any], game_dir: Path) -> None:
    """
    Builds Player sprite animations from files in:
      <game_dir>/assets/generated/

    Naming:
      player_idle_0.png, player_idle_1.png, ...
      player_run_0.png,  player_run_1.png,  ...

    It replaces Player.animations if it finds any animations.
    Safe to run multiple times (idempotent-ish).
    """
    assets_dir = game_dir / "assets" / "generated"
    if not assets_dir.exists():
        return

    anim_map = _scan_player_anims(assets_dir)
    if not anim_map:
        return

    player_obj = _find_object(scene, "Player")
    if not isinstance(player_obj, dict):
        return
    if player_obj.get("type") != "Sprite":
        # If template uses different type, do nothing.
        return

    animations: List[Dict[str, Any]] = []
    for anim_name in _preferred_order(anim_map.keys()):
        frames = anim_map.get(anim_name)
        if not frames:
            continue
        animations.append(_make_sprite_animation(anim_name, frames))

    if not animations:
        return

    player_obj["animations"] = animations


def _scan_player_anims(assets_dir: Path) -> Dict[str, List[str]]:
    """
    Returns: { "Idle": ["player_idle_0", "player_idle_1", ...], "Run": [...] }
    Values are resource names (stems), not file paths.
    """
    found: Dict[str, List[Tuple[int, str]]] = {}

    for p in assets_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".png", ".webp", ".jpg", ".jpeg"):
            continue

        stem = p.stem  # resource name used in game.json
        m = _PLAYER_RE.match(stem)
        if not m:
            continue

        anim_raw = m.group("anim").lower()
        frame = int(m.group("frame"))

        # Normalize animation naming
        if anim_raw in ("idle",):
            anim = "Idle"
        elif anim_raw in ("run", "walk", "move"):
            anim = "Run"
        elif anim_raw in ("hit", "hurt"):
            anim = "Hit"
        else:
            anim = anim_raw.capitalize()

        found.setdefault(anim, []).append((frame, stem))

    out: Dict[str, List[str]] = {}
    for anim, items in found.items():
        items.sort(key=lambda t: t[0])
        out[anim] = [stem for _, stem in items]

    return out


def _preferred_order(keys) -> List[str]:
    preferred = ["Idle", "Run", "Hit"]
    rest = [k for k in sorted(keys) if k not in preferred]
    return [k for k in preferred if k in keys] + rest


def _make_sprite_animation(name: str, frames: List[str]) -> Dict[str, Any]:
    """
    GDevelop Sprite object animation structure (single direction).
    Each sprite frame references resource by "image": "<resourceName>".
    """
    sprites = []
    for res_name in frames:
        sprites.append(
            {
                "image": res_name,
                "originPoint": {"x": 0, "y": 0},
                "centerPoint": {"x": 0, "y": 0},
                "points": [],
                "hasCustomCollisionMask": False,
                "customCollisionMask": [],
            }
        )

    return {
        "name": name,
        "directionType": "LeftRight",
        "useMultipleDirections": False,
        "loop": True,
        "speed": 8,
        "directions": [{"sprites": sprites}],
    }


def _find_object(scene: Dict[str, Any], name: str) -> Dict[str, Any] | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None
    for o in objects:
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None
