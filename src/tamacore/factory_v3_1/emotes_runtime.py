# type: ignore
"""TamaCore Factory v3.1 - Pet Emotes & Visual Reactions System"""

def apply_emotes_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Pet_CurrentEmote", "value": "None"},
        {"name": "Pet_EmoteTimer", "value": "0"},
        {"name": "Pet_IsBeingPetted", "value": "0"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            # Taputus- / Silitysmekaniikka (Petting)
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "CursorOnObject"}, "parameters": ["PetObject", "", "no", ""]},
                    {"type": {"value": "MouseButtonPressed"}, "parameters": ["", "Left"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Happiness", "+", "5"]},
                    {"type": {"value": "VarGlobalString"}, "parameters": ["Pet_CurrentEmote", "=", "Heart"]}
                ]
            })

    return game_data
