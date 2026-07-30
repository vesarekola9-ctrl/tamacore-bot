# type: ignore
"""TamaCore Factory v3.1 - Photo Album & Milestones System"""

def apply_album_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Album_EggUnlocked", "value": "1"},
        {"name": "Album_Stage1Unlocked", "value": "0"},
        {"name": "Album_Stage2Unlocked", "value": "0"},
        {"name": "Album_Stage3Unlocked", "value": "0"},
        {"name": "Album_Stage4Unlocked", "value": "0"},
        {"name": "Album_UltimateUnlocked", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
