# type: ignore
"""TamaCore Factory v3.1 - Save Runtime"""

def apply_save_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Save_AutoSaveEnabled", "value": "1"},
        {"name": "Save_LastSaveTimestamp", "value": "0"},
        {"name": "Save_Version", "value": "3.1"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
