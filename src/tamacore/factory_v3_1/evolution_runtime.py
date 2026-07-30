# type: ignore
"""TamaCore Factory v3.1 - Evolution Runtime"""
def apply_evolution_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Pet_AgeDays", "value": "0"},
        {"name": "Pet_GrowthStage", "value": "Baby"},
        {"name": "Pet_EvolutionBranch", "value": "Normal"},
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
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "2"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Baby"]}
                    ],
                    "actions": [
                        {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Child"]}
                    ]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", "==", "5"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Child"]}
                    ],
                    "actions": [
                        {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Teen"]}
                    ]
                },
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", "==", "10"]},
                        {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Teen"]}
                    ],
                    "actions": [
                        {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Adult"]}
                    ]
                }
            ])
    return game_data
