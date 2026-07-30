# type: ignore
"""TamaCore Factory v3.1 - v3_2 Patch"""
def apply_v3_2_patch(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [{"name": "Patch_v3_2_Applied", "value": "1"}]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
