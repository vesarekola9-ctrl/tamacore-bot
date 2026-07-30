# type: ignore
"""TamaCore Factory v3.1 - Cosmetics & Sprite Overlay Attachment Runtime"""

def apply_cosmetics_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Cosmetic_EquippedHat", "value": "None"},
        {"name": "Cosmetic_EquippedOutfit", "value": "None"},
        {"name": "Cosmetic_EquippedSkin", "value": "PinkFluff"},
        {"name": "Cosmetic_Has_TopHat", "value": "0"},
        {"name": "Cosmetic_Has_PinkBow", "value": "0"},
        {"name": "Cosmetic_Has_Crown", "value": "0"},
        {"name": "Cosmetic_Has_Hoodie", "value": "0"}
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

            # Asuste-objektit
            overlay_objs = [
                {
                    "name": "Pet_HatObject",
                    "type": "Sprite",
                    "variables": [],
                    "behaviors": [],
                    "animations": [{"name": "Default", "directions": [{"timeBetweenFrames": 1.0, "loops": True, "sprites": [{"image": "top_hat.png"}]}]}]
                },
                {
                    "name": "Pet_OutfitObject",
                    "type": "Sprite",
                    "variables": [],
                    "behaviors": [],
                    "animations": [{"name": "Default", "directions": [{"timeBetweenFrames": 1.0, "loops": True, "sprites": [{"image": "hoodie.png"}]}]}]
                }
            ]

            for obj in overlay_objs:
                if obj["name"] not in existing_objs:
                    objects.append(obj)

            overlay_insts = [
                {"name": "Pet_HatObject", "x": 200, "y": 160, "angle": 0, "zOrder": 5, "layer": "", "customSize": True, "width": 48, "height": 48},
                {"name": "Pet_OutfitObject", "x": 200, "y": 230, "angle": 0, "zOrder": 4, "layer": "", "customSize": True, "width": 64, "height": 64}
            ]

            for inst in overlay_insts:
                if inst["name"] not in existing_insts:
                    instances.append(inst)

            events = layout.setdefault("events", [])
            # Kiinnitetään asusteet lemmikin koordinaatteihin
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [],
                "actions": [
                    {"type": {"value": "SetXPosition"}, "parameters": ["Pet_HatObject", "=", "PetObject.X() + 46"]},
                    {"type": {"value": "SetYPosition"}, "parameters": ["Pet_HatObject", "=", "PetObject.Y() - 20"]},
                    {"type": {"value": "SetXPosition"}, "parameters": ["Pet_OutfitObject", "=", "PetObject.X() + 38"]},
                    {"type": {"value": "SetYPosition"}, "parameters": ["Pet_OutfitObject", "=", "PetObject.Y() + 50"]}
                ]
            })

    return game_data
