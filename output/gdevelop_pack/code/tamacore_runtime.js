// TamaCore Runtime PRO (GDevelop JavaScript event)
// Paste this into a single JavaScript event per scene, then call:
// tc_tick(runtimeScene);
//
// Scenes expected: Home, Shop, Inventory, Activity
// Objects expected (create as Sprite/Text objects in each scene):
//
// Text: TxtHUD, TxtToast, TxtTitle
//
// Home buttons: BtnFeed BtnSleep BtnClean BtnChest BtnShop BtnInventory BtnPlay
// Shop buttons: BtnBack BtnBuy BtnRevive BtnReroll
// Inventory buttons: BtnBack BtnPrevPage BtnNextPage BtnEquip BtnUnequip
//
// Pet sprites: Pet, PetHat, PetGlasses, PetSkinOverlay (optional)
//
// Shop UI: ShopThumb0..ShopThumb11, ShopPreview, TxtShopInfo, TxtPrice
// Inventory UI: InvThumb0..InvThumb11, InvPreview, TxtInvInfo, TxtPage
//
// Optional: GlowBadge (Sprite) + TxtRarity (Text)

function tc_load() {
  try {
    const raw = localStorage.getItem("tc_save_v2");
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    console.log("load fail", e);
    return null;
  }
}

function tc_save(state) {
  try {
    localStorage.setItem("tc_save_v2", JSON.stringify(state));
    return true;
  } catch (e) {
    console.log("save fail", e);
    return false;
  }
}

function tc_day_index(ts) {
  return Math.floor(ts / 86400000);
}
function tc_now() { return Date.now(); }
function tc_clamp100(x) { x = Math.floor(x); return Math.max(0, Math.min(100, x)); }
function tc_rand(seed) { // deterministic-ish
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function tc_default_state() {
  return {
    version: 2,

    coins: 1000,
    gems: 25,

    hunger: 100,
    energy: 100,
    clean: 100,

    // death timer
    lastCareAt: tc_now(),
    isDead: false,

    // daily + quests
    dailyChestDay: -1,
    dailyStreak: 0,
    questDay: -1,
    q_feed: 0,
    q_play: 0,
    q_shop: 0,

    // inventory + cosmetics
    owned: ["skin_basic", "hat_none", "glasses_none"],
    equipped: { skin: "skin_basic", hat: "hat_none", glasses: "glasses_none" },

    // cooldowns
    cd_adRewardUntil: 0,
    cd_gachaUntil: 0,

    // shop rotation / bundle offers
    shopRotSeed: 12345,
    shopRotDay: -1,
    shopFeatured: [],

    // selection UI
    ui_selectedShopId: "",
    ui_selectedInvId: "",
    ui_invPage: 0,

    // pet animation state
    petMood: "neutral", // neutral, happy, tired, dirty, hungry, dead
    petBlinkUntil: 0,
    petEmoteUntil: 0,

    events: {}
  };
}

function tc_inc_event(state, key, by = 1) {
  state.events[key] = (state.events[key] || 0) + by;
}

function tc_care_ok(state) {
  return state.hunger > 0 && state.energy > 0 && state.clean > 0;
}

function tc_decay(state, dtMs) {
  const dh = dtMs / 3600000.0;

  state.hunger = tc_clamp100(state.hunger - 2.2 * dh);
  state.energy = tc_clamp100(state.energy - 1.6 * dh);
  state.clean  = tc_clamp100(state.clean  - 1.2 * dh);

  if (tc_care_ok(state)) state.lastCareAt = tc_now();

  if (!state.isDead && !tc_care_ok(state)) {
    const sevenDays = 7 * 24 * 60 * 60 * 1000;
    if (tc_now() - state.lastCareAt >= sevenDays) {
      state.isDead = true;
      state.petMood = "dead";
      tc_inc_event(state, "pet_died");
    }
  }
}

function tc_ensure_daily(state) {
  const di = tc_day_index(tc_now());
  if (state.questDay !== di) {
    state.questDay = di;
    state.q_feed = 0; state.q_play = 0; state.q_shop = 0;
    tc_inc_event(state, "daily_reset");
  }
}

function tc_chest_ready(state) {
  return state.dailyChestDay !== tc_day_index(tc_now());
}

function tc_claim_chest(state) {
  if (!tc_chest_ready(state)) return { ok:false, msg:"Daily chest already claimed." };

  const di = tc_day_index(tc_now());
  const prev = state.dailyChestDay;
  state.dailyStreak = (prev === di - 1) ? (state.dailyStreak + 1) : 1;
  state.dailyChestDay = di;

  const coins = 250 + Math.min(10, state.dailyStreak) * 40;
  const gems  = (state.dailyStreak % 3 === 0) ? 2 : 1;

  state.coins += coins;
  state.gems += gems;

  tc_inc_event(state, "daily_chest");
  return { ok:true, msg:`Daily chest: +${coins} coins, +${gems} gems (streak ${state.dailyStreak})` };
}

// -----------------------------
// ECONOMY + ITEMS (PRO)
// -----------------------------
const TC_ITEMS = [
  // skins
  { id:"skin_basic", type:"skin", rarity:"common", priceCoins:0,  priceGems:0,  thumb:"skin_basic" },
  { id:"skin_red",   type:"skin", rarity:"common", priceCoins:600, priceGems:0,  thumb:"skin_red" },
  { id:"skin_neon",  type:"skin", rarity:"rare",   priceCoins:0,  priceGems:12, thumb:"skin_neon" },

  // hats
  { id:"hat_none",   type:"hat", rarity:"common", priceCoins:0,  priceGems:0,  thumb:"hat_none" },
  { id:"hat_cap",    type:"hat", rarity:"common", priceCoins:400, priceGems:0,  thumb:"hat_cap" },
  { id:"hat_crown",  type:"hat", rarity:"epic",   priceCoins:0,  priceGems:25, thumb:"hat_crown" },

  // glasses
  { id:"glasses_none", type:"glasses", rarity:"common", priceCoins:0, priceGems:0, thumb:"glasses_none" },
  { id:"glasses_round",type:"glasses", rarity:"common", priceCoins:350,priceGems:0, thumb:"glasses_round" },
  { id:"glasses_star", type:"glasses", rarity:"rare",   priceCoins:0, priceGems:10, thumb:"glasses_star" },
];

const TC_RARITY = {
  common: { label:"COMMON", glow:0 },
  rare:   { label:"RARE", glow:1 },
  epic:   { label:"EPIC", glow:2 },
  mythic: { label:"MYTHIC", glow:3 },
};

function tc_item_by_id(id) {
  return TC_ITEMS.find(x => x.id === id) || null;
}

function tc_has(state, id) {
  return state.owned.indexOf(id) >= 0;
}

function tc_add_item(state, id) {
  if (!tc_has(state, id)) state.owned.push(id);
}

function tc_can_afford(state, item) {
  if (!item) return false;
  if (item.priceCoins > 0) return state.coins >= item.priceCoins;
  if (item.priceGems > 0) return state.gems >= item.priceGems;
  return true;
}

function tc_pay(state, item) {
  if (!item) return false;
  if (item.priceCoins > 0) state.coins -= item.priceCoins;
  if (item.priceGems > 0) state.gems -= item.priceGems;
  return true;
}

function tc_equip(state, itemId) {
  const it = tc_item_by_id(itemId);
  if (!it) return { ok:false, msg:"Unknown item" };
  if (!tc_has(state, itemId)) return { ok:false, msg:"You don't own this item." };

  if (it.type === "skin") state.equipped.skin = itemId;
  if (it.type === "hat") state.equipped.hat = itemId;
  if (it.type === "glasses") state.equipped.glasses = itemId;

  tc_inc_event(state, "equip");
  return { ok:true, msg:`Equipped ${itemId}` };
}

function tc_unequip(state, type) {
  if (type === "hat") state.equipped.hat = "hat_none";
  if (type === "glasses") state.equipped.glasses = "glasses_none";
  if (type === "skin") state.equipped.skin = "skin_basic";
  tc_inc_event(state, "unequip");
  return { ok:true, msg:`Unequipped ${type}` };
}

// -----------------------------
// SHOP ROTATION + BUNDLES
// -----------------------------
function tc_shop_rotate(state) {
  const di = tc_day_index(tc_now());
  if (state.shopRotDay === di && state.shopFeatured.length) return;

  state.shopRotDay = di;
  state.shopFeatured = [];

  // pick 6 non-free items deterministically per day
  const pool = TC_ITEMS.filter(it => (it.priceCoins > 0 || it.priceGems > 0));
  const seed = di + state.shopRotSeed;
  const picked = [];
  for (let i=0; i<pool.length; i++) {
    const r = tc_rand(seed + i*97.13);
    picked.push({ r, it: pool[i] });
  }
  picked.sort((a,b)=>a.r-b.r);
  state.shopFeatured = picked.slice(0, 6).map(x => x.it.id);

  // default selection
  state.ui_selectedShopId = state.shopFeatured[0] || "";

  tc_inc_event(state, "shop_rotate");
}

function tc_buy_selected(state) {
  const id = state.ui_selectedShopId;
  const it = tc_item_by_id(id);
  if (!it) return { ok:false, msg:"Select an item." };
  if (tc_has(state, id)) return { ok:false, msg:"Already owned." };
  if (!tc_can_afford(state, it)) return { ok:false, msg:"Not enough coins/gems." };

  tc_pay(state, it);
  tc_add_item(state, id);

  tc_ensure_daily(state);
  state.q_shop += 1;
  tc_inc_event(state, "buy");
  return { ok:true, msg:`Bought ${id}` };
}

// -----------------------------
// PET CARE ACTIONS
// -----------------------------
function tc_set_mood(state) {
  if (state.isDead) { state.petMood = "dead"; return; }

  if (state.hunger <= 20) state.petMood = "hungry";
  else if (state.clean <= 20) state.petMood = "dirty";
  else if (state.energy <= 20) state.petMood = "tired";
  else state.petMood = "neutral";
}

function tc_blink(state) {
  // blink randomly
  if (state.petBlinkUntil > tc_now()) return;
  const r = Math.random();
  if (r < 0.01) { // ~1% tick
    state.petBlinkUntil = tc_now() + 160;
  }
}

function tc_emote(state, kind) {
  state.petEmoteUntil = tc_now() + 900;
  state.petMood = kind;
}

function tc_feed(state) {
  if (state.isDead) return { ok:false, msg:"Pet is dead. Revive in Shop." };
  state.hunger = tc_clamp100(state.hunger + 28);
  state.energy = tc_clamp100(state.energy + 6);
  state.coins += 30;
  state.lastCareAt = tc_now();

  tc_ensure_daily(state);
  state.q_feed += 1;

  tc_emote(state, "happy");
  tc_inc_event(state, "feed");
  return { ok:true, msg:"Fed 🍗" };
}

function tc_sleep(state) {
  if (state.isDead) return { ok:false, msg:"Pet is dead. Revive in Shop." };
  state.energy = tc_clamp100(state.energy + 32);
  state.hunger = tc_clamp100(state.hunger - 6);
  state.lastCareAt = tc_now();

  tc_emote(state, "tired");
  tc_inc_event(state, "sleep");
  return { ok:true, msg:"Slept 😴" };
}

function tc_clean(state) {
  if (state.isDead) return { ok:false, msg:"Pet is dead. Revive in Shop." };
  state.clean = tc_clamp100(state.clean + 38);
  state.lastCareAt = tc_now();

  tc_emote(state, "happy");
  tc_inc_event(state, "clean");
  return { ok:true, msg:"Cleaned 🧼" };
}

function tc_revive(state) {
  const cost = 10;
  if (!state.isDead) return { ok:false, msg:"Not dead." };
  if (state.gems < cost) return { ok:false, msg:"Need 10 gems to revive." };

  state.gems -= cost;
  state.isDead = false;
  state.hunger = 60; state.energy = 60; state.clean = 60;
  state.lastCareAt = tc_now();

  tc_inc_event(state, "revive");
  return { ok:true, msg:"Revived ✅" };
}

// -----------------------------
// UI / GDevelop helpers
// -----------------------------
function tc_obj(scene, name) {
  const arr = scene.getObjects(name);
  return (arr && arr.length) ? arr[0] : null;
}

function tc_set_text(scene, name, text) {
  const o = tc_obj(scene, name);
  if (o) o.setString(String(text));
}

function tc_mouse(scene) {
  const input = scene.getGame().getInputManager();
  return {
    click: input.isMouseButtonReleased("Left") || input.isTouchEnded(),
    mx: input.getMouseX(scene),
    my: input.getMouseY(scene),
  };
}

function tc_hit(scene, objName, mouse) {
  if (!mouse.click) return false;
  const o = tc_obj(scene, objName);
  if (!o) return false;
  const x = o.getX(), y = o.getY(), w = o.getWidth(), h = o.getHeight();
  return mouse.mx >= x && mouse.mx <= x + w && mouse.my >= y && mouse.my <= y + h;
}

function tc_toast(scene, msg) {
  tc_set_text(scene, "TxtToast", msg);
}

function tc_draw_hud(scene, state) {
  const lines = [
    `Coins: ${Math.floor(state.coins)}   Gems: ${Math.floor(state.gems)}`,
    `Hunger: ${Math.floor(state.hunger)}  Energy: ${Math.floor(state.energy)}  Clean: ${Math.floor(state.clean)}`,
    state.isDead ? "💀 DEAD (Revive in Shop)" : `Mood: ${state.petMood}`,
    `Daily chest: ${tc_chest_ready(state) ? "READY" : "claimed"} | streak ${state.dailyStreak}`,
    `Quests today: feed ${state.q_feed}/3 | play ${state.q_play}/1 | shop ${state.q_shop}/1`,
  ];
  tc_set_text(scene, "TxtHUD", lines.join("\n"));
}

function tc_apply_equipped_overlays(scene, state) {
  // This assumes you created Pet, PetHat, PetGlasses, PetSkinOverlay sprites.
  // You must assign each cosmetic an animation name matching item id (or swap image manually).
  // Minimal: update visibility / title text only.
  const hat = tc_obj(scene, "PetHat");
  const gla = tc_obj(scene, "PetGlasses");
  const skin = tc_obj(scene, "PetSkinOverlay");

  if (hat) hat.hide(state.equipped.hat === "hat_none");
  if (gla) gla.hide(state.equipped.glasses === "glasses_none");
  if (skin) skin.hide(false);

  // If you set animations with same names, enable:
  try {
    if (hat && hat.getAnimationName && hat.setAnimationName) hat.setAnimationName(state.equipped.hat);
    if (gla && gla.getAnimationName && gla.setAnimationName) gla.setAnimationName(state.equipped.glasses);
    if (skin && skin.getAnimationName && skin.setAnimationName) skin.setAnimationName(state.equipped.skin);
  } catch(e) {}
}

function tc_draw_shop(scene, state) {
  tc_shop_rotate(state);

  // fill thumb slots
  for (let i=0; i<12; i++) {
    const o = tc_obj(scene, "ShopThumb"+i);
    if (!o) continue;

    const id = state.shopFeatured[i] || "";
    o.hide(!id);

    // optional: set animation name to id
    try { if (id && o.setAnimationName) o.setAnimationName(id); } catch(e) {}

    // store id on instance variable if possible
    try { o.getVariables().get("itemId").setString(id); } catch(e) {}
  }

  const sel = tc_item_by_id(state.ui_selectedShopId);
  if (sel) {
    tc_set_text(scene, "TxtShopInfo", `${sel.id}\n${TC_RARITY[sel.rarity].label}  (${sel.type})`);
    tc_set_text(scene, "TxtPrice", sel.priceCoins>0 ? `${sel.priceCoins} coins` : `${sel.priceGems} gems`);
  } else {
    tc_set_text(scene, "TxtShopInfo", "Select item");
    tc_set_text(scene, "TxtPrice", "");
  }

  // rarity glow badge scaffold
  const badge = tc_obj(scene, "GlowBadge");
  const rt = tc_obj(scene, "TxtRarity");
  if (sel && badge) badge.hide(false);
  if (sel && rt) rt.setString(TC_RARITY[sel.rarity].label);
}

function tc_draw_inventory(scene, state) {
  const perPage = 12;
  const page = Math.max(0, state.ui_invPage);
  const start = page * perPage;

  const owned = state.owned.slice().filter(id => id !== "hat_none" && id !== "glasses_none"); // keep list clean
  const pageItems = owned.slice(start, start + perPage);

  for (let i=0; i<12; i++) {
    const o = tc_obj(scene, "InvThumb"+i);
    if (!o) continue;

    const id = pageItems[i] || "";
    o.hide(!id);

    try { if (id && o.setAnimationName) o.setAnimationName(id); } catch(e) {}
    try { o.getVariables().get("itemId").setString(id); } catch(e) {}
  }

  const maxPage = Math.max(0, Math.floor((owned.length - 1) / perPage));
  state.ui_invPage = Math.min(state.ui_invPage, maxPage);

  tc_set_text(scene, "TxtPage", `Page ${state.ui_invPage+1}/${maxPage+1}`);

  const sel = tc_item_by_id(state.ui_selectedInvId);
  if (sel) {
    const eq = (state.equipped[sel.type] === sel.id);
    tc_set_text(scene, "TxtInvInfo", `${sel.id}\n${TC_RARITY[sel.rarity].label} (${sel.type})\n${eq ? "EQUIPPED" : ""}`);
  } else {
    tc_set_text(scene, "TxtInvInfo", "Select owned item");
  }
}

// -----------------------------
// MAIN TICK
// -----------------------------
let __tc_state = null;
let __tc_last = tc_now();

function tc_tick(runtimeScene) {
  if (!__tc_state) {
    __tc_state = tc_load() || tc_default_state();
    __tc_last = tc_now();
  }

  const now = tc_now();
  const dt = Math.min(60000, now - __tc_last);
  __tc_last = now;

  tc_decay(__tc_state, dt);
  tc_ensure_daily(__tc_state);
  tc_set_mood(__tc_state);
  tc_blink(__tc_state);

  const mouse = tc_mouse(runtimeScene);
  const sceneName = runtimeScene.getName();

  // --- Scene navigation buttons (common) ---
  if (tc_hit(runtimeScene, "BtnShop", mouse)) {
    runtimeScene.getGame().getSceneStack().push("Shop");
    tc_toast(runtimeScene, "Shop");
  }
  if (tc_hit(runtimeScene, "BtnInventory", mouse)) {
    runtimeScene.getGame().getSceneStack().push("Inventory");
    tc_toast(runtimeScene, "Inventory");
  }
  if (tc_hit(runtimeScene, "BtnPlay", mouse)) {
    __tc_state.q_play += 1;
    tc_inc_event(__tc_state, "play");
    runtimeScene.getGame().getSceneStack().push("Activity");
    tc_toast(runtimeScene, "Activity");
  }
  if (tc_hit(runtimeScene, "BtnBack", mouse)) {
    runtimeScene.getGame().getSceneStack().pop();
  }

  // --- HOME ---
  if (sceneName === "Home") {
    if (tc_hit(runtimeScene, "BtnFeed", mouse)) {
      const r = tc_feed(__tc_state); tc_toast(runtimeScene, r.msg);
    }
    if (tc_hit(runtimeScene, "BtnSleep", mouse)) {
      const r = tc_sleep(__tc_state); tc_toast(runtimeScene, r.msg);
    }
    if (tc_hit(runtimeScene, "BtnClean", mouse)) {
      const r = tc_clean(__tc_state); tc_toast(runtimeScene, r.msg);
    }
    if (tc_hit(runtimeScene, "BtnChest", mouse)) {
      const r = tc_claim_chest(__tc_state); tc_toast(runtimeScene, r.msg);
    }

    tc_apply_equipped_overlays(runtimeScene, __tc_state);
  }

  // --- SHOP ---
  if (sceneName === "Shop") {
    tc_shop_rotate(__tc_state);

    // click thumbnails
    for (let i=0; i<12; i++) {
      const name = "ShopThumb"+i;
      if (tc_hit(runtimeScene, name, mouse)) {
        const o = tc_obj(runtimeScene, name);
        let id = "";
        try { id = o.getVariables().get("itemId").getAsString(); } catch(e) {}
        if (!id && __tc_state.shopFeatured[i]) id = __tc_state.shopFeatured[i];
        __tc_state.ui_selectedShopId = id;
        tc_toast(runtimeScene, `Selected: ${id}`);
      }
    }

    if (tc_hit(runtimeScene, "BtnBuy", mouse)) {
      const r = tc_buy_selected(__tc_state);
      tc_toast(runtimeScene, r.msg);
    }

    if (tc_hit(runtimeScene, "BtnRevive", mouse)) {
      const r = tc_revive(__tc_state);
      tc_toast(runtimeScene, r.msg);
    }

    if (tc_hit(runtimeScene, "BtnReroll", mouse)) {
      // gem reroll
      if (__tc_state.gems >= 2) {
        __tc_state.gems -= 2;
        __tc_state.shopRotSeed += 777;
        __tc_state.shopRotDay = -1;
        tc_shop_rotate(__tc_state);
        tc_toast(runtimeScene, "Shop rerolled (-2 gems)");
      } else {
        tc_toast(runtimeScene, "Need 2 gems to reroll");
      }
    }

    tc_draw_shop(runtimeScene, __tc_state);
  }

  // --- INVENTORY ---
  if (sceneName === "Inventory") {
    // select owned
    for (let i=0; i<12; i++) {
      const name = "InvThumb"+i;
      if (tc_hit(runtimeScene, name, mouse)) {
        const o = tc_obj(runtimeScene, name);
        let id = "";
        try { id = o.getVariables().get("itemId").getAsString(); } catch(e) {}
        __tc_state.ui_selectedInvId = id;
        tc_toast(runtimeScene, `Selected: ${id}`);
      }
    }

    if (tc_hit(runtimeScene, "BtnPrevPage", mouse)) {
      __tc_state.ui_invPage = Math.max(0, __tc_state.ui_invPage - 1);
    }
    if (tc_hit(runtimeScene, "BtnNextPage", mouse)) {
      __tc_state.ui_invPage = __tc_state.ui_invPage + 1;
    }

    if (tc_hit(runtimeScene, "BtnEquip", mouse)) {
      const r = tc_equip(__tc_state, __tc_state.ui_selectedInvId);
      tc_toast(runtimeScene, r.msg);
    }

    if (tc_hit(runtimeScene, "BtnUnequip", mouse)) {
      const it = tc_item_by_id(__tc_state.ui_selectedInvId);
      if (it) {
        const r = tc_unequip(__tc_state, it.type);
        tc_toast(runtimeScene, r.msg);
      } else {
        tc_toast(runtimeScene, "Select item to unequip");
      }
    }

    tc_draw_inventory(runtimeScene, __tc_state);
  }

  // --- Activity (placeholder mini-loop) ---
  if (sceneName === "Activity") {
    // reward coins on activity entry / time
    if (now % 5000 < 20) {
      __tc_state.coins += 15;
    }
  }

  // autosave ~10s
  if (now % 10000 < 30) tc_save(__tc_state);

  // Draw HUD everywhere
  tc_draw_hud(runtimeScene, __tc_state);
}
