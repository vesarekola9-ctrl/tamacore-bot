from __future__ import annotations

from pathlib import Path

from ..utils import ensure_dir, write_json, write_text


def create_pack(pack_dir: Path, name: str = "New Pack") -> None:
    ensure_dir(pack_dir)
    ensure_dir(pack_dir / "assets" / "background")
    ensure_dir(pack_dir / "assets" / "player")
    ensure_dir(pack_dir / "assets" / "coin")
    ensure_dir(pack_dir / "assets" / "enemy")
    ensure_dir(pack_dir / "assets" / "ui")

    write_json(
        pack_dir / "pack.json",
        {
            "name": name,
            "version": "1.0.0",
            "scene": "Main",
            "display": {
                "mode": "portrait",
                "virtualWidth": 720,
                "virtualHeight": 1280
            },
            "worldBounds": {
                "xMin": 0,
                "yMin": 0,
                "xMax": 720,
                "yMax": 1280
            },
            "camera": {
                "followObject": "Player",
                "lerp": 0.12
            },
            "ui": {
                "layer": "UI",
                "hud": {
                    "objectName": "HUD",
                    "anchor": "top-left",
                    "marginX": 24,
                    "marginY": 24
                },
                "joystick": {
                    "objectName": "TouchJoystick",
                    "anchor": "bottom-left",
                    "marginX": 36,
                    "marginY": 36
                }
            },
            "coinSpawn": {
                "objectName": "Coin",
                "count": 8,
                "enabled": True,
                "respawnOnCollect": True,
                "minDistanceFromPlayer": 120
            },
            "enemySpawn": {
                "objectName": "Enemy",
                "count": 2,
                "enabled": True,
                "respawnOnCollect": False,
                "minDistanceFromPlayer": 180
            },
            "levels": {
                "count": 5,
                "coinBase": 8,
                "coinStep": 2,
                "enemyBase": 1,
                "enemyStep": 1,
                "seed": 1337
            },
            "shop": {
                "currencyVariable": "Coins",
                "upgrades": [
                    {
                        "id": "speed_1",
                        "name": "Speed +50",
                        "cost": 100,
                        "effect": {
                            "playerMaxSpeedAdd": 50
                        }
                    },
                    {
                        "id": "coins_bonus",
                        "name": "Coins +100",
                        "cost": 75,
                        "effect": {
                            "coinsAdd": 100
                        }
                    }
                ]
            }
        },
    )

    write_text(
        pack_dir / "assets" / "background" / "background.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="720" height="1280" fill="url(#bg)"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "player" / "player_idle_01.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <rect x="42" y="84" width="44" height="22" rx="11" fill="#f59e0b"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "player" / "player_walk_01.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <rect x="40" y="84" width="48" height="22" rx="11" fill="#f59e0b"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "coin" / "coin.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">
  <circle cx="48" cy="48" r="30" fill="#fde047"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "enemy" / "enemy.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <circle cx="64" cy="64" r="32" fill="#ef4444"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "ui" / "touch_joystick.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">
  <circle cx="80" cy="80" r="60" fill="#cbd5e1" opacity="0.35"/>
</svg>
""",
    )

    write_text(
        pack_dir / "assets" / "ui" / "hud_label.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="320" height="80" viewBox="0 0 320 80">
  <rect x="4" y="4" width="312" height="72" rx="18" fill="#0f172a" opacity="0.68" stroke="#334155" stroke-width="2"/>
  <text x="20" y="49" font-family="Arial" font-size="28" font-weight="700" fill="#f8fafc">HUD</text>
</svg>
""",
    )
