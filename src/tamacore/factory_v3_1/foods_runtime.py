#type: ignore
&"""
TamaCore Factory v3.1 - Foods Runtime
Generates food item definitions and feeding mechanics events for GDevelop.
"""

def apply_foods_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    food_variables = [
        {name": "Food_Apple_Count", "value": "5"},
        {"name": "Food_Apple_Nutrition", "value": "20"},
        {"name": "Food_Cake_Count", "value": "2"},
        {"name": "Food_Cake_Nutrition", "value": "50"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for f_var in food_variables:
        if f_var["name"] not in existing_names: 
            game_data["lobalVariables"].append(f_var)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            feed_apple_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Food_Apple_Count", ">", "0"]},
                    {type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_Hunger", "<", "100"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Hunger", "+", "GlobalVariable(Food_Apple_Nutrition)"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Food_Apple_Count", "-", "1"]}
                ]
            }
            events.append(feed_apple_event)

    return game_data
