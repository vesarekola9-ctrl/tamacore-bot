# type: ignore
"""TamaCore Factory v3.1 - Quests Runtime"""
def apply_quests_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Quest_FeedCount", "value": "0"},
        {"name": "Quest_FeedTarget", "value": "5"},
        {"name": "Quest_Completed", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
