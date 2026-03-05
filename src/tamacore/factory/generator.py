from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import read_json, write_json, is_image_file
from ..template_ops import ensure_template_exists, copy_template
from ..patch_gdevelop import copy_assets_into_game, patch_project
from .providers import RulesV2Provider
from .providers.base import Design


@dataclass
class GameSpec:
    name: str
    packageName: str
    version: str
    theme: str
    difficulty: str
    seed: int
    prompt: str
    provider: str
    modules: List[str]
    tuning: Dict[str, Any]


DEFAULT_SPEC = GameSpec(
    name="TamaCore: Neon Run",
    packageName="com.vesa.tamacore.neonrun",
    version="0.3.0",
    theme="neon",
    difficulty="normal",
    seed=1337,
    prompt="Top-down arcade. Collect coins. Avoid enemies. Mobile joystick. Shop upgrades.",
    provider="rules-v2",
    modules=["collect", "shop", "settings", "mobile_ui"],
    tuning={"player_base_speed": 240},
)


def generate_game(spec_path: Path, out_dir: Path, template_dir: Path, seed_assets_dir: Path) -> None:
    ensure_template_exists(template_dir)
    spec = load_spec(spec_path)
    design = generate_design(spec)

    # clean output if it was generated before
    if out_dir.exists():
        if (out_dir / "game.json").exists():
            shutil.rmtree(out_dir)
        else:
            raise RuntimeError(
                f"Output folder exists but doesn't look like a generated game: {out_dir}\n"
                "Pick another --out or remove it."
            )

    copy_template(template_dir, out_dir)

    # seed assets (optional) -> themed assets -> copy into game
    seed_dir = pick_seed_dir(seed_assets_dir, template_dir)
    themed_assets_dir = create_themed_assets(seed_dir, out_dir, spec, design)

    image_map = copy_assets_into_game(themed_assets_dir, out_dir)

    game_json = out_dir / "game.json"
    patch_project(game_json, image_map)

    project = read_json(game_json)
    patch_metadata(project, spec, design)
    patch_globals(project, spec, design)
    write_json(game_json, project)

    write_design(out_dir, spec, design, image_map)

    print("[OK] Factory v3 generated:", out_dir)
    print("[NEXT] Open in GDevelop:", out_dir / "game.json")


def generate_design(spec: GameSpec) -> Design:
    if spec.provider == "rules-v2":
        return RulesV2Provider().generate(spec_to_dict(spec))
    raise ValueError(f"Unknown provider: {spec.provider} (use rules-v2)")


def load_spec(spec_path: Path) -> GameSpec:
    if not spec_path.exists():
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(spec_path, spec_to_dict(DEFAULT_SPEC))
        print("[i] Spec missing -> created default:", spec_path)

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
        "prompt": s.prompt,
        "provider": s.provider,
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
        prompt=str(d.get("prompt", DEFAULT_SPEC.prompt)),
        provider=str(d.get("provider", DEFAULT_SPEC.provider)),
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
    if seed_assets_dir.exists() and any(is_image_file(p) for p in seed_assets_dir.rglob("*")):
        return seed_assets_dir
    tmpl_gen = template_dir / "assets" / "generated"
    if tmpl_gen.exists() and any(is_image_file(p) for p in tmpl_gen.rglob("*")):
        return tmpl_gen
    # last resort: use template root assets if exists
    tmpl_assets = template_dir / "assets"
    if tmpl_assets.exists() and any(is_image_file(p) for p in tmpl_assets.rglob("*")):
        return tmpl_assets
    raise FileNotFoundError("No seed images found in assets/ or template assets/.")


def create_themed_assets(seed_dir: Path, out_dir: Path, spec: GameSpec, design: Design) -> Path:
    """
    v3: still no image-gen. We just package deterministic placeholders so game always has needed keys:
      bg.png, player.png, coin.png, enemy.png, ui_button.png + theme variants
    """
    tmp = out_dir / ".factory_assets"
    tmp.mkdir(parents=True, exist_ok=True)

    bg = find_first(seed_dir, ["bg.png", "background.png"]) or first_image(seed_dir)
    player = find_first(seed_dir, ["player.png", "hero.png", "character.png"]) or first_image(seed_dir)
    coin = find_first(seed_dir, ["coin.png", "pickup.png", "gem.png"]) or first_image(seed_dir)
    enemy = find_first(seed_dir, ["enemy.png"]) or coin
    ui_btn = find_first(seed_dir, ["ui_button.png", "button.png"]) or coin

    if not bg or not player or not coin:
        raise FileNotFoundError(f"Seed dir has too few images: {seed_dir}")

    copies: List[Tuple[Path, str]] = [
        (bg, "bg.png"),
        (player, "player.png"),
        (coin, "coin.png"),
        (enemy, "enemy.png"),
        (ui_btn, "ui_button.png"),
        (bg, f"bg_{spec.theme}.png"),
        (player, f"player_{spec.theme}.png"),
        (coin, f"coin_{spec.theme}.png"),
        (enemy, f"enemy_{spec.theme}.png"),
    ]

    for src, name in copies:
        shutil.copy2(src, tmp / name)

    return tmp


def find_first(folder: Path, names: List[str]) -> Optional[Path]:
    for n in names:
        p = folder / n
        if p.exists() and p.is_file():
            return p
    return None


def first_image(folder: Path) -> Optional[Path]:
    for p in sorted(folder.rglob("*")):
        if is_image_file(p):
            return p
    return None


def patch_metadata(project: Dict[str, Any], spec: GameSpec, design: Design) -> None:
    props = project.get("properties")
    if not isinstance(props, dict):
        props = {}
        project["properties"] = props

    props["name"] = design.title or spec.name
    props["packageName"] = spec.packageName
    props["version"] = spec.version


def patch_globals(project: Dict[str, Any], spec: GameSpec, design: Design) -> None:
    """
    Store everything needed for a “factory runtime engine”.
    v3 goal: template can read variables and behave differently per generated game.
    """
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_

    def upsert(name: str, vtype: str, value: str) -> None:
        for item in vars_:
            if isinstance(item, dict) and item.get("name") == name:
                item["type"] = vtype
                item["value"] = value
                item.setdefault("children", [])
                return
        vars_.append({"name": name, "type": vtype, "value": value, "children": []})

    def set_num(name: str, v: Any) -> None:
        try:
            upsert(name, "number", str(float(v)))
        except Exception:
            upsert(name, "number", "0")

    def set_str(name: str, v: Any) -> None:
        upsert(name, "string", str(v))

    # identity
    set_str("FactoryVersion", "v3")
    set_str("FactoryProvider", design.meta.get("provider", spec.provider))
    set_str("FactoryTheme", spec.theme)
    set_str("FactoryDifficulty", spec.difficulty)
    set_num("FactorySeed", spec.seed)

    # design text
    set_str("DesignTitle", design.title)
    set_str("DesignTagline", design.tagline)
    set_str("DesignGenre", design.genre)
    set_str("DesignLoop", design.loop)
    set_str("DesignCurve", design.difficulty_curve)

    # UI strings
    for k, v in (design.ui or {}).items():
        set_str(f"UI_{k}", v)

    # tuning merge: spec can override provider
    merged: Dict[str, Any] = {}
    merged.update(design.tuning or {})
    merged.update(spec.tuning or {})
    for k, v in merged.items():
        set_num(f"Tuning_{k}", v)

    # modules
    for m in design.modules:
        set_num("Module_" + m, 1)

    # JSON blobs for future template engine
    set_str("DesignEnemiesJSON", json.dumps(design.enemies, ensure_ascii=False))
    set_str("DesignShopJSON", json.dumps(design.shop_items, ensure_ascii=False))


def write_design(out_dir: Path, spec: GameSpec, design: Design, image_map: Dict[str, str]) -> None:
    payload = {
        "factory_version": "v3",
        "spec": spec_to_dict(spec),
        "design": {
            "title": design.title,
            "tagline": design.tagline,
            "genre": design.genre,
            "loop": design.loop,
            "difficulty_curve": design.difficulty_curve,
            "modules": design.modules,
            "tuning": design.tuning,
            "enemies": design.enemies,
            "shop_items": design.shop_items,
            "ui": design.ui,
            "meta": design.meta,
        },
        "images": image_map,
    }
    (out_dir / "FACTORY_DESIGN.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "FACTORY_MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
