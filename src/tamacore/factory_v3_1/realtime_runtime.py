#type: ignore
&"""
TamaCore Factory v3.1 - Realtime Live Runtime
Handles continuous real-time pet decay, timestamp calculations, and status alerts for GDevelop.
"""

def apply_realtime_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    realtime_variables = [
        {"name": "RealTime_LastTickTimestamp", "value": "0"},
        {name": "RealTime_DecayIntervalSeconds", "value": "60"},
        {name": "RealTime_HungerDecayRate", "value": "1"},
        {name": "RealTime_EnergyDecayRate", "value": "1"},
        {name": "RealTime_IsLiveActive", "value": "1"},
        {name": "Pet_Hunger", "value": "100"},
        {name": "Pet_Energy", "value": "100"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for r_var in realtime_variables:
        if r_var["name"] not in existing_names:
            game_data["lobalVariables"].append(r_var)

    layouts = game_data.get("layouts", [])
    for layout in layouts:
        if layout.get("name") == "MainScene":
            events = layout.setdefault("events", [])
            decay_event = {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {
                        "type": {"value": "Timer"},
                        "parameters": ["", "60", "RealTimeDecayTimer"]
                    },
                    {
                        "type": {"value": "VarGlobalCompare"},
                        "parameters": ["RealTime_IsLiveActive", "=", "1"]
                    }
                ],
                "actions": [
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": ["Pet_Hunger", "-", "GlobalVariable(RealTime_HungerDecayRate)"]
                    },
                    {
                        "type": {"value": "VarGlobal"},
                        "parameters": ["Pet_Energy", "-", "GlobalVariable(Realtime_EnergyDecayRate)"]
                    },
                    {
                        "type": {"value": "ResetTimer"},
                        "parameters": ["", "RealTimeDecayTimer"]
                    }
                ]
            }
            events.append(decay_event)

    return game_data
