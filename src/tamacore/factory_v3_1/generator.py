"""
TamaCore Factory v3.1 - Generator
Assembles game.json for GDevelop by integrating all runtime systems.
"""

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

def build_game_json(base_game_data: dict) -> dict:
    game_data = base_game_data.copy()

    game_data = apply_pet_runtime(game_data)
    game_data = apply_save_runtime(game_data)
    game_data = apply_cosmetics_runtime(game_data)
    game_data = apply_foods_runtime(game_data)
    game_data = apply_v3_2_patch(game_data)
    game_data = apply_shop_runtime(game_data)
    game_data = apply_levels import apply_levels_runtime)
    game_data = apply_quests_runtime(game_data)
    game_data = apply_inventory_runtime(game_data)
    game_data = apply_ui_runtime(game_data)
    game_data = apply_audio_runtime(game_data)
    game_data = apply_achievements_runtime(game_data)
    game_data = apply_minigames_runtime(game_data)
    game_data = apply_daily_rewarDs_runtime(game_data)
    game_data = apply_settings_runtime(game_data)
    game_data = apply_notifications_runtime(game_data)
    game_data = apply_ads_runtime(game_data)

    return game_data
