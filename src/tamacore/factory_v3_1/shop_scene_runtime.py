# type: ignore
"""TamaCore Factory v3.1 - Dedicated ShopScene Runtime"""

def apply_shop_scene_runtime(game_data: dict) -> dict:
    layouts = game_data.setdefault("layouts", [])
    existing_layout_names = {l.get("name") for l in layouts if isinstance(l, dict)}

    if "ShopScene" not in existing_layout_names:
        shop_layout = {
            "name": "ShopScene",
            "objects": [
                {
                    "name": "Shop_Title",
                    "type": "TextObject::Text",
                    "string": "✨ PASTEL SHOP ✨",
                    "characterSize": 28,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 105, "b": 180}
                },
                {
                    "name": "Card_RainbowSkin_Btn",
                    "type": "TextObject::Text",
                    "string": "[ Rainbow Skin - 600 💎 ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 219, "g": 112, "b": 147}
                },
                {
                    "name": "Card_Halo_Btn",
                    "type": "TextObject::Text",
                    "string": "[ Angel Halo - 400 💎 ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 215, "b": 0}
                },
                {
                    "name": "Card_DailyReward_Btn",
                    "type": "TextObject::Text",
                    "string": "[ Daily Chest €3.99 ]",
                    "characterSize": 20,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 147, "g": 112, "b": 219}
                },
                {
                    "name": "Btn_BackToMain",
                    "type": "TextObject::Text",
                    "string": "< TAKAISIN PELIIN",
                    "characterSize": 22,
                    "fontName": "",
                    "bold": True,
                    "italic": False,
                    "smoothed": True,
                    "color": {"r": 255, "g": 255, "b": 255}
                }
            ],
            "instances": [
                {"name": "Shop_Title", "x": 140, "y": 40, "angle": 0, "zOrder": 1, "layer": "", "customSize": False},
                {"name": "Card_RainbowSkin_Btn", "x": 80, "y": 140, "angle": 0, "zOrder": 2, "layer": "", "customSize": False},
                {"name": "Card_Halo_Btn", "x": 80, "y": 220, "angle": 0, "zOrder": 2, "layer": "", "customSize": False},
                {"name": "Card_DailyReward_Btn", "x": 80, "y": 300, "angle": 0, "zOrder": 2, "layer": "", "customSize": False},
                {"name": "Btn_BackToMain", "x": 160, "y": 860, "angle": 0, "zOrder": 10, "layer": "", "customSize": False}
            ],
            "events": [
                {
                    "type": "BuiltinCommonInstructions::Standard",
                    "conditions": [
                        {"type": {"value": "CursorOnObject"}, "parameters": ["Btn_BackToMain", "", "no", ""]},
                        {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                    ],
                    "actions": [
                        {"type": {"value": "ChangeScene"}, "parameters": ["", "'MainScene'", ""]}
                    ]
                }
            ]
        }
        layouts.append(shop_layout)

    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "CursorOnObject"}, "parameters": ["Button_ShopIAP", "", "no", ""]},
                    {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                ],
                "actions": [
                    {"type": {"value": "ChangeScene"}, "parameters": ["", "'ShopScene'", ""]}
                ]
            })

    return game_data
