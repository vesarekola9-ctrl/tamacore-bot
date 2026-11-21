"""Curated collectible catalog: fair coin-priced outfits and home decoration."""
from __future__ import annotations

CATEGORIES = {
    "outfit": [
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
        ("sofa", "Cloud Sofa", "🛋️", 210),
        ("bed", "Dream Bed", "🛏️", 320),
        ("lamp", "Star Lamp", "💡", 120),
        ("rug", "Rainbow Rug", "🌈", 180),
        ("plant", "Happy Plant", "🪴", 100),
        ("shelf", "Toy Shelf", "🧸", 260),
        ("table", "Tea Table", "🪑", 170),
    ],
    "wallpaper": [
        ("sky", "Blue Sky", "☁️", 150),
        ("forest", "Magic Forest", "🌳", 240),
        ("space", "Starry Space", "🌌", 290),
        ("candy", "Candy Clouds", "🍬", 220),
    ],
    "toy": [
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
    return {
        "version": 1,
        "items": items,
        "rules": {
            "permanentOwnership": True,
            "freeCoinsCanPurchaseAll": True,
            "randomPaidRewards": False,
            "realMoneyPurchasesImplemented": False,
        },
    }
