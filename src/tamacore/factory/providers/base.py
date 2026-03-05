from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass(frozen=True)
class Design:
    title: str
    tagline: str
    genre: str
    loop: str
    difficulty_curve: str
    shop_items: List[Dict[str, Any]]
    enemies: List[Dict[str, Any]]
    ui: Dict[str, str]
    tuning: Dict[str, float]
    modules: List[str]
    meta: Dict[str, Any]


class GameDesignProvider(Protocol):
    name: str

    def generate(self, spec: Dict[str, Any]) -> Design:
        ...
