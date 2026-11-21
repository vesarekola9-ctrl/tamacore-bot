"""Curated collectible catalog: fair coin-priced outfits and home decoration."""
from __future__ import annotations

CATEGORIES = {
    "outfit": [
        ("scarf", "Winter Scarf", "🧣", 120),
        ("cap", "Sport Cap", "🧢", 95),
        ("tophat", "Magic Hat", "🎩", 250),
        ("dress", "Party Dress", "👗", 220),
        ("shirt", "Sailor Shirt", "👕", 145),
        ("mittens", "Snow Mittens", "🧤", 85),
        ("backpack", "Adventure Backpack", "🎒", 180),
        ("headphones", "Music Headphones", "🎧", 210),
        ("sunhat", "Sunny Hat", "👒", 90),
        ("bow", "Pastel Bow", "🎀", 110),
        ("hoodie", "Cozy Hoodie", "🧥", 160),
        ("glasses", "Star Glasses", "🕶️", 190),
        ("cape", "Hero Cape", "🦸", 240),
        ("crown", "Royal Crown", "👑", 390),
        ("pajamas", "Cloud Pajamas", "🌙", 210),
        ("boots", "Rain Boots", "🥾", 140),
    ],
    "furniture": [
        ("desk", "Craft Desk", "🪑", 220),
        ("clock", "Vintage Clock", "🕰️", 160),
        ("mirror", "Star Mirror", "🪞", 180),
        ("basket", "Picnic Basket", "🧺", 125),
        ("books", "Reading Corner", "📚", 170),
        ("piano", "Mini Piano", "🎹", 410),
        ("flowers", "Flower Vase", "💐", 110),
        ("aquarium", "Aquarium", "🐠", 350),
        ("sofa", "Cloud Sofa", "🛋️", 210),
        ("bed", "Dream Bed", "🛏️", 320),
        ("lamp", "Star Lamp", "💡", 120),
        ("rug", "Rainbow Rug", "🌈", 180),
        ("plant", "Happy Plant", "🪴", 100),
        ("shelf", "Toy Shelf", "🧸", 260),
        ("table", "Tea Table", "🪑", 170),
    ],
    "wallpaper": [
        ("ocean", "Ocean Breeze", "🌊", 180),
        ("snow", "Snow Village", "❄️", 200),
        ("sunset", "Golden Sunset", "🌅", 190),
        ("garden", "Flower Garden", "🌷", 160),
        ("sky", "Blue Sky", "☁️", 150),
        ("forest", "Magic Forest", "🌳", 240),
        ("space", "Starry Space", "🌌", 290),
        ("candy", "Candy Clouds", "🍬", 220),
    ],
    "toy": [
        ("train", "Toy Train", "🚂", 195),
        ("robot", "Buddy Robot", "🤖", 240),
        ("drum", "Mini Drum", "🥁", 155),
        ("blocks", "Building Blocks", "🧱", 105),
        ("rocket", "Toy Rocket", "🚀", 200),
        ("guitar", "Tiny Guitar", "🎸", 190),
        ("ball", "Bouncy Ball", "⚽", 65),
        ("teddy", "Tiny Teddy", "🧸", 135),
        ("kite", "Rainbow Kite", "🪁", 175),
        ("puzzle", "Puzzle Box", "🧩", 115),
    ],
}


def collectible_catalog() -> dict:
    items = []
    for category, entries in CATEGORIES.items():
        for key, name, emoji, coins in entries:
            items.append({
                "id": f"{category}_{key}", "category": category,
                "name": name, "emoji": emoji, "coinPrice": coins,
                "premiumOnly": False, "cashPrice": None,
            })
    # Permanent themed variants give players more decorative choices.
    themes = [
        ("pastel", "Pastel", 20), ("royal", "Royal", 65),
        ("winter", "Winter", 35), ("garden", "Garden", 30),
    ]
    originals = list(items)
    for item in originals:
        if item["category"] == "wallpaper":
            continue
        for theme, label, surcharge in themes:
            items.append({
                **item, "id": item["id"] + "_" + theme,
                "name": label + " " + item["name"],
                "coinPrice": item["coinPrice"] + surcharge,
                "theme": theme,
            })
    return {
        "version": 2,
        "items": items,
        "rules": {
            "permanentOwnership": True,
            "freeCoinsCanPurchaseAll": True,
            "randomPaidRewards": False,
            "realMoneyPurchasesImplemented": False,
        },
    }
