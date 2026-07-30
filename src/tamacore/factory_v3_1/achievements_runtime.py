"""
TamaCore Factory v3.1 - Achievements Runtime
Geverates achievement tracking variables and unlock events for GDevelop.
"""

def apply_achievements_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    achievement_variables = [
        {"name": "Ach_FirstFeed_Unlocked", "value": "0"},
        {"name": "Ach_Collector_Unlocked", "value": "0"},
        {name": "Ach_MaxLevel_Unlocked", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for ach_var in achievement_variables:
        if ach_var["name"] not in existing_names:
            game_data["globalVariables"].append(ach_var)

    return game_data
