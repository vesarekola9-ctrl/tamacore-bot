# type: ignore
"""TamaCore Factory v3.1 - Hygiene & Bathing System"""

def apply_hygiene_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Pet_Hygiene", "value": "100"},
        {"name": "Soap_Count", "value": "5"},
        {"name": "Shop_Price_Soap", "value": "15"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            objects = layout.setdefault("objects", [])
            instances = layout.setdefault("instances", [])
            existing_objs = {obj.get("name") for obj in objects}
            existing_insts = {inst.get("name") for inst in instances}

            if "Button_Wash" not in existing_objs:
                objects.append({
                    "name": "Button_Wash",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "[ PESE ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 135, "g": 206, "b": 250}
                })

            if "Button_Wash" not in existing_insts:
                instances.append({"name": "Button_Wash", "x": 40, "y": 850, "angle": 0, "zOrder": 10, "layer": "", "customSize": False})

            events = layout.setdefault("events", [])
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "CursorOnObject"}, "parameters": ["Button_Wash", "", "no", ""]},
                    {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Hygiene", "=", "100"]}
                ]
            })

    return game_data
