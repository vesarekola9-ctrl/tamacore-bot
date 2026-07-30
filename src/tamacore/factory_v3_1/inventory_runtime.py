# type: ignore
"""TamaCore Factory v3.1 - Inventory Runtime"""
def apply_inventory_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Inventory_MaxSlots", "value": "20"},
        {"name": "Inventory_UsedSlots", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
