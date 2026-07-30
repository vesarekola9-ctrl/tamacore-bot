# type: ignore
"""TamaCore Factory v3.1 - Achievements Runtime"""
def apply_achievements_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Ach_FirstFeed_Unlocked", "value": "0"},
        {"name": "Ach_Collector_Unlocked", "value": "0"},
        {"name": "Ach_MaxLevel_Unlocked", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
