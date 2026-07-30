# type: ignore
"""TamaCore Factory v3.1 - Project Properties & Android Configuration"""

def apply_project_properties(game_data: dict) -> dict:
    props = game_data.setdefault("properties", {})
    props["name"] = "TamaCore Virtual Pet"
    props["packageName"] = "com.tamacore.virtualpet"
    props["version"] = "1.0.0"
    props["windowWidth"] = 540
    props["windowHeight"] = 960
    props["orientation"] = "portrait"
    props["adaptWindowSizeCustomToTargetSize"] = True

    game_data["androidConfig"] = {
        "packageName": "com.tamacore.virtualpet",
        "orientation": "portrait",
        "permissions": [
            "android.permission.INTERNET",
            "com.android.vending.BILLING"
        ]
    }
    return game_data
