from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

Json = Dict[str, Any]


def apply_character_animations(project: Dict[str, Any], scene: Dict[str, Any], game_dir: Path) -> None:
    player = _find_object(scene, "Player")
    if not isinstance(player, dict):
        return

    generated = game_dir / "assets" / "generated"
    frames = _find_candidate_frames(generated)

    if not frames["idle"]:
        return

    # GDevelop expects image resources as well as sprite frame paths.
    resource_table = project.setdefault("resources", {})
    resources = resource_table.setdefault("resources", [])
    registered = {item.get("name") for item in resources if isinstance(item, dict)}
    for image_path in dict.fromkeys([frame for group in frames.values() for frame in group]):
        if image_path not in registered:
            resources.append({
                "alwaysLoaded": False,
                "file": image_path,
                "kind": "image",
                "metadata": "",
                "name": image_path,
                "smoothed": True,
                "userAdded": True,
            })
            registered.add(image_path)

    # Keep a stable animation order for GDevelop event-sheet references.
    player["type"] = "Sprite"
    player["animations"] = []
    for state, paths in frames.items():
        if not paths:
            continue
        player["animations"].append({
            "name": state.capitalize(),
            "useMultipleDirections": False,
            "directions": [{
                "timeBetweenFrames": 0.12 if state != "walk" else 0.08,
                "looping": True,
                "sprites": [_sprite_frame(path) for path in paths],
            }],
        })


def apply_pet_animation_events(scene: Json) -> None:
    """Connect the Pet_State variable to Player's named GDevelop animations.

    This creates GDevelop event-sheet actions, not just sprite metadata.
    The existing pet runtime owns changes to Pet_State; this bridge only
    chooses the visual state. Safe to call repeatedly.
    """
    player = _find_object(scene, "Player")
    if not isinstance(player, dict):
        return
    available = {
        animation.get("name") for animation in player.get("animations", [])
        if isinstance(animation, dict)
    }
    events = scene.setdefault("events", [])
    indexes = {animation.get("name"): index for index, animation in enumerate(player.get("animations", [])) if isinstance(animation, dict)}
    for name in ("Idle", "Walk", "Sleep", "Eat", "Play"):
        if name not in available:
            continue
        marker = f"TamaCorePetAnimation_{name}"
        if any(isinstance(event, dict) and event.get("name") == marker for event in events):
            continue
        events.append({
            "type": "BuiltinCommonInstructions::Standard",
            "name": marker,
            "conditions": [{
                "type": {"value": "VarGlobalStringCompare"},
                "parameters": ["Pet_State", "=", name],
            }],
            "actions": [{
                "type": {"value": "SetAnimation"},
                "parameters": ["Player", str(indexes[name])],
            }],
        })


def _find_object(scene: Json, name: str) -> Json | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None

    for obj in objects:
        if isinstance(obj, dict) and obj.get("name") == name:
            return obj

    return None


def _find_candidate_frames(generated_dir: Path) -> Dict[str, List[str]]:
    out = {"idle": [], "walk": [], "sleep": [], "eat": [], "play": []}

    if not generated_dir.exists():
        return out

    preferred_dirs = [
        generated_dir / "player",
        generated_dir / "pet",
        generated_dir / "character",
    ]

    candidates: List[Path] = []
    for folder in preferred_dirs:
        if folder.exists():
            for file_path in sorted(folder.rglob("*")):
                if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
                    candidates.append(file_path)

    if not candidates:
        for file_path in sorted(generated_dir.rglob("*")):
            if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
                if any(key in file_path.stem.lower() for key in ("player", "pet", "character")):
                    candidates.append(file_path)

    for path in candidates:
        rel = path.relative_to(generated_dir.parent.parent).as_posix()
        name = path.stem.lower()
        # The common prefix "player_" contains "play": only classify the\n        # animation suffix, not the character identifier.\n        animation_name = name.removeprefix("player_").removeprefix("pet_").removeprefix("character_")\n        state = next((key for key in ("walk", "sleep", "eat", "play") if animation_name.startswith(key)), "idle")
        out[state].append(rel)

    if not out["idle"] and out["walk"]:
        out["idle"] = out["walk"][:1]


    for state in out:
        out[state] = out[state][:8]

    return out


def _sprite_frame(image_path: str) -> Json:
    return {
        "image": image_path,
        "originPoint": {"name": "Origin", "x": 0, "y": 0},
        "centerPoint": {"name": "Center", "x": 64, "y": 64},
        "points": [],
        "hasCustomCollisionMask": False,
        "customCollisionMask": [],
    }
