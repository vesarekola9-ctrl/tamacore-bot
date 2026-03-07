from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import write_json
from .schema import PackCfg, ShopUpgrade


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_effect(effect: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(effect, dict):
        return {}

    out: Dict[str, Any] = {}
    for key, value in effect.items():
        if isinstance(value, (int, float, str, bool)):
            out[str(key)] = value
    return out


def _owned_variable_name(upgrade: ShopUpgrade) -> str:
    uid = (upgrade.id or "").strip()
    if not uid:
        return "Owned_upgrade"
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in uid)
    return f"Owned_{safe}"


def _upgrade_to_dict(upgrade: ShopUpgrade, index: int) -> Dict[str, Any]:
    uid = (upgrade.id or "").strip()
    if not uid:
        uid = f"upgrade_{index + 1}"

    name = (upgrade.name or "").strip() or uid.replace("_", " ").title()
    cost = max(0, _safe_int(upgrade.cost, 0))
    effect = _normalize_effect(upgrade.effect)

    return {
        "id": uid,
        "name": name,
        "cost": cost,
        "effect": effect,
        "ownedVariable": _owned_variable_name(upgrade),
        "uiText": f"BUY: {name} ({cost}c)",
    }


def write_shop(pack: PackCfg, out_dir: Path) -> Dict[str, Any]:
    upgrades: List[Dict[str, Any]] = []

    for index, upgrade in enumerate(pack.shop.upgrades):
        if not getattr(upgrade, "id", "") and not getattr(upgrade, "name", ""):
            continue
        upgrades.append(_upgrade_to_dict(upgrade, index))

    shop = {
        "currencyVariable": pack.shop.currencyVariable or "Coins",
        "upgrades": upgrades,
    }

    write_json(out_dir / "shop.json", shop)
    return shop
