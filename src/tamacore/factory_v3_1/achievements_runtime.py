# type: ignore
"""TamaCore Factory v3.1 - Achievements Runtime"""

def apply_achievements_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Ach_FirstFeed_Unlocked", "value": "0"},
        {"name": "Ach_Collector_Unlocked", "value": "0"},
        {"name": "Ach_MaxLevel_Unlocked", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Food_Apple_Count", "<", "5"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Ach_FirstFeed_Unlocked", "=", "0"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Ach_FirstFeed_Unlocked", "=", "1"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Shop_Coins", "+", "20"]}
                ]
            })

    return game_data
