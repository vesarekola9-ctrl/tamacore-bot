from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .ai_content_generator import generate_ai_content
from .ai_level_generator import generate_ai_levels
from .ai_pack_generator import generate_ai_pack
from .ai_pet_generator import generate_ai_pet
from .ai_shop_generator import generate_ai_shop
from .asset_generator import generate_placeholder_assets


def generate_ai_full_pack(
    pack_dir: Path,
    shop_count: int = 4,
    foods_count: int = 4,
    cosmetics_count: int = 4,
) -> Dict[str, Any]:
    generate_ai_pack(pack_dir)
    pet = generate_ai_pet(pack_dir)
    shop = generate_ai_shop(pack_dir, upgrade_count=shop_count)
    levels = generate_ai_levels(pack_dir)
    content = generate_ai_content(
        pack_dir,
        foods_count=foods_count,
        cosmetics_count=cosmetics_count,
    )
    generate_placeholder_assets(pack_dir)

    return {
        "packDir": str(pack_dir),
        "pet": pet.get("name", ""),
        "shopUpgrades": len(shop.get("upgrades", [])),
        "levelCount": levels.get("count", 0),
        "foodCount": len(content.get("foods", [])),
        "cosmeticCount": len(content.get("cosmetics", [])),
    }
