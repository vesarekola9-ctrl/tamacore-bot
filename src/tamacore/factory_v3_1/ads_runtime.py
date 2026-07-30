# type: ignore
"""TamaCore Factory v3.1 - Ads Runtime"""
def apply_ads_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Ads_RewardedWatchCount", "value": "0"},
        {"name": "Ads_AdFreeActive", "value": "0"},
        {"name": "Ads_LastAdTimestamp", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
