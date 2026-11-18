"""TamaCore Factory v3.1 - Master Generator with Emotes & Seasonals"""
from .project_properties import apply_project_properties
from .resources_runtime import apply_resources_runtime
from .pet_runtime import apply_pet_runtime
from .save_runtime import apply_save_runtime
from .cosmetics_runtime import apply_cosmetics_runtime
from .foods_runtime import apply_foods_runtime
from .v3_2_patch import apply_v3_2_patch
from .shop import apply_shop_runtime
from .levels import apply_levels_runtime
from .quests_runtime import apply_quests_runtime
from .inventory_runtime import apply_inventory_runtime
from .ui_runtime import apply_ui_runtime
from .audio_runtime import apply_audio_runtime
from .achievements_runtime import apply_achievements_runtime
from .minigames_runtime import apply_minigames_runtime
from .daily_rewards_runtime import apply_daily_rewards_runtime
from .settings_runtime import apply_settings_runtime
from .notifications_runtime import apply_notifications_runtime
from .ads_runtime import apply_ads_runtime
from .analytics_runtime import apply_analytics_runtime
from .cloud_save_runtime import apply_cloud_save_runtime
from .realtime_runtime import apply_realtime_runtime
from .evolution_runtime import apply_evolution_runtime
from .iap_runtime import apply_iap_runtime
from .shop_scene_runtime import apply_shop_scene_runtime
from .home_runtime import apply_home_runtime
from .hygiene_runtime import apply_hygiene_runtime
from .sickness_runtime import apply_sickness_runtime
from .daynight_runtime import apply_daynight_runtime
from .jumpgame_runtime import apply_jumpgame_runtime
from .album_runtime import apply_album_runtime
from .wheel_runtime import apply_wheel_runtime
from .social_runtime import apply_social_runtime
from .emotes_runtime import apply_emotes_runtime
from .seasonal_runtime import apply_seasonal_runtime

def build_game_json(base_game_data: dict) -> dict:
    game_data = base_game_data.copy()

    game_data = apply_project_properties(game_data)
    game_data = apply_resources_runtime(game_data)
    game_data = apply_pet_runtime(game_data)
    game_data = apply_save_runtime(game_data)
    game_data = apply_cosmetics_runtime(game_data)
    game_data = apply_foods_runtime(game_data)
    game_data = apply_v3_2_patch(game_data)
    game_data = apply_shop_runtime(game_data)
    game_data = apply_levels_runtime(game_data)
    game_data = apply_quests_runtime(game_data)
    game_data = apply_inventory_runtime(game_data)
    game_data = apply_ui_runtime(game_data)
    game_data = apply_audio_runtime(game_data)
    game_data = apply_achievements_runtime(game_data)
    game_data = apply_minigames_runtime(game_data)
    game_data = apply_daily_rewards_runtime(game_data)
    game_data = apply_settings_runtime(game_data)
    game_data = apply_notifications_runtime(game_data)
    game_data = apply_ads_runtime(game_data)
    game_data = apply_analytics_runtime(game_data)
    game_data = apply_cloud_save_runtime(game_data)
    game_data = apply_realtime_runtime(game_data)
    game_data = apply_evolution_runtime(game_data)
    game_data = apply_iap_runtime(game_data)
    game_data = apply_shop_scene_runtime(game_data)
    game_data = apply_home_runtime(game_data)
    game_data = apply_hygiene_runtime(game_data)
    game_data = apply_sickness_runtime(game_data)
    game_data = apply_daynight_runtime(game_data)
    game_data = apply_jumpgame_runtime(game_data)
    game_data = apply_album_runtime(game_data)
    game_data = apply_wheel_runtime(game_data)
    game_data = apply_social_runtime(game_data)
    game_data = apply_emotes_runtime(game_data)
    game_data = apply_seasonal_runtime(game_data)

    return game_data



def run_factory_v3_1(
    pack_dir,
    template_dir,
    game_dir,
    with_demo_layout=True,
    enable_v3_2=False,
):
    """Build a GDevelop project while retaining all v3.1 master runtime modules.

    This compatibility entry point restores the CLI import contract.
    """
    from pathlib import Path
    from ..factory_v3.generator import run_factory_v3
    from ..utils import read_json, write_json
    from .schema import load_pack_cfg

    pack_dir = Path(pack_dir)
    template_dir = Path(template_dir)
    game_dir = Path(game_dir)
    cfg = load_pack_cfg(pack_dir)
    raw_pack = read_json(pack_dir / "pack.json")
    if not isinstance(raw_pack, dict):
        raise ValueError("pack.json must contain a JSON object")

    run_factory_v3(
        pack_dir=pack_dir,
        template_dir=template_dir,
        game_dir=game_dir,
        scene_name=cfg.scene,
        seed=cfg.levels.seed,
        with_demo_layout=with_demo_layout,
    )

    game_path = game_dir / "game.json"
    project = read_json(game_path)
    if not isinstance(project, dict):
        raise ValueError("Generated game.json must contain a JSON object")

    # Build the base v3.1 scene before applying optional subsystems.
    from .patch_rules import apply_v3_1_rules
    from .character_builder import apply_character_animations

    layouts = project.get("layouts", [])
    scene = next(
        (item for item in layouts if isinstance(item, dict)
         and item.get("name") == cfg.scene),
        None,
    )
    if scene is None:
        raise ValueError(f"Generated GDevelop scene not found: {cfg.scene}")

    apply_v3_1_rules(project, scene, cfg)
    apply_character_animations(project, scene, game_dir)

    # Preserve every registered v3.1 subsystem.
    project = build_game_json(project)
    if not isinstance(project, dict):
        raise ValueError("Master generator returned an invalid project")

    # Legacy runtime modules use "globalVariables", while GDevelop
    # stores project-wide variables in "variables". Merge without
    # overwriting variables already defined by the project.
    legacy_variables = project.pop("globalVariables", [])
    project_variables = project.setdefault("variables", [])
    if not isinstance(project_variables, list):
        raise ValueError("GDevelop project variables must be a list")
    existing_names = {
        item.get("name") for item in project_variables
        if isinstance(item, dict)
    }
    if isinstance(legacy_variables, list):
        for item in legacy_variables:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not isinstance(name, str) or not name or name in existing_names:
                continue
            value = item.get("value", "0")
            project_variables.append({
                "name": name,
                "type": "number" if str(value).replace(".", "", 1).lstrip("-").isdigit() else "string",
                "value": value,
                "children": [],
            })
            existing_names.add(name)

    write_json(game_path, project)

    manifest_path = game_dir / "FACTORY_MANIFEST.json"
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        manifest = {}
    manifest.update({
        "factory": "v3.2" if enable_v3_2 else "v3.1",
        "pack": {"name": cfg.name, "version": cfg.version, "scene": cfg.scene},
        "masterRuntimeApplied": True,
        "display": raw_pack.get("display", {}),
        "worldBounds": raw_pack.get("worldBounds", {}),
        "camera": raw_pack.get("camera", {}),
        "ui": raw_pack.get("ui", {}),
        "spawns": {
            "coin": raw_pack.get("coinSpawn", {}),
            "enemy": raw_pack.get("enemySpawn", {}),
        },
        "levels": raw_pack.get("levels", {}),
        "shopUpgrades": raw_pack.get("shop", {}).get("upgrades", []),
    })
    write_json(manifest_path, manifest)
    print("[OK] TamaCore master generator output:", game_path)
