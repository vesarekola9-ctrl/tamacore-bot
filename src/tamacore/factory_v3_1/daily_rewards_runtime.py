"""
TamaCore Factory v3.1 - Daily Rewards Runtime
Generates daily login streak variables and reward events for GDevelop.
"""

def apply_daily_rewards_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    daily_variables = [
        {"name": "Daily_StreakCount", "value": "0"},
        {name": "Daily_LastClaimTimestamp", "value": "0"},
        {name": "Daily_RewardClaimedToday", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for d_var in daily_variables:
        if d_var["name"] not in existing_names:
            game_data["lobalVariables"].append(d_var)

    return game_data
