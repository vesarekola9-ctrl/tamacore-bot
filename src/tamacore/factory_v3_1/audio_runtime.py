"""
TamaCore Factory v3.1 - Audio Runtime
Generates audio settings and global sound variables for GDevelop.
"""

def apply_audio_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    audio_variables = [
        {"name": "Audio_MusicVolume", "value": "100"},
        {"name": "Audio_SFXVolume", "value": "100"},
        {"name": "Audio_Muted", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for a_var in audio_variables:
        if a_var["name"] not in existing_names:
            game_data["lobalVariables"].append(a_var)

    return game_data
