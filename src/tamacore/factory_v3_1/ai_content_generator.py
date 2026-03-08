from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json, write_json


FOOD_NAMES = [
    ("Berry Snack", 8, 6),
    ("Fish Meal", 16, 14),
    ("Golden Cookie", 12, 18),
    ("Energy Soup", 10, 12),
    ("Moon Milk", 7, 10),
    ("Crunch Cubes", 9, 9),
]

COSMETIC_NAMES = [
    ("Star Hat", 20),
    ("Pixel Glasses", 18),
    ("Mini Cape", 24),
    ("Royal Bow", 16),
    ("Shadow Mask", 22),
    ("Cloud Halo", 28),
]


def generate_ai_content(
    pack_dir: Path,
    foods_count: int = 4,
    cosmetics_count: int = 4,
) -> Dict[str, Any]:
    pack_path = pack_dir / "pack.json"
    if not pack_path.exists():
        raise FileNotFoundError(f"Missing file: {pack_path}")

    data = read_json(pack_path)
    if not isinstance(data, dict):
        raise ValueError("pack.json must be an object")

    foods = _make_foods(max(1, foods_count))
    cosmetics = _make_cosmetics(max(1, cosmetics_count))

    data["foods"] = foods
    data["cosmetics"] = cosmetics

    write_json(pack_path, data)
    write_json(
        pack_dir / "content.ai.json",
        {
            "foods": foods,
            "cosmetics": cosmetics,
        },
    )

    return {
        "foods": foods,
        "cosmetics": cosmetics,
    }


def _make_foods(count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    used_ids: set[str] = set()

    for i in range(count):
        name, hunger_base, price_base = random.choice(FOOD_NAMES)
        hunger = hunger_base + random.randint(0, 6)
        energy = random.randint(0, 6)
        mood = random.randint(0, 5)
        price = price_base + random.randint(0, 12)

        uid = _unique_id(name, i + 1, used_ids)
        out.append(
            {
                "id": uid,
                "name": name,
                "hunger": hunger,
                "energy": energy,
                "mood": mood,
                "price": price,
            }
        )

    return out


def _make_cosmetics(count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    used_ids: set[str] = set()

    for i in range(count):
        name, price_base = random.choice(COSMETIC_NAMES)
        price = price_base + random.randint(0, 15)
        style_bonus = random.randint(1, 5)

        uid = _unique_id(name, i + 1, used_ids)
        out.append(
            {
                "id": uid,
                "name": name,
                "styleBonus": style_bonus,
                "price": price,
            }
        )

    return out


def _unique_id(name: str, index: int, used_ids: set[str]) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
    uid = f"{slug}_{index}"
    while uid in used_ids:
        uid = f"{slug}_{index}_{random.randint(1, 99)}"
    used_ids.add(uid)
    return uid
