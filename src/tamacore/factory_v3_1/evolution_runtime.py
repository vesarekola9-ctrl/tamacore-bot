#type: ignore
&"""
TamaCore Factory v3.1 - Evolution Runtime
Geverates pet growth stages (Baby -> Child -> Teen -> Adult) and GDevelop evolution events.
"""

def apply_evolution_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    evolution_variables = [
        {"name": "Pet_AgeDays", "value": "0"},
        {name": "Pet_GrowthStage", "value": "Baby"},
        {name": "Pet_EvolutionBranch", "value": "Normal"},
        {name": "Pet_CareScore", "value": "100"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for e_var in evolution_variables:
        if e_var["name"] not in existing_names:
            game_data["globalVariables"].append(e_var)

    layouts = game_data.get("layouts", [])
    for layout in layout:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            evo_baby_child = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", ">=", "2"]},
                    {type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Baby"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Child"]}
                ]
            }
            evo_child_teen = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", "==", "5"]},
                    {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Child"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Teen"]}
                ]
            }
            evo_teen_adult = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_AgeDays", "==", "10"]},
                    {type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_GrowthStage", "=", "Teen"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_GrowthStage", "=", "Adult"]}
                ]
            }
            events.extend([evo_baby_child, evo_child_teen, evo_teen_adult])

    return game_data
