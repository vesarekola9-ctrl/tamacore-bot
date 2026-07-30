# type: ignore
"""TamaCore Factory v3.1 - Daily Rewards Runtime"""
def apply_daily_rewards_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []
    vars_list = [
        {"name": "Daily_StreakCount", "value": "0"},
        {"name": "Daily_LastClaimTimestamp", "value": "0"},
        {"name": "Daily_RewardClaimedToday", "value": "0"}
    ]
    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)
    return game_data
