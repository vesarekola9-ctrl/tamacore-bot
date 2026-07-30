# type: ignore
"""TamaCore Factory v3.1 - Pet Runtime"""

def apply_pet_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Pet_Name", "value": "Tama"},
        {"name": "Pet_Hunger", "value": "100"},
        {"name": "Pet_Energy", "value": "100"},
        {"name": "Pet_Happiness", "value": "100"},
        {"name": "Pet_Health", "value": "100"},
        {"name": "Pet_State", "value": "Idle"},
        {"name": "Pet_CurrentAnimation", "value": "idle_anim"}
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            objects = layout.setdefault("objects", [])
            existing_objs = {obj.get("name") for obj in objects}
            if "PetObject" not in existing_objs:
                objects.append({
                    "name": "PetObject",
                    "type": "Sprite",
                    "variables": [],
                    "behaviors": [],
                    "animations": [
                        {
                            "name": "Idle",
                            "directions": [{"timeBetweenFrames": 0.2, "loops": True, "sprites": [{"image": "stage1.png"}]}]
                        },
                        {
                            "name": "Feed",
                            "directions": [{"timeBetweenFrames": 0.15, "loops": False, "sprites": [{"image": "apple.png"}]}]
                        },
                        {
                            "name": "Sleep",
                            "directions": [{"timeBetweenFrames": 0.5, "loops": True, "sprites": [{"image": "stage1.png"}]}]
                        },
                        {
                            "name": "Evolve",
                            "directions": [{"timeBetweenFrames": 0.1, "loops": False, "sprites": [{"image": "ultimate.png"}]}]
                        }
                    ]
                })

            events = layout.setdefault("events", [])
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "VarGlobalStringCompare"}, "parameters": ["Pet_State", "=", "Sleep"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Energy", "+", "0.5"]},
                    {"type": {"value": "SetAnimationName"}, "parameters": ["PetObject", "Sleep"]}
                ]
            })

    return game_data
