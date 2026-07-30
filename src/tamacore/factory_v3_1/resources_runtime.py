# type: ignore
"""TamaCore Factory v3.1 - Resources Runtime"""

def apply_resources_runtime(game_data: dict) -> dict:
    if "resources" not in game_data or not isinstance(game_data["resources"], dict):
        game_data["resources"] = {"resources": []}
    
    res_list = game_data["resources"].setdefault("resources", [])
    existing_files = {r.get("file") for r in res_list if isinstance(r, dict)}

    assets = [
        {"kind": "image", "name": "egg.png", "file": "assets/egg.png", "origin": ""},
        {"kind": "image", "name": "stage1.png", "file": "assets/stage1.png", "origin": ""},
        {"kind": "image", "name": "stage2.png", "file": "assets/stage2.png", "origin": ""},
        {"kind": "image", "name": "stage3.png", "file": "assets/stage3.png", "origin": ""},
        {"kind": "image", "name": "stage4.png", "file": "assets/stage4.png", "origin": ""},
        {"kind": "image", "name": "ultimate.png", "file": "assets/ultimate.png", "origin": ""},
        {"kind": "image", "name": "apple.png", "file": "assets/apple.png", "origin": ""},
        {"kind": "image", "name": "cake.png", "file": "assets/cake.png", "origin": ""},
        {"kind": "image", "name": "coin.png", "file": "assets/coin.png", "origin": ""}
    ]

    for asset in assets:
        if asset["file"] not in existing_files:
            res_list.append(asset)

    return game_data
