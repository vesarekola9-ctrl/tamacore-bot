# type: ignore
"""TamaCore Factory v3.1 - Massive Wardrobe Catalog"""

def apply_cosmetics_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        # Slotit
        {"name": "Cosmetic_EquippedHat", "value": "None"},
        {"name": "Cosmetic_EquippedOutfit", "value": "None"},
        {"name": "Cosmetic_EquippedSkin", "value": "PinkFluff"},
        # Hatut
        {"name": "Cosmetic_Has_TopHat", "value": "0"},
        {"name": "Cosmetic_Has_PinkBow", "value": "0"},
        {"name": "Cosmetic_Has_Crown", "value": "0"},
        {"name": "Cosmetic_Has_PartyHat", "value": "0"},
        {"name": "Cosmetic_Has_CatEars", "value": "0"},
        {"name": "Cosmetic_Has_PirateHat", "value": "0"},
        {"name": "Cosmetic_Has_WizardHat", "value": "0"},
        {"name": "Cosmetic_Has_ChefHat", "value": "0"},
        {"name": "Cosmetic_Has_Glasses", "value": "0"},
        {"name": "Cosmetic_Has_Sunglasses", "value": "0"},
        # Vaatteet
        {"name": "Cosmetic_Has_Hoodie", "value": "0"},
        {"name": "Cosmetic_Has_Tuxedo", "value": "0"},
        {"name": "Cosmetic_Has_Dress", "value": "0"},
        {"name": "Cosmetic_Has_Cape", "value": "0"},
        {"name": "Cosmetic_Has_Sailor", "value": "0"},
        {"name": "Cosmetic_Has_Pajamas", "value": "0"},
        # Skinit
        {"name": "Cosmetic_Has_RainbowSkin", "value": "0"},
        {"name": "Cosmetic_Has_GoldSkin", "value": "0"},
        {"name": "Cosmetic_Has_GalaxySkin", "value": "0"},
        {"name": "Cosmetic_Has_MatchaSkin", "value": "0"},
        {"name": "Cosmetic_Has_BlackSkin", "value": "0"},
        {"name": "Cosmetic_Has_SakuraSkin", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
