#type: ignore
&"""
TamaCore Factory v3.1 - UI Runtime
Generates Mobile UIHUD elements (coin counter, stat displays) for GDevelop.
"""

def apply_ui_runtime(game_data: dict) -> dict:
    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            objects = layout.setdefault("objects", [])
            existing_names = {obj.get("name") for obj in objects}
            
            hud_objects = [
                {
                    "name": "HUD_CoinsText",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "Coins: 100",
                    "characterSize": 24,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 215, "b": 0}
                },
                {
                    "name": "HUD_StatusText",
                    "type": "TextObject::Text",
                    "variables": [],
                    "behaviors": [],
                    "string": "Pet Status: Normal",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": False,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 255, "b": 255}
                }
            ]
            
            for hud_obj in hud_objects:
                if hud_obj["name"] not in existing_names:
                    objects.append(hud_obj)
                    
    return game_data
