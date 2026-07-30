# type: ignore
"""TamaCore Factory v3.1 - Shop Runtime"""

def apply_shop_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Shop_Coins", "value": "100"},
        {"name": "Shop_ItemPrice_Apple", "value": "10"},
        {"name": "Shop_ItemPrice_Cake", "value": "25"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            buy_apple_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Shop_Coins", ">=", "GlobalVariable(Shop_ItemPrice_Apple)"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["Inventory_UsedSlots", "<", "GlobalVariable(Inventory_MaxSlots)"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Shop_Coins", "-", "GlobalVariable(Shop_ItemPrice_Apple)"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Food_Apple_Count", "+", "1"]}
                ]
            }
            events.append(buy_apple_event)

    return game_data
