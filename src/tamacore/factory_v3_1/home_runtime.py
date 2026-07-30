# type: ignore
"""TamaCore Factory v3.1 - Home & Room Decor System"""

def apply_home_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Home_Wallpaper", "value": "PastelPink"},
        {"name": "Home_Flooring", "value": "Wood"},
        {"name": "Home_EquippedBed", "value": "CozyBed"},
        {"name": "Home_EquippedPlant", "value": "BasicPlant"},
        {"name": "Home_EquippedFurniture", "value": "None"},
        {"name": "Home_Has_CozyBed", "value": "1"},
        {"name": "Home_Has_PastelSofa", "value": "0"},
        {"name": "Home_Has_StarryWallpaper", "value": "0"}
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

            home_objs = [
                {
                    "name": "Decor_Bed",
                    "type": "Sprite",
                    "variables": [],
                    "behaviors": [],
                    "animations": [{"name": "Default", "directions": [{"timeBetweenFrames": 1.0, "loops": True, "sprites": [{"image": "pet_bed.png"}]}]}]
                },
                {
                    "name": "Decor_Plant",
                    "type": "Sprite",
                    "variables": [],
                    "behaviors": [],
                    "animations": [{"name": "Default", "directions": [{"timeBetweenFrames": 1.0, "loops": True, "sprites": [{"image": "plant.png"}]}]}]
                }
            ]
            for obj in home_objs:
                if obj["name"] not in existing_objs:
                    objects.append(obj)

            home_insts = [
                {"name": "Decor_Bed", "x": 100, "y": 280, "angle": 0, "zOrder": 1, "layer": "", "customSize": True, "width": 96, "height": 64},
                {"name": "Decor_Plant", "x": 420, "y": 260, "angle": 0, "zOrder": 1, "layer": "", "customSize": True, "width": 48, "height": 80}
            ]
            for inst in home_insts:
                if inst["name"] not in existing_insts:
                    instances.append(inst)

    return game_data
