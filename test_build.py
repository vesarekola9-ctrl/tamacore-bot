import json
import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from tamacore.factory_v3_1.generator import build_game_json

def test_generate():
    base_data = {
        "properties": {"name": "TamaCore Game"},
        "layouts": [{"name": "MainScene", "objects": [], "events": []}],
        "globalVariables": []
    }
    print("Building game.json...")
    result = build_game_json(base_data)
    
    with open("game.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"Success! game.json generated with {len(result.get('globalVariables', []))} global variables.")

if __name__ == "__main__":
    test_generate()
