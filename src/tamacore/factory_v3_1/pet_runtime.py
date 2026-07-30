# type: ignore
"""TamaCore Factory v3.1 - Pet Runtime"""
def apply_pet_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Pet_Name", "value": "Tama"},
        {"name": "Pet_Hunger", "value": "100"},
        {"name": "Pet_Energy", "value": "100"},
        {"name": "Pet_Happiness", "value": "100"},
        {"name": "Pet_Health", "value": "100"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
