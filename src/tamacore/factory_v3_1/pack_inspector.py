from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from ..utils import is_image_file, read_json


def inspect_pack(pack_dir: Path) -> List[str]:
    errors: List[str] = []

    pack_json = pack_dir / "pack.json"
    assets_dir = pack_dir / "assets"

    if not pack_json.exists():
        return [f"Missing file: {pack_json}"]

    if not assets_dir.exists():
        return [f"Missing directory: {assets_dir}"]

    data = read_json(pack_json)
    if not isinstance(data, dict):
        return ["pack.json must be a JSON object"]

    required_asset_groups = ["background", "player", "coin", "enemy", "ui"]
    for group in required_asset_groups:
        group_dir = assets_dir / group
        if not group_dir.exists():
            errors.append(f"Missing asset directory: assets/{group}")
            continue

        images = [p for p in group_dir.rglob("*") if p.is_file() and is_image_file(p)]
        if not images:
            errors.append(f"No images in: assets/{group}")

    shop = data.get("shop", {})
    if not isinstance(shop, dict):
        errors.append("pack.json: shop must be an object")
    else:
        upgrades = shop.get("upgrades", [])
        if not isinstance(upgrades, list) or not upgrades:
            errors.append("pack.json: shop.upgrades missing or empty")
        else:
            seen_ids: Dict[str, int] = {}
            for i, item in enumerate(upgrades):
                if not isinstance(item, dict):
                    errors.append(f"pack.json: upgrade {i} must be object")
                    continue

                uid = str(item.get("id", "")).strip()
                name = str(item.get("name", "")).strip()
                cost = item.get("cost")
                effect = item.get("effect")

                if not uid:
                    errors.append(f"pack.json: upgrade {i} missing id")
                else:
                    seen_ids[uid] = seen_ids.get(uid, 0) + 1

                if not name:
                    errors.append(f"pack.json: upgrade {i} missing name")

                try:
                    int(cost)
                except Exception:
                    errors.append(f"pack.json: upgrade {i} invalid cost")

                if not isinstance(effect, dict) or not effect:
                    errors.append(f"pack.json: upgrade {i} missing effect")

            for uid, count in seen_ids.items():
                if count > 1:
                    errors.append(f"pack.json: duplicate upgrade id '{uid}'")

    return errors
