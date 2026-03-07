from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .factory_v3.generator import run_factory_v3
from .factory_v3_1.export_android_stub import export_android_stub
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


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(prog="tamacore")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build")
    build.add_argument("--pack", required=True)
    build.add_argument("--template", required=True)
    build.add_argument("--out", required=True)
    build.add_argument("--with-demo-layout", action="store_true")
    build.add_argument("--v31", action="store_true")
    build.add_argument("--v32", action="store_true")
    build.add_argument("--scene", default="Main")
    build.add_argument("--seed", type=int, default=1337)

    make_game = sub.add_parser("make-game")
    make_game.add_argument("--pack", required=True)
    make_game.add_argument("--template", required=True)
    make_game.add_argument("--out", required=True)
    make_game.add_argument("--with-demo-layout", action="store_true")
    make_game.add_argument("--v31", action="store_true")
    make_game.add_argument("--v32", action="store_true")

    export = sub.add_parser("export")
    export.add_argument("--game-dir", required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--type", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "build":
        return _build_game(
            Path(args.pack),
            Path(args.template),
            Path(args.out),
            args.with_demo_layout,
            args.v31,
            args.v32,
            args.scene,
            args.seed,
        )

    if args.cmd == "make-game":
        rc = _build_game(
            Path(args.pack),
            Path(args.template),
            Path(args.out),
            args.with_demo_layout,
            args.v31 or args.v32,
            args.v32,
            "Main",
            1337,
        )

        if rc != 0:
            return rc

        errors = validate_build_output(Path(args.out))
        if errors:
            for e in errors:
                print(e)
            return 1

        print("OK make-game")
        return 0

    if args.cmd == "export":

        game_dir = Path(args.game_dir)
        out_dir = Path(args.out)

        if args.type == "web":
            export_web(game_dir, out_dir)

        elif args.type == "zip":
            export_zip(game_dir, out_dir / "game.zip")

        elif args.type == "android":
            export_android_stub(game_dir, out_dir)

        else:
            print("Unknown export type")
            return 1

        print("OK export")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
