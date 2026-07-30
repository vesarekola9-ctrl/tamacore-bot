# type: ignore
"""TamaCore Factory v3.1 - Social Friend Visit System"""

def apply_social_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Social_FriendCode", "value": "TAMA-9982"},
        {"name": "Social_VisitedFriendID", "value": ""},
        {"name": "Social_PettedFriendPet", "value": "0"},
        {"name": "Social_GiftsSentCount", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
