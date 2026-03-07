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

    if not frames:
        return

    player["type"] = "Sprite"
    player["animations"] = [
        {
            "name": "Idle",
            "useMultipleDirections": False,
            "directions": [
                {
                    "timeBetweenFrames": 0.12,
                    "sprites": [_sprite_frame(path) for path in frames["idle"]],
                }
            ],
        }
    ]

    if frames["walk"]:
        player["animations"].append(
            {
                "name": "Walk",
                "useMultipleDirections": False,
                "directions": [
                    {
                        "timeBetweenFrames": 0.08,
                        "sprites": [_sprite_frame(path) for path in frames["walk"]],
                    }
                ],
            }
        )


def _find_object(scene: Json, name: str) -> Json | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None

    for obj in objects:
        if isinstance(obj, dict) and obj.get("name") == name:
            return obj

    return None


def _find_candidate_frames(generated_dir: Path) -> Dict[str, List[str]]:
    out = {"idle": [], "walk": []}

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
        if "walk" in name or "run" in name:
            out["walk"].append(rel)
        else:
            out["idle"].append(rel)

    if not out["idle"] and out["walk"]:
        out["idle"] = out["walk"][:1]

    if not out["walk"] and len(out["idle"]) > 1:
        out["walk"] = out["idle"][:]

    out["idle"] = out["idle"][:8]
    out["walk"] = out["walk"][:8]

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
