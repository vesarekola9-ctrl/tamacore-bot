from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .factory_v3.generator import run_factory_v3
from .factory_v3_1.asset_generator import generate_placeholder_assets
from .factory_v3_1.auto_mode import run_auto_mode
from .factory_v3_1.auto_validate import validate_auto_workspace
from .factory_v3_1.batch_factory import run_batch_factory
from .factory_v3_1.export_android_stub import export_android_stub
from .factory_v3_1.export_report import write_export_report
from .factory_v3_1.export_validate import validate_exports
from .factory_v3_1.export_web import export_web
from .factory_v3_1.export_zip import export_zip
from .factory_v3_1.generator import run_factory_v3_1
from .factory_v3_1.pack_inspector import inspect_pack
from .factory_v3_1.pack_scaffold import create_pack
from .factory_v3_1.release_bundle import bundle_release
from .factory_v3_1.validate import validate_build_output


def _build_game(
    pack_dir: Path,
    template_dir: Path,
    out_dir: Path,
    with_demo_layout: bool,
    use_v31: bool,
    use_v32: bool,
    scene: str,
    seed: int,
) -> int:
    pack_errors = inspect_pack(pack_dir)
    if pack_errors:
        for err in pack_errors:
            print(err)
        return 1

    if use_v31 or use_v32:
        run_factory_v3_1(
            pack_dir=pack_dir,
            template_dir=template_dir,
            game_dir=out_dir,
            with_demo_layout=with_demo_layout,
            enable_v3_2=use_v32,
        )
        return 0

    run_factory_v3(
        pack_dir=pack_dir,
        template_dir=template_dir,
        game_dir=out_dir,
        scene_name=scene,
        seed=seed,
        with_demo_layout=with_demo_layout,
    )
    return 0


def _export_game(game_dir: Path, out_dir: Path, export_type: str) -> int:
    if export_type == "web":
        export_web(game_dir, out_dir)
        return 0
    if export_type == "zip":
        export_zip(game_dir, out_dir / "game.zip")
        return 0
    if export_type == "android":
        export_android_stub(game_dir, out_dir)
        return 0

    print(f"Unknown export type: {export_type}")
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(prog="tamacore", description="TamaCore AI Game Factory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build")
    build.add_argument("--pack", required=True)
    build.add_argument("--template", default="templates/gdevelop_template")
    build.add_argument("--out", required=True)
    build.add_argument("--with-demo-layout", action="store_true")
    build.add_argument("--v31", action="store_true")
    build.add_argument("--v32", action="store_true")
    build.add_argument("--scene", default="Main")
    build.add_argument("--seed", type=int, default=1337)

    make_game = sub.add_parser("make-game")
    make_game.add_argument("--pack", required=True)
    make_game.add_argument("--template", default="templates/gdevelop_template")
    make_game.add_argument("--out", required=True)
    make_game.add_argument("--with-demo-layout", action="store_true")
    make_game.add_argument("--v31", action="store_true")
    make_game.add_argument("--v32", action="store_true")
    make_game.add_argument("--scene", default="Main")
    make_game.add_argument("--seed", type=int, default=1337)
    make_game.add_argument("--export-web", action="store_true")
    make_game.add_argument("--export-zip", action="store_true")
    make_game.add_argument("--export-android", action="store_true")
    make_game.add_argument("--export-out", default="exports")
    make_game.add_argument("--bundle-out", default="")
    make_game.add_argument("--bundle-release", action="store_true")
    make_game.add_argument("--generate-assets", action="store_true")

    batch = sub.add_parser("make-batch")
    batch.add_argument("--packs-root", required=True)
    batch.add_argument("--template", default="templates/gdevelop_template")
    batch.add_argument("--out-root", required=True)
    batch.add_argument("--export-root", default="batch_exports")
    batch.add_argument("--bundle-root", default="batch_bundles")
    batch.add_argument("--with-demo-layout", action="store_true")
    batch.add_argument("--v32", action="store_true")
    batch.add_argument("--generate-assets", action="store_true")
    batch.add_argument("--export-web", action="store_true")
    batch.add_argument("--export-zip", action="store_true")
    batch.add_argument("--bundle-release", action="store_true")

    auto = sub.add_parser("auto")
    auto.add_argument("--workspace", default="auto_workspace")
    auto.add_argument("--template", default="templates/gdevelop_template")
    auto.add_argument("--pack-name", default="auto_pack")
    auto.add_argument("--game-name", default="auto_game")

    validate = sub.add_parser("validate")
    validate.add_argument("--game-dir", required=True)

    validate_exports_cmd = sub.add_parser("validate-exports")
    validate_exports_cmd.add_argument("--export-dir", required=True)

    validate_auto_cmd = sub.add_parser("validate-auto")
    validate_auto_cmd.add_argument("--workspace", required=True)

    inspect = sub.add_parser("inspect-pack")
    inspect.add_argument("--pack", required=True)

    init_pack = sub.add_parser("init-pack")
    init_pack.add_argument("--out", required=True)
    init_pack.add_argument("--name", default="New Pack")

    gen_assets = sub.add_parser("generate-assets")
    gen_assets.add_argument("--pack", required=True)

    export = sub.add_parser("export")
    export.add_argument("--game-dir", required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--type", required=True, choices=["web", "zip", "android"])

    bundle = sub.add_parser("bundle-release")
    bundle.add_argument("--game-dir", required=True)
    bundle.add_argument("--export-dir", required=True)
    bundle.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "build":
        return _build_game(
            pack_dir=Path(args.pack),
            template_dir=Path(args.template),
            out_dir=Path(args.out),
            with_demo_layout=bool(args.with_demo_layout),
            use_v31=bool(args.v31),
            use_v32=bool(args.v32),
            scene=str(args.scene),
            seed=int(args.seed),
        )

    if args.cmd == "make-game":
        pack_dir = Path(args.pack)
        if args.generate_assets:
            generate_placeholder_assets(pack_dir)

        rc = _build_game(
            pack_dir=pack_dir,
            template_dir=Path(args.template),
            out_dir=Path(args.out),
            with_demo_layout=bool(args.with_demo_layout),
            use_v31=bool(args.v31 or args.v32),
            use_v32=bool(args.v32),
            scene=str(args.scene),
            seed=int(args.seed),
        )
        if rc != 0:
            return rc

        errors = validate_build_output(Path(args.out))
        if errors:
            for err in errors:
                print(err)
            return 1

        export_out = Path(args.export_out)
        exported = {"web": False, "zip": False, "android": False}

        if args.export_web:
            rc = _export_game(Path(args.out), export_out, "web")
            if rc != 0:
                return rc
            exported["web"] = True

        if args.export_zip:
            rc = _export_game(Path(args.out), export_out, "zip")
            if rc != 0:
                return rc
            exported["zip"] = True

        if args.export_android:
            rc = _export_game(Path(args.out), export_out, "android")
            if rc != 0:
                return rc
            exported["android"] = True

        if any(exported.values()):
            write_export_report(export_out, exported)
            export_errors = validate_exports(export_out)
            if export_errors:
                for err in export_errors:
                    print(err)
                return 1

        if args.bundle_release:
            bundle_out = Path(args.bundle_out) if str(args.bundle_out).strip() else Path("release_bundle")
            bundle_release(Path(args.out), export_out, bundle_out)
            print(f"[OK] release bundle created: {bundle_out}")
            print(f"[OK] release zip created: {bundle_out}.zip")

        print("[OK] make-game complete")
        return 0

    if args.cmd == "make-batch":
        summary = run_batch_factory(
            packs_root=Path(args.packs_root),
            template_dir=Path(args.template),
            out_root=Path(args.out_root),
            export_root=Path(args.export_root),
            bundle_root=Path(args.bundle_root),
            with_demo_layout=bool(args.with_demo_layout),
            enable_v3_2=bool(args.v32),
            generate_assets=bool(args.generate_assets),
            export_web_enabled=bool(args.export_web),
            export_zip_enabled=bool(args.export_zip),
            bundle_enabled=bool(args.bundle_release),
        )
        print(f"[OK] batch complete: {summary['okCount']}/{summary['count']}")
        if int(summary["failedCount"]) > 0:
            return 1
        return 0

    if args.cmd == "auto":
        result = run_auto_mode(
            workspace_dir=Path(args.workspace),
            template_dir=Path(args.template),
            pack_name=str(args.pack_name),
            game_name=str(args.game_name),
        )
        print(f"[OK] auto complete: {result['gameDir']}")
        return 0

    if args.cmd == "validate":
        errors = validate_build_output(Path(args.game_dir))
        if errors:
            for err in errors:
                print(err)
            return 1
        print("[OK] Build validation passed")
        return 0

    if args.cmd == "validate-exports":
        errors = validate_exports(Path(args.export_dir))
        if errors:
            for err in errors:
                print(err)
            return 1
        print("[OK] Export validation passed")
        return 0

    if args.cmd == "validate-auto":
        errors = validate_auto_workspace(Path(args.workspace))
        if errors:
            for err in errors:
                print(err)
            return 1
        print("[OK] Auto workspace validation passed")
        return 0

    if args.cmd == "inspect-pack":
        errors = inspect_pack(Path(args.pack))
        if errors:
            for err in errors:
                print(err)
            return 1
        print("[OK] Pack validation passed")
        return 0

    if args.cmd == "init-pack":
        create_pack(Path(args.out), str(args.name))
        print(f"[OK] Pack created: {Path(args.out)}")
        return 0

    if args.cmd == "generate-assets":
        generate_placeholder_assets(Path(args.pack))
        print(f"[OK] Placeholder assets generated: {Path(args.pack)}")
        return 0

    if args.cmd == "export":
        rc = _export_game(
            game_dir=Path(args.game_dir),
            out_dir=Path(args.out),
            export_type=str(args.type),
        )
        if rc != 0:
            return rc

        exported = {
            "web": args.type == "web",
            "zip": args.type == "zip",
            "android": args.type == "android",
        }
        write_export_report(Path(args.out), exported)

        errors = validate_exports(Path(args.out))
        if errors:
            for err in errors:
                print(err)
            return 1

        print("[OK] Export complete")
        return 0

    if args.cmd == "bundle-release":
        bundle_release(
            game_dir=Path(args.game_dir),
            export_dir=Path(args.export_dir),
            bundle_dir=Path(args.out),
        )
        print(f"[OK] release bundle created: {Path(args.out)}")
        print(f"[OK] release zip created: {Path(args.out)}.zip")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
