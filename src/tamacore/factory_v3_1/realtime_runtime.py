#type: ignore
&"""
TamaCore Factory v3.1 - Realtime Live Runtime
Handles continuous real-time pet decay and timestamp calculation.
"""

def apply_realtime_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    realtime_variables = [
        {"name": "RealTime_LastTickTimestamp", "value": "0"},
        {name": "RealTime_DecayIntervalSeconds", "value": "60"},
        {name": "RealTime_HungerDecayRate", "value": "1"},
        {name": "RealTime_EnergyDecayRate", "value": "1"},
        {name": "RealTime_IsLiveActive", "value": "1"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for r_var in realtime_variables:
        if r_var["name"] not in existing_names:
            game_data["lobalVariables"].append(r_var)

    return game_data
