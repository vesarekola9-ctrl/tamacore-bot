# type: ignore
"""TamaCore Factory v3.1 - Settings Runtime"""
def apply_settings_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Setting_Language", "value": "fi"},
        {"name": "Setting_NotificationsEnabled", "value": "1"},
        {"name": "Setting_FPSLimit", "value": "60"},
        {"name": "Setting_VibrationEnabled", "value": "1"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
