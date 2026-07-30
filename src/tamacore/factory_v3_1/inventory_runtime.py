# type: ignore
"""TamaCore Factory v3.1 - Inventory Runtime"""

def apply_inventory_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Inventory_MaxSlots", "value": "20"},
        {"name": "Inventory_UsedSlots", "value": "0"},
        {"name": "Inventory_SelectedSlot", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            update_inventory_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [],
                "actions": [
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": [
                            "Inventory_UsedSlots",
                            "=",
                            "GlobalVariable(Food_Apple_Count) + GlobalVariable(Food_Cake_Count)"
                        ]
                    }
                ]
            }
            events.append(update_inventory_event)

    return game_data
