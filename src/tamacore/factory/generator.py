from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import read_json, write_json
from ..template_ops import ensure_template_exists, copy_template
from ..patch_gdevelop import copy_assets_into_game, patch_project


@dataclass
class GameSpec:
    name: str
    packageName: str
    version: str
    theme: str
    difficulty: str
    seed: int
    modules: List[str]
    tuning: Dict[str, Any]


DEFAULT_SPEC = GameSpec(
    name="TamaCore",
    packageName="com.yourcompany.tamacore",
    version="0.1.0",
    theme="neon",
    difficulty="normal",
    seed=1337,
    modules=["collect", "dodge", "shop", "settings", "mobile_ui"],
    tuning={
        "enemy_base_speed": 60,
        "enemy_speed_per_score": 4,
        "enemy_speed_cap": 240,
        "unlock_enemy2_score": 10,
        "unlock_enemy3_score": 20,
        "hp_start": 3,
        "stamina_start": 100,
        "stamina_drain_per_sec": 60,
        "stamina_regen_per_sec": 30,
    },
)


def generate_game(spec_path: Path, out_dir: Path, template_dir: Path, seed_assets_dir: Path) -> None:
    ensure_template_exists(template_dir)

    spec = load_spec(spec_path)

    # 1) Copy template to out_dir
    if out_dir.exists():
        # wipe only if it looks like a generated folder (has game.json)
        if (out_dir / "game.json").exists():
            shutil.rmtree(out_dir)
        else:
            raise RuntimeError(
                f"Output folder exists but doesn't look like a generated game: {out_dir}\n"
                "Pick another --out or remove it."
            )
    copy_template(template_dir, out_dir)

    # 2) Assets: seed -> generated variants -> copy into out_dir/assets/generated
    # We generate variants by copying existing seed images and renaming to themed names.
    seed_dir = pick_seed_dir(seed_assets_dir, template_dir)
    themed_assets_dir = create_themed_assets(seed_dir, out_dir, spec)

    # 3) Patch resources + events via existing patcher
    image_map = copy_assets_into_game(themed_assets_dir, out_dir)

    game_json = out_dir / "game.json"
    patch_project(game_json, image_map)

    # 4) Patch project metadata + factory tuning variables into game.json
    project = read_json(game_json)
    patch_metadata(project, spec)
    patch_factory_variables(project, spec)
    write_json(game_json, project)

    # 5) Write a tiny manifest
    write_manifest(out_dir, spec, image_map)

    print("[OK] Factory generated game at:", out_dir)
    print("[OK] Open in GDevelop:", out_dir / "game.json")
    print("[TIP] Change spec and rerun to generate a new game.")


def load_spec(spec_path: Path) -> GameSpec:
    if not spec_path.exists():
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(spec_to_dict(DEFAULT_SPEC), f, ensure_ascii=False, indent=2)
        print("[i] Spec was missing, created default at:", spec_path)

    data = read_json(spec_path)
    merged = deep_merge(spec_to_dict(DEFAULT_SPEC), data if isinstance(data, dict) else {})
    return dict_to_spec(merged)


def spec_to_dict(s: GameSpec) -> Dict[str, Any]:
    return {
        "name": s.name,
        "packageName": s.packageName,
        "version": s.version,
        "theme": s.theme,
        "difficulty": s.difficulty,
        "seed": s.seed,
        "modules": list(s.modules),
        "tuning": dict(s.tuning),
    }


def dict_to_spec(d: Dict[str, Any]) -> GameSpec:
    return GameSpec(
        name=str(d.get("name", DEFAULT_SPEC.name)),
        packageName=str(d.get("packageName", DEFAULT_SPEC.packageName)),
        version=str(d.get("version", DEFAULT_SPEC.version)),
        theme=str(d.get("theme", DEFAULT_SPEC.theme)),
        difficulty=str(d.get("difficulty", DEFAULT_SPEC.difficulty)),
        seed=int(d.get("seed", DEFAULT_SPEC.seed)),
        modules=list(d.get("modules", DEFAULT_SPEC.modules)),
        tuning=dict(d.get("tuning", DEFAULT_SPEC.tuning)),
    )


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def pick_seed_dir(seed_assets_dir: Path, template_dir: Path) -> Path:
    # Prefer repo seed assets if exists, else template assets/generated if exists
    if seed_assets_dir.exists():
        return seed_assets_dir
    tmpl_gen = template_dir / "assets" / "generated"
    if tmpl_gen.exists():
        return tmpl_gen
    raise FileNotFoundError(
        "No seed assets found. Create 'assets/' with bg.png, player.png, coin.png etc "
        "or ensure template has templates/gdevelop_template/assets/generated."
    )


def create_themed_assets(seed_dir: Path, out_dir: Path, spec: GameSpec) -> Path:
    """
    Creates a temp folder under out_dir/.factory_assets containing renamed copies.
    No image processing yet (v1), just deterministic naming so game can evolve.
    """
    tmp = out_dir / ".factory_assets"
    tmp.mkdir(parents=True, exist_ok=True)

    # seed picks
    bg = find_first(seed_dir, ["bg.png", "background.png", "bg.jpg", "bg.webp"])
    player = find_first(seed_dir, ["player.png", "hero.png", "character.png"])
    coin = find_first(seed_dir, ["coin.png", "pickup.png", "gem.png"])

    # Fallback: copy any images
    if bg is None:
        bg = first_image(seed_dir)
    if player is None:
        player = first_image(seed_dir)
    if coin is None:
        coin = first_image(seed_dir)

    if bg is None or player is None or coin is None:
        raise FileNotFoundError(f"Seed assets folder has no images: {seed_dir}")

    # Theme naming
    # These names (stems) become resource names via image_map in patch_gdevelop.
    # autogen expects bg/player/coin names too, so we ALSO export those canonical keys.
    copies: List[Tuple[Path, str]] = [
        (bg, "bg.png"),
        (player, "player.png"),
        (coin, "coin.png"),
        (bg, f"bg_{spec.theme}.png"),
        (player, f"player_{spec.theme}.png"),
        (coin, f"coin_{spec.theme}.png"),
    ]

    for src, name in copies:
        dst = tmp / name
        shutil.copy2(src, dst)

    return tmp


def find_first(folder: Path, names: List[str]) -> Optional[Path]:
    for n in names:
        p = folder / n
        if p.exists() and p.is_file():
            return p
    return None


def first_image(folder: Path) -> Optional[Path]:
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            return p
    return None


def patch_metadata(project: Dict[str, Any], spec: GameSpec) -> None:
    props = project.get("properties")
    if not isinstance(props, dict):
        props = {}
        project["properties"] = props

    props["name"] = spec.name
    props["packageName"] = spec.packageName
    props["version"] = spec.version


def patch_factory_variables(project: Dict[str, Any], spec: GameSpec) -> None:
    """
    Stores factory tuning into GLOBAL variables so future patches (or runtime events)
    can read from VariableString / Variable etc.
    """
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    def upsert_num(name: str, value: Any) -> None:
        for v in vars_:
            if isinstance(v, dict) and v.get("name") == name:
                v["type"] = "number"
                v["value"] = str(value)
                v.setdefault("children", [])
                return
        vars_.append({"name": name, "type": "number", "value": str(value), "children": []})

    def upsert_str(name: str, value: str) -> None:
        for v in vars_:
            if isinstance(v, dict) and v.get("name") == name:
                v["type"] = "string"
                v["value"] = value
                v.setdefault("children", [])
                return
        vars_.append({"name": name, "type": "string", "value": value, "children": []})

    upsert_str("FactoryTheme", spec.theme)
    upsert_str("FactoryDifficulty", spec.difficulty)
    upsert_num("FactorySeed", spec.seed)

    # tuning -> globals (prefixed)
    for k, v in spec.tuning.items():
        key = "Tuning_" + str(k)
        # keep numeric in v1
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace(".", "", 1).isdigit()):
            upsert_num(key, v)
        else:
            upsert_str(key, str(v))

    # module flags
    for m in spec.modules:
        upsert_num("Module_" + m, 1)


def write_manifest(out_dir: Path, spec: GameSpec, image_map: Dict[str, str]) -> None:
    mf = {
        "name": spec.name,
        "packageName": spec.packageName,
        "version": spec.version,
        "theme": spec.theme,
        "difficulty": spec.difficulty,
        "seed": spec.seed,
        "modules": spec.modules,
        "tuning": spec.tuning,
        "images": image_map,
    }
    (out_dir / "FACTORY_MANIFEST.json").write_text(json.dumps(mf, ensure_ascii=False, indent=2), encoding="utf-8")
