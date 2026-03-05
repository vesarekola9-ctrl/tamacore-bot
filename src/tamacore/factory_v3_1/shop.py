from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import write_json
from .schema import PackCfg


def write_shop(pack: PackCfg, out_dir: Path) -> Dict[str, Any]:
    shop = {
        "currencyVariable": pack.shop.currencyVariable,
        "upgrades": [
            {"id": u.id, "name": u.name, "cost": u.cost, "effect": u.effect}
            for u in pack.shop.upgrades
            if u.id
        ],
    }
    write_json(out_dir / "shop.json", shop)
    return shop
