from __future__ import annotations

from pathlib import Path
import json
import shutil
from datetime import datetime
import re
from typing import Any, Dict, List, Tuple

ROOT = Path(".")
OUT = Path("output")

PACK = OUT / "gdevelop_pack"
ASSETS = PACK / "assets"
CODE = PACK / "code"
DOCS = PACK / "docs"

ATLAS_DIR = OUT / "atlas"
ATLAS_PNG = ATLAS_DIR / "atlas.png"
ATLAS_JSON = ATLAS_DIR / "atlas.json"

MAPPING = OUT / "assets_raw" / "mapping.json"


# -----------------------------
# FS helpers
# -----------------------------
def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def write_json(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def copy_if_exists(src: Path, dst: Path):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


# -----------------------------
# Data loaders
# -----------------------------
def load_frames_from_atlas() -> List[str]:
    if not ATLAS_JSON.exists():
        return []
    data = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    frames = list(data.get("frames", {}).keys())
    return frames


def load_mapping() -> Dict[str, Any]:
    if not MAPPING.exists():
        return {}
    try:
        return json.loads(MAPPING.read_text(encoding="utf-8"))
    except Exception:
        return {}


# -----------------------------
# Catalog builder (from mapping/frames)
# -----------------------------
def _guess_slot(name: str) -> str:
    s = name.lower()
    # crude but effective conventions
    if "hat" in s or "cap" in s or "beanie" in s:
        return "hat"
    if "glass" in s or "glasses" in s or "shade" in s:
        return "glasses"
    if "skin" in s or "outfit" in s or "body" in s:
        return "skin"
    return "misc"


def _guess_rarity(name: str) -> str:
    s = name.lower()
    # support your "rarity economy logic 😈"
    if any(t in s for t in ["mythic", "legend", "legendary", "ultra"]):
        return "legendary"
    if any(t in s for t in ["epic", "rareplus", "rare_plus"]):
        return "epic"
    if "rare" in s:
        return "rare"
    if "uncommon" in s:
        return "uncommon"
    return "common"


def _price_for_rarity(r: str) -> Tuple[int, int]:
    # (coins, gems)
    table = {
        "common": (120, 0),
        "uncommon": (250, 0),
        "rare": (450, 1),
        "epic": (900, 3),
        "legendary": (1600, 7),
    }
    return table.get(r, (200, 0))


def build_catalog(frames: List[str], mapping: Dict[str, Any]) -> Dict[str, Any]:
    """
    Output:
      {
        "items": [
          { "id": "...", "name": "...", "slot": "hat|glasses|skin|misc",
            "rarity":"...", "priceCoins":123, "priceGems":0,
            "thumb":"<atlas frame filename>" }
        ]
      }
    """
    items: List[Dict[str, Any]] = []

    # mapping.json structure can vary; we’ll accept both:
    # 1) {"files":[{"file":"...","category":"cosmetics"}...]}
    # 2) {"mapping":{"filename.png":"cosmetics", ...}}
    files = mapping.get("files", [])
    mapping_dict = mapping.get("mapping", {})

    candidates: List[str] = []

    if isinstance(files, list) and files:
        for row in files:
            try:
                cat = (row.get("category") or "").lower()
                fn = row.get("file") or row.get("filename") or ""
                if fn and ("cosmetic" in cat or cat == "cosmetics"):
                    candidates.append(fn)
            except Exception:
                pass

    if isinstance(mapping_dict, dict) and mapping_dict:
        for fn, cat in mapping_dict.items():
            cat = str(cat).lower()
            if fn and ("cosmetic" in cat or cat == "cosmetics"):
                candidates.append(fn)

    # If mapping didn't catch cosmetics, just use some atlas frames as fallback
    if not candidates:
        # choose anything that looks like wearable
        for f in frames:
            if any(t in f.lower() for t in ["hat", "glass", "skin", "outfit", "cosmetic"]):
                candidates.append(f)
        # still none -> use first 24 frames
        if not candidates:
            candidates = frames[:24]

    # Build unique ids
    seen = set()
    for fn in candidates:
        base = Path(fn).stem
        # strip category prefix if naming_pro added e.g. cosmetics__x__v001
        base2 = re.sub(r"^(cosmetics|ui|effects|backgrounds|pet)__", "", base)
        item_id = re.sub(r"[^a-zA-Z0-9_]+", "_", base2).lower().strip("_")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)

        rarity = _guess_rarity(base2)
        coins, gems = _price_for_rarity(rarity)
        slot = _guess_slot(base2)

        # thumb: prefer exact frame match if present
        thumb = None
        if fn in frames:
            thumb = fn
        else:
            # find a frame containing the stem
            stem = Path(fn).stem.lower()
            for fr in frames:
                if stem and stem in fr.lower():
                    thumb = fr
                    break
        thumb = thumb or (frames[0] if frames else "")

        items.append(
            {
                "id": item_id,
                "name": base2,
                "slot": slot,
                "rarity": rarity,
                "priceCoins": coins,
                "priceGems": gems,
                "thumb": thumb,
            }
        )

    # Cap size for v1 runtime
    items = items[:120]
    return {"items": items}


# -----------------------------
# Runtime JS generator
# -----------------------------
def build_runtime_js(sample_frames: List[str], catalog: Dict[str, Any]) -> str:
    sample = json.dumps(sample_frames[:60], ensure_ascii=False, indent=2)
    cat = json.dumps(catalog, ensure_ascii=False, indent=2)

    return f"""// TamaCore Runtime (paste into a GDevelop "JavaScript code" event)
// Generated: {datetime.utcnow().isoformat()}Z
// -----------------------------
// Embedded catalog (v1)
// -----------------------------
const TC_CATALOG = {cat};
const TC_SAMPLE_THUMBS = {sample};

// -----------------------------
// GLOBAL SAVE (Storage)
// -----------------------------
function tc_load() {{
  try {{
    const raw = localStorage.getItem("tc_save_v1");
    return raw ? JSON.parse(raw) : null;
  }} catch(e) {{
    console.log("load fail", e);
    return null;
  }}
}}

function tc_save(state) {{
  try {{
    localStorage.setItem("tc_save_v1", JSON.stringify(state));
    return true;
  }} catch(e) {{
    console.log("save fail", e);
    return false;
  }}
}}

// -----------------------------
// DEFAULT STATE
// -----------------------------
function tc_default_state() {{
  return {{
    coins: 1000,
    gems: 25,
    boxes: 3,

    level: 1,
    xp: 0,

    hunger: 100,
    energy: 100,
    clean: 100,

    lastCareAt: Date.now(),
    isDead: false,

    // daily
    dailyChestDay: -1,
    dailyStreak: 0,

    // inventory
    owned: [], // item ids
    equipped: {{ skin:"none", hat:"none", glasses:"none" }},

    // UI memory
    lastToast: "",

    // cooldowns
    cd_adRewardUntil: 0,
    cd_gachaUntil: 0,

    // telemetry counters (local)
    events: {{}},
  }};
}}

// -----------------------------
// HELPERS
// -----------------------------
function tc_day_index(ts) {{ return Math.floor(ts / 86400000); }}
function tc_inc_event(state, key, by=1) {{ state.events[key] = (state.events[key] || 0) + by; }}
function tc_clamp100(x) {{ x = Math.floor(x); return Math.max(0, Math.min(100, x)); }}
function tc_care_ok(state) {{ return state.hunger > 0 && state.energy > 0 && state.clean > 0; }}

function tc_decay(state, dtMs) {{
  // decay per hour
  const dh = dtMs / 3600000.0;
  state.hunger = tc_clamp100(state.hunger - 2.2 * dh);
  state.energy = tc_clamp100(state.energy - 1.6 * dh);
  state.clean  = tc_clamp100(state.clean  - 1.2 * dh);

  if (tc_care_ok(state)) state.lastCareAt = Date.now();

  // 7 day death if any stat is 0 long enough
  if (!state.isDead && !tc_care_ok(state)) {{
    const sevenDays = 7 * 24 * 60 * 60 * 1000;
    if (Date.now() - state.lastCareAt >= sevenDays) {{
      state.isDead = true;
      tc_inc_event(state, "pet_died");
    }}
  }}
}}

function tc_ensure_daily(state) {{
  const di = tc_day_index(Date.now());
  // only chest in v1; quests can be added later
  // keep stub for forward compatibility
}}

function tc_chest_ready(state) {{
  return state.dailyChestDay !== tc_day_index(Date.now());
}}

function tc_claim_chest(state) {{
  if (!tc_chest_ready(state)) return {{ok:false, msg:"Chest already claimed"}};
  const di = tc_day_index(Date.now());
  const prev = state.dailyChestDay;
  state.dailyStreak = (prev === di - 1) ? (state.dailyStreak + 1) : 1;
  state.dailyChestDay = di;

  const coins = 250 + Math.min(10, state.dailyStreak) * 40;
  const gems = (state.dailyStreak % 3 === 0) ? 2 : 1;
  state.coins += coins;
  state.gems += gems;

  tc_inc_event(state, "daily_chest");
  return {{ok:true, msg:`+${{coins}} coins, +${{gems}} gems (streak ${{state.dailyStreak}})`}};
}}

function tc_feed(state) {{
  if (state.isDead) return {{ok:false, msg:"Pet is dead. Revive in shop."}};
  state.hunger = tc_clamp100(state.hunger + 28);
  state.energy = tc_clamp100(state.energy + 6);
  state.coins += 30;
  state.xp += 8;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "feed");
  return {{ok:true, msg:"Fed ✅"}};
}}

function tc_sleep(state) {{
  if (state.isDead) return {{ok:false, msg:"Pet is dead. Revive in shop."}};
  state.energy = tc_clamp100(state.energy + 32);
  state.hunger = tc_clamp100(state.hunger - 6);
  state.xp += 10;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "sleep");
  return {{ok:true, msg:"Slept ✅"}};
}}

function tc_clean(state) {{
  if (state.isDead) return {{ok:false, msg:"Pet is dead. Revive in shop."}};
  state.clean = tc_clamp100(state.clean + 38);
  state.xp += 9;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "clean");
  return {{ok:true, msg:"Cleaned ✅"}};
}}

function tc_revive(state) {{
  const cost = 10;
  if (!state.isDead) return {{ok:false, msg:"Not dead"}};
  if (state.gems < cost) return {{ok:false, msg:"Need 10 gems to revive"}};
  state.gems -= cost;
  state.isDead = false;
  state.hunger = 60;
  state.energy = 60;
  state.clean  = 60;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "revive");
  return {{ok:true, msg:"Revived ✅"}};
}}

function tc_find_item(id) {{
  const items = TC_CATALOG.items || [];
  for (let i=0;i<items.length;i++) if (items[i].id === id) return items[i];
  return null;
}}

function tc_owns(state, id) {{
  return state.owned.indexOf(id) >= 0;
}}

function tc_buy(state, id) {{
  const it = tc_find_item(id);
  if (!it) return {{ok:false, msg:"Item not found"}};
  if (tc_owns(state, id)) return {{ok:false, msg:"Already owned"}};
  if (state.coins < it.priceCoins) return {{ok:false, msg:"Not enough coins"}};
  if (state.gems < it.priceGems) return {{ok:false, msg:"Not enough gems"}};

  state.coins -= it.priceCoins;
  state.gems  -= it.priceGems;
  state.owned.push(id);
  tc_inc_event(state, "buy_" + it.rarity);
  return {{ok:true, msg:`Bought ${{it.name}} ✅`}};
}}

function tc_equip(state, id) {{
  const it = tc_find_item(id);
  if (!it) return {{ok:false, msg:"Item not found"}};
  if (!tc_owns(state, id)) return {{ok:false, msg:"You don't own this"}};
  if (it.slot === "hat") state.equipped.hat = id;
  else if (it.slot === "glasses") state.equipped.glasses = id;
  else if (it.slot === "skin") state.equipped.skin = id;
  else return {{ok:false, msg:"Not equipable"}};

  tc_inc_event(state, "equip_" + it.slot);
  return {{ok:true, msg:`Equipped ${{it.slot}} ✅`}};
}}

// -----------------------------
// GDevelop UI helpers
// -----------------------------
function tc_obj(runtimeScene, name) {{
  const arr = runtimeScene.getObjects(name);
  return arr && arr.length ? arr[0] : null;
}}

function tc_set_text(runtimeScene, name, s) {{
  const t = tc_obj(runtimeScene, name);
  if (t) t.setString(s);
}}

function tc_toast(runtimeScene, msg) {{
  const t = tc_obj(runtimeScene, "TxtToast");
  if (t) t.setString(msg);
}}

function tc_draw_hud(runtimeScene, state) {{
  const h = tc_obj(runtimeScene, "TxtHUD");
  if (!h) return;
  h.setString(
    `Coins: ${{Math.floor(state.coins)}} Gems: ${{Math.floor(state.gems)}} Boxes: ${{Math.floor(state.boxes)}}\\n` +
    `Hunger: ${{Math.floor(state.hunger)}} Energy: ${{Math.floor(state.energy)}} Clean: ${{Math.floor(state.clean)}}\\n` +
    (state.isDead ? "DEAD (Revive in Shop)" : "Alive ✅") + `\\n` +
    `Daily: chest ${{tc_chest_ready(state) ? "READY" : "claimed"}} | streak ${{state.dailyStreak}}`
  );
}}

function tc_apply_equipped(runtimeScene, state) {{
  // overlays are optional; if you don't create PetHat/PetGlasses it won't crash
  const pet = tc_obj(runtimeScene, "Pet");
  const hat = tc_obj(runtimeScene, "PetHat");
  const gla = tc_obj(runtimeScene, "PetGlasses");

  // We only store IDs; visuals are up to your sprite setup.
  // v1 behaviour:
  // - If you use different animations per cosmetic, map them in GDevelop OR use "Change animation" by id.
  // Here we just write small debug strings if TxtInv exists.
  if (hat && state.equipped.hat !== "none") {{
    // you can manually map id->animation in GDevelop later
  }}
  if (gla && state.equipped.glasses !== "none") {{
  }}
  if (pet && state.equipped.skin !== "none") {{
  }}
}}

// -----------------------------
// Click hit-test (simple)
// -----------------------------
function tc_hit(runtimeScene, objName) {{
  const input = runtimeScene.getGame().getInputManager();
  const click = input.isMouseButtonReleased("Left");
  if (!click) return false;
  const o = tc_obj(runtimeScene, objName);
  if (!o) return false;
  const mx = input.getMouseX(runtimeScene);
  const my = input.getMouseY(runtimeScene);
  return mx >= o.getX() && mx <= o.getX() + o.getWidth() && my >= o.getY() && my <= o.getY() + o.getHeight();
}}

// -----------------------------
// Scene-specific UI
// -----------------------------
function tc_render_shop(runtimeScene, state) {{
  const items = (TC_CATALOG.items || []).slice(0, 6);
  // expects Text objects: TxtShop
  let lines = [];
  for (let i=0;i<items.length;i++) {{
    const it = items[i];
    const owned = tc_owns(state, it.id) ? "OWNED" : `${{it.priceCoins}}c/${{it.priceGems}}g`;
    lines.push(`${{i+1}}) [${{it.rarity}}] ${{it.name}} | ${{it.slot}} | ${{owned}}`);
  }}
  tc_set_text(runtimeScene, "TxtShop", "SHOP\\n" + lines.join("\\n") + "\\nTap Slot1..6 to buy. BtnBack to Home.");
}}

function tc_render_inventory(runtimeScene, state) {{
  // expects Text: TxtInv
  const owned = state.owned.slice(0, 6);
  let lines = [];
  for (let i=0;i<owned.length;i++) {{
    const it = tc_find_item(owned[i]);
    if (!it) continue;
    lines.push(`${{i+1}}) [${{it.rarity}}] ${{it.name}} | ${{it.slot}} | tap Inv${{i+1}} to equip`);
  }}
  if (!lines.length) lines = ["(empty) buy items in Shop"];
  tc_set_text(runtimeScene, "TxtInv", "INVENTORY\\n" + lines.join("\\n") + "\\nBtnBack to Home.");
}}

// -----------------------------
// MAIN TICK
// -----------------------------
let __tc_state = null;
let __tc_last = Date.now();

function tc_tick(runtimeScene) {{
  if (!__tc_state) {{
    __tc_state = tc_load() || tc_default_state();
    __tc_last = Date.now();
  }}

  const now = Date.now();
  const dt = Math.min(60000, now - __tc_last);
  __tc_last = now;

  tc_decay(__tc_state, dt);
  tc_ensure_daily(__tc_state);

  // Global buttons on Home
  if (tc_hit(runtimeScene, "BtnFeed")) {{
    tc_toast(runtimeScene, tc_feed(__tc_state).msg);
  }}
  if (tc_hit(runtimeScene, "BtnSleep")) {{
    tc_toast(runtimeScene, tc_sleep(__tc_state).msg);
  }}
  if (tc_hit(runtimeScene, "BtnClean")) {{
    tc_toast(runtimeScene, tc_clean(__tc_state).msg);
  }}
  if (tc_hit(runtimeScene, "BtnChest")) {{
    tc_toast(runtimeScene, tc_claim_chest(__tc_state).msg);
  }}

  // Navigation buttons (optional)
  if (tc_hit(runtimeScene, "BtnShop")) {{
    runtimeScene.getGame().getSceneStack().push("Shop");
    tc_toast(runtimeScene, "Shop 🛒");
  }}
  if (tc_hit(runtimeScene, "BtnInventory")) {{
    runtimeScene.getGame().getSceneStack().push("Inventory");
    tc_toast(runtimeScene, "Inventory 🎒");
  }}
  if (tc_hit(runtimeScene, "BtnBack")) {{
    runtimeScene.getGame().getSceneStack().pop();
    tc_toast(runtimeScene, "Back");
  }}

  // Shop actions (expects Slot1..Slot6 sprites)
  for (let i=1;i<=6;i++) {{
    if (tc_hit(runtimeScene, "Slot" + i)) {{
      const it = (TC_CATALOG.items || [])[i-1];
      if (it) {{
        const r = tc_buy(__tc_state, it.id);
        tc_toast(runtimeScene, r.msg);
      }}
    }}
  }}

  // Inventory equip (expects Inv1..Inv6 sprites)
  for (let i=1;i<=6;i++) {{
    if (tc_hit(runtimeScene, "Inv" + i)) {{
      const id = __tc_state.owned[i-1];
      if (id) {{
        const r = tc_equip(__tc_state, id);
        tc_toast(runtimeScene, r.msg);
      }}
    }}
  }}

  // Shop revive
  if (tc_hit(runtimeScene, "BtnRevive")) {{
    tc_toast(runtimeScene, tc_revive(__tc_state).msg);
  }}

  // Renders
  tc_draw_hud(runtimeScene, __tc_state);
  tc_apply_equipped(runtimeScene, __tc_state);

  // Scene info text (only if objects exist)
  tc_render_shop(runtimeScene, __tc_state);
  tc_render_inventory(runtimeScene, __tc_state);

  // autosave every ~10s
  if (now % 10000 < 30) tc_save(__tc_state);
}}
"""


def build_scene_layouts() -> Dict[str, List[Dict[str, Any]]]:
    # Quick placement plan; you can move later.
    return {
        "Home": [
            {"name": "TxtHUD", "type": "Text", "x": 40, "y": 30},
            {"name": "TxtToast", "type": "Text", "x": 40, "y": 240},

            {"name": "Pet", "type": "Sprite", "x": 260, "y": 520},
            {"name": "PetHat", "type": "Sprite", "x": 260, "y": 520},
            {"name": "PetGlasses", "type": "Sprite", "x": 260, "y": 520},

            {"name": "BtnFeed", "type": "Sprite", "x": 40, "y": 900},
            {"name": "BtnSleep", "type": "Sprite", "x": 260, "y": 900},
            {"name": "BtnClean", "type": "Sprite", "x": 480, "y": 900},
            {"name": "BtnChest", "type": "Sprite", "x": 520, "y": 700},

            {"name": "BtnShop", "type": "Sprite", "x": 40, "y": 1020},
            {"name": "BtnInventory", "type": "Sprite", "x": 260, "y": 1020},
        ],
        "Shop": [
            {"name": "TxtHUD", "type": "Text", "x": 40, "y": 30},
            {"name": "TxtToast", "type": "Text", "x": 40, "y": 240},
            {"name": "TxtShop", "type": "Text", "x": 40, "y": 320},

            {"name": "Slot1", "type": "Sprite", "x": 40, "y": 720},
            {"name": "Slot2", "type": "Sprite", "x": 240, "y": 720},
            {"name": "Slot3", "type": "Sprite", "x": 440, "y": 720},
            {"name": "Slot4", "type": "Sprite", "x": 40, "y": 860},
            {"name": "Slot5", "type": "Sprite", "x": 240, "y": 860},
            {"name": "Slot6", "type": "Sprite", "x": 440, "y": 860},

            {"name": "BtnRevive", "type": "Sprite", "x": 260, "y": 980},
            {"name": "BtnBack", "type": "Sprite", "x": 40, "y": 1020},
        ],
        "Inventory": [
            {"name": "TxtHUD", "type": "Text", "x": 40, "y": 30},
            {"name": "TxtToast", "type": "Text", "x": 40, "y": 240},
            {"name": "TxtInv", "type": "Text", "x": 40, "y": 320},

            {"name": "Inv1", "type": "Sprite", "x": 40, "y": 720},
            {"name": "Inv2", "type": "Sprite", "x": 240, "y": 720},
            {"name": "Inv3", "type": "Sprite", "x": 440, "y": 720},
            {"name": "Inv4", "type": "Sprite", "x": 40, "y": 860},
            {"name": "Inv5", "type": "Sprite", "x": 240, "y": 860},
            {"name": "Inv6", "type": "Sprite", "x": 440, "y": 860},

            {"name": "BtnBack", "type": "Sprite", "x": 40, "y": 1020},
        ],
        "Activity": [
            {"name": "TxtHUD", "type": "Text", "x": 40, "y": 30},
            {"name": "TxtToast", "type": "Text", "x": 40, "y": 240},
            {"name": "BtnBack", "type": "Sprite", "x": 40, "y": 1020},
        ],
    }


def build_import_checklist() -> str:
    return """# GDevelop Import Checklist (TamaCore)

## 1) Import assets (Atlas)
1. Project manager → Resources
2. Add → Image → select: output/gdevelop_pack/assets/atlas.png
3. Optional: if your GDevelop supports atlas JSON import:
   - Import spritesheet/atlas frames using output/gdevelop_pack/assets/atlas.json

If your version doesn't support atlas-json directly:
- you can still run the game using any placeholder images for buttons/slots.

## 2) Create scenes
Create scenes:
- Home
- Shop
- Inventory
(Optional: Activity)

## 3) Create objects (same names)
Text:
- TxtHUD
- TxtToast
- TxtShop (only in Shop scene)
- TxtInv  (only in Inventory scene)

Sprites (buttons / slots / pet / overlays):
Home:
- BtnFeed BtnSleep BtnClean BtnChest BtnShop BtnInventory
- Pet PetHat PetGlasses

Shop:
- Slot1 Slot2 Slot3 Slot4 Slot5 Slot6
- BtnRevive
- BtnBack

Inventory:
- Inv1 Inv2 Inv3 Inv4 Inv5 Inv6
- BtnBack

## 4) Add ONE JavaScript event per scene
Events → Add event → JavaScript code
Paste contents from:
- output/gdevelop_pack/code/tamacore_runtime.js

Then inside that JS event, call each frame:
- tc_tick(runtimeScene);

## 5) Position objects quickly
Use layout positions from:
- output/gdevelop_pack/docs/layouts.json

## 6) Test (what should work now)
Home:
- Feed/Sleep/Clean change stats
- Daily chest works

Shop:
- Tap Slot1..Slot6 to buy first 6 catalog items
- Revive works (costs gems)

Inventory:
- Shows owned items (first 6)
- Tap Inv1..Inv6 to equip (hat/glasses/skin)

Notes:
- Visuals for equip (PetHat/PetGlasses/Pet skin) are intentionally left “mapping-ready”.
  Next sprint will auto-map item id → atlas frame → animation/frame swap.
"""


def main():
    safe_mkdir(PACK)
    safe_mkdir(ASSETS)
    safe_mkdir(CODE)
    safe_mkdir(DOCS)

    # Copy atlas if exists
    if ATLAS_PNG.exists() and ATLAS_JSON.exists():
        copy_if_exists(ATLAS_PNG, ASSETS / "atlas.png")
        copy_if_exists(ATLAS_JSON, ASSETS / "atlas.json")
    else:
        print("[!] Atlas missing. Run atlas_pack.py first to generate atlas.png/json")

    frames = load_frames_from_atlas()
    mapping = load_mapping()

    catalog = build_catalog(frames, mapping)

    runtime = build_runtime_js(frames, catalog)
    write_text(CODE / "tamacore_runtime.js", runtime)

    layouts = build_scene_layouts()
    write_json(DOCS / "layouts.json", layouts)

    write_text(DOCS / "IMPORT_CHECKLIST.md", build_import_checklist())

    # Also copy mapping.json for reference
    copy_if_exists(MAPPING, DOCS / "mapping.json")

    # Export catalog for debugging
    write_json(DOCS / "catalog.json", catalog)

    print("[✓] GDevelop pack generated at:", PACK)
    print(" - assets/atlas.png + atlas.json")
    print(" - code/tamacore_runtime.js")
    print(" - docs/IMPORT_CHECKLIST.md + layouts.json + catalog.json")


if __name__ == "__main__":
    main()
