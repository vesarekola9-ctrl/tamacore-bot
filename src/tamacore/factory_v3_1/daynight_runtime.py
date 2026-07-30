# type: ignore
"""TamaCore Factory v3.1 - Day & Night Cycle System"""

def apply_daynight_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "World_IsNight", "value": "0"},
        {"name": "World_Weather", "value": "Sunny"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
