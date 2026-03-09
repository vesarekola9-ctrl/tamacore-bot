from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .ai_full_pack_generator import generate_ai_full_pack
from .export_report import write_export_report
from .export_validate import validate_exports
from .export_web import export_web
from .export_zip import export_zip
from .generator import run_factory_v3_1
from .release_bundle import bundle_release
from .validate import validate_build_output


def run_ai_make_game(
    pack_dir: Path,
    template_dir: Path,
    out_dir: Path,
    export_dir: Path,
    bundle_dir: Path | None = None,
    shop_count: int = 4,
    foods_count: int = 4,
    cosmetics_count: int = 4,
    with_demo_layout: bool = True,
    enable_v3_2: bool = True,
    export_web_enabled: bool = True,
    export_zip_enabled: bool = True,
    bundle_enabled: bool = True,
) -> Dict[str, Any]:
    pack_info = generate_ai_full_pack(
        pack_dir=pack_dir,
        shop_count=shop_count,
        foods_count=foods_count,
        cosmetics_count=cosmetics_count,
    )

    run_factory_v3_1(
        pack_dir=pack_dir,
        template_dir=template_dir,
        game_dir=out_dir,
        with_demo_layout=with_demo_layout,
        enable_v3_2=enable_v3_2,
    )

    build_errors = validate_build_output(out_dir)
    if build_errors:
        raise RuntimeError("Build validation failed:\n" + "\n".join(build_errors))

    exported = {
        "web": False,
        "zip": False,
        "android": False,
    }

    if export_web_enabled:
        export_web(out_dir, export_dir)
        exported["web"] = True

    if export_zip_enabled:
        export_zip(out_dir, export_dir / "game.zip")
        exported["zip"] = True

    if any(exported.values()):
        write_export_report(export_dir, exported)
        export_errors = validate_exports(export_dir)
        if export_errors:
            raise RuntimeError("Export validation failed:\n" + "\n".join(export_errors))

    if bundle_enabled:
        final_bundle_dir = bundle_dir if bundle_dir is not None else Path("release_bundle")
        bundle_release(out_dir, export_dir, final_bundle_dir)

    return {
        "pack": pack_info,
        "gameDir": str(out_dir),
        "exportDir": str(export_dir),
        "bundleDir": str(bundle_dir) if bundle_dir is not None else "",
    }
