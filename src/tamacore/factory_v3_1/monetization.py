"""Transparent, non-pay-to-win monetization configuration for TamaCore.

No purchase is fulfilled locally: Google Play Billing purchases must be
verified by a trusted backend before any paid entitlement is granted.
"""
from __future__ import annotations

from dataclasses import dataclass

COINS_PER_GEM = 20
DAILY_FREE_COINS = 100
REWARDED_AD_COINS = 40
MAX_REWARDED_ADS_PER_DAY = 3

PRODUCTS = (
    {"id": "com.tamacore.gems250", "kind": "consumable", "gems": 250, "coins": 0,
     "description": "250 optional premium gems"},
    {"id": "com.tamacore.rainbowskin", "kind": "non_consumable", "gems": 0, "coins": 0,
     "description": "Permanent rainbow cosmetic"},
    {"id": "com.tamacore.removeads", "kind": "non_consumable", "gems": 0, "coins": 0,
     "description": "Remove optional advertising"},
)

def exchange_gems_for_coins(gems: int, balance: int) -> tuple[int, int]:
    """Spend gems and receive soft currency, never real money."""
    if not isinstance(gems, int) or isinstance(gems, bool) or gems <= 0:
        raise ValueError("gems must be a positive integer")
    if not isinstance(balance, int) or isinstance(balance, bool) or balance < gems:
        raise ValueError("insufficient gem balance")
    return balance - gems, gems * COINS_PER_GEM


def rewarded_coins(watched_today: int, *, verified_reward: bool) -> int:
    """Only award a verified opt-in ad reward, at most three per day."""
    if not isinstance(watched_today, int) or watched_today < 0:
        raise ValueError("invalid ad count")
    return REWARDED_AD_COINS if verified_reward and watched_today < MAX_REWARDED_ADS_PER_DAY else 0


def monetization_manifest() -> dict:
    return {
        "version": 1,
        "currency": {
            "soft": "coins", "premium": "gems", "gemsToCoinsRate": COINS_PER_GEM,
            "coinsToRealMoney": False, "cashOut": False, "transferable": False,
        },
        "freeDailyCoins": DAILY_FREE_COINS,
        "rewardedAds": {
            "optInOnly": True, "coinsPerVerifiedAd": REWARDED_AD_COINS,
            "dailyCap": MAX_REWARDED_ADS_PER_DAY,
            "rewardRequiresServerVerification": True,
        },
        "products": list(PRODUCTS),
        "purchaseFulfillment": "trusted_backend_only",
        "status": "configuration_only_not_live_billing",
        "principles": {
            "noPayToWin": True, "noLootBoxes": True, "noForcedAds": True,
            "noPurchaseToKeepPetAlive": True, "clearPricesAtCheckout": True,
            "noRealMoneyPayouts": True,
        },
    }
