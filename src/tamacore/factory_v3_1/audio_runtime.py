# type: ignore
"""TamaCore Factory v3.1 - Audio Runtime"""
def apply_audio_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Audio_MusicVolume", "value": "100"},
        {"name": "Audio_SFXVolume", "value": "100"},
        {"name": "Audio_Muted", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
