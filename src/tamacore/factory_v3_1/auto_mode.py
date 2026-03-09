from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .ai_content_generator import generate_ai_content
from .ai_level_generator import generate_ai_levels
from .ai_pack_generator import generate_ai_pack
from .ai_pet_generator import generate_ai_pet
from .ai_shop_generator import generate_ai_shop
from .asset_generator import generate_placeholder_assets
from .auto_report import write_auto_report
from .batch_factory import run_batch_factory


def run_auto_mode(
    workspace_dir: Path,
    template_dir: Path,
    pack_name: str = "auto_pack",
    game_name: str = "auto_game",
) -> Dict[str, Any]:
    packs_root = workspace_dir / "packs"
    out_root = workspace_dir / "games"
    export_root = workspace_dir / "exports"
    bundle_root = workspace_dir / "bundles"

    pack_dir = packs_root / pack_name
    pack_dir.mkdir(parents=True, exist_ok=True)

    if not (pack_dir / "pack.json").exists():
        generate_ai_pack(pack_dir)

    pet = generate_ai_pet(pack_dir)
    shop = generate_ai_shop(pack_dir, upgrade_count=4)
    levels = generate_ai_levels(pack_dir)
    content = generate_ai_content(pack_dir, foods_count=4, cosmetics_count=4)
    generate_placeholder_assets(pack_dir)

    summary = run_batch_factory(
        packs_root=packs_root,
        template_dir=template_dir,
        out_root=out_root,
        export_root=export_root,
        bundle_root=bundle_root,
        with_demo_layout=True,
        enable_v3_2=True,
        generate_assets=True,
        export_web_enabled=True,
        export_zip_enabled=True,
        bundle_enabled=True,
    )

    result = {
        "workspace": str(workspace_dir),
        "packDir": str(pack_dir),
        "gameDir": str(out_root / pack_name),
        "exportDir": str(export_root / pack_name),
        "bundleDir": str(bundle_root / pack_name),
        "summary": summary,
        "gameName": game_name,
        "pet": pet.get("name", ""),
        "shopUpgrades": len(shop.get("upgrades", [])),
        "levelCount": levels.get("count", 0),
        "foodCount": len(content.get("foods", [])),
        "cosmeticCount": len(content.get("cosmetics", [])),
    }

    write_auto_report(workspace_dir, result)
    return result
