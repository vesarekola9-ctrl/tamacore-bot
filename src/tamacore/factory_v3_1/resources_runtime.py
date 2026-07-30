# type: ignore
"""TamaCore Factory v3.1 - Master Resources Catalog"""

def apply_resources_runtime(game_data: dict) -> dict:
    if "resources" not in game_data or not isinstance(game_data["resources"], dict):
        game_data["resources"] = {"resources": []}
    
    res_list = game_data["resources"].setdefault("resources", [])
    existing_files = {r.get("file") for r in res_list if isinstance(r, dict)}

    assets = [
        # Evoluutio & Hahmo
        {"kind": "image", "name": "egg.png", "file": "assets/egg.png", "origin": ""},
        {"kind": "image", "name": "stage1.png", "file": "assets/stage1.png", "origin": ""},
        {"kind": "image", "name": "stage2.png", "file": "assets/stage2.png", "origin": ""},
        {"kind": "image", "name": "stage3.png", "file": "assets/stage3.png", "origin": ""},
        {"kind": "image", "name": "stage4.png", "file": "assets/stage4.png", "origin": ""},
        {"kind": "image", "name": "ultimate.png", "file": "assets/ultimate.png", "origin": ""},
        {"kind": "image", "name": "pet_dead.png", "file": "assets/pet_dead.png", "origin": ""},
        # Ruoat
        {"kind": "image", "name": "apple.png", "file": "assets/apple.png", "origin": ""},
        {"kind": "image", "name": "cake.png", "file": "assets/cake.png", "origin": ""},
        {"kind": "image", "name": "pizza.png", "file": "assets/pizza.png", "origin": ""},
        {"kind": "image", "name": "icecream.png", "file": "assets/icecream.png", "origin": ""},
        {"kind": "image", "name": "donut.png", "file": "assets/donut.png", "origin": ""},
        {"kind": "image", "name": "burger.png", "file": "assets/burger.png", "origin": ""},
        {"kind": "image", "name": "sushi.png", "file": "assets/sushi.png", "origin": ""},
        {"kind": "image", "name": "strawberry.png", "file": "assets/strawberry.png", "origin": ""},
        {"kind": "image", "name": "pancake.png", "file": "assets/pancake.png", "origin": ""},
        {"kind": "image", "name": "cookie.png", "file": "assets/cookie.png", "origin": ""},
        # Juomat
        {"kind": "image", "name": "water.png", "file": "assets/water.png", "origin": ""},
        {"kind": "image", "name": "milk.png", "file": "assets/milk.png", "origin": ""},
        {"kind": "image", "name": "boba.png", "file": "assets/boba.png", "origin": ""},
        {"kind": "image", "name": "juice.png", "file": "assets/juice.png", "origin": ""},
        {"kind": "image", "name": "soda.png", "file": "assets/soda.png", "origin": ""},
        {"kind": "image", "name": "cocoa.png", "file": "assets/cocoa.png", "origin": ""},
        {"kind": "image", "name": "coffee.png", "file": "assets/coffee.png", "origin": ""},
        # Vaatteet & Hatut
        {"kind": "image", "name": "top_hat.png", "file": "assets/top_hat.png", "origin": ""},
        {"kind": "image", "name": "pink_bow.png", "file": "assets/pink_bow.png", "origin": ""},
        {"kind": "image", "name": "crown.png", "file": "assets/crown.png", "origin": ""},
        {"kind": "image", "name": "party_hat.png", "file": "assets/party_hat.png", "origin": ""},
        {"kind": "image", "name": "cat_ears.png", "file": "assets/cat_ears.png", "origin": ""},
        {"kind": "image", "name": "hoodie.png", "file": "assets/hoodie.png", "origin": ""},
        {"kind": "image", "name": "tuxedo.png", "file": "assets/tuxedo.png", "origin": ""},
        {"kind": "image", "name": "dress.png", "file": "assets/dress.png", "origin": ""},
        # Koti & Huonekalut
        {"kind": "image", "name": "pet_bed.png", "file": "assets/pet_bed.png", "origin": ""},
        {"kind": "image", "name": "princess_bed.png", "file": "assets/princess_bed.png", "origin": ""},
        {"kind": "image", "name": "plant.png", "file": "assets/plant.png", "origin": ""},
        {"kind": "image", "name": "cactus.png", "file": "assets/cactus.png", "origin": ""},
        {"kind": "image", "name": "sofa.png", "file": "assets/sofa.png", "origin": ""},
        {"kind": "image", "name": "desk.png", "file": "assets/desk.png", "origin": ""},
        {"kind": "image", "name": "coin.png", "file": "assets/coin.png", "origin": ""}
    ]

    for asset in assets:
        if asset["file"] not in existing_files:
            res_list.append(asset)

    return game_data
