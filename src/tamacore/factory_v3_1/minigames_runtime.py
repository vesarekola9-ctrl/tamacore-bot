# type: ignore
"""TamaCore Factory v3.1 - Minigames Runtime"""

def apply_minigames_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Minigame_HighScore", "value": "0"},
        {"name": "Minigame_LastScore", "value": "0"},
        {"name": "Minigame_CoinsEarned", "value": "0"},
        {"name": "Minigame_IsActive", "value": "0"},
        {"name": "Minigame_Timer", "value": "30"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            minigame_end_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Minigame_IsActive", "=", "1"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Minigame_Timer", "<=", "0"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Minigame_IsActive", "=", "0"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Shop_Coins", "+", "GlobalVariable(Minigame_CoinsEarned)"]}
                ]
            }
            events.append(minigame_end_event)

    return game_data
