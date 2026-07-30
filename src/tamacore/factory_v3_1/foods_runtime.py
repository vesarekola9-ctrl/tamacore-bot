# type: ignore
"""TamaCore Factory v3.1 - Foods Runtime"""
def apply_foods_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Food_Apple_Count", "value": "5"},
        {"name": "Food_Apple_Nutrition", "value": "20"},
        {"name": "Food_Cake_Count", "value": "2"},
        {"name": "Food_Cake_Nutrition", "value": "50"}
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
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Food_Apple_Count", ">", "0"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_Hunger", "<", "100"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Hunger", "+", "GlobalVariable(Food_Apple_Nutrition)"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Food_Apple_Count", "-", "1"]}
                ]
            })
    return game_data
