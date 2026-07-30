# type: ignore
"""TamaCore Factory v3.1 - Evolution Runtime (6 Stages)"""

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

    return game_data
