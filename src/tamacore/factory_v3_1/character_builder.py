from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

Json = Dict[str, Any]


def apply_character_animations(project: Dict[str, Any], scene: Dict[str, Any], game_dir: Path) -> None:
    player = _find_object(scene, "Player")
    if not isinstance(player, dict):
        return

    generated = game_dir / "assets" / "generated"
    image_paths = _find_candidate_frames(generated)

    if not image_paths:
        return

    player["type"] = "Sprite"
    player["animations"] = [
        {
            "name": "Idle",
            "useMultipleDirections": False,
            "directions": [
                {
                    "timeBetweenFrames": 0.12,
                    "sprites": [_sprite_frame(path) for path in image_paths],
                }
            ],
        }
    ]


def _find_object(scene: Json, name: str) -> Json | None:
    objects = scene.get("objects")
    if not isinstance(objects, list):
        return None

    for obj in objects:
        if isinstance(obj, dict) and obj.get("name") == name:
            return obj

    return None


def _find_candidate_frames(generated_dir: Path) -> List[str]:
    if not generated_dir.exists():
        return []

    candidates: List[Path] = []

    preferred_dirs = [
        generated_dir / "player",
        generated_dir / "pet",
        generated_dir / "character",
    ]

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

    rels = []
    for path in candidates[:8]:
        rel = path.relative_to(generated_dir.parent.parent)
        rels.append(rel.as_posix())

    return rels


def _sprite_frame(image_path: str) -> Json:
    return {
        "image": image_path,
        "originPoint": {"name": "Origin", "x": 0, "y": 0},
        "centerPoint": {"name": "Center", "x": 64, "y": 64},
        "points": [],
        "hasCustomCollisionMask": False,
        "customCollisionMask": [],
    }
