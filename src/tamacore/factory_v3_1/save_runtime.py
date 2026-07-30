# type: ignore
"""
TamaCore Factory v3.1 - Save Runtime
Generates game save variables for GDevelop.
"""

def apply_save_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    save_variables = [
        {"name": "Save_AutoSaveEnabled", "value": "1"},
        {"name": "Save_LastSaveTimestamp", "value": "0"},
        {"name": "Save_Version", "value": "3.1"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for s_var in save_variables:
        if s_var["name"] not in existing_names:
            game_data["globalVariables"].append(s_var)

    return game_data