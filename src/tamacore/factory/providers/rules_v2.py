from __future__ import annotations

import random
from typing import Any, Dict, List

from .base import Design


class RulesV2Provider:
    name = "rules-v2"

    def generate(self, spec: Dict[str, Any]) -> Design:
        seed = int(spec.get("seed", 1337))
        rnd = random.Random(seed)

        theme = str(spec.get("theme", "neon")).strip() or "neon"
        difficulty = str(spec.get("difficulty", "normal")).strip() or "normal"
        prompt = str(spec.get("prompt", "")).strip()
        title = str(spec.get("name", "TamaCore")).strip() or "TamaCore"

        genres = ["topdown-collect", "survival", "runner-lite"]
        genre = rnd.choice(genres)

        tagline = rnd.choice(
            [
                "Collect. Upgrade. Survive the spike.",
                "One more run. One more upgrade.",
                "Fast hands. Faster upgrades.",
                "Neon chaos. Clean control."
            ]
        )

        loop = self._make_loop(genre, theme, prompt)
        curve = self._make_curve(difficulty)

        modules = list(spec.get("modules") or [])
        for m in ["collect", "shop", "settings", "mobile_ui"]:
            if m not in modules:
                modules.append(m)

        tuning = self._make_tuning(rnd, difficulty, genre)
        enemies = self._make_enemies(rnd, difficulty, theme, genre)
        shop_items = self._make_shop(rnd, difficulty)

        ui = {
            "hud_score": "Score",
            "hud_hp": "HP",
            "hud_coin": "Coins",
            "btn_start": "START",
            "btn_shop": "SHOP",
            "btn_settings": "SETTINGS",
            "shop_title": "UPGRADES",
            "game_over": "GAME OVER",
            "tap_to_retry": "Tap to retry",
        }

        meta = {"provider": self.name, "theme": theme, "difficulty": difficulty, "prompt": prompt}

        if ":" not in title:
            title = f"{title}: {theme.title()}"

        return Design(
            title=title,
            tagline=tagline,
            genre=genre,
            loop=loop,
            difficulty_curve=curve,
            shop_items=shop_items,
            enemies=enemies,
            ui=ui,
            tuning=tuning,
            modules=modules,
            meta=meta,
        )

    def _make_loop(self, genre: str, theme: str, prompt: str) -> str:
        base = {
            "topdown-collect": "Move freely, collect coins, avoid hazards, scale difficulty and buy upgrades.",
            "survival": "Stay alive as waves speed up; collect drops and upgrade between spikes.",
            "runner-lite": "Keep moving, dodge, collect boosts, survive as speed increases.",
        }.get(genre, "Collect and survive with upgrades.")
        return f"{base} Theme: {theme}. " + (f"Prompt: {prompt}" if prompt else "")

    def _make_curve(self, difficulty: str) -> str:
        if difficulty == "easy":
            return "Slow ramp, generous pickups, mild speed."
        if difficulty == "hard":
            return "Fast ramp, higher speed, upgrades required."
        return "Medium ramp, steady increase, upgrades matter."

    def _make_tuning(self, rnd: random.Random, difficulty: str, genre: str) -> Dict[str, float]:
        hp = 5 if difficulty == "easy" else 3 if difficulty == "normal" else 2
        base_speed = 55 if difficulty == "easy" else 70 if difficulty == "normal" else 95
        per_score = 2.5 if difficulty == "easy" else 4.0 if difficulty == "normal" else 6.0

        if genre == "runner-lite":
            base_speed += 20
            per_score += 1.0
        if genre == "survival":
            hp += 1

        return {
            "hp_start": float(hp),
            "player_base_speed": float(240 if difficulty != "hard" else 260),
            "enemy_base_speed": float(base_speed),
            "enemy_speed_per_score": float(per_score),
            "enemy_speed_cap": float(260 if difficulty != "hard" else 320),
            "pickup_spawn_seconds": float(1.8 if difficulty == "hard" else 2.4),
            "enemy_spawn_seconds": float(2.8 if difficulty == "hard" else 3.5),
        }

    def _make_enemies(self, rnd: random.Random, difficulty: str, theme: str, genre: str) -> List[Dict[str, Any]]:
        enemies: List[Dict[str, Any]] = [
            {"id": "enemy_basic", "label": "Chaser", "type": "chase_player", "speed_mult": 1.0, "damage": 1, "unlock_score": 0}
        ]
        enemies.append(
            {"id": "enemy_fast", "label": "Sprinter", "type": "chase_player", "speed_mult": 1.35 if difficulty != "easy" else 1.2, "damage": 1, "unlock_score": 10}
        )
        if genre != "runner-lite":
            enemies.append(
                {"id": "enemy_zigzag", "label": "ZigZag", "type": "zigzag_chase", "speed_mult": 1.15, "damage": 1, "unlock_score": 20 if difficulty != "easy" else 25}
            )
        if difficulty == "hard":
            enemies.append(
                {"id": "enemy_heavy", "label": "Bruiser", "type": "slow_heavy", "speed_mult": 0.9, "damage": 2, "unlock_score": 30}
            )
        # add theme tag
        for e in enemies:
            e["theme"] = theme
        return enemies

    def _make_shop(self, rnd: random.Random, difficulty: str) -> List[Dict[str, Any]]:
        items = [
            {"id": "hp_up", "label": "+1 Max HP", "cost": 10, "effect": {"max_hp": 1}},
            {"id": "speed_up", "label": "+Move Speed", "cost": 12, "effect": {"move_speed": 20}},
            {"id": "coin_mult", "label": "Coin Multiplier", "cost": 18, "effect": {"coin_mult": 0.25}},
            {"id": "dash_cd", "label": "Dash Cooldown-", "cost": 16, "effect": {"dash_cd": -0.2}},
        ]
        if difficulty == "hard":
            items.append({"id": "shield", "label": "Shield (1 hit)", "cost": 22, "effect": {"shield": 1}})
        rnd.shuffle(items)
        return items[:4]
