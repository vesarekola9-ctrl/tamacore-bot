# type: ignore
"""TamaCore Factory v3.1 - Advanced Push Notifications System"""

def apply_notifications_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["globalVariables"] = []

    vars_list = [
        {"name": "Notif_HungerAlertSent", "value": "0"},
        {"name": "Notif_CriticalAlertSent", "value": "0"},
        {"name": "Notif_DailyChestAlertSent", "value": "0"},
        {"name": "Notif_ScheduledTimeSeconds", "value": "14400"} # 4 Tuntia
    ]

    existing = {v["name"] for v in game_data["globalVariables"]}
    for item in vars_list:
        if item["name"] not in existing:
            game_data["globalVariables"].append(item)

    return game_data
