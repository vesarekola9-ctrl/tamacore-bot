"""
TamaCore Factory v3.1 - Evolution Runtime
Geverates pet growth stages and evolution triggers for GDevelop.
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


    return game_data
