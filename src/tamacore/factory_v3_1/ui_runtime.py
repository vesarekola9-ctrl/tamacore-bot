# type: ignore
"""TamaCore Factory v3.1 - Enhanced Pastel & IAP UI Runtime"""

def apply_ui_runtime(game_data: dict) -> dict:
    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            objects = layout.setdefault("objects", [])
            instances = layout.setdefault("instances", [])
            existing_objs = {obj.get("name") for obj in objects}
            existing_insts = {inst.get("name") for inst in instances}

            hud_objects = [
                {
                    "name": "HUD_CoinsText",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "Coins: 600 🪙",
                    "characterSize": 22,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 215, "b": 0}
                },
                {
                    "name": "HUD_GemsText",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "Gems: 50 💎",
                    "characterSize": 22,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 238, "g": 130, "b": 238}
                },
                {
                    "name": "HUD_StatusText",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "Pet: Happy | Stage: Egg",
                    "characterSize": 18,
                    "fontName": "",
                    "bold": False,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 240, "b": 245}
                },
                {
                    "name": "Button_Feed",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "[ 🍎 SYÖTÄ ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 105, "b": 180}
                },
                {
                    "name": "Button_Sleep",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "[ 🌙 NUKU ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 147, "g": 112, "b": 219}
                },
                {
                    "name": "Button_ShopIAP",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "[ 🛒 KAUPPA (PLAY IAP) ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 215, "b": 0}
                }
            ]

            for hud_obj in hud_objects:
                if hud_obj["name"] not in existing_objs:
                    objects.append(hud_obj)

            default_instances = [
                {"name": "PetObject", "x": 340, "y": 220, "angle": 0, "zOrder": 1, "layer": "", "customSize": True, "width": 128, "height": 128},
                {"name": "HUD_CoinsText", "x": 20, "y": 20, "angle": 0, "zOrder": 10, "layer": "", "customSize": False},
                {"name": "HUD_GemsText", "x": 200, "y": 20, "angle": 0, "zOrder": 10, "layer": "", "customSize": False},
                {"name": "HUD_StatusText", "x": 20, "y": 60, "angle": 0, "zOrder": 10, "layer": "", "customSize": False},
                {"name": "Button_Feed", "x": 80, "y": 480, "angle": 0, "zOrder": 10, "layer": "", "customSize": False},
                {"name": "Button_Sleep", "x": 280, "y": 480, "angle": 0, "zOrder": 10, "layer": "", "customSize": False},
                {"name": "Button_ShopIAP", "x": 460, "y": 480, "angle": 0, "zOrder": 10, "layer": "", "customSize": False}
            ]

            for inst in default_instances:
                if inst["name"] not in existing_insts:
                    instances.append(inst)

    return game_data
