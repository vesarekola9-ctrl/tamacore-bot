from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .factory_v3.generator import run_factory_v3
from .factory_v3_1.generator import run_factory_v3_1
from .factory_v3_1.pack_inspector import inspect_pack
from .factory_v3_1.pack_scaffold import create_pack
from .factory_v3_1.validate import validate_build_output


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

    validate = sub.add_parser("validate", help="Validate generated game output")
    validate.add_argument("--game-dir", required=True, help="Generated game directory")

    inspect = sub.add_parser("inspect-pack", help="Validate pack before build")
    inspect.add_argument("--pack", required=True, help="Pack directory")

    init_pack = sub.add_parser("init-pack", help="Create a new pack scaffold")
    init_pack.add_argument("--out", required=True, help="Output pack directory")
    init_pack.add_argument("--name", default="New Pack", help="Pack name")

    args = parser.parse_args(argv)

    if args.cmd == "build":
        pack_dir = Path(args.pack)
        template_dir = Path(args.template)
        out_dir = Path(args.out)

        pack_errors = inspect_pack(pack_dir)
        if pack_errors:
            for err in pack_errors:
                print(err)
            return 1

        if args.v31 or args.v32:
            run_factory_v3_1(
                pack_dir=pack_dir,
                template_dir=template_dir,
                game_dir=out_dir,
                with_demo_layout=bool(args.with_demo_layout),
                enable_v3_2=bool(args.v32),
            )
            return 0

        run_factory_v3(
            pack_dir=pack_dir,
            template_dir=template_dir,
            game_dir=out_dir,
            scene_name=str(args.scene),
            seed=int(args.seed),
            with_demo_layout=bool(args.with_demo_layout),
        )
        return 0

    if args.cmd == "validate":
        errors = validate_build_output(Path(args.game_dir))
        if errors:
            for err in errors:
                print(err)
            return 1
        print("[OK] Build validation passed")
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
