from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .asset_generator import generate_placeholder_assets
from .batch_factory import run_batch_factory
from .pack_scaffold import create_pack


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
    if not (pack_dir / "pack.json").exists():
        create_pack(pack_dir, pack_name)

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

    return {
        "workspace": str(workspace_dir),
        "packDir": str(pack_dir),
        "gameDir": str(out_root / pack_name),
        "exportDir": str(export_root / pack_name),
        "bundleDir": str(bundle_root / pack_name),
        "summary": summary,
        "gameName": game_name,
    }
