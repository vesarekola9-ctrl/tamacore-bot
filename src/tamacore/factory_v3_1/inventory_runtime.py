"""
TamaCore Factory v3.1 - Inventory Runtime
Generates inventory tracking structures and item usage events for GDevelop.
"""


def apply_inventory_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    inventory_variables = [
        {"name": "Inventory_SelectedCategory", "value": "Foods"},
        {"name": "Inventory_Slot_0_ID", "value": "apple"},
        {"name": "Inventory_Slot_0_Count", "value": "1"},
        {"name": "Inventory_Slot_1_ID", "value": "none"},
        {"name": "Inventory_Slot_1_Count", "value": "0"},
        {"name": "Inventory_Slot_2_ID", "value": "none"},
        {"name": "Inventory_Slot_2_Count", "value": "0"},
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for inv_var in inventory_variables:
        if inv_var["name"] not in existing_names:
            game_data["globalVariables"].append(inv_var)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])

            use_item_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": ["Inventory_Slot_0_Count", ">", "0"],
                    }
                ],
                "actions": [
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": ["Inventory_Slot_0_Count", "-", "1"],
                    }
                ],
            }

            events.append(use_item_event)

    return game_data
