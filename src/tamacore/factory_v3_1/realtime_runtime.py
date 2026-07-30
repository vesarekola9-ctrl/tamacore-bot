# type: ignore
"""TamaCore Factory v3.1 - RealTime Runtime"""
def apply_realtime_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "RealTime_LastTickTimestamp", "value": "0"},
        {"name": "RealTime_DecayIntervalSeconds", "value": "60"},
        {"name": "RealTime_HungerDecayRate", "value": "1"},
        {"name": "RealTime_EnergyDecayRate", "value": "1"},
        {"name": "RealTime_IsLiveActive", "value": "1"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            events.append({
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": {"value": "Timer"}, "parameters": ["", "60", "RealTimeDecayTimer"]},
                    {"type": {"value": "VarGlobalCompare"}, "parameters": ["RealTime_IsLiveActive", "=", "1"]}
                ],
                "actions": [
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Hunger", "-", "GlobalVariable(RealTime_HungerDecayRate)"]},
                    {"type": {"value": "VarGlobal"}, "parameters": ["Pet_Energy", "-", "GlobalVariable(RealTime_EnergyDecayRate)"]},
                    {"type": {"value": "ResetTimer"}, "parameters": ["", "RealTimeDecayTimer"]}
                ]
            })
    return game_data
