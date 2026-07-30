# type: ignore
"""TamaCore Factory v3.1 - Concept Shop Runtime"""

def apply_shop_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Shop_Coins", "value": "600"},
        {"name": "Shop_Price_RainbowSkin", "value": "600"},
        {"name": "Shop_Price_Halo", "value": "400"},
        {"name": "Shop_Price_420Glasses", "value": "150"},
        {"name": "Shop_Price_CoolHat", "value": "100"},
        {"name": "Shop_Price_MemeFrog", "value": "150"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
