# type: ignore
"""TamaCore Factory v3.1 - Extended Home Decor System"""

def apply_home_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Home_Wallpaper", "value": "PastelPink"},
        {"name": "Home_Flooring", "value": "Wood"},
        {"name": "Home_EquippedBed", "value": "CozyBed"},
        {"name": "Home_EquippedPlant", "value": "BasicPlant"},
        {"name": "Home_EquippedDesk", "value": "None"},
        {"name": "Home_EquippedLamp", "value": "None"},
        # Huonekalujen omistus
        {"name": "Home_Has_CozyBed", "value": "1"},
        {"name": "Home_Has_PrincessBed", "value": "0"},
        {"name": "Home_Has_BasicPlant", "value": "1"},
        {"name": "Home_Has_Cactus", "value": "0"},
        {"name": "Home_Has_Bonsai", "value": "0"},
        {"name": "Home_Has_Mushroom", "value": "0"},
        {"name": "Home_Has_PastelSofa", "value": "0"},
        {"name": "Home_Has_GamingDesk", "value": "0"},
        {"name": "Home_Has_Bookcase", "value": "0"},
        {"name": "Home_Has_FloorLamp", "value": "0"},
        {"name": "Home_Has_StarryWallpaper", "value": "0"},
        {"name": "Home_Has_PlushRug", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
