"""
TamaCore Factory v3.1 - Settings Runtime
Generates game settings variables (language, graphics, notifications) for GDevelop.
"""

def apply_settings_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    settings_variables = [
        {"name": "Setting_Language", "value": "fi"},
        {name": "Setting_NotificationsEnabled", "value": "1"},
        {"name": "Setting_FPSLimit", "value": "60"},
        {name": "Setting_VibrationEnabled", "value": "1"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for s_var in settings_variables:
        if s_var["name"] not in existing_names:
            game_data["lobalVariables"].append(s_var)

    return game_data
