# type: ignore
"""TamaCore Factory v3.1 - Balanced Minigame Economy"""

def apply_minigames_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Minigame_HighScore", "value": "0"},
        {"name": "Minigame_LastScore", "value": "0"},
        {"name": "Minigame_CoinsEarned", "value": "0"},
        {"name": "Minigame_IsActive", "value": "0"},
        {"name": "Minigame_Timer", "value": "30"},
        {"name": "Minigame_CoinMultiplier", "value": "1.5"} # Reilu ja mielekäs palkkio
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
