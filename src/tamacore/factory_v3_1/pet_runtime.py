# type: ignore
"""
TamaCore Factory v3.1 - Pet Runtime
Generates core pet status variables for GDevelop.
"""

def apply_pet_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    pet_variables = [
        {"name": "Pet_Name", "value": "Tama"},
        {"name": "Pet_Hunger", "value": "100"},
        {"name": "Pet_Energy", "value": "100"},
        {"name": "Pet_Happiness", "value": "100"},
        {"name": "Pet_Health", "value": "100"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for p_var in pet_variables:
        if p_var["name"] not in existing_names:
            game_data["globalVariables"].append(p_var)

    return game_data