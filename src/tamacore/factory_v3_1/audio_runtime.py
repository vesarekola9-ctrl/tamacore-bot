# type: ignore
"""TamaCore Factory v3.1 - Advanced Audio & SFX Events Runtime"""

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

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            
            # Global Master Volume Event
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Audio_Muted", "=", "1"]}
                ],
                "actions": [
                    {"type": {"value": "SetGlobalVolume"}, "parameters": ["0"]}
                ]
            })

            # Feed SFX Event
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "CursorOnObject"}, "parameters": ["Button_Feed", "", "no", ""]},
                    {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                ],
                "actions": [
                    {"type": {"value": "PlaySound"}, "parameters": ["", "assets/sfx_feed.wav", "", "GlobalVariable(Audio_SFXVolume)", "100"]}
                ]
            })

            # Sleep SFX Event
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "CursorOnObject"}, "parameters": ["Button_Sleep", "", "no", ""]},
                    {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                ],
                "actions": [
                    {"type": {"value": "PlaySound"}, "parameters": ["", "assets/sfx_sleep.wav", "", "GlobalVariable(Audio_SFXVolume)", "100"]}
                ]
            })

    return game_data
