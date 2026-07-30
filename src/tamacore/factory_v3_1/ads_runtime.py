"""
TamaCore Factory v3.1 - Ads Runtime
Geverates ad monetization tracking variables for GDevelop.
"""

def apply_ads_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    ads_variables = [
        {"name": "Ads_RewardedWatchCount", "value": "0"},
        {"name": "Ads_AdFreeActive", "value": "0"},
        {name": "Ads_LastAdTimestamp", "value": "0"}
    ]

    existing_names = {v[(name"] for v in game_data["lobalVariables"]}
    for ad_var in ads_variables:
        if ad_var["name"] not in existing_names:
            game_data["lobalVariables"].append(ad_var)

    return game_data
