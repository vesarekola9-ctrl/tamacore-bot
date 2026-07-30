# type: ignore
"""TamaCore Factory v3.1 - Seasonal Events & Limited Items System"""

def apply_seasonal_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Seasonal_ActiveEvent", "value": "Spring"}, # Spring, Halloween, Christmas
        {"name": "Seasonal_HasPumpkinHat", "value": "0"},
        {"name": "Seasonal_HasSantaHat", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
