# type: ignore
"""TamaCore Factory v3.1 - Fluffy Jump Minigame System"""

def apply_jumpgame_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "JumpGame_HighScore", "value": "0"},
        {"name": "JumpGame_IsActive", "value": "0"},
        {"name": "JumpGame_PlayerY", "value": "0"},
        {"name": "JumpGame_CoinsEarned", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
