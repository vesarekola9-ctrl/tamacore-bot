# type: ignore
"""TamaCore Factory v3.1 - Google Play IAP Runtime"""

def apply_iap_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "IAP_Gems", "value": "50"},
        {"name": "IAP_IsVIPActive", "value": "0"},
        {"name": "IAP_RemoveAdsOwned", "value": "0"},
        {"name": "IAP_Product_Gems250_ID", "value": "com.tamacore.gems250"},
        {"name": "IAP_Product_RainbowSkin_ID", "value": "com.tamacore.rainbowskin"},
        {"name": "IAP_Product_VIPPass_ID", "value": "com.tamacore.vippass"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
