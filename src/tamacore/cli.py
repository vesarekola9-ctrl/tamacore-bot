from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .factory_v3.generator import run_factory_v3
from .factory_v3_1.export_android_stub import export_android_stub
from .factory_v3_1.export_report import write_export_report
from .factory_v3_1.export_validate import validate_exports
from .factory_v3_1.export_web import export_web
from .factory_v3_1.export_zip import export_zip
from .factory_v3_1.generator import run_factory_v3_1
from .factory_v3_1.pack_inspector import inspect_pack
from .factory_v3_1.pack_scaffold import create_pack
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

    build = sub.add_parser("build", help="Build game from pack + template")
    build.add_argument("--pack", required=True, help="Pack directory, e.g. assets/packs/demo_pack")
    build.add_argument("--template", default="templates/gdevelop_template", help="Template directory")
    build.add_argument("--out", required=True, help="Output game directory")
    build.add_argument("--with-demo-layout", action="store_true")
    build.add_argument("--v31", action="store_true")
    build.add_argument("--v32", action="store_true")
    build.add_argument("--scene", default="Main")
    build.add_argument("--seed", type=int, default=1337)

    make_game = sub.add_parser("make-game", help="Inspect + build + validate in one command")
    make_game.add_argument("--pack", required=True, help="Pack directory, e.g. assets/packs/demo_pack")
    make_game.add_argument("--template", default="templates/gdevelop_template", help="Template directory")
    make_game.add_argument("--out", required=True, help="Output game directory")
    make_game.add_argument("--with-demo-layout", action="store_true")
    make_game.add_argument("--v31", action="store_true")
    make_game.add_argument("--v32", action="store_true")
    make_game.add_argument("--scene", default="Main")
    make_game.add_argument("--seed", type=int, default=1337)
    make_game.add_argument("--export-web", action="store_true")
    make_game.add_argument("--export-zip", action="store_true")
    make_game.add_argument("--export-android", action="store_true")
    make_game.add_argument("--export-out", default="exports", help="Export output directory")

    validate = sub.add_parser("validate", help="Validate generated game output")
    validate.add_argument("--game-dir", required=True, help="Generated game directory")

    validate_exports_cmd = sub.add_parser("validate-exports", help="Validate export output")
    validate_exports_cmd.add_argument("--export-dir", required=True, help="Export directory")

    inspect = sub.add_parser("inspect-pack", help="Validate pack before build")
    inspect.add_argument("--pack", required=True, help="Pack directory")

    init_pack = sub.add_parser("init-pack", help="Create a new pack scaffold")
    init_pack.add_argument("--out", required=True, help="Output pack directory")
    init_pack.add_argument("--name", default="New Pack", help="Pack name")

    export = sub.add_parser("export", help="Export existing build")
    export.add_argument("--game-dir", required=True, help="Built game directory")
    export.add_argument("--out", required=True, help="Export output directory")
    export.add_argument("--type", required=True, choices=["web", "zip", "android"])

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
        rc = _build_game(
            pack_dir=Path(args.pack),
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
        exported = {
            "web": False,
            "zip": False,
            "android": False,
        }

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

        print("[OK] make-game complete")
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
