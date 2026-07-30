# type: ignore
"""TamaCore Factory v3.1 - Extended Wardrobe & Cosmetics Runtime"""

def apply_cosmetics_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Cosmetic_EquippedHat", "value": "None"},
        {"name": "Cosmetic_EquippedOutfit", "value": "None"},
        {"name": "Cosmetic_EquippedSkin", "value": "PinkFluff"},
        {"name": "Cosmetic_Has_TopHat", "value": "0"},
        {"name": "Cosmetic_Has_PinkBow", "value": "0"},
        {"name": "Cosmetic_Has_Crown", "value": "0"},
        {"name": "Cosmetic_Has_Hoodie", "value": "0"},
        {"name": "Cosmetic_Has_RainbowSkin", "value": "0"},
        {"name": "Cosmetic_Has_Halo", "value": "0"},
        {"name": "Cosmetic_Has_420Glasses", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
