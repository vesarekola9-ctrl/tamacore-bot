# type: ignore
"""TamaCore Factory v3.1 - Levels Runtime"""
def apply_levels_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Level_Current", "value": "1"},
        {"name": "Level_XP", "value": "0"},
        {"name": "Level_XPToNext", "value": "100"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
