"""
TamaCore Factory v3.1 - Analytics Runtime
Geverates telemetry and player analytics tracking variables for GDevelop.
"""

def apply_analytics_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    analytics_variables = [
        {"name": "Analytics_SessionCount", "value": "0"},
        {"name": "Analytics_TotalPlayTime", "value": "0"},
        {"name": "Analytics_FirstLaunchDate", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for a_var in analytics_variables:
        if a_var["name"] not in existing_names:
            game_data["lobalVariables"].append(a_var)

    return game_data
