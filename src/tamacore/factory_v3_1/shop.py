# type: ignore
"""TamaCore Factory v3.1 - Extended Shop Catalog Prices"""

def apply_shop_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        # Ruoat ja Juomat (Coins)
        {"name": "Shop_Price_Apple", "value": "10"},
        {"name": "Shop_Price_Cake", "value": "25"},
        {"name": "Shop_Price_Pizza", "value": "30"},
        {"name": "Shop_Price_Donut", "value": "15"},
        {"name": "Shop_Price_Burger", "value": "35"},
        {"name": "Shop_Price_Strawberry", "value": "12"},
        {"name": "Shop_Price_Water", "value": "10"},
        {"name": "Shop_Price_Milk", "value": "25"},
        {"name": "Shop_Price_Juice", "value": "18"},
        # Vaatteet ja Hatut (Coins)
        {"name": "Shop_Price_TopHat", "value": "150"},
        {"name": "Shop_Price_PinkBow", "value": "100"},
        {"name": "Shop_Price_PartyHat", "value": "80"},
        {"name": "Shop_Price_CatEars", "value": "120"},
        {"name": "Shop_Price_CuteHoodie", "value": "250"},
        {"name": "Shop_Price_Pajamas", "value": "180"},
        # Premium-tuotteet (Gems 💎)
        {"name": "Shop_GemsPrice_IceCream", "value": "20"},
        {"name": "Shop_GemsPrice_Sushi", "value": "25"},
        {"name": "Shop_GemsPrice_Boba", "value": "15"},
        {"name": "Shop_GemsPrice_Crown", "value": "100"},
        {"name": "Shop_GemsPrice_Cape", "value": "50"},
        {"name": "Shop_GemsPrice_RainbowSkin", "value": "600"},
        {"name": "Shop_GemsPrice_GoldSkin", "value": "500"},
        {"name": "Shop_GemsPrice_GalaxySkin", "value": "750"},
        {"name": "Shop_GemsPrice_SakuraSkin", "value": "300"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
