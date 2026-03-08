from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..utils import ensure_dir, read_json, write_json, write_text


PET_BASES = [
    {"species": "Cat", "body": "#f59e0b", "accent": "#fbbf24"},
    {"species": "Dog", "body": "#a16207", "accent": "#facc15"},
    {"species": "Fox", "body": "#ea580c", "accent": "#fdba74"},
    {"species": "Bunny", "body": "#c084fc", "accent": "#e9d5ff"},
    {"species": "Slime", "body": "#22c55e", "accent": "#86efac"},
    {"species": "Bear", "body": "#92400e", "accent": "#fcd34d"},
]

PET_NAMES = [
    "Milo",
    "Nori",
    "Pico",
    "Lumi",
    "Rubi",
    "Koda",
    "Zuzu",
    "Nova",
    "Bibi",
    "Tofu",
]

TEMPERAMENTS = [
    "playful",
    "sleepy",
    "curious",
    "loyal",
    "chaotic",
    "gentle",
]

SOUND_KEYS = [
    "idle",
    "happy",
    "sad",
    "eat",
    "sleep",
]


def generate_ai_pet(pack_dir: Path) -> Dict[str, Any]:
    ensure_dir(pack_dir)

    pet_dir = pack_dir / "assets" / "pet"
    sound_dir = pack_dir / "assets" / "sounds"
    ensure_dir(pet_dir)
    ensure_dir(sound_dir)

    base = random.choice(PET_BASES)
    pet_name = f"{random.choice(PET_NAMES)}{random.randint(1, 99)}"

    pet_data: Dict[str, Any] = {
        "name": pet_name,
        "species": base["species"],
        "temperament": random.choice(TEMPERAMENTS),
        "stats": {
            "hunger": random.randint(45, 75),
            "energy": random.randint(45, 75),
            "mood": random.randint(45, 75),
            "cleanliness": random.randint(45, 75),
        },
        "behavior": {
            "idleSecondsMin": random.randint(2, 4),
            "idleSecondsMax": random.randint(5, 8),
            "moveChance": round(random.uniform(0.2, 0.8), 2),
            "sleepThreshold": random.randint(15, 35),
            "eatThreshold": random.randint(20, 40),
        },
        "sounds": {key: f"assets/sounds/{key}.txt" for key in SOUND_KEYS},
        "frames": {
            "idle": [
                "assets/pet/pet_idle_01.svg",
                "assets/pet/pet_idle_02.svg",
            ],
            "walk": [
                "assets/pet/pet_walk_01.svg",
                "assets/pet/pet_walk_02.svg",
            ],
        },
    }

    _write_pet_svg(
        pet_dir / "pet_idle_01.svg",
        body=base["body"],
        accent=base["accent"],
        eye_y=47,
        mouth_curve="Q64 76 79 66",
        body_w=40,
        body_h=22,
        body_x=44,
        body_y=84,
    )
    _write_pet_svg(
        pet_dir / "pet_idle_02.svg",
        body=base["body"],
        accent=base["accent"],
        eye_y=49,
        mouth_curve="Q64 73 78 67",
        body_w=44,
        body_h=24,
        body_x=42,
        body_y=83,
    )
    _write_pet_svg(
        pet_dir / "pet_walk_01.svg",
        body=base["body"],
        accent=base["accent"],
        eye_y=48,
        mouth_curve="Q64 78 80 66",
        body_w=42,
        body_h=22,
        body_x=40,
        body_y=84,
    )
    _write_pet_svg(
        pet_dir / "pet_walk_02.svg",
        body=base["body"],
        accent=base["accent"],
        eye_y=48,
        mouth_curve="Q64 74 78 67",
        body_w=42,
        body_h=22,
        body_x=46,
        body_y=84,
    )

    for key in SOUND_KEYS:
        write_text(sound_dir / f"{key}.txt", f"{pet_name} {key} sound placeholder\n")

    write_json(pack_dir / "pet.json", pet_data)
    _merge_pet_into_pack(pack_dir, pet_data)

    return pet_data


def _merge_pet_into_pack(pack_dir: Path, pet_data: Dict[str, Any]) -> None:
    pack_path = pack_dir / "pack.json"
    pack: Dict[str, Any]

    if pack_path.exists():
        data = read_json(pack_path)
        pack = data if isinstance(data, dict) else {}
    else:
        pack = {
            "name": pack_dir.name,
            "version": 1,
            "scene": "Main",
            "display": {
                "mode": "portrait",
                "virtualWidth": 720,
                "virtualHeight": 1280,
            },
            "worldBounds": {
                "xMin": 0,
                "yMin": 0,
                "xMax": 720,
                "yMax": 1280,
            },
            "levels": {
                "count": 3,
                "seed": 1337,
            },
            "coinSpawn": {
                "objectName": "Coin",
                "count": 5,
                "enabled": True,
            },
            "enemySpawn": {
                "objectName": "Enemy",
                "count": 2,
                "enabled": True,
            },
            "shop": {
                "currencyVariable": "Coins",
                "upgrades": [],
            },
        }

    pack["pet"] = pet_data

    foods = pack.get("foods")
    if not isinstance(foods, list):
        foods = []
        pack["foods"] = foods

    if not foods:
        foods.extend(
            [
                {"id": "pet_food_apple", "name": "Apple", "hunger": 10, "price": 8},
                {"id": "pet_food_fish", "name": "Fish", "hunger": 16, "price": 14},
            ]
        )

    cosmetics = pack.get("cosmetics")
    if not isinstance(cosmetics, list):
        cosmetics = []
        pack["cosmetics"] = cosmetics

    if not cosmetics:
        cosmetics.extend(
            [
                {"id": "pet_hat_star", "name": "Star Hat", "price": 20},
                {"id": "pet_bow_mini", "name": "Mini Bow", "price": 15},
            ]
        )

    write_json(pack_path, pack)


def _write_pet_svg(
    path: Path,
    body: str,
    accent: str,
    eye_y: int,
    mouth_curve: str,
    body_w: int,
    body_h: int,
    body_x: int,
    body_y: int,
) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="108" rx="28" ry="10" fill="#000000" opacity="0.18"/>
  <circle cx="64" cy="54" r="34" fill="{accent}"/>
  <circle cx="52" cy="{eye_y}" r="5" fill="#0f172a"/>
  <circle cx="76" cy="{eye_y}" r="5" fill="#0f172a"/>
  <path d="M49 66 {mouth_curve}" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
  <rect x="{body_x}" y="{body_y}" width="{body_w}" height="{body_h}" rx="11" fill="{body}"/>
</svg>
"""
    write_text(path, svg)
