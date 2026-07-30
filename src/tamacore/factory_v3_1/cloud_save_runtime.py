# type: ignore
"""TamaCore Factory v3.1 - Cloud Save Runtime"""
def apply_cloud_save_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "CloudSave_UserID", "value": ""},
        {"name": "CloudSave_LastSyncTimestamp", "value": "0"},
        {"name": "CloudSave_SyncStatus", "value": "idle"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
