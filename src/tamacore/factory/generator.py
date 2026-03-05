from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import read_json, write_json
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
    version="0.2.0",
    theme="neon",
    difficulty="normal",
    seed=1337,
    prompt="Fast top-down arcade with clean mobile controls and upgrades.",
    provider="rules-v2",
    modules=["collect", "shop", "settings", "mobile_ui"],
    tuning={
        "hp_start": 3,
        "enemy_base_speed": 70,
        "enemy_speed_per_score": 4,
        "enemy_speed_cap": 260,
        "pickup_spawn_seconds": 2.4,
        "enemy_spawn_seconds": 3.5,
    },
)


def generate_game(spec_path: Path, out_dir: Path, template_dir: Path, seed_assets_dir: Path) -> None:
    ensure_template_exists(template_dir)

    spec = load_spec(spec_path)
    design = generate_design(spec)

    # 1) Copy template to out_dir
    if out_dir.exists():
        if (out_dir / "game.json").exists():
            shutil.rmtree(out_dir)
        else:
            raise RuntimeError(
                f"Output folder exists but doesn't look like a generated game: {out_dir}\n"
                "Pick another --out or remove it."
            )
    copy_template(template_dir, out_dir)

    # 2) Assets: seed -> themed variants -> copy into out_dir/assets/generated
    seed_dir = pick_seed_dir(seed_assets_dir, template_dir)
    themed_assets_dir = create_themed_assets(seed_dir, out_dir, spec, design)

    # 3) Patch resources + base template patcher
    image_map = copy_assets_into_game(themed_assets_dir, out_dir)
    game_json = out_dir / "game.json"
    patch_project(game_json, image_map)

    # 4) Patch metadata + factory globals + write DESIGN json
    project = read_json(game_json)
    patch_metadata(project, spec, design)
    patch_factory_variables(project, spec, design)
    write_json(game_json, project)

    write_manifest(out_dir, spec, design, image_map)
    write_design(out_dir, design)

    print("[OK] Factory v2 generated game at:", out_dir)
    print("[OK] Open in GDevelop:", out_dir / "game.json")
    print("[OK] Design file:", out_dir / "FACTORY_DESIGN.json")


def generate_design(spec: GameSpec) -> Design:
    if spec.provider == "rules-v2":
        provider = RulesV2Provider()
        return provider.generate(spec_to_dict(spec))

    # Future: openai/local-llm providers (v2.1+)
    raise ValueError(
        f"Unknown provider: {spec.provider}\n"
        "Use: rules-v2 (default)"
    )


def load_spec(spec_path: Path) -> GameSpec:
    if not spec_path.exists():
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(spec_to_dict(DEFAULT_SPEC), f, ensure_ascii=False, indent=2)
        print("[i] Spec missing -> created default at:", spec_path)

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
    if seed_assets_dir.exists():
        return seed_assets_dir
    tmpl_gen = template_dir / "assets" / "generated"
    if tmpl_gen.exists():
        return tmpl_gen
    raise FileNotFoundError(
        "No seed assets found. Create 'assets/' with images or ensure template has templates/gdevelop_template/assets/generated."
    )


def create_themed_assets(seed_dir: Path, out_dir: Path, spec: GameSpec, design: Design) -> Path:
    """
    v2: still no pixel processing (that comes later with image_gen),
    but we export a richer set of canonical names for template use.
    """
    tmp = out_dir / ".factory_assets"
    tmp.mkdir(parents=True, exist_ok=True)

    bg = find_first(seed_dir, ["bg.png", "background.png", "bg.jpg", "bg.webp"]) or first_image(seed_dir)
    player = find_first(seed_dir, ["player.png", "hero.png", "character.png"]) or first_image(seed_dir)
    coin = find_first(seed_dir, ["coin.png", "pickup.png", "gem.png"]) or first_image(seed_dir)

    if bg is None or player is None or coin is None:
        raise FileNotFoundError(f"Seed assets folder has no images: {seed_dir}")

    # Enemy assets: reuse player/coin as placeholders in v2
    enemy = coin
    ui_btn = coin

    copies: List[Tuple[Path, str]] = [
        (bg, "bg.png"),
        (player, "player.png"),
        (coin, "coin.png"),
        (enemy, "enemy.png"),
        (ui_btn, "ui_button.png"),
        # themed variants
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
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
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


def patch_factory_variables(project: Dict[str, Any], spec: GameSpec, design: Design) -> None:
    """
    v2: Store the entire design into GLOBAL variables so template events/UI can read it.
    We keep it simple: strings + numbers + JSON blobs as strings.
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

    def upsert_num(name: str, value: Any) -> None:
        upsert(name, "number", str(value))

    def upsert_str(name: str, value: str) -> None:
        upsert(name, "string", value)

    # Core identity
    upsert_str("FactoryProvider", design.meta.get("provider", spec.provider))
    upsert_str("FactoryTheme", spec.theme)
    upsert_str("FactoryDifficulty", spec.difficulty)
    upsert_num("FactorySeed", spec.seed)

    # Design text
    upsert_str("DesignTitle", design.title)
    upsert_str("DesignTagline", design.tagline)
    upsert_str("DesignGenre", design.genre)
    upsert_str("DesignLoop", design.loop)
    upsert_str("DesignCurve", design.difficulty_curve)

    # UI strings (flatten)
    for k, v in design.ui.items():
        upsert_str(f"UI_{k}", str(v))

    # Tuning: provider tuning overrides spec tuning (spec can still override by editing file)
    merged_tuning: Dict[str, Any] = {}
    merged_tuning.update(spec.tuning or {})
    merged_tuning.update(design.tuning or {})
    for k, v in merged_tuning.items():
        key = f"Tuning_{k}"
        try:
            upsert_num(key, float(v))
        except Exception:
            upsert_str(key, str(v))

    # Modules flags
    for m in design.modules:
        upsert_num("Module_" + m, 1)

    # Enemies + shop as JSON strings (template can parse in JS events later if needed)
    upsert_str("DesignEnemiesJSON", json.dumps(design.enemies, ensure_ascii=False))
    upsert_str("DesignShopJSON", json.dumps(design.shop_items, ensure_ascii=False))


def write_manifest(out_dir: Path, spec: GameSpec, design: Design, image_map: Dict[str, str]) -> None:
    mf = {
        "factory_version": "v2",
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
    (out_dir / "FACTORY_MANIFEST.json").write_text(json.dumps(mf, ensure_ascii=False, indent=2), encoding="utf-8")


def write_design(out_dir: Path, design: Design) -> None:
    d = {
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
    }
    (out_dir / "FACTORY_DESIGN.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
