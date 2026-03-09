from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import read_json, write_json


DEFAULT_PET = {
    "name": "Pet",
    "species": "Cat",
    "temperament": "playful",
    "stats": {
        "hunger": 60,
        "energy": 60,
        "mood": 60,
        "cleanliness": 60,
    },
    "behavior": {
        "idleSecondsMin": 2,
        "idleSecondsMax": 5,
        "moveChance": 0.35,
        "sleepThreshold": 20,
        "eatThreshold": 25,
    },
}


def write_pet_runtime(pack_dir: Path, game_dir: Path) -> Dict[str, Any]:
    pet = _load_pet(pack_dir)

    runtime = {
        "name": str(pet.get("name", "Pet")),
        "species": str(pet.get("species", "Cat")),
        "temperament": str(pet.get("temperament", "playful")),
        "stats": {
            "hunger": _clamp(_num(pet.get("stats", {}).get("hunger"), 60)),
            "energy": _clamp(_num(pet.get("stats", {}).get("energy"), 60)),
            "mood": _clamp(_num(pet.get("stats", {}).get("mood"), 60)),
            "cleanliness": _clamp(_num(pet.get("stats", {}).get("cleanliness"), 60)),
        },
        "behavior": {
            "sleepThreshold": _num(pet.get("behavior", {}).get("sleepThreshold"), 20),
            "eatThreshold": _num(pet.get("behavior", {}).get("eatThreshold"), 25),
            "moveChance": float(pet.get("behavior", {}).get("moveChance", 0.35)),
        },
        "actions": {
            "feed": {"hungerAdd": 18, "moodAdd": 4, "coinsCost": 8},
            "play": {"moodAdd": 12, "energyAdd": -8, "hungerAdd": -5},
            "sleep": {"energyAdd": 20, "moodAdd": 3, "cleanlinessAdd": -4},
            "clean": {"cleanlinessAdd": 20, "moodAdd": 2, "coinsCost": 5},
        },
        "decay": {
            "hungerPerTick": 1,
            "energyPerTick": 1,
            "moodPerTick": 1,
            "cleanlinessPerTick": 1,
        },
    }

    write_json(game_dir / "pet_runtime.json", runtime)
    return runtime


def _load_pet(pack_dir: Path) -> Dict[str, Any]:
    pet_json = pack_dir / "pet.json"
    pack_json = pack_dir / "pack.json"

    if pet_json.exists():
        data = read_json(pet_json)
        if isinstance(data, dict):
            return data

    if pack_json.exists():
        data = read_json(pack_json)
        if isinstance(data, dict):
            pet = data.get("pet")
            if isinstance(pet, dict):
                return pet

    return DEFAULT_PET.copy()


def _num(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))
