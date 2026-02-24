from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

from tools.config import PATHS

def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def main():
    PATHS.scaffold_dir.mkdir(parents=True, exist_ok=True)

    # --- Systems (data-driven) ---
    needs = {
        "stats": ["hunger", "energy", "fun", "clean"],
        "decay_per_minute": {"hunger": 0.25, "energy": 0.15, "fun": 0.20, "clean": 0.10},
        "clamp_min": 0,
        "clamp_max": 100
    }

    mood = {
        "weights": {"hunger": 0.30, "energy": 0.25, "fun": 0.25, "clean": 0.20},
        "thresholds": {"happy": 80, "ok": 55, "sad": 35, "angry": 20}
    }

    economy = {
        "currency": {"soft_name": "Coins"},
        "daily_reward": {"base": 50}
    }

    write_json(PATHS.scaffold_dir / "Data/needs.json", needs)
    write_json(PATHS.scaffold_dir / "Data/mood.json", mood)
    write_json(PATHS.scaffold_dir / "Data/economy.json", economy)

    # --- Scene scaffolds (yaml-like text; keep it simple & readable) ---
    home_yaml = """scene: Home
layers: [BG, Pet, UI, FX, Debug]
objects:
  - { name: PetSprite, type: Sprite }
  - { name: BtnFeed, type: Button }
  - { name: BtnSleep, type: Button }
  - { name: BtnPlay, type: Button }
  - { name: BtnClean, type: Button }
  - { name: HudNeeds, type: UIGroup }
events:
  - OnSceneStart: Load Data/needs.json into variables
  - Every 60s: Apply decay to Needs
  - OnNeedsChanged: Recompute moodScore + moodState
  - OnMoodStateChanged: Set emotion animation + FX + UI
"""
    shop_yaml = """scene: Shop
layers: [BG, UI, FX]
objects:
  - { name: ShopGrid, type: UIGrid }
  - { name: BtnBuy, type: Button }
events:
  - OnOpen: Load catalog
  - OnBuy: Deduct currency + add inventory
"""
    inv_yaml = """scene: Inventory
layers: [BG, UI]
objects:
  - { name: InvGrid, type: UIGrid }
  - { name: BtnEquip, type: Button }
events:
  - OnOpen: Load inventory
  - OnEquip: Apply cosmetics to pet
"""

    write_text(PATHS.scaffold_dir / "Scenes/Home.yaml", home_yaml)
    write_text(PATHS.scaffold_dir / "Scenes/Shop.yaml", shop_yaml)
    write_text(PATHS.scaffold_dir / "Scenes/Inventory.yaml", inv_yaml)

    # --- GDevelop snippets: copy/paste event plan ---
    snippets = f"""TamaCore Scaffold Snippets (GDevelop) | {datetime.utcnow().isoformat()}Z

HOME (External Events / Event Sheet PSEUDO):
1) At the beginning of the scene:
   - Load JSON "output/scaffold/Data/needs.json" into global vars:
     GlobalVariable(Needs).hunger/energy/fun/clean = 100
   - Load mood weights + thresholds from mood.json
   - Set GlobalVariable(MoodState) = "ok"

2) Every 60 seconds:
   - Needs.hunger -= decay.hunger
   - Needs.energy -= decay.energy
   - Needs.fun    -= decay.fun
   - Needs.clean  -= decay.clean
   - Clamp all Needs 0..100
   - Trigger "NeedsChanged"

3) When "NeedsChanged":
   - moodScore = weighted average of Needs
   - if moodScore >= happy -> MoodState="happy"
     else if >= ok -> "ok"
     else if >= sad -> "sad"
     else if >= angry -> "angry"
     else -> "panic"
   - Trigger "MoodStateChanged"

4) When "MoodStateChanged":
   - Change PetSprite animation based on MoodState
   - Spawn FX for state (effects folder / atlas frames)
   - Update HudNeeds bars/icons

SHOP/INVENTORY:
- Use economy.json as the base values
- Inventory = array of item ids + equipped slots
"""

    write_text(PATHS.scaffold_dir / "Snippets/GDevelop_Paste.txt", snippets)

    print("[✓] Scaffold generated ->", PATHS.scaffold_dir)

if __name__ == "__main__":
    main()
