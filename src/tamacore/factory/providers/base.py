from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass(frozen=True)
class Design:
    # High-level theme & pitch
    title: str
    tagline: str
    genre: str  # e.g. "topdown-collect", "runner", "survival"

    # Core loop & difficulty
    loop: str  # short description
    difficulty_curve: str  # short description

    # Game economy / shop items
    shop_items: List[Dict[str, Any]]

    # Enemies and rules (for template to interpret)
    enemies: List[Dict[str, Any]]

    # UI texts
    ui: Dict[str, str]

    # Numeric tuning params (globals)
    tuning: Dict[str, float]

    # Optional feature flags/modules
    modules: List[str]

    # Anything else to store
    meta: Dict[str, Any]


class GameDesignProvider(Protocol):
    name: str

    def generate(self, spec: Dict[str, Any]) -> Design:
        """
        Given a spec dict (name/theme/difficulty/seed/prompt/etc), return a Design object.
        This MUST be deterministic for a given seed (unless provider chooses otherwise).
        """
        ...
