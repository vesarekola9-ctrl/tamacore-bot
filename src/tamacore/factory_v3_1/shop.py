# type: ignore
"""TamaCore Factory v3.1 - Gold Standard Economy & Balanced Shop Catalog"""

def apply_shop_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        # Valuutat
        {"name": "Shop_Coins", "value": "150"},
        # Ruoat (Hinnat tasapainotettu hyötysuhteen mukaan)
        {"name": "Shop_Price_Strawberry", "value": "8"},
        {"name": "Shop_Price_Apple", "value": "12"},
        {"name": "Shop_Price_Donut", "value": "18"},
        {"name": "Shop_Price_Burger", "value": "30"},
        {"name": "Shop_Price_Pizza", "value": "45"},
        # Juomat
        {"name": "Shop_Price_Water", "value": "8"},
        {"name": "Shop_Price_Juice", "value": "15"},
        {"name": "Shop_Price_Milk", "value": "25"},
        # Hygienia & Terveys
        {"name": "Shop_Price_Soap", "value": "15"},
        {"name": "Shop_Price_Medicine", "value": "40"},
        # Vaatteet & Hatut (Coins)
        {"name": "Shop_Price_PartyHat", "value": "80"},
        {"name": "Shop_Price_PinkBow", "value": "100"},
        {"name": "Shop_Price_TopHat", "value": "150"},
        {"name": "Shop_Price_CatEars", "value": "180"},
        {"name": "Shop_Price_CuteHoodie", "value": "300"},
        {"name": "Shop_Price_Tuxedo", "value": "450"},
        # Premium-tuotteet (Gems 💎)
        {"name": "Shop_GemsPrice_Boba", "value": "10"},
        {"name": "Shop_GemsPrice_IceCream", "value": "10"},
        {"name": "Shop_GemsPrice_Sushi", "value": "15"},
        {"name": "Shop_GemsPrice_Cape", "value": "50"},
        {"name": "Shop_GemsPrice_Crown", "value": "100"},
        {"name": "Shop_GemsPrice_SakuraSkin", "value": "300"},
        {"name": "Shop_GemsPrice_GoldSkin", "value": "500"},
        {"name": "Shop_GemsPrice_RainbowSkin", "value": "600"},
        {"name": "Shop_GemsPrice_GalaxySkin", "value": "750"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
