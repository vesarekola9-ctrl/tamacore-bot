from pathlib import Path
import json
import shutil
from datetime import datetime

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

def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def copy_if_exists(src: Path, dst: Path):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def load_frames_from_atlas():
    if not ATLAS_JSON.exists():
        return []
    data = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    frames = list(data.get("frames", {}).keys())
    # return only filenames (good for thumbnails)
    return frames[:60]  # cap for UI preview

def build_runtime_js(sample_frames):
    # Use atlas frame names as example thumbnails for shop/inventory.
    # GDevelop side: create Sprite objects that use atlas frames OR individual images.
    sample = json.dumps(sample_frames, ensure_ascii=False, indent=2)

    return f"""// TamaCore Runtime (paste into a GDevelop "JavaScript code" event)
// Generated: {datetime.utcnow().isoformat()}Z

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
    questDay: -1,
    q_feed: 0,
    q_play: 0,
    q_shop: 0,

    // inventory
    owned: [],               // item ids
    equipped: {{ skin:"none", hat:"none", glasses:"none" }},

    // cooldowns
    cd_adRewardUntil: 0,
    cd_gachaUntil: 0,

    // shop offers
    offerEndsAt: 0,
    offerId: "",
    offerPriceCoins: 0,
    offerPriceGems: 0,

    // telemetry counters (local)
    events: {{}},
  }};
}}

// -----------------------------
// HELPERS
// -----------------------------
function tc_day_index(ts) {{
  return Math.floor(ts / 86400000);
}}

function tc_inc_event(state, key, by=1) {{
  state.events[key] = (state.events[key] || 0) + by;
}}

function tc_clamp100(x) {{
  x = Math.floor(x);
  return Math.max(0, Math.min(100, x));
}}

function tc_care_ok(state) {{
  return state.hunger > 0 && state.energy > 0 && state.clean > 0;
}}

function tc_decay(state, dtMs) {{
  // decay per hour
  const dh = dtMs / 3600000.0;
  state.hunger = tc_clamp100(state.hunger - 2.2 * dh);
  state.energy = tc_clamp100(state.energy - 1.6 * dh);
  state.clean  = tc_clamp100(state.clean  - 1.2 * dh);

  if (tc_care_ok(state)) state.lastCareAt = Date.now();

  // 7 day death if any stat is 0 for long time
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
  if (state.questDay !== di) {{
    state.questDay = di;
    state.q_feed = 0; state.q_play = 0; state.q_shop = 0;
    tc_inc_event(state, "daily_reset");
  }}
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
  const gems  = (state.dailyStreak % 3 === 0) ? 2 : 1;

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
  tc_ensure_daily(state);
  state.q_feed += 1;
  tc_inc_event(state, "feed");
  return {{ok:true, msg:"Fed 🍗"}};
}}

function tc_sleep(state) {{
  if (state.isDead) return {{ok:false, msg:"Pet is dead. Revive in shop."}};
  state.energy = tc_clamp100(state.energy + 32);
  state.hunger = tc_clamp100(state.hunger - 6);
  state.xp += 10;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "sleep");
  return {{ok:true, msg:"Slept 😴"}};
}}

function tc_clean(state) {{
  if (state.isDead) return {{ok:false, msg:"Pet is dead. Revive in shop."}};
  state.clean = tc_clamp100(state.clean + 38);
  state.xp += 9;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "clean");
  return {{ok:true, msg:"Cleaned 🧼"}};
}}

function tc_revive(state) {{
  const cost = 10;
  if (!state.isDead) return {{ok:false, msg:"Not dead"}};
  if (state.gems < cost) return {{ok:false, msg:"Need 10 gems to revive"}};
  state.gems -= cost;
  state.isDead = false;
  state.hunger = 60; state.energy = 60; state.clean = 60;
  state.lastCareAt = Date.now();
  tc_inc_event(state, "revive");
  return {{ok:true, msg:"Revived ✅"}};
}}

// -----------------------------
// SHOP / INVENTORY (PRO scaffold)
// -----------------------------
// Example thumbnails list from atlas (optional):
const TC_SAMPLE_THUMBS = {sample};

// -----------------------------
// GDevelop HOOKS
// -----------------------------
// Expected scene objects (names):
// Text: TxtHUD, TxtToast
// Buttons sprites: BtnFeed BtnSleep BtnClean BtnChest BtnShop BtnInventory BtnPlay BtnBack BtnRevive
//
// In each frame, call tc_tick(runtimeScene).

function tc_toast(runtimeScene, msg) {{
  const t = runtimeScene.getObjects("TxtToast")[0];
  if (t) t.setString(msg);
}}

function tc_draw_hud(runtimeScene, state) {{
  const h = runtimeScene.getObjects("TxtHUD")[0];
  if (!h) return;
  h.setString(
    `Coins: ${{Math.floor(state.coins)}}  Gems: ${{Math.floor(state.gems)}}  Boxes: ${{Math.floor(state.boxes)}}\\n` +
    `Hunger: ${{Math.floor(state.hunger)}}  Energy: ${{Math.floor(state.energy)}}  Clean: ${{Math.floor(state.clean)}}\\n` +
    (state.isDead ? "💀 DEAD (Revive in Shop)" : "Alive ✅") + `\\n` +
    `Daily: chest ${{tc_chest_ready(state) ? "READY" : "claimed"}} | streak ${{state.dailyStreak}}`
  );
}}

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

  // simple click hit-test via cursor+bounding box
  const input = runtimeScene.getGame().getInputManager();
  const click = input.isMouseButtonReleased("Left");
  const mx = input.getMouseX(runtimeScene);
  const my = input.getMouseY(runtimeScene);

  function hit(objName) {{
    if (!click) return false;
    const o = runtimeScene.getObjects(objName)[0];
    if (!o) return false;
    return mx >= o.getX() && mx <= o.getX() + o.getWidth() &&
           my >= o.getY() && my <= o.getY() + o.getHeight();
  }}

  if (hit("BtnFeed")) {{
    const r = tc_feed(__tc_state); tc_toast(runtimeScene, r.msg);
  }}
  if (hit("BtnSleep")) {{
    const r = tc_sleep(__tc_state); tc_toast(runtimeScene, r.msg);
  }}
  if (hit("BtnClean")) {{
    const r = tc_clean(__tc_state); tc_toast(runtimeScene, r.msg);
  }}
  if (hit("BtnChest")) {{
    const r = tc_claim_chest(__tc_state); tc_toast(runtimeScene, r.msg);
  }}
  if (hit("BtnRevive")) {{
    const r = tc_revive(__tc_state); tc_toast(runtimeScene, r.msg);
  }}

  // autosave every ~10s
  if (now % 10000 < 30) tc_save(__tc_state);

  tc_draw_hud(runtimeScene, __tc_state);
}}
"""

def build_scene_layouts():
    # Provide a simple coordinate plan for objects in Home.
    # User creates objects with these names; then positions quickly.
    return {
        "Home": [
            {"name":"TxtHUD","type":"Text","x":40,"y":30},
            {"name":"TxtToast","type":"Text","x":40,"y":250},
            {"name":"BtnFeed","type":"Sprite","x":40,"y":900},
            {"name":"BtnSleep","type":"Sprite","x":260,"y":900},
            {"name":"BtnClean","type":"Sprite","x":480,"y":900},
            {"name":"BtnChest","type":"Sprite","x":520,"y":700},
            {"name":"BtnShop","type":"Sprite","x":40,"y":1020},
            {"name":"BtnInventory","type":"Sprite","x":260,"y":1020},
            {"name":"BtnPlay","type":"Sprite","x":480,"y":1020},
            {"name":"Pet","type":"Sprite","x":260,"y":520},
            {"name":"PetHat","type":"Sprite","x":260,"y":520},
            {"name":"PetGlasses","type":"Sprite","x":260,"y":520},
        ],
        "Shop": [
            {"name":"TxtHUD","type":"Text","x":40,"y":30},
            {"name":"TxtToast","type":"Text","x":40,"y":250},
            {"name":"BtnRevive","type":"Sprite","x":260,"y":900},
            {"name":"BtnBack","type":"Sprite","x":40,"y":1020},
        ],
        "Inventory": [
            {"name":"TxtHUD","type":"Text","x":40,"y":30},
            {"name":"TxtToast","type":"Text","x":40,"y":250},
            {"name":"BtnBack","type":"Sprite","x":40,"y":1020},
        ],
        "Activity": [
            {"name":"TxtHUD","type":"Text","x":40,"y":30},
            {"name":"TxtToast","type":"Text","x":40,"y":250},
            {"name":"BtnBack","type":"Sprite","x":40,"y":1020},
        ],
    }

def build_import_checklist():
    return """# GDevelop Import Checklist (TamaCore)

## 1) Import assets (Atlas)
1. Project manager → Resources
2. Add → Image → select: output/gdevelop_pack/assets/atlas.png
3. (Optional) If your GDevelop supports atlas JSON import:
   - Import spritesheet/atlas frames using output/gdevelop_pack/assets/atlas.json

If your version doesn't support atlas-json directly:
- skip atlas frames and use individual PNGs from output/assets_raw/* instead.

## 2) Create these scenes
Create scenes:
- Home
- Shop
- Inventory
- Activity

## 3) Create these objects (same names)
Create objects (you can use any image for now, then swap later):
Text:
- TxtHUD
- TxtToast

Sprites (buttons / pet / overlays):
- BtnFeed BtnSleep BtnClean BtnChest BtnShop BtnInventory BtnPlay
- BtnBack BtnRevive
- Pet PetHat PetGlasses

## 4) Add ONE JavaScript event per scene
Events → Add event → JavaScript code
Paste contents from:
output/gdevelop_pack/code/tamacore_runtime.js

Then inside that JS event, add at bottom:
tc_tick(runtimeScene);

(Or if you already pasted the full file: keep it as-is and just call tc_tick.)

## 5) Position objects quickly
Use layout positions from:
output/gdevelop_pack/docs/layouts.json

## 6) Test
Run preview in GDevelop:
- Feed/Sleep/Clean change stats
- Daily chest works
- Death after 7 days of neglect (simulated if stats hit 0)
- Revive costs gems

Next: we'll add Shop thumbnails, Inventory paging, Equip overlays, cooldowns, gacha & rarity glow.
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
    runtime = build_runtime_js(frames)
    write_text(CODE / "tamacore_runtime.js", runtime)

    layouts = build_scene_layouts()
    write_text(DOCS / "layouts.json", json.dumps(layouts, indent=2, ensure_ascii=False))
    write_text(DOCS / "IMPORT_CHECKLIST.md", build_import_checklist())

    # Also copy mapping.json for reference
    copy_if_exists(MAPPING, DOCS / "mapping.json")

    print("[✓] GDevelop pack generated at:", PACK)
    print("    - assets/atlas.png + atlas.json")
    print("    - code/tamacore_runtime.js")
    print("    - docs/IMPORT_CHECKLIST.md + layouts.json")

if __name__ == "__main__":
    main()
