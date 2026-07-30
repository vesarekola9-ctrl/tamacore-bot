# type: ignore
"""TamaCore Factory v3.1 - Foods Runtime"""

def apply_foods_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Food_Apple_Count", "value": "5"},
        {"name": "Food_Apple_Nutrition", "value": "20"},
        {"name": "Food_Cake_Count", "value": "2"},
        {"name": "Food_Cake_Nutrition", "value": "50"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
