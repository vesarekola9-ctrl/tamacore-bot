# type: ignore
"""TamaCore Factory v3.1 - Concept Evolution Runtime (6 Stages)"""

def apply_evolution_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Pet_AgeDays", "value": "0"},
        {"name": "Pet_GrowthStage", "value": "Egg"},
        {"name": "Pet_EvolutionBranch", "value": "Ultimate"},
        {"name": "Pet_CareScore", "value": "100"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            events.extend([
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "1"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Egg"]}
                    ],
                    "actions": [{"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Stage 1"]}]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "3"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Stage 1"]}
                    ],
                    "actions": [{"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Stage 2"]}]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "6"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Stage 2"]}
                    ],
                    "actions": [{"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Stage 3"]}]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "10"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Stage 3"]}
                    ],
                    "actions": [{"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Stage 4"]}]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "15"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Stage 4"]}
                    ],
                    "actions": [{"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Ultimate"]}]
                }
            ])

    return game_data
