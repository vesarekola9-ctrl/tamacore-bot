"""
TamaCore Factory v3.1 - Quests Runtime
Generates quest tracking variables, event logic, and rewards for GDevelop.
"""


def apply_quests_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    quest_variables = [
        {"name": "Quest_FeedCount", "value": "0"},
        {"name": "Quest_FeedTarget", "value": "3"},
        {"name": "Quest_FeedReward", "value": "50"},
        {"name": "Quest_FeedCompleted", "value": "0"},
        {"name": "Quest_PlayCount", "value": "0"},
        {"name": "Quest_PlayTarget", "value": "2"},
        {"name": "Quest_PlayReward", "value": "75"},
        {"name": "Quest_PlayCompleted", "value": "0"},
        {"name": "PlayerCoins", "value": "100"},
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for q_var in quest_variables:
        if q_var["name"] not in existing_names:
            game_data["globalVariables"].append(q_var)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])

            quest_feed_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": [
                            "Quest_FeedCount",
                            ">=",
                            "GlobalVariable(Quest_FeedTarget)",
                        ],
                    },
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": ["Quest_FeedCompleted", "=", "0"],
                    },
                ],
                "actions": [
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": [
                            "PlayerCoins",
                            "+",
                            "GlobalVariable(Quest_FeedReward)",
                        ],
                    },
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": ["Quest_FeedCompleted", "=", "1"],
                    },
                ],
            }

            quest_play_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": [
                            "Quest_PlayCount",
                            ">=",
                            "GlobalVariable(Quest_PlayTarget)",
                        ],
                    },
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": ["Quest_PlayCompleted", "=", "0"],
                    },
                ],
                "actions": [
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": [
                            "PlayerCoins",
                            "+",
                            "GlobalVariable(Quest_PlayReward)",
                        ],
                    },
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": ["Quest_PlayCompleted", "=", "1"],
                    },
                ],
            }

            events.append(quest_feed_event)
            events.append(quest_play_event)

    return game_data
