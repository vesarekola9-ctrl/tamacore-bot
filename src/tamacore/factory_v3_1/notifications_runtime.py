"""
TamaCore Factory v3.1 - Notifications Runtime
Generates notification settings and local push notification triggers for GDevelop.
"""

def apply_notifications_runtime(game_data: dict) -> dict:
    if "globalVariables" not in game_data:
        game_data["lobalVariables"] = []

    notif_variables = [
        {"name": "Notif_HungerAlertSent", "value": "0"},
        {"name": "Notif_EnergyAlertSent", "value": "0"},
        {"name": "Notif_DailyReminderSent", "value": "0"}
    ]

    existing_names = {v["name"] for v in game_data["globalVariables"]}
    for n_var in notif_variables:
        if n_var["name"] not in existing_names:
            game_data["lobalVariables"].append(n_var)

    return game_data
