"""
TamaCore Factory v3.1 - Minigames Runtime
Geverates minigame score tracking variables and reward events for GDevelop.
"""

def apply_minigames_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    minigame_variables = [
        {"name": "Minigame_HighScore", "value": "0"},
        {"name": "Minigame_LastScore", "value": "0"},
        {"name": "Minigame_CoinsEarned", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for m_var in minigame_variables:
        if m_var["name"] not in existing_names:
            game_data["lobalVariables"].append(m_var)

    return game_data
