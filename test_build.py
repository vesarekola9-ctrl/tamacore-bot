import json
import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from tamacore.factory_v3_1.generator import build_game_json

def test_generate():
    # GDevelop 5:n vaatima virallinen juurirakenne
    base_data = {
        "gdVersion": {
            "build": 99,
            "major": 4,
            "minor": 0,
            "revision": 0
        },
        "properties": {
            "name": "TamaCore Virtual Pet",
            "author": "TamaCore Team",
            "version": "1.0.0",
            "packageName": "com.tamacore.virtualpet",
            "windowWidth": 540,
            "windowHeight": 960,
            "orientation": "portrait",
            "adaptWindowSizeCustomToTargetSize": True,
            "sizeOnStartupMode": "adaptWidth",
            "projectFileLayoutVersion": 1
        },
        "firstLayout": "MainScene",
        "objects": [],
        "eventsFunctionsExtensions": [],
        "layouts": [
            {
                "name": "MainScene",
                "uiSettings": {
                    "grid": False,
                    "gridR": 255,
                    "gridG": 255,
                    "gridB": 255,
                    "gridWidth": 32,
                    "gridHeight": 32,
                    "gridOffsetX": 0,
                    "gridOffsetY": 0,
                    "snap": False
                },
                "objects": [],
                "instances": [],
                "events": [],
                "layers": [
                    {
                        "name": "",
                        "visibility": True,
                        "cameras": [],
                        "effects": []
                    }
                ]
            }
        ],
        "globalVariables": [],
        "resources": {
            "resources": []
        }
    }
    
    print("Building GDevelop 5 compatible game.json...")
    result = build_game_json(base_data)

    with open("game.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Success! GDevelop 5 compatible game.json generated.")

if __name__ == "__main__":
    test_generate()