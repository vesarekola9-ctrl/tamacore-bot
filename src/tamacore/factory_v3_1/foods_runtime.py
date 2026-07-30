# type: ignore
"""TamaCore Factory v3.1 - Extended Foods & Drinks Catalog"""

def apply_foods_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        # Ruoat
        {"name": "Food_Apple_Count", "value": "5"},
        {"name": "Food_Cake_Count", "value": "2"},
        {"name": "Food_Pizza_Count", "value": "1"},
        {"name": "Food_IceCream_Count", "value": "0"},
        {"name": "Food_Donut_Count", "value": "3"},
        {"name": "Food_Burger_Count", "value": "0"},
        {"name": "Food_Sushi_Count", "value": "0"},
        {"name": "Food_Strawberry_Count", "value": "4"},
        {"name": "Food_Pancake_Count", "value": "1"},
        {"name": "Food_Cookie_Count", "value": "5"},
        # Juomat
        {"name": "Drink_Water_Count", "value": "5"},
        {"name": "Drink_Milk_Count", "value": "2"},
        {"name": "Drink_Boba_Count", "value": "0"},
        {"name": "Drink_Juice_Count", "value": "3"},
        {"name": "Drink_Soda_Count", "value": "1"},
        {"name": "Drink_Cocoa_Count", "value": "0"},
        {"name": "Drink_Coffee_Count", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
