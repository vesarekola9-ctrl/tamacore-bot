# type: ignore
"""TamaCore Factory v3.1 - Quests Runtime"""

def apply_quests_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Quest_FeedCount", "value": "0"},
        {"name": "Quest_FeedTarget", "value": "3"},
        {"name": "Quest_Completed", "value": "0"},
        {"name": "Quest_RewardCoins", "value": "50"}
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
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Quest_FeedCount", ">=", "GlobalVariable(Quest_FeedTarget)"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Quest_Completed", "=", "0"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Quest_Completed", "=", "1"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Shop_Coins", "+", "GlobalVariable(Quest_RewardCoins)"]}
                ]
            })

    return game_data
