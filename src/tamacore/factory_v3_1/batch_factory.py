from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import ensure_dir, write_json
from .asset_generator import generate_placeholder_assets
from .export_report import write_export_report
from .export_validate import validate_exports
from .export_web import export_web
from .export_zip import export_zip
from .generator import run_factory_v3_1
from .pack_inspector import inspect_pack
from .release_bundle import bundle_release
from .validate import validate_build_output


def run_batch_factory(
    packs_root: Path,
    template_dir: Path,
    out_root: Path,
    export_root: Path,
    bundle_root: Path,
    with_demo_layout: bool = True,
    enable_v3_2: bool = True,
    generate_assets: bool = False,
    export_web_enabled: bool = True,
    export_zip_enabled: bool = True,
    bundle_enabled: bool = False,
) -> Dict[str, Any]:
    ensure_dir(out_root)
    ensure_dir(export_root)
    ensure_dir(bundle_root)

    results: List[Dict[str, Any]] = []

    pack_dirs = sorted(
        p for p in packs_root.iterdir()
        if p.is_dir() and (p / "pack.json").exists()
    ) if packs_root.exists() else []

    for pack_dir in pack_dirs:
        pack_name = pack_dir.name
        game_dir = out_root / pack_name
        exports_dir = export_root / pack_name
        bundle_dir = bundle_root / pack_name

        item: Dict[str, Any] = {
            "pack": pack_name,
            "ok": False,
            "buildOk": False,
            "exportOk": False,
            "bundleOk": False,
            "errors": [],
        }

        try:
            if generate_assets:
                generate_placeholder_assets(pack_dir)

            inspect_errors = inspect_pack(pack_dir)
            if inspect_errors:
                item["errors"].extend(inspect_errors)
                results.append(item)
                continue

            run_factory_v3_1(
                pack_dir=pack_dir,
                template_dir=template_dir,
                game_dir=game_dir,
                with_demo_layout=with_demo_layout,
                enable_v3_2=enable_v3_2,
            )

            build_errors = validate_build_output(game_dir)
            if build_errors:
                item["errors"].extend(build_errors)
                results.append(item)
                continue

            item["buildOk"] = True

            exported = {
                "web": False,
                "zip": False,
                "android": False,
            }

            if export_web_enabled:
                export_web(game_dir, exports_dir)
                exported["web"] = True

            if export_zip_enabled:
                export_zip(game_dir, exports_dir / "game.zip")
                exported["zip"] = True

            if any(exported.values()):
                write_export_report(exports_dir, exported)
                export_errors = validate_exports(exports_dir)
                if export_errors:
                    item["errors"].extend(export_errors)
                    results.append(item)
                    continue

            item["exportOk"] = True

            if bundle_enabled:
                bundle_release(game_dir, exports_dir, bundle_dir)
                item["bundleOk"] = True

            item["ok"] = True

        except Exception as exc:
            item["errors"].append(str(exc))

        results.append(item)

    summary = {
        "packsRoot": str(packs_root),
        "templateDir": str(template_dir),
        "outRoot": str(out_root),
        "exportRoot": str(export_root),
        "bundleRoot": str(bundle_root),
        "count": len(results),
        "okCount": sum(1 for r in results if r.get("ok")),
        "failedCount": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }

    write_json(out_root / "BATCH_REPORT.json", summary)
    return summary
