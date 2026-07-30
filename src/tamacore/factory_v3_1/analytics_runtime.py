# type: ignore
"""TamaCore Factory v3.1 - Analytics Runtime"""
def apply_analytics_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Analytics_SessionCount", "value": "0"},
        {"name": "Analytics_TotalPlayTime", "value": "0"},
        {"name": "Analytics_FirstLaunchDate", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
