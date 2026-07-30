# type: ignore
"""TamaCore Factory v3.1 - Sickness & Medicine System"""

def apply_sickness_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Pet_IsSick", "value": "0"},
        {"name": "Medicine_Count", "value": "2"},
        {"name": "Shop_Price_Medicine", "value": "30"}
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
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Pet_Hygiene", "<=", "20"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_IsSick", "=", "1"]}
                ]
            })

    return game_data
