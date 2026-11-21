"""Generate a self-contained playable browser edition from a TamaCore pack.

This is a browser game, not a compiled GDevelop export.
"""
from __future__ import annotations

import json
from pathlib import Path


def write_playable_browser_game(game_dir: Path, pack: dict, levels: list, shop: dict) -> Path:
    """Write a playable HTML game next to game.json for immediate testing."""
    from .collectibles_catalog import collectible_catalog
    config = {
        "collectibles": collectible_catalog()["items"],
        "name": pack.get("name", "TamaCore"),
        "levels": levels,
        "shop": shop.get("upgrades", []),
        "foods": [{**food, "price": max(0, float(food.get("price", food.get("cost", 0)) or 0)), "energy": float(food.get("energy", 0) or 0)} for food in pack.get("foods", []) if isinstance(food, dict)],
        "cosmetics": pack.get("cosmetics", []),
        "pet": pack.get("pet", {}),
    }
    # Prevent embedded JSON from terminating the script element.
    payload = json.dumps(config, ensure_ascii=False).replace("<", "\\u003c")
    html = _HTML.replace("__GAME_CONFIG__", payload)
    target = Path(game_dir) / "PLAY_GAME.html"
    target.write_text(html, encoding="utf-8")
    return target


_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>TamaCore — Play</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 20% 0%,#304e79 0%,#141f39 43%,#0b1224 100%);color:#fff;font:16px system-ui,sans-serif}
main{max-width:950px;margin:auto;padding:clamp(10px,2vw,22px)}header{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 16px;background:#ffffff0c;border:1px solid #ffffff25;border-radius:18px;margin-bottom:12px;box-shadow:0 12px 28px #0002}
h1{font-size:clamp(21px,3vw,29px);margin:6px 0;color:#ffe6a8;text-shadow:0 2px 10px #0006}button{background:linear-gradient(160deg,#567db7,#314b81);color:#fff;border:1px solid #86a4d0;border-radius:12px;padding:10px 14px;cursor:pointer;font-weight:650;box-shadow:0 3px 0 #172d54;transition:filter .15s,transform .15s}button:active{transform:translateY(2px);box-shadow:0 1px 0 #172d54}button:disabled{opacity:.5;cursor:not-allowed}
button:hover{background:#4967a0}#stats{margin:8px 0;color:#bfe6ff}canvas{display:block;width:100%;height:auto;max-height:65vh;aspect-ratio:4/3;border:2px solid #4c7b9e;border-radius:16px;background:#142b3d;touch-action:none}
#panel{background:linear-gradient(145deg,#213756,#14233c);border:1px solid #54749c;border-radius:18px;padding:16px;margin-top:12px;box-shadow:0 12px 28px #0003}#shop{display:none}#shop.open{display:block}
#shop button,#careActions button{margin:4px}#message{min-height:24px;color:#ffe68c}#touch{display:flex;justify-content:space-between;margin-top:10px}
#quickHud{display:flex;gap:7px;flex-wrap:wrap;margin:8px 0 10px}#quickHud span{background:#172e4a;border:1px solid #56779d;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;color:#e6f4ff}#touch button{min-width:64px;min-height:50px}small{color:#b8c9dc}#stats{background:#ffffff0b;border:1px solid #ffffff20;border-radius:12px;padding:10px 12px;font-weight:650;line-height:1.5}#challenges{margin-top:16px;padding:14px;background:#ffffff09;border:1px solid #ffffff1c;border-radius:14px}#challenges h2{font-size:19px;color:#ffe5aa;margin:0 0 12px}#challengeList{display:grid;gap:8px}#milestones{margin-top:16px;padding:14px;background:#ffffff09;border:1px solid #ffffff1c;border-radius:14px}#milestones h2{font-size:19px;color:#ffe5aa;margin:0 0 12px}#milestoneList{display:grid;gap:8px}.milestone{padding:10px;border:1px solid #54749c;border-radius:10px;background:#15273d;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.milestone.locked{opacity:.65}#achievements{margin-top:16px;padding:14px;background:#ffffff09;border:1px solid #ffffff1c;border-radius:14px}#achievements h2{font-size:19px;color:#ffe5aa;margin:0 0 12px}#achievementList{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}.achievement{border:1px solid #526b87;border-radius:10px;padding:9px;background:#15273d}.achievement.locked{opacity:.55}.achievement strong{display:block}.achievement small{display:block;margin-top:3px}#foodMenu,#wardrobe{margin-top:16px;padding:14px;background:#ffffff09;border:1px solid #ffffff1c;border-radius:14px}#foodMenu h2,#wardrobe h2,#shop h2{font-size:19px;margin:0 0 12px;color:#ffe5aa}#foodChoice{background:#233c5f;color:#fff;border:1px solid #7f9dbb;border-radius:10px;padding:10px;max-width:100%;margin:0 8px 8px 0}#petStatus{line-height:1.7}#message{font-weight:650}#game{box-shadow:0 12px 32px #0005}#touch{gap:10px;flex-wrap:wrap}#careActions{display:flex;gap:6px;flex-wrap:wrap}#careActions button{flex:1 1 130px}@media(max-width:600px){#touch button{min-width:52px;padding:10px}#touch>div{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;flex:1}#touch>button{flex:1}#quickHud{gap:5px}#quickHud span{font-size:12px;padding:6px 9px}#touch{position:sticky;bottom:6px;z-index:20;background:#14243de8;padding:8px;border:1px solid #6c8bab;border-radius:14px;backdrop-filter:blur(8px)}#touch button{min-height:56px;touch-action:manipulation}#touch>div{min-width:190px}header>div{display:flex;gap:5px;flex-wrap:wrap}header button{padding:9px}#panel{padding:12px}}
#welcome{position:fixed;inset:0;z-index:100;display:grid;place-items:center;background:#071323dd;padding:18px;backdrop-filter:blur(10px)}#welcome[hidden]{display:none}#welcomeCard{width:min(100%,480px);background:linear-gradient(150deg,#345579,#15263f);border:2px solid #a6d9f3;border-radius:24px;padding:clamp(20px,5vw,36px);text-align:center;box-shadow:0 24px 80px #0009}#welcomeCard h2{font-size:clamp(26px,5vw,38px);color:#ffe6a8;margin:8px 0}#welcomeCard p{color:#d6e9fa;line-height:1.6}#welcomeCard button{font-size:19px;min-height:54px;width:100%;margin-top:14px;background:linear-gradient(135deg,#49a990,#287d91)}
#victory{position:fixed;inset:0;z-index:110;display:grid;place-items:center;background:#071323e8;padding:18px;backdrop-filter:blur(10px)}#victory[hidden]{display:none}#victoryCard{width:min(100%,490px);padding:clamp(22px,5vw,38px);text-align:center;border-radius:25px;border:2px solid #ffdd8c;background:linear-gradient(155deg,#42577e,#17243d);box-shadow:0 25px 90px #000b}#victoryCard h2{color:#ffe3a1;font-size:clamp(26px,5vw,39px);margin:10px 0}#victoryCard p{line-height:1.6;color:#dceeff}#victoryCard button{width:100%;font-size:17px;margin-top:12px;min-height:50px}

/* TamaCore expanded pet-home UI */
#petIdentity,#petWellness,#petGarden,#extraPlay,#townExpansion,#longTermGoals,#extraSettings,#livingExpansion,#rhythmExpansion{margin:12px 0;padding:14px;border-radius:17px;background:linear-gradient(145deg,#253b60dd,#18283fdd);border:1px solid #9ec6ed55;box-shadow:0 7px 22px #0002}
#petIdentity h3,#petWellness h3,#petGarden h3,#extraPlay h3,#townExpansion h3,#longTermGoals h3,#extraSettings h3,#livingExpansion h3,#rhythmExpansion h3{margin:0 0 10px;color:#ffe6aa}
#petIdentity button,#petWellness button,#petGarden button,#extraPlay button,#townExpansion button,#longTermGoals button,#extraSettings button,#livingExpansion button,#rhythmExpansion button{margin:4px;min-height:42px;touch-action:manipulation}
#petIdentity input,#petIdentity select,#extraSettings input[type=file]{background:#101c32;color:#fff;border:1px solid #9fc0e2;border-radius:10px;padding:9px;max-width:100%}
#petIdentity label,#extraSettings label{display:inline-block;margin:6px}
#extraGames,#roomButtons,#decorButtons,#townButtons,#goalButtons,#livingActions,#livingToys,#rhythmButtons{display:flex;flex-wrap:wrap;gap:5px}
#gameArena button{min-width:66px;min-height:66px}
#livingNarrative,#rhythmGreeting,#petWishStatus{font-weight:650;color:#ffe6b0}
@media(max-width:540px){#petIdentity,#petWellness,#petGarden,#extraPlay,#townExpansion,#longTermGoals,#extraSettings,#livingExpansion,#rhythmExpansion{padding:10px;margin:9px 0}#extraGames button,#livingActions button,#rhythmButtons button{flex:1 1 43%}#gameArena{padding:8px!important}}

</style></head><body><div id="victory" role="dialog" aria-modal="true" aria-labelledby="victoryTitle" hidden><div id="victoryCard"><div style="font-size:64px">🏆🐰🎉</div><h2 id="victoryTitle">Adventure Complete!</h2><p id="victorySummary"></p><button id="victoryClose">✨ View my achievements</button><button id="victoryRestart">🔄 Start a new adventure</button></div></div><div id="welcome" role="dialog" aria-modal="true" aria-labelledby="welcomeTitle"><div id="welcomeCard"><div style="font-size:58px">🐰✨</div><h2 id="welcomeTitle">Welcome to TamaCore!</h2><p>Collect coins, dodge enemies and explore new worlds with your bunny companion. Feed, train and evolve your pet as you play.</p><p><strong>Move:</strong> WASD, arrow keys or touch controls<br><strong>Dash:</strong> Space or 💨 button<br><strong>Pet:</strong> Tap your bunny companion</p><button id="startGame">▶ Start adventure</button></div></div><main><header><h1 id="title">TamaCore</h1><div>
<button id="soundToggle" aria-pressed="false">🔇 Sound off</button><button id="musicToggle" aria-pressed="false">🎵 Music off</button><button id="effectsToggle" aria-pressed="false">✨ Full effects</button><button id="homeToggle">🏠 Pet home</button><button id="shopToggle">Shop</button><button id="pause">Pause</button><button id="exportSave">💾 Export save</button><button id="importSave">📂 Import save</button><input id="saveFile" type="file" accept=".json,application/json" hidden><button id="reset">New game</button></div></header>
<div id="careAlert" role="status" aria-live="polite" hidden></div><div id="stats" aria-live="polite"></div><div id="quickHud" aria-label="Game status"><span id="hudLevel"></span><span id="hudCoins"></span><span id="hudPet"></span><span id="hudPower"></span></div>
<canvas id="game" width="800" height="600" aria-label="Playable game field"></canvas>
<div id="touch"><div><button data-key="ArrowLeft">◀</button><button data-key="ArrowUp">▲</button><button data-key="ArrowDown">▼</button><button data-key="ArrowRight">▶</button></div><button id="feed">Feed pet</button><button id="dash">💨 Dash</button></div>
<div id="panel"><div id="message">Collect gold coins, avoid red enemies, and finish every level.</div>
<div id="shop"><h2>Shop</h2><div id="items"></div></div>
<div id="wardrobe"><h2>Wardrobe</h2><div id="cosmetics"></div></div>
<section id="collectibleStore" style="margin-top:16px;padding:14px;border:1px solid #54749c;border-radius:14px;background:#15273d"><h2>🎁 Outfit & Home Boutique</h2><p>Earn coins by playing. Every item can be bought with free coins; no real-money checkout.</p><p id="boutiqueBalance"></p><div id="boutiqueTabs"></div><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><input id="boutiqueSearch" type="search" placeholder="Search items" aria-label="Search boutique items"><select id="boutiqueTheme" aria-label="Filter collection"><option value="">All collections</option><option value="classic">Classic</option><option value="pastel">Pastel</option><option value="royal">Royal</option><option value="winter">Winter</option><option value="garden">Garden</option></select><label><input type="checkbox" id="boutiqueOwnedOnly"> Owned only</label><label><input type="checkbox" id="boutiqueWishlist"> Wishlist</label><label><input type="checkbox" id="boutiqueFavorites"> Favorites</label><select id="boutiqueSort" aria-label="Sort products"><option value="default">Default order</option><option value="cheap">Price: low to high</option><option value="expensive">Price: high to low</option><option value="name">Name</option></select></div><p id="boutiqueCount"></p><div id="boutiqueItems" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px;margin-top:10px"></div><p id="boutiqueEquipped"></p><div id="boutiquePreview" aria-live="polite" style="position:relative;min-height:230px;overflow:hidden;border-radius:18px;border:2px solid #6385b1;background:linear-gradient(#b2ddf5,#f6e8cd);text-align:center;padding:16px"><div id="boutiquePreviewWallpaper" style="position:absolute;inset:0;opacity:.35;pointer-events:none"></div><div id="boutiquePreviewFurniture" style="position:relative;font-size:58px;margin-top:20px">🛋️</div><div id="boutiquePreviewPet" style="position:relative;font-size:80px;line-height:1.3">🐰</div><div id="boutiquePreviewOutfit" style="position:relative;font-size:42px;margin-top:-34px;margin-left:45px">🎀</div><div id="boutiquePreviewToy" style="position:relative;font-size:32px">🧸</div><small style="position:relative;color:#233d59">Your pet and room preview</small></div></section>
<div id="foodMenu"><h2>🐰 Tamagotchi pet care</h2><section id="roomDecor"><h3>🏠 Decorate your pet's room</h3><p id="roomStatus"></p><div id="roomButtons"></div></section><p id="careHint">Your pet needs food, play, sleep and cleaning even between adventures.</p><p id="dayNightStatus" aria-live="polite"></p><p id="foodPreference"></p><p id="fullnessStatus" aria-live="polite"></p><p id="weightStatus" aria-live="polite"></p><label for="foodChoice">Food: </label><select id="foodChoice"></select><button id="feedSelected">Feed selected food</button><div id="careActions"><button id="cleanPet">🧼 Clean (15 coins)</button><button id="toiletPet">🚽 Toilet</button><button id="disciplinePet">📣 Teach manners</button><button id="playPet">🎾 Play</button><button id="restPet">💤 Rest</button><button id="sleepPet">🌙 Sleep / Wake</button><button id="healPet">💊 Medicine (25 coins)</button><button id="petPet">❤️ Pet companion</button><button id="friendTrick">🐾 Teach a trick (30 friendship)</button><button id="friendPicnic">🧺 Friendship picnic (60 friendship)</button><button id="friendDance">💞 Best-friend dance (85 friendship)</button><button id="trainPet">🎓 Train (20 coins)</button><button id="skillPet">✨ Upgrade skill (100 coins)</button></div><div id="homeSurprise" hidden role="status" aria-live="polite"><p id="surpriseText"></p><button id="surpriseAccept">✨ Join your pet</button><button id="surpriseDismiss">Later</button></div><section id="petGarden"><h3>🌱 Little garden</h3><p id="gardenStatus" aria-live="polite"></p><button id="plantCarrot">🥕 Plant carrots · 8 coins</button><button id="plantBerry">🍓 Plant berries · 10 coins</button><button id="plantFlower">🌷 Plant flowers · 6 coins</button><button id="waterGarden">💧 Water garden</button><button id="harvestGarden">🧺 Harvest</button></section><section id="petWellness"><h3>🍳 Kitchen & wellness</h3><p id="petWellnessStats"></p><button id="cookPetMeal">🍲 Cook a healthy meal · 10 coins</button><button id="cookPetSnack">🧁 Bake a sweet snack · 12 coins</button><button id="bathePet">🛁 Give a bubble bath</button><button id="brushPetTeeth">🪥 Brush teeth</button><button id="visitPetClinic">🩺 Visit the pet clinic · 15 coins</button><p id="petWellnessTip"></p></section><section id="petIdentity"><h3>🐰 Your little companion</h3><label for="petNameInput">Pet name</label><input id="petNameInput" maxlength="24" placeholder="Pet name"><button id="savePetName">💾 Save name</button><p id="petIdentityStatus"></p><label for="petSpeciesSelect">Pet kind</label><select id="petSpeciesSelect"><option value="bunny">🐰 Bunny</option><option value="kitten">🐱 Kitten</option><option value="puppy">🐶 Puppy</option></select><label for="petColorSelect">Favorite color</label><select id="petColorSelect"><option value="mint">🍃 Mint</option><option value="peach">🍑 Peach</option><option value="lavender">💜 Lavender</option><option value="sky">🩵 Sky</option></select><button id="savePetStyle">🎨 Save appearance</button><p id="petWishStatus" aria-live="polite"></p><button id="petNameCall">📣 Call your pet</button><button id="petWishHelp">💗 Help with wish</button><p id="petWishHistory"></p></section><section id="petCelebrations"><h3>🎂 Birthdays & milestones</h3><p id="celebrationStatus"></p><button id="celebratePet" hidden>🎉 Celebrate together</button></section><section id="petDiary"><h3>📖 Pet memories</h3><div id="diaryEntries" aria-live="polite"></div></section><p id="dailyCare" aria-live="polite"></p><p id="petPersonality"></p><p id="petHumorStatus"></p><p id="petHabitsStatus" aria-live="polite"></p><p id="cleaningSkillStatus" aria-live="polite"></p><section id="petChores"><h3>🏡 Little home chores</h3><p id="choreSkills" aria-live="polite"></p><p id="choreRanks"></p><p id="choreFavorite"></p><button id="switchFavoriteChore">💖 Change favorite chore</button><button id="startFavoriteChore">▶️ Start favorite chore</button><button id="tidyToys">🧸 Organize toys</button><button id="waterPlants">🪴 Water plants</button><button id="practiceChore">🎯 Practice a chore</button><p id="choreCooldown" aria-live="polite"></p><p id="choreStreakStatus"></p><p id="choreCelebration" aria-live="polite"></p><p id="choreSpeedHint">⚡ Finish with over 5 seconds left for +5 coins!</p><p id="choreOverview" aria-live="polite"></p><p id="choreDetailedStats"></p><p id="choreAccuracy"></p><p id="choreRetryTip">💡 Missed a chore? Try again without a cooldown.</p><p id="choreProgress" aria-live="polite"></p><progress id="choreProgressBar" max="100" value="0"></progress><p id="choreDailyStatus"></p><button id="claimChoreDaily">🎁 Claim daily chore reward</button><p id="choreFatigueHint">⚡ Harder chores use more energy.</p><p id="choreEnergyHint"></p><p id="choreMoodHint"></p><p id="choreBadges"></p><p id="choreMedalTier"></p><p id="choreMilestoneHint">📖 Every 10 chores are remembered in your pet diary.</p><details><summary>🏆 Home helper challenges</summary><div id="choreChallenges"></div></details><p id="choreCleanHint">✨ A clean room grants +2 coins for completed chores.</p><p id="choreFriendHint">💞 Best friends get an extra mood bonus from chores.</p><p id="choreWeeklyStatus"></p><button id="claimChoreWeekly">🏅 Claim 10-chore milestone</button><div id="choreRetryPanel" hidden><p id="choreRetryMessage" aria-live="polite"></p><button id="choreRetryButton">🔁 Try again</button></div></section><div id="humorResponse" hidden><p id="humorPrompt" aria-live="polite"></p><button id="humorLaugh">😂 Laugh along</button><button id="humorScold">☝️ Scold gently</button><button id="humorPraise">💖 Praise</button></div><div id="prankInteraction" hidden><p id="prankInteractionPrompt" aria-live="polite"></p><button id="prankInteractionButton">🎲 Respond to prank</button></div><p id="petStatus"></p><p id="petProgress"></p><p id="petEmotion" aria-live="polite"></p><p id="questStatus"></p><p id="eventStatus" aria-live="polite"></p></div><section id="achievements"><h2>🏅 Achievements</h2><div id="achievementList"></div></section><section id="milestones"><h2>🎁 Journey rewards</h2><div id="milestoneList"></div></section><section id="challenges"><h2>🏆 Long-term challenges</h2><div id="challengeList"></div></section>
<small>Move: WASD / arrow keys or touch buttons. Collect yellow coins. Avoid red enemies. Progress saves automatically in this browser.</small></div>
</main><script id="config" type="application/json">__GAME_CONFIG__</script><script>
"use strict";
const cfg=JSON.parse(document.getElementById("config").textContent);
const canvas=document.getElementById("game"),ctx=canvas.getContext("2d");
const W=canvas.width,H=canvas.height,KEY="tamacore_browser_save_v1";
const $=id=>document.getElementById(id);
let soundEnabled=false,musicEnabled=false,reducedEffects=false,audioCtx=null,musicClock=0,musicStep=0;
try{reducedEffects=localStorage.getItem("tamacore_reduced_effects")==="1"||(!localStorage.getItem("tamacore_reduced_effects")&&window.matchMedia("(prefers-reduced-motion: reduce)").matches);}catch(_){}
function updateEffectsButton(){$("effectsToggle").textContent=reducedEffects?"🌿 Lite effects":"✨ Full effects";$("effectsToggle").setAttribute("aria-pressed",String(reducedEffects));}
$("effectsToggle").onclick=()=>{reducedEffects=!reducedEffects;try{localStorage.setItem("tamacore_reduced_effects",reducedEffects?"1":"0");}catch(_){}updateEffectsButton();};updateEffectsButton();
const melodies=[[392,440,523,440,349,392,440,330],[330,392,494,392,294,330,392,262],[440,523,587,523,392,440,523,349],[349,392,466,392,330,349,392,294]];
function musicTick(dt){if(!musicEnabled||paused||won)return;
musicClock-=dt;if(musicClock>0)return;musicClock=.42;
try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
if(!audioCtx)audioCtx=new AC();if(audioCtx.state!=="running")return;
const theme=melodies[Math.floor(state.level/5)%melodies.length];const frequency=theme[musicStep%theme.length];
const now=audioCtx.currentTime,osc=audioCtx.createOscillator(),gain=audioCtx.createGain();
osc.type="sine";osc.frequency.setValueAtTime(frequency,now);
gain.gain.setValueAtTime(.0001,now);gain.gain.exponentialRampToValueAtTime(.018,now+.04);
gain.gain.exponentialRampToValueAtTime(.0001,now+.36);
osc.connect(gain);gain.connect(audioCtx.destination);osc.start(now);osc.stop(now+.38);
musicStep++;}catch(_){}}
$("musicToggle").onclick=()=>{musicEnabled=!musicEnabled;$("musicToggle").textContent=musicEnabled?"🎵 Music on":"🎵 Music off";$("musicToggle").setAttribute("aria-pressed",String(musicEnabled));musicClock=0;
if(musicEnabled){try{const AC=window.AudioContext||window.webkitAudioContext;if(AC){if(!audioCtx)audioCtx=new AC();audioCtx.resume();}}catch(_){}}};
function sound(kind){if(!soundEnabled)return;
try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
if(!audioCtx)audioCtx=new AC();if(audioCtx.state==="suspended")audioCtx.resume();
const now=audioCtx.currentTime;const notes=kind==="coin"?[[880,.06],[1175,.09]]:kind==="hit"?[[210,.13],[125,.16]]:kind==="win"?[[523,.12],[659,.12],[784,.16],[1047,.3]]:kind==="power"?[[440,.09],[660,.09],[880,.15]]:kind==="belly"?[[175,.12],[130,.18],[210,.13]]:kind==="skinny"?[[660,.08],[490,.12]]:kind==="hiccup"?[[520,.07],[750,.06]]:kind==="sneeze"?[[860,.05],[310,.17]]:kind==="toot"?[[145,.13],[95,.2]]:kind==="trip"?[[380,.08],[240,.12]]:[[620,.08]];
let offset=0;for(const [frequency,duration] of notes){const osc=audioCtx.createOscillator(),gain=audioCtx.createGain();
osc.type=kind==="hit"?"triangle":"sine";osc.frequency.setValueAtTime(frequency,now+offset);
gain.gain.setValueAtTime(.0001,now+offset);gain.gain.exponentialRampToValueAtTime(.055,now+offset+.012);
gain.gain.exponentialRampToValueAtTime(.0001,now+offset+duration);
osc.connect(gain);gain.connect(audioCtx.destination);osc.start(now+offset);osc.stop(now+offset+duration+.015);offset+=duration*.75;}
}catch(_){}}
$("soundToggle").onclick=()=>{soundEnabled=!soundEnabled;$("soundToggle").textContent=soundEnabled?"🔊 Sound on":"🔇 Sound off";$("soundToggle").setAttribute("aria-pressed",String(soundEnabled));if(soundEnabled)sound("power");};
$("title").textContent=cfg.name;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const rand=(a,b)=>a+Math.random()*(b-a);
const state={coins:250,speed:200,level:0,owned:{},petHunger:75,petName:"Nuppu",petSpecies:"bunny",petColor:"mint",petWish:"",petWishAt:0,petWishCompleted:0,petNameCalls:0,petRecipesMade:0,petBaths:0,petTeethBrushed:0,petClinicVisits:0,petCookingSkill:0,petHygieneSkill:0,petGarden:{seed:"",plantedAt:0,wateredAt:0,harvests:0,flowers:0},petWeight:50,petFullness:45,treatsToday:0,treatDate:"",petEnergy:75,petMood:75,petCleanliness:75,cosmeticsOwned:{},equippedCosmetic:"",petXP:0,petStage:1,questsCompleted:0,goldMedals:0,silverMedals:0,bronzeMedals:0,totalCoinsCollected:0,achievements:{},trainingSessions:0,petSkill:0,levelsCompleted:0,claimedMilestones:{},starTokens:0,claimedChallenges:{},bossChallengesWon:0,petSleeping:false,sleepStartedAt:0,dreamKind:"",lastMorningDate:"",petSick:false,petBornAt:Date.now(),petDiscipline:50,cleaningSkill:0,tidyingSkill:0,gardeningSkill:0,lastChoreAt:0,choreStreak:0,bestChoreStreak:0,choreDaily:{date:"",done:0,claimed:false},choreTotal:0,choreWeeklyClaimed:0,favoriteChore:"toy",choreRewardsClaimed:[],choreFailures:0,choreFastWins:0,choreToyWins:0,chorePlantWins:0,choreFirstReward:false,petMess:0,careQuality:65,friendship:20,favoriteFood:0,dislikedFood:1,petMemories:[],celebrationsClaimed:{},petTrait:"",petPersonality:"",petHumor:"",humorHabits:{prank:30,clown:30,polite:30},roomOwned:{},roomEquipped:{wall:"default",floor:"default",furniture:"none",toy:"none"},homeSurprise:{kind:"",expires:0,nextAt:Date.now()+90000},dailyCare:{date:"",feed:0,play:0,clean:0,rest:0,claimed:false}};
try{const saved=JSON.parse(localStorage.getItem(KEY)||"null");if(saved&&typeof saved==="object"){
for(const k of ["coins","speed","level","petHunger","petWeight","petFullness","petEnergy","petMood","petCleanliness","petXP","petStage","questsCompleted","goldMedals","silverMedals","bronzeMedals","totalCoinsCollected","trainingSessions","petSkill","levelsCompleted","starTokens","bossChallengesWon"])if(Number.isFinite(saved[k]))state[k]=saved[k];
if(typeof saved.petName==="string")state.petName=saved.petName.slice(0,24).replace(/[<>]/g,"").trim()||"Nuppu";
if(["bunny","kitten","puppy"].includes(saved.petSpecies))state.petSpecies=saved.petSpecies;
if(["mint","peach","lavender","sky"].includes(saved.petColor))state.petColor=saved.petColor;
if(["feed","play","cuddle","clean","rest",""].includes(saved.petWish))state.petWish=saved.petWish;
for(const k of ["petWishAt","petWishCompleted","petNameCalls"])if(Number.isFinite(saved[k])&&saved[k]>=0)state[k]=saved[k];
for(const k of ["petRecipesMade","petBaths","petTeethBrushed","petClinicVisits","petCookingSkill","petHygieneSkill"])if(Number.isFinite(saved[k]))state[k]=clamp(saved[k],0,99999);
if(saved.petGarden&&typeof saved.petGarden==="object"){const g=saved.petGarden;state.petGarden={seed:["","carrot","flower","berry"].includes(g.seed)?g.seed:"",plantedAt:Number.isFinite(g.plantedAt)?g.plantedAt:0,wateredAt:Number.isFinite(g.wateredAt)?g.wateredAt:0,harvests:clamp(Number(g.harvests)||0,0,99999),flowers:clamp(Number(g.flowers)||0,0,99999)};}
if(saved.owned&&typeof saved.owned==="object")state.owned=saved.owned;
if(saved.achievements&&typeof saved.achievements==="object")state.achievements=saved.achievements;
if(saved.claimedMilestones&&typeof saved.claimedMilestones==="object")state.claimedMilestones=saved.claimedMilestones;
if(saved.claimedChallenges&&typeof saved.claimedChallenges==="object")state.claimedChallenges=saved.claimedChallenges;
if(saved.cosmeticsOwned&&typeof saved.cosmeticsOwned==="object")state.cosmeticsOwned=saved.cosmeticsOwned;
if(typeof saved.equippedCosmetic==="string")state.equippedCosmetic=saved.equippedCosmetic;
if(typeof saved.petSleeping==="boolean")state.petSleeping=saved.petSleeping;
if(typeof saved.petSick==="boolean")state.petSick=saved.petSick;
if(Number.isFinite(saved.petDiscipline))state.petDiscipline=clamp(saved.petDiscipline,0,100);
if(Number.isFinite(saved.cleaningSkill))state.cleaningSkill=clamp(saved.cleaningSkill,0,100);
for(const k of ["tidyingSkill","gardeningSkill"])if(Number.isFinite(saved[k]))state[k]=clamp(saved[k],0,100);
if(Number.isFinite(saved.lastChoreAt)&&saved.lastChoreAt>=0)state.lastChoreAt=saved.lastChoreAt;
for(const k of ["choreStreak","bestChoreStreak"])if(Number.isFinite(saved[k]))state[k]=clamp(saved[k],0,9999);
if(Array.isArray(saved.choreRewardsClaimed))state.choreRewardsClaimed=saved.choreRewardsClaimed.filter(x=>typeof x==="string").slice(0,100);
if(typeof saved.choreFirstReward==="boolean")state.choreFirstReward=saved.choreFirstReward;
for(const k of ["choreFailures","choreFastWins","choreToyWins","chorePlantWins"])if(Number.isFinite(saved[k]))state[k]=clamp(saved[k],0,999999);
for(const k of ["choreTotal","choreWeeklyClaimed"])if(Number.isFinite(saved[k]))state[k]=clamp(saved[k],0,999999);
if(["toy","plant"].includes(saved.favoriteChore))state.favoriteChore=saved.favoriteChore;
if(saved.choreDaily&&typeof saved.choreDaily==="object")state.choreDaily={date:String(saved.choreDaily.date||""),done:clamp(Number(saved.choreDaily.done)||0,0,3),claimed:!!saved.choreDaily.claimed};
if(Number.isFinite(saved.petMess))state.petMess=clamp(saved.petMess,0,5);
if(Number.isFinite(saved.careQuality))state.careQuality=clamp(saved.careQuality,0,100);
if(Number.isFinite(saved.friendship))state.friendship=clamp(saved.friendship,0,100);
if(Number.isFinite(saved.petFullness))state.petFullness=clamp(saved.petFullness,0,100);
if(Number.isFinite(saved.petWeight))state.petWeight=clamp(saved.petWeight,5,100);
if(Number.isInteger(saved.treatsToday)&&saved.treatsToday>=0)state.treatsToday=Math.min(20,saved.treatsToday);
if(typeof saved.treatDate==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(saved.treatDate))state.treatDate=saved.treatDate;
if(Number.isInteger(saved.favoriteFood)&&saved.favoriteFood>=0&&saved.favoriteFood<cfg.foods.length+3)state.favoriteFood=saved.favoriteFood;
if(Number.isInteger(saved.dislikedFood)&&saved.dislikedFood>=0&&saved.dislikedFood<cfg.foods.length+3)state.dislikedFood=saved.dislikedFood;
if(saved.celebrationsClaimed&&typeof saved.celebrationsClaimed==="object"&&!Array.isArray(saved.celebrationsClaimed))for(const k of ["day1","day7","day30","birthday1","birthday2","birthday3","birthday4","birthday5"])if(saved.celebrationsClaimed[k]===true)state.celebrationsClaimed[k]=true;
if(Array.isArray(saved.petMemories))state.petMemories=saved.petMemories.filter(e=>e&&Number.isFinite(e.time)&&e.time>0&&e.time<=Date.now()&&typeof e.text==="string").slice(-30).map(e=>({time:e.time,text:e.text.slice(0,140)}));
if(["kind","brave","mischievous"].includes(saved.petTrait))state.petTrait=saved.petTrait;
if(Number.isFinite(saved.petBornAt)&&saved.petBornAt>0&&saved.petBornAt<=Date.now())state.petBornAt=saved.petBornAt;
if(["playful","gentle","curious"].includes(saved.petPersonality))state.petPersonality=saved.petPersonality;
if(["prankster","clown","polite"].includes(saved.petHumor))state.petHumor=saved.petHumor;
if(saved.humorHabits&&typeof saved.humorHabits==="object"&&!Array.isArray(saved.humorHabits))for(const k of ["prank","clown","polite"])if(Number.isFinite(saved.humorHabits[k]))state.humorHabits[k]=clamp(saved.humorHabits[k],5,95);
if(Number.isFinite(saved.sleepStartedAt)&&saved.sleepStartedAt>0&&saved.sleepStartedAt<=Date.now())state.sleepStartedAt=saved.sleepStartedAt;
if(["happy","adventure","nightmare"].includes(saved.dreamKind))state.dreamKind=saved.dreamKind;
if(typeof saved.lastMorningDate==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(saved.lastMorningDate))state.lastMorningDate=saved.lastMorningDate;
if(saved.roomOwned&&typeof saved.roomOwned==="object"&&!Array.isArray(saved.roomOwned))for(const k of ["wall:mint","wall:peach","floor:wood","floor:cloud","furniture:bed","furniture:plant","toy:ball","toy:blocks"])if(saved.roomOwned[k]===true)state.roomOwned[k]=true;
if(saved.roomEquipped&&typeof saved.roomEquipped==="object")for(const [slot,allowed] of Object.entries({wall:["default","mint","peach"],floor:["default","wood","cloud"],furniture:["none","bed","plant"],toy:["none","ball","blocks"]})){const item=saved.roomEquipped[slot];if(allowed.includes(item)&&(item===allowed[0]||state.roomOwned[slot+":"+item]))state.roomEquipped[slot]=item;}
if(saved.homeSurprise&&typeof saved.homeSurprise==="object"){const v=saved.homeSurprise;
state.homeSurprise={kind:["gift","dance","discovery"].includes(v.kind)?v.kind:"",expires:Number.isFinite(v.expires)?Math.min(Date.now()+300000,v.expires):0,nextAt:Number.isFinite(v.nextAt)?Math.max(0,v.nextAt):Date.now()+90000};}
if(saved.dailyCare&&typeof saved.dailyCare==="object"&&!Array.isArray(saved.dailyCare)){const d=saved.dailyCare;if(typeof d.date==="string")state.dailyCare={date:d.date,feed:Number(d.feed)||0,play:Number(d.play)||0,clean:Number(d.clean)||0,rest:Number(d.rest)||0,claimed:d.claimed===true};}
}}catch(_){}
state.level=clamp(Math.floor(state.level),0,Math.max(0,cfg.levels.length-1));
let reactionUntil=0,reactionText="",reactionKind="",lastCareAlert="",funnyEventUntil=0,funnyEventIcon="",funnyEventKind="",humorPending="",humorPendingUntil=0,prankSurprise="",prankSurpriseUntil=0,toyHidingSpot=0,toySearchTries=0,messPieces=0,messHelperClock=0,messHelperActions=0,choreVisualKind="",choreVisualUntil=0,choreVisualStart=0,choreToyMask=0,choreWaterCount=0,choreDrag=null,choreDifficulty=1,choreGoal=3,choreRetryKind="",feedingVisual={until:0,emoji:"",liked:false,disliked:false};
if(!state.petPersonality)state.petPersonality=["playful","gentle","curious"][Math.floor(state.petBornAt/1000)%3];
if(!state.petHumor)state.petHumor=["prankster","clown","polite"][Math.floor(state.petBornAt/10000)%3];
function dailyDate(){const d=new Date();return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");}
function dailyProgress(){const today=dailyDate();if(state.dailyCare.date!==today)state.dailyCare={date:today,feed:0,play:0,clean:0,rest:0,claimed:false};}
function recordCare(action){dailyProgress();state.dailyCare[action]=1;const d=state.dailyCare;
if(!d.claimed&&d.feed&&d.play&&d.clean&&d.rest){d.claimed=true;state.coins+=75;state.petMood=clamp(state.petMood+10,0,100);petReaction("reward","🎁 Daily care complete!");msg("🎁 Daily routine completed! +75 coins and +10 mood.");}save();updateStats();}
function careAlert(){let notice="";
if(state.petSick)notice="💊 Your pet is sick! Give medicine.";
else if(state.petMess>=2)notice="🚽 Your pet needs the toilet!";
else if(state.petHunger<25)notice="🍽️ Your pet is hungry! Feed it.";
else if(state.petCleanliness<25)notice="🧼 Your pet needs a bath!";
else if(state.petEnergy<25&&!state.petSleeping)notice="💤 Your pet is tired! Let it sleep.";
else if(state.petMood<25)notice="🎾 Your pet is lonely! Play together.";
const el=$("careAlert");el.hidden=!notice;el.textContent=notice;
if(notice&&notice!==lastCareAlert){el.style.cssText="padding:12px;border:2px solid #f8c87d;border-radius:12px;background:#433329;color:#fff3cb;font-weight:bold;text-align:center;margin:8px 0";}
lastCareAlert=notice;}
function petReaction(kind,label){reactionKind=kind;reactionText=label;reactionUntil=performance.now()+2600;}
const petLifeStages=["🥚 Egg","🐣 Baby","🐥 Child","🐰 Teen","🐇 Adult"];
const growthMinutes=[0,2,15,60,180];let hatchAnimationUntil=0;
function petAgeMinutes(){return Math.max(0,(Date.now()-state.petBornAt)/60000);}
function updatePetGrowth(){const age=petAgeMinutes();let stage=1;
for(let i=1;i<growthMinutes.length;i++)if(age>=growthMinutes[i])stage=i+1;
if(stage>state.petStage){const wasEgg=state.petStage===1;state.petStage=stage;if(wasEgg)hatchAnimationUntil=performance.now()+4500;
if(stage>=3){state.petTrait=state.careQuality>=75&&state.petDiscipline>=60?"kind":state.petDiscipline>=75?"brave":"mischievous";}
rememberPet(wasEgg?"🐣 Your egg hatched":"✨ Grew into "+petLifeStages[stage-1]);msg(wasEgg?"🐣 Your egg hatched!":"✨ Your pet grew into "+petLifeStages[stage-1]+"!");save();updateStats();}}
function petAgeLabel(){const minutes=Math.floor(petAgeMinutes());return minutes<60?minutes+" min":Math.floor(minutes/60)+" h "+minutes%60+" min";}
const careStampKey="tamacore_last_care_v1";
try{const now=Date.now(),last=Number(localStorage.getItem(careStampKey))||now;
const elapsed=Math.min(48*60*60,Math.max(0,now-last)),ticks=Math.floor(elapsed/(20*60*1000));
if(ticks>0){state.petHunger=clamp(state.petHunger-ticks*2,0,100);state.petFullness=clamp(state.petFullness-ticks*3,0,100);
if(state.petHunger<20)state.petWeight=clamp(state.petWeight-Math.min(12,ticks*.65),5,100);
state.petEnergy=clamp(state.petEnergy+(state.petSleeping?ticks*3:-ticks),0,100);
state.petCleanliness=clamp(state.petCleanliness-ticks,0,100);
if(state.petHunger<25||state.petCleanliness<25)state.petMood=clamp(state.petMood-Math.min(ticks,30),0,100);
if(ticks>=3&&(state.petHunger<15||state.petCleanliness<15))state.petSick=true;}
localStorage.setItem(careStampKey,String(now));}catch(_){}
function surpriseTick(){const now=Date.now(),v=state.homeSurprise;
if(v.kind&&now>=v.expires){v.kind="";v.nextAt=now+90000;save();}
if(!v.kind&&now>=v.nextAt&&!state.petSleeping&&!state.petSick&&state.petStage>=2){v.kind=["gift","dance","discovery"][Math.floor(Math.random()*3)];v.expires=now+120000;petReaction("surprise","✨ A surprise!");save();}
const panel=$("homeSurprise");panel.hidden=!v.kind||!homeMode;
if(v.kind)$("surpriseText").textContent=v.kind==="gift"?"🎁 Your pet found a little present!":v.kind==="dance"?"🎶 Your pet wants to dance!":"🔍 Your pet discovered something interesting!";}
$("surpriseAccept").onclick=()=>{const v=state.homeSurprise;if(!v.kind||Date.now()>=v.expires)return;
const kind=v.kind;v.kind="";v.nextAt=Date.now()+120000;
if(kind==="gift"){state.coins+=20;rememberPet("🎁 Found a surprise gift");msg("🎁 Your pet found 20 coins!");}
else if(kind==="dance"){state.petMood=clamp(state.petMood+15,0,100);rememberPet("🎶 Danced together at home");msg("🎶 Dancing made your pet happy!");}
else{state.petDiscipline=clamp(state.petDiscipline+5,0,100);rememberPet("🔍 Discovered something new");msg("🔍 Your pet learned something new!");}
petReaction("surprise","✨ What a fun moment!");save();updateStats();surpriseTick();};
$("surpriseDismiss").onclick=()=>{state.homeSurprise.kind="";state.homeSurprise.nextAt=Date.now()+90000;save();surpriseTick();};
const roomItems=[{slot:"wall",id:"mint",name:"🌿 Mint walls",price:80},{slot:"wall",id:"peach",name:"🍑 Peach walls",price:80},{slot:"floor",id:"wood",name:"🪵 Wooden floor",price:65},{slot:"floor",id:"cloud",name:"☁️ Cloud floor",price:65},{slot:"furniture",id:"bed",name:"🛏️ Cozy bed",price:110},{slot:"furniture",id:"plant",name:"🪴 Happy plant",price:95},{slot:"toy",id:"ball",name:"⚽ Bouncy ball",price:70},{slot:"toy",id:"blocks",name:"🧩 Building blocks",price:85}];
function renderRoomShop(){const root=$("roomButtons");root.replaceChildren();
for(const item of roomItems){const key=item.slot+":"+item.id,owned=state.roomOwned[key],equipped=state.roomEquipped[item.slot]===item.id;
const button=document.createElement("button");button.textContent=item.name+" • "+(equipped?"Equipped":owned?"Use":item.price+" coins");button.disabled=equipped;
button.onclick=()=>{if(!state.roomOwned[key]){if(state.coins<item.price){msg("Not enough coins for room decoration.");return;}state.coins-=item.price;state.roomOwned[key]=true;}
state.roomEquipped[item.slot]=item.id;save();updateStats();renderRoomShop();msg("🏠 Room updated: "+item.name);};root.appendChild(button);}
$("roomStatus").textContent="Walls: "+state.roomEquipped.wall+" • Floor: "+state.roomEquipped.floor+" • Decoration: "+state.roomEquipped.furniture+" • Toy: "+state.roomEquipped.toy;}
function petDayPhase(){const h=new Date().getHours();return h>=6&&h<18?"day":h>=18&&h<21?"evening":"night";}
function updateDayNight(){const phase=petDayPhase();const label=phase==="day"?"☀️ Daytime":phase==="evening"?"🌇 Evening":"🌙 Nighttime";
$("dayNightStatus").textContent=label+" • Your pet follows the local day and night cycle.";
return phase;}
function choosePetDream(){const r=Math.random();return r<.12?"nightmare":r<.55?"adventure":"happy";}
function dreamWakeMessage(kind){const p=state.petPersonality;
if(kind==="nightmare")return p==="gentle"?"😟 A scary dream... can I have a cuddle?":p==="playful"?"😵 Whew, what a wild dream!":"😯 That dream was strange!";
if(kind==="adventure")return p==="curious"?"🔍 I discovered a whole new world!":p==="playful"?"🚀 That dream was an epic adventure!":"🌟 I dreamed of exploring!";
return p==="gentle"?"💗 I dreamed of cuddles!":p==="playful"?"🎾 I dreamed of playing!":"🌈 What a lovely dream!";}
function morningTick(){const now=new Date();if(now.getHours()<6||now.getHours()>=11||state.petSleeping||state.petStage<2)return;
const day=now.getFullYear()+"-"+String(now.getMonth()+1).padStart(2,"0")+"-"+String(now.getDate()).padStart(2,"0");
if(state.lastMorningDate===day)return;state.lastMorningDate=day;
state.petMood=clamp(state.petMood+5,0,100);petReaction("morning","☀️ Good morning!");msg("☀️ A new day! Your pet feels refreshed.");save();updateStats();}
function petCelebration(){const born=new Date(state.petBornAt),now=new Date();const days=Math.max(0,Math.floor((Date.now()-state.petBornAt)/86400000));
const milestones=[{key:"day1",days:1,label:"First day together"},{key:"day7",days:7,label:"One week together"},{key:"day30",days:30,label:"One month together"}];
const year=now.getFullYear()-born.getFullYear();
if(year>=1&&year<=5&&(now.getMonth()>born.getMonth()||(now.getMonth()===born.getMonth()&&now.getDate()>=born.getDate())))milestones.push({key:"birthday"+year,days:0,label:year+(year===1?"st":year===2?"nd":year===3?"rd":"th")+" birthday"});
return {days,ready:milestones.find(m=>days>=m.days&&!state.celebrationsClaimed[m.key])};}
function renderCelebration(){const v=petCelebration();$("celebrationStatus").textContent="🐰 Together for "+v.days+" day"+(v.days===1?"":"s")+(v.ready?" • 🎉 "+v.ready.label+" is ready!":" • More celebrations ahead!");$("celebratePet").hidden=!v.ready;}
$("celebratePet").onclick=()=>{const v=petCelebration();if(!v.ready)return;
state.celebrationsClaimed[v.ready.key]=true;state.coins+=50;state.petMood=clamp(state.petMood+20,0,100);gainFriendship(5);
rememberPet("🎂 Celebrated "+v.ready.label);petReaction("celebrate","🎉 Happy celebration!");save();updateStats();msg("🎂 "+v.ready.label+"! +50 coins, +20 mood, +5 friendship.");};
function humorPetMoment(){if(state.petSleeping||state.petSick||state.petStage===1||performance.now()<reactionUntil)return;
const habits=state.humorHabits,weights={prank:habits.prank+(state.petHumor==="prankster"?25:0),clown:habits.clown+(state.petHumor==="clown"?25:0),polite:habits.polite+(state.petHumor==="polite"?25:0)};
const total=weights.prank+weights.clown+weights.polite,roll=Math.random()*total;
const selected=roll<weights.prank?"prank":roll<weights.prank+weights.clown?"clown":"polite";
let kind,icon,line;
if(selected==="prank"){kind="prank";icon="😈";state.petDiscipline=clamp(state.petDiscipline-1,0,100);
const surprise=["toy","mess","boo"][Math.floor(Math.random()*3)];prankSurprise=surprise;prankSurpriseUntil=performance.now()+15000;if(surprise==="toy"){toyHidingSpot=Math.floor(Math.random()*3);toySearchTries=0;}if(surprise==="mess"){messPieces=15;messHelperClock=0;messHelperActions=0;}
if(surprise==="toy"){icon="🧸";line="🧸 Heehee! I hid my toy! Can you spot it?";}
else if(surprise==="mess"){icon="🌀";line="🌀 Oops! I made a silly mess!";state.petMess=clamp(state.petMess+1,0,5);state.petCleanliness=clamp(state.petCleanliness-4,0,100);}
else{icon="👻";line="👻 BOO! Did I surprise you?";}
}
else if(selected==="clown"){kind="clown";icon="🤡";line="🎪 Ta-da! Watch my silly dance!";state.petMood=clamp(state.petMood+2,0,100);}
else{kind="polite";icon="🎩";line="🎩 Ahem! I am a very proper bunny!";state.petDiscipline=clamp(state.petDiscipline+1,0,100);}
funnyEventUntil=performance.now()+3000;funnyEventIcon=icon;funnyEventKind=kind;humorPending=kind;humorPendingUntil=performance.now()+18000;petReaction(kind,line);sound(kind==="clown"?"hiccup":"coin");updateStats();}
function searchToySpot(spot){if(prankSurprise!=="toy"||performance.now()>prankSurpriseUntil)return;
if(spot!==toyHidingSpot){toySearchTries++;petReaction("look",toySearchTries===1?"🔎 Not there! Keep looking!":"🐾 Nope! Try another hiding spot!");sound("skinny");msg("🔎 No toy here. Try another spot!");return;}
prankSurprise="";prankSurpriseUntil=0;state.coins+=8;state.petMood=clamp(state.petMood+6,0,100);gainFriendship(3);state.humorHabits.prank=clamp(state.humorHabits.prank+2,5,95);petReaction("play","🧸 You found my secret hiding spot!");sound("coin");save();updateStats();msg("🧸 Found the hidden toy! +8 coins.");}
function collectMessPiece(index,byPet=false){if(prankSurprise!=="mess"||performance.now()>prankSurpriseUntil)return;const bit=1<<index;if(!(messPieces&bit))return;messPieces&=~bit;if(byPet){const previous=Math.floor(state.cleaningSkill/20);state.cleaningSkill=clamp(state.cleaningSkill+2,0,100);if(Math.floor(state.cleaningSkill/20)>previous){state.coins+=5;msg("🏅 Cleaning skill milestone! +5 coins.");}save();}petReaction("clean",byPet?"🐰 Look! I'm helping tidy up!":"🧹 One piece picked up!");sound("coin");
if(messPieces===0){prankSurprise="";prankSurpriseUntil=0;state.petMess=clamp(state.petMess-1,0,5);state.petCleanliness=clamp(state.petCleanliness+12,0,100);state.petDiscipline=clamp(state.petDiscipline+3,0,100);state.humorHabits.prank=clamp(state.humorHabits.prank+2,5,95);petReaction("clean","✨ Spotless! We did it together!");sound("power");save();msg("🧹 All litter collected! The room is clean.");}else if(!byPet)msg("🧹 Keep tapping the litter!");updateStats();}
function choreToyPositions(){return [W*.12,W*.28,W*.44,W*.6,W*.72];}
function refreshChoreDaily(){const d=new Date().toLocaleDateString("en-CA");if(state.choreDaily.date!==d)state.choreDaily={date:d,done:0,claimed:false};}
$("claimChoreDaily").onclick=()=>{refreshChoreDaily();if(state.choreDaily.done<3||state.choreDaily.claimed)return;state.choreDaily.claimed=true;state.coins+=25;gainFriendship(3);save();updateStats();msg("🎁 Daily chores complete! +25 coins.");};
$("claimChoreWeekly").onclick=()=>{if(state.choreTotal-state.choreWeeklyClaimed<10)return;state.choreWeeklyClaimed+=10;state.coins+=40;save();updateStats();msg("🏅 Ten chores completed! +40 coins.");};
$("startFavoriteChore").onclick=()=>doPetChore(state.favoriteChore);
$("switchFavoriteChore").onclick=()=>{state.favoriteChore=state.favoriteChore==="toy"?"plant":"toy";save();updateStats();msg("💖 Favorite chore updated!");};
function finishChoreInteraction(){if(!state.choreFirstReward){state.choreFirstReward=true;state.coins+=15;msg("🎁 First chore reward: +15 coins!");}const remaining=choreVisualUntil-performance.now();if(remaining>5000){state.coins+=5;state.choreFastWins++;msg("⚡ Speed bonus! +5 coins.");}rememberPet((choreVisualKind==="toy"?"Organized toys":"Watered plants")+" together • level "+choreDifficulty+" • streak "+(state.choreStreak+1));state.choreTotal++;if(state.choreTotal%10===0)rememberPet("🏅 Completed "+state.choreTotal+" home chores!");refreshChoreDaily();state.choreDaily.done=clamp(state.choreDaily.done+1,0,3);choreRetryKind="";state.choreStreak++;state.bestChoreStreak=Math.max(state.bestChoreStreak,state.choreStreak);state.coins+=Math.min(10,Math.floor(state.choreStreak/3)*2);if(state.choreStreak>0&&state.choreStreak%5===0){state.petMood=clamp(state.petMood+8,0,100);petReaction("play","🎉 Five chores in a row! Woohoo!");msg("🎊 Five-chore streak! +8 mood!");}const toy=choreVisualKind==="toy";if(!choreVisualKind)return;if(toy)state.choreToyWins++;else state.chorePlantWins++;const skill=toy?"tidyingSkill":"gardeningSkill",old=Math.floor(state[skill]/20);state[skill]=clamp(state[skill]+4+choreDifficulty-1,0,100);state.coins+=choreDifficulty-1;state.petMood=clamp(state.petMood+(choreVisualKind===state.favoriteChore?7:4),0,100);gainFriendship(choreVisualKind===state.favoriteChore?3:2);if(state.petMess===0){state.coins+=2;msg("✨ Spotless room bonus! +2 coins.");}if(state.friendship>=85){state.petMood=clamp(state.petMood+3,0,100);msg("💞 Best-friend teamwork! +3 mood.");}if(Math.floor(state[skill]/20)>old){state.coins+=5;msg("🏅 Chore skill milestone! +5 coins.");}petReaction("kind",toy?"🧸 We tidied everything together!":"🌻 Thanks for watering with me!");sound("power");choreVisualKind="";choreVisualUntil=0;choreDrag=null;save();updateStats();msg("✨ Level "+choreDifficulty+" teamwork bonus! Extra skill and coins.");}
function interactChore(x,y){if(!choreVisualKind||performance.now()>choreVisualUntil)return false;if(choreVisualKind==="toy"){const xs=choreToyPositions().slice(0,choreGoal);const i=xs.findIndex((v,i)=>!(choreToyMask&(1<<i))&&Math.hypot(x-v,y-H*.79)<43);if(i<0)return false;choreToyMask|=1<<i;sound("coin");if(choreToyMask===(1<<choreGoal)-1)finishChoreInteraction();else msg("🧸 Toy in the basket! Keep going.");return true;}
if(Math.hypot(x-W*.77,y-H*.75)>90&&Math.hypot(x-W*.52,y-H*.48)>75)return false;choreWaterCount++;sound("coin");if(choreWaterCount>=choreGoal)finishChoreInteraction();else msg("💧 Water the plant "+(choreGoal-choreWaterCount)+" more times!");return true;}
function doPetChore(kind,retry=false){if(choreVisualKind&&performance.now()<choreVisualUntil){msg("🏡 Finish the current chore before starting another.");return;}if(state.petEnergy<8){msg("😴 Too tired for chores! Let your pet rest first.");petReaction("sleep","💤 A little nap first, please!");return;}if(state.petSleeping||state.petSick||state.petStage===1){msg("🐰 Your pet needs to be awake and healthy to help.");return;}
const wait=retry?0:Math.max(0,30000-(Date.now()-state.lastChoreAt));if(wait>0){msg("⏳ Your pet needs "+Math.ceil(wait/1000)+" more seconds before another chore.");return;}
const toy=kind==="toy",skill=toy?"tidyingSkill":"gardeningSkill";choreRetryKind="";choreVisualKind=kind;choreDifficulty=state[skill]>=70?3:state[skill]>=30?2:1;choreGoal=choreDifficulty+2;choreVisualStart=performance.now();choreVisualUntil=choreVisualStart+(14-choreDifficulty*2+(state.petMood>=75?2:state.petMood<30?-2:0))*1000;choreToyMask=0;choreWaterCount=0;choreDrag=null;state.lastChoreAt=Date.now();const oldLevel=Math.floor(state[skill]/20);state[skill]=clamp(state[skill]+(state.petDiscipline>=65?7:5),0,100);
state.petEnergy=clamp(state.petEnergy-(3+choreDifficulty-1),0,100);state.petMood=clamp(state.petMood+(toy?5:3),0,100);state.petDiscipline=clamp(state.petDiscipline+2,0,100);gainFriendship(2);
if(Math.floor(state[skill]/20)>oldLevel){state.coins+=5;msg("🏅 New chore skill milestone! +5 coins.");}
petReaction("kind",toy?"🧸 All my toys are in place!":"🪴 Sip, sip! Happy plants!");sound("power");save();updateStats();msg(toy?"🧸 Toys organized! Tidying skill improved.":"🪴 Plants watered! Gardening skill improved.");}
$("tidyToys").onclick=()=>doPetChore("toy");$("waterPlants").onclick=()=>doPetChore("plant");$("practiceChore").onclick=()=>{if(choreVisualKind){msg("🎯 Finish the current chore first.");return;}doPetChore(state.tidyingSkill<=state.gardeningSkill?"toy":"plant",true);};$("choreRetryButton").onclick=()=>{if(!choreRetryKind)return;const kind=choreRetryKind;doPetChore(kind,true);};
function respondToPrank(){if(!prankSurprise||performance.now()>prankSurpriseUntil){prankSurprise="";updateStats();msg("That prank is already over!");return;}
if(prankSurprise==="toy"){msg("🔎 Tap one of the three hiding spots inside the room!");return;}
if(prankSurprise==="mess"){msg("🧹 Tap all four pieces of litter inside the room!");return;}
const kind=prankSurprise;prankSurprise="";prankSurpriseUntil=0;
if(kind==="toy"){state.coins+=8;state.petMood=clamp(state.petMood+6,0,100);gainFriendship(3);petReaction("play","🧸 Found it! You're a great detective!");sound("coin");msg("🧸 You found the hidden toy! +8 coins.");}
else if(kind==="mess"){state.petMess=clamp(state.petMess-1,0,5);state.petCleanliness=clamp(state.petCleanliness+12,0,100);state.petDiscipline=clamp(state.petDiscipline+3,0,100);petReaction("clean","🧹 All tidy again!");sound("power");msg("🧹 You cleaned up the prank mess!");}
else{state.petMood=clamp(state.petMood+10,0,100);gainFriendship(4);petReaction("play","😱 EEK! You got me back!");sound("hiccup");msg("👻 Boo! You startled your pet back!");}
state.humorHabits.prank=clamp(state.humorHabits.prank+2,5,95);save();updateStats();}
$("prankInteractionButton").onclick=respondToPrank;
function respondToHumor(choice){if(!humorPending||performance.now()>humorPendingUntil){humorPending="";updateStats();msg("That silly moment has passed!");return;}
const kind=humorPending;humorPending="";humorPendingUntil=0;
if(choice==="laugh"){state.humorHabits[kind]=clamp(state.humorHabits[kind]+7,5,95);state.petMood=clamp(state.petMood+9,0,100);gainFriendship(3);if(kind==="prank")state.petDiscipline=clamp(state.petDiscipline-2,0,100);petReaction("play","😂 Haha! You liked that!");}
else if(choice==="scold"){state.humorHabits[kind]=clamp(state.humorHabits[kind]-9,5,95);state.humorHabits.polite=clamp(state.humorHabits.polite+4,5,95);state.petDiscipline=clamp(state.petDiscipline+7,0,100);state.petMood=clamp(state.petMood-3,0,100);petReaction("discipline","😳 Okay, I'll behave!");}
else{state.humorHabits[kind]=clamp(state.humorHabits[kind]+5,5,95);state.petMood=clamp(state.petMood+5,0,100);gainFriendship(4);state.petDiscipline=clamp(state.petDiscipline+2,0,100);petReaction("kind","💖 Thank you!");}
save();updateStats();msg(choice==="laugh"?"😂 You laughed together!":choice==="scold"?"☝️ A gentle reminder to behave.":"💖 Your pet loved the praise!");}
$("humorLaugh").onclick=()=>respondToHumor("laugh");$("humorScold").onclick=()=>respondToHumor("scold");$("humorPraise").onclick=()=>respondToHumor("praise");
function funnyPetMoment(){if(state.petSleeping||state.petSick||state.petStage===1||performance.now()<reactionUntil)return;
const roll=Math.random();let kind,icon,line;
if(state.petFullness>=70&&roll<.45){kind="hiccup";icon="❗";line="😮 HIC! Was that my tummy?";}
else if(state.petFullness>=65&&roll<.7){kind="toot";icon="💨";line=state.petPersonality==="playful"?"💨 Pfffft! Heehee!":"💨 Oops... was that me?";}
else if(state.petPersonality==="curious"&&roll<.65){kind="sneeze";icon="🤧";line="🤧 Achoo! Dusty discovery!";}
else if(state.petPersonality==="playful"&&roll<.7){kind="trip";icon="💫";line="🙃 Whoops! Silly feet!";}
else if(roll<.5){kind="sneeze";icon="🤧";line="🤧 Achoo! Excuse me!";}
else{kind="trip";icon="💫";line="😵 Oopsie-daisy!";}
funnyEventUntil=performance.now()+3000;funnyEventIcon=icon;funnyEventKind=kind;petReaction(kind,line);sound(kind);}
function petHelpClean(dt){if(prankSurprise!=="mess"||state.petSleeping||state.petSick||state.petStage===1||performance.now()>prankSurpriseUntil)return;
messHelperClock+=dt;if(messHelperClock<Math.max(1.2,3-state.cleaningSkill*.017))return;messHelperClock=0;
const helpful=state.petDiscipline>=65&&state.humorHabits.polite>=state.humorHabits.prank;
const naughty=state.petDiscipline<40||state.humorHabits.prank>state.humorHabits.polite+20;
if(helpful&&Math.random()<Math.min(.95,.65+state.cleaningSkill*.003)){const available=[0,1,2,3].filter(i=>messPieces&(1<<i));if(available.length){messHelperActions++;collectMessPiece(available[Math.floor(Math.random()*available.length)],true);}}
else if(naughty&&messHelperActions<2&&Math.random()<.35){const cleared=[0,1,2,3].filter(i=>!(messPieces&(1<<i)));if(cleared.length){messPieces|=1<<cleared[Math.floor(Math.random()*cleared.length)];messHelperActions++;petReaction("mischief","🙃 Oops! More litter!");msg("🙃 Your cheeky pet scattered some litter again!");updateStats();}}
}
function checkChoreTimeout(){if(choreVisualKind&&performance.now()>=choreVisualUntil)choreDrag=null;$("choreProgress").textContent=choreVisualKind?"⏳ "+Math.ceil(Math.max(0,choreVisualUntil-performance.now())/1000)+"s • "+(choreVisualKind==="toy"?"Toys "+(choreToyMask.toString(2).split("1").length-1)+"/"+choreGoal:"Water "+choreWaterCount+"/"+choreGoal):"";$("choreProgressBar").value=choreVisualKind?Math.round(100*(choreVisualKind==="toy"?(choreToyMask.toString(2).split("1").length-1):choreWaterCount)/choreGoal):0;if(!choreVisualKind||performance.now()<choreVisualUntil)return;state.choreFailures++;rememberPet("Tried "+(choreVisualKind==="toy"?"organizing toys":"watering plants")+" but ran out of time");state.choreStreak=0;choreRetryKind=choreVisualKind;choreVisualKind="";state.petMood=clamp(state.petMood+1,0,100);choreDrag=null;state.petMood=clamp(state.petMood-2,0,100);petReaction("sad","😅 Oops! We ran out of time. Let's try again!");sound("skinny");msg("⏰ Time is up! Your pet wants to try again.");updateStats();save();}
function petWishTick(){if(state.petStage===1||state.petSleeping||state.petSick)return;if(state.petWish&&Date.now()-state.petWishAt>600000){state.petWish="";save();}if(!state.petWish&&Date.now()-state.petWishAt>180000){const choices=state.petHunger<55?["feed","feed","cuddle"]:state.petMood<55?["play","play","cuddle"]:state.petCleanliness<55?["clean","clean","cuddle"]:state.petEnergy<40?["rest","rest","cuddle"]:["play","feed","cuddle","clean"];state.petWish=choices[Math.floor(Math.random()*choices.length)];state.petWishAt=Date.now();petReaction("happy","💭 "+state.petName+" has a little wish!");save();updateStats();}}
function completePetWish(kind){if(!state.petWish||state.petWish!==kind)return false;state.petWish="";state.petWishCompleted++;state.coins+=8;gainFriendship(2);state.petMood=clamp(state.petMood+4,0,100);rememberPet("💖 Helped "+state.petName+" with a "+kind+" wish");petReaction("kind","💖 Thank you! You remembered my wish!");msg("💝 Wish fulfilled! +8 coins, friendship and mood.");save();updateStats();return true;}
function careTick(dt){petWishTick();checkChoreTimeout();updatePetGrowth();morningTick();surpriseTick();petHelpClean(dt);careClock+=dt;if(careClock<20)return;careClock=0;
state.petHunger=clamp(state.petHunger-1,0,100);state.petFullness=clamp(state.petFullness-2,0,100);
if(Math.random()<.1)funnyPetMoment();else if(Math.random()<.08)humorPetMoment();
if(state.petHunger<20)state.petWeight=clamp(state.petWeight-.45,5,100);
else if(state.petHunger>=40&&state.petHunger<=85&&state.petWeight>50)state.petWeight=clamp(state.petWeight-.08,5,100);const night=petDayPhase()==="night";
state.petEnergy=clamp(state.petEnergy+(state.petSleeping?(state.roomEquipped.furniture==="bed"?5:3)+(night?1:0):-1),0,100);
if(night&&!state.petSleeping&&state.petEnergy<45)state.petMood=clamp(state.petMood-1,0,100);
state.petCleanliness=clamp(state.petCleanliness-(state.petMess>0?2:1),0,100);
const wellCared=state.petHunger>=45&&state.petEnergy>=35&&state.petMood>=40&&state.petCleanliness>=45&&!state.petSick&&state.petMess<3;
state.careQuality=clamp(state.careQuality+(wellCared?.3:-.6),0,100);
if((state.petDiscipline<35||state.petTrait==="mischievous")&&Math.random()<.12){state.petMood=clamp(state.petMood-3,0,100);petReaction("mischief","🙃 Feeling mischievous!");}
if(state.petTrait==="kind"&&!state.petSleeping&&!state.petSick&&Math.random()<.14){state.petMood=clamp(state.petMood+3,0,100);petReaction("kind","💗 Sending love!");}
if(state.petTrait==="brave"&&!state.petSleeping&&state.petEnergy>20&&Math.random()<.12){state.petEnergy=clamp(state.petEnergy-1,0,100);petReaction("brave","🛡️ Ready for adventure!");}
if(Math.random()<.16&&state.petMess<5){state.petMess++;if(state.petMess>=3)petReaction("mess","🚽 I need the toilet!");}
if(state.petHunger<20||state.petCleanliness<20)state.petMood=clamp(state.petMood-1,0,100);
if(state.petHunger<10||state.petCleanliness<10||state.petMess>=5)state.petSick=true;
if(state.petSick)state.petMood=clamp(state.petMood-1,0,100);
if(state.petSick||state.petHunger<25||state.petCleanliness<25||state.petEnergy<25||state.petMood<25)petReaction("need",state.petSick?"💊 Help me!":state.petHunger<25?"🍽️ I'm hungry!":state.petCleanliness<25?"🧼 Bath time!":state.petEnergy<25?"💤 So sleepy!":"🎾 Play with me!");
try{localStorage.setItem(careStampKey,String(Date.now()));}catch(_){}save();updateStats();}
let player={x:W/2,y:H/2,r:17},targets=[],enemies=[],obstacles=[],collected=0,hit=0,invincible=0,won=false;
let questProgress=0,questTarget=5,questKind="collect",questDone=false,companionCollectCooldown=0,trainingCooldown=0,eventKind="none",eventTimer=0,eventDone=false,eventProgress=0,eventTarget=0;
let scenery=[],visualTime=0,playerMoving=false,playerFacing=1,hearts=[],petCooldown=0,particles=[],levelBanner=0,hitFlash=0,treasures=[],hazards=[],hazardCooldown=0,magnetTime=0,shieldTime=0,boostTime=0;
let dashCooldown=0,dashRequested=false,homeMode=true;let joystick=null,paused=true,careClock=0,pet={x:W/2+65,y:H/2+35},petMoodClock=0,petWander=0,petTarget={x:W/2+65,y:H/2+35};
function canvasPoint(e){const rect=canvas.getBoundingClientRect();return{x:(e.clientX-rect.left)*W/rect.width,y:(e.clientY-rect.top)*H/rect.height};}
canvas.addEventListener("pointerdown",e=>{const tap=canvasPoint(e);
if(homeMode){e.preventDefault();if(state.petStage===1){msg("🥚 Your little pet is still hatching!");return;}if(Math.hypot(tap.x-homeWander.x,tap.y-(H/2+60))<105){state.petMood=clamp(state.petMood+3,0,100);gainFriendship(1);petReaction("happy","💗 "+state.petName+" loves gentle pats!");if(typeof extra!=="undefined"&&extra&&extra.living){extra.living.petting++;extraSave();livingRender();}completePetWish("cuddle");save();updateStats();}else{homeWander.target=clamp(tap.x,170,620);homeWander.next=visualTime+7;petReaction("happy","🐾 "+state.petName+" comes to explore!");}return;}
if(Math.hypot(tap.x-pet.x,tap.y-pet.y)<38){e.preventDefault();petCompanion();return;}
if(e.pointerType==="mouse")return;
if(joystick!==null)return;const p=canvasPoint(e);joystick={id:e.pointerId,start:p,now:p};canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener("pointermove",e=>{if(joystick&&joystick.id===e.pointerId)joystick.now=canvasPoint(e);});
function releaseJoystick(e){if(joystick&&joystick.id===e.pointerId)joystick=null;}
for(const event of ["pointerup","pointercancel","lostpointercapture"])canvas.addEventListener(event,releaseJoystick);
const keys=new Set();
function save(){try{localStorage.setItem(KEY,JSON.stringify(state));}catch(_){}}
$("exportSave").onclick=()=>{const payload={format:"tamacore-save",version:1,exportedAt:new Date().toISOString(),progress:state};
const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob);
const link=document.createElement("a");link.href=url;link.download="tamacore-save.json";document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
msg("Save file exported. Keep it somewhere safe!");};
$("importSave").onclick=()=>$("saveFile").click();
$("saveFile").onchange=async()=>{const file=$("saveFile").files[0];if(!file)return;
try{if(file.size>1024*1024)throw Error("Save file is too large.");
const data=JSON.parse(await file.text());if(!data||data.format!=="tamacore-save"||data.version!==1||!data.progress||typeof data.progress!=="object"||Array.isArray(data.progress))throw Error("Not a supported TamaCore save.");
const incoming=data.progress;
if(!Number.isInteger(incoming.level)||incoming.level<0||incoming.level>=cfg.levels.length)throw Error("Invalid level in save.");
const numeric=["coins","speed","petHunger","petEnergy","petMood","petCleanliness","petXP","petStage","questsCompleted","goldMedals","silverMedals","bronzeMedals","totalCoinsCollected","trainingSessions","petSkill","levelsCompleted","starTokens","bossChallengesWon"];
for(const key of numeric)if(incoming[key]!==undefined&&(!Number.isFinite(incoming[key])||incoming[key]<0||incoming[key]>100000000))throw Error("Invalid "+key+" in save.");
const objects=["owned","achievements","claimedMilestones","claimedChallenges","cosmeticsOwned"];
for(const key of objects)if(incoming[key]!==undefined&&(!incoming[key]||typeof incoming[key]!=="object"||Array.isArray(incoming[key])))throw Error("Invalid "+key+" in save.");
if(!confirm("Replace current progress with this imported save?"))return;
const defaults={coins:250,speed:200,level:0,owned:{},petHunger:75,petEnergy:75,petMood:75,petCleanliness:75,cosmeticsOwned:{},equippedCosmetic:"",petXP:0,petStage:1,questsCompleted:0,goldMedals:0,silverMedals:0,bronzeMedals:0,totalCoinsCollected:0,achievements:{},trainingSessions:0,petSkill:0,levelsCompleted:0,claimedMilestones:{},starTokens:0,claimedChallenges:{},bossChallengesWon:0};
for(const key of Object.keys(defaults)){const value=incoming[key];state[key]=value===undefined?defaults[key]:value;}
state.level=incoming.level;state.equippedCosmetic=typeof incoming.equippedCosmetic==="string"?incoming.equippedCosmetic:"";
boutiqueSave=normalizeBoutique(incoming.boutique);state.boutique=boutiqueSave;boutiqueRender();
won=false;paused=true;$("pause").textContent="Resume";$("victory").hidden=true;save();startLevel();renderShop();renderWardrobe();updateStats();msg("Save imported! Press Resume to continue.");
}catch(error){msg("Import failed: "+error.message);}finally{$("saveFile").value="";}};
function msg(t){$("message").textContent=t;}
function point(radius){return{x:rand(radius+15,W-radius-15),y:rand(radius+15,H-radius-15),r:radius};}
const worlds=[{name:"Meadow",floor:"#17384b",grid:"#234b60",obstacle:"#558e69"},
{name:"Crystal Cave",floor:"#242344",grid:"#36355f",obstacle:"#796dc2"},
{name:"Sunset Desert",floor:"#66442d",grid:"#825d3d",obstacle:"#c18b4e"},
{name:"Frost Valley",floor:"#27455a",grid:"#3c6278",obstacle:"#8bd2e5"}];
function world(){return worlds[state.level%worlds.length];}
function blocked(x,y,r){return obstacles.some(o=>Math.hypot(x-o.x,y-o.y)<r+o.r+6);}
function safePoint(radius){for(let i=0;i<100;i++){const p=point(radius);
if(!blocked(p.x,p.y,radius)&&Math.hypot(p.x-W/2,p.y-H/2)>75)return p;}
return point(radius);}
function moveAroundObstacles(entity,dx,dy){const nx=clamp(entity.x+dx,entity.r,W-entity.r);
if(!blocked(nx,entity.y,entity.r))entity.x=nx;
const ny=clamp(entity.y+dy,entity.r,H-entity.r);
if(!blocked(entity.x,ny,entity.r))entity.y=ny;}
function generateScenery(){scenery=[];
for(let i=0;i<65;i++){const x=((i*127+state.level*59)%W),y=((i*211+state.level*83)%H);
scenery.push({x,y,size:3+(i%5)*2,kind:i%4,phase:i*.67});}}
function drawWorldBackdrop(){const theme=state.level%worlds.length;
const colors=[["#346c63","#132c41"],["#4c3b82","#16192f"],["#b87549","#53352d"],["#609cb5","#213e5a"]][theme];
const gradient=ctx.createLinearGradient(0,0,0,H);gradient.addColorStop(0,colors[0]);gradient.addColorStop(1,colors[1]);
ctx.fillStyle=gradient;ctx.fillRect(0,0,W,H);
ctx.save();ctx.globalAlpha=.18;
for(let layer=0;layer<3;layer++){const offset=Math.sin(visualTime*.16+layer)*12;
ctx.fillStyle=theme===0?"#b2f5c8":theme===1?"#b9a1f7":theme===2?"#f6ca80":"#d6f3ff";
ctx.beginPath();ctx.moveTo(0,H);for(let x=0;x<=W+20;x+=20){const y=H*(.68+layer*.11)+Math.sin(x*.011+layer*2)*20+Math.sin(x*.023+layer)*8+offset;ctx.lineTo(x,y);}ctx.lineTo(W,H);ctx.closePath();ctx.fill();}
ctx.restore();
// Animated light shafts and atmosphere are subtle enough not to obscure gameplay.
ctx.save();ctx.globalAlpha=.055;ctx.fillStyle="#ffffff";
for(let i=0;i<5;i++){const x=((i*179+visualTime*6)%(W+240))-120;
ctx.beginPath();ctx.moveTo(x-65,0);ctx.lineTo(x+5,0);ctx.lineTo(x+180,H);ctx.lineTo(x+80,H);ctx.closePath();ctx.fill();}
ctx.restore();}
function drawScenery(){const theme=state.level%worlds.length;
for(const d of scenery){ctx.save();ctx.translate(d.x,d.y);ctx.globalAlpha=.25+(Math.sin(visualTime*1.3+d.phase)+1)*.12;
if(theme===0){ctx.fillStyle=d.kind%2?"#b0e8a2":"#f6c0e2";
for(let j=0;j<5;j++){ctx.beginPath();ctx.ellipse(Math.cos(j*1.256)*d.size*.5,Math.sin(j*1.256)*d.size*.5,d.size*.36,d.size*.55,j*1.256,0,Math.PI*2);ctx.fill();}
circle(0,0,d.size*.22,"#ffdf87");}
else if(theme===1){ctx.fillStyle=d.kind%2?"#9ad9f8":"#d6a9ff";ctx.beginPath();ctx.moveTo(0,-d.size);ctx.lineTo(d.size*.65,0);ctx.lineTo(0,d.size);ctx.lineTo(-d.size*.65,0);ctx.closePath();ctx.fill();}
else if(theme===2){ctx.strokeStyle="#efc184";ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,d.size,0,Math.PI);ctx.stroke();}
else{ctx.fillStyle="#d8f6ff";for(let j=0;j<3;j++){ctx.save();ctx.rotate(j*Math.PI/3);ctx.fillRect(-1,-d.size,2,d.size*2);ctx.restore();}}
ctx.restore();}}
function burst(x,y,color,count=12){if(reducedEffects)count=Math.min(8,Math.ceil(count/4));for(let i=0;i<count;i++){const angle=i*Math.PI*2/count+rand(-.15,.15),speed=rand(45,145);
particles.push({x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-25,life:rand(.35,.85),maxLife:.85,r:rand(2,5),color});}
const limit=reducedEffects?60:220;if(particles.length>limit)particles.splice(0,particles.length-limit);}
function drawParticles(){for(const p of particles){ctx.save();ctx.globalAlpha=clamp(p.life/p.maxLife,0,1);
circle(p.x,p.y,p.r*p.life/p.maxLife,p.color);ctx.restore();}}
function updateEvent(){const status=$("eventStatus");if(eventKind==="none"){status.textContent="";return;}
const label=eventKind==="rush"?"⚡ Coin Rush":"💎 Treasure Hunt";
status.textContent=label+" • "+eventProgress+"/"+eventTarget+" • "+Math.ceil(eventTimer)+"s remaining"+(eventDone?" • ✓ Completed":"");}
function eventCollect(kind){if(eventKind==="none"||eventDone||eventTimer<=0)return;
if((eventKind==="rush"&&kind==="coin")||(eventKind==="treasure"&&kind==="gem")){
eventProgress++;if(eventProgress>=eventTarget){eventDone=true;
const reward=eventKind==="rush"?120:180;state.coins+=reward;gainPetXP(25);
save();updateStats();msg("🎉 Event complete! +"+reward+" coins and +25 pet XP.");}updateEvent();}}
function startLevel(){dashCooldown=0;dashRequested=false;const lv=cfg.levels[state.level];if(!lv){won=true;msg("Game complete!");return;}
player.x=W/2;player.y=H/2;levelBanner=2.1;companionCollectCooldown=0;generateScenery();beginQuest();pet.x=player.x+65;pet.y=player.y+35;petTarget={x:pet.x,y:pet.y};collected=0;hit=0;invincible=0;
obstacles=[];
for(let i=0;i<Math.min(14,3+state.level);i++){
const p=point(rand(20,32));if(Math.hypot(p.x-W/2,p.y-H/2)>115&&!blocked(p.x,p.y,p.r))obstacles.push(p);}
targets=Array.from({length:Math.min(150,Math.max(0,lv.coinCount||0))},()=>safePoint(10));
treasures=Array.from({length:Math.min(5,1+Math.floor(state.level/3))},(_,i)=>({...safePoint(14),kind:["gem","magnet","shield","boost","star"][((state.level+i)%5)]}));
magnetTime=0;shieldTime=0;boostTime=0;hazardCooldown=0;
hazards=state.level>=5?Array.from({length:Math.min(6,1+Math.floor(state.level/4))},()=>({...safePoint(24),phase:rand(0,Math.PI*2)})):[];
eventKind=state.level>0&&state.level%3===0?"rush":state.level>0&&state.level%5===0?"treasure":"none";
eventTimer=eventKind==="none"?0:60;eventProgress=0;eventDone=false;
eventTarget=eventKind==="rush"?Math.min(8,Math.max(3,targets.length)):eventKind==="treasure"?1:0;
if(eventKind==="treasure"&&!treasures.some(t=>t.kind==="gem"))treasures.push({...safePoint(14),kind:"gem"});
updateEvent();
enemies=Array.from({length:Math.min(50,Math.max(0,lv.enemyCount||0))},(_,i)=>{
const type=(state.level+1)%5===0&&i===0?"boss":state.level>=7&&i%7===0?"guardian":(state.level>=4&&i%5===0)?"chaser":(state.level>=2&&i%3===0)?"sprinter":"wanderer";
const difficulty=Math.min(1.65,1+state.level*.025);
const speed=(type==="boss"?rand(75,95):type==="guardian"?rand(35,55):type==="sprinter"?rand(115,155):rand(45,90))*difficulty;
const angle=rand(0,Math.PI*2);return {...safePoint(type==="boss"?25:16),vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,type,speed};});
msg(world().name+" • Level "+(state.level+1)+": collect "+targets.length+" coins and avoid enemies.");
updateStats();}
function beginQuest(){questKind=state.level%2===0?"collect":"survive";questProgress=0;questDone=false;
questTarget=questKind==="collect"?Math.min(8,3+state.level):15+state.level*3;
updateQuest();}
function updateQuest(){$("questStatus").textContent="🎯 Quest: "+(questKind==="collect"?"Collect coins":"Survive")+" "+Math.min(questProgress,questTarget)+"/"+questTarget+(questKind==="survive"?" sec":"");}
function advanceQuest(amount){if(questProgress>=questTarget)return;
questProgress=Math.min(questTarget,questProgress+amount);updateQuest();
if(questProgress>=questTarget){questDone=true;const bonus=30+state.level*10;state.coins+=bonus;state.questsCompleted++;
gainPetXP(20);save();updateStats();msg("🎉 Quest complete! +"+bonus+" coins and +20 pet XP.");}}
function petEmotion(){if(state.petHunger<20)return "🍽️ Hungry";
if(state.petEnergy<20)return "💤 Sleepy";
if(state.petCleanliness<20)return "🛁 Needs a bath";
if(state.petMood<30)return "😢 Sad";
if(state.petMood>80)return "🥰 Happy";return "🙂 Content";}
const achievementDefs=[
{id:"first_coin",name:"🪙 First Treasure",desc:"Collect your first coin",test:()=>state.totalCoinsCollected>=1},
{id:"collector",name:"💰 Coin Hunter",desc:"Collect 100 coins",test:()=>state.totalCoinsCollected>=100},
{id:"quest",name:"🎯 Quest Starter",desc:"Complete 1 quest",test:()=>state.questsCompleted>=1},
{id:"quests_10",name:"🌟 Quest Master",desc:"Complete 10 quests",test:()=>state.questsCompleted>=10},
{id:"gold",name:"🥇 Perfect Run",desc:"Earn a gold medal",test:()=>state.goldMedals>=1},
{id:"evolution",name:"🐰 Growing Up",desc:"Reach pet evolution stage 3",test:()=>state.petStage>=3},
{id:"evolution_max",name:"👑 Best Friend",desc:"Reach pet evolution stage 5",test:()=>state.petStage>=5},
{id:"trainer",name:"🎓 Dedicated Trainer",desc:"Complete 10 training sessions",test:()=>state.trainingSessions>=10},
{id:"skill_master",name:"✨ Skill Master",desc:"Upgrade companion skill to level 3",test:()=>state.petSkill>=3},
{id:"star_collector",name:"🌟 Star Collector",desc:"Collect 5 star tokens",test:()=>state.starTokens>=5}
];
function refreshAchievements(){let changed=false;
for(const a of achievementDefs){if(!state.achievements[a.id]&&a.test()){
state.achievements[a.id]=true;state.coins+=40;changed=true;msg("🏅 Achievement unlocked: "+a.name+"! +40 coins.");}}
if(changed)save();const box=$("achievementList");box.replaceChildren();
for(const a of achievementDefs){const item=document.createElement("div");item.className="achievement"+(state.achievements[a.id]?"":" locked");
const heading=document.createElement("strong");heading.textContent=(state.achievements[a.id]?"✓ ":"🔒 ")+a.name;
const detail=document.createElement("small");detail.textContent=a.desc+(state.achievements[a.id]?" • Unlocked":" • +40 coins");
item.append(heading,detail);box.append(item);}}
const milestoneDefs=[{level:3,coins:150,xp:30},{level:6,coins:300,xp:60},
{level:10,coins:500,xp:100},{level:15,coins:800,xp:150},{level:20,coins:1200,xp:200}];
function renderMilestones(){const box=$("milestoneList");box.replaceChildren();
for(const reward of milestoneDefs){const unlocked=state.levelsCompleted>=reward.level;
const claimed=!!state.claimedMilestones[reward.level];const item=document.createElement("div");
item.className="milestone"+(unlocked?"":" locked");const info=document.createElement("span");
info.textContent="Level "+reward.level+" • 🪙 "+reward.coins+" coins • ⭐ "+reward.xp+" pet XP";
const button=document.createElement("button");button.textContent=claimed?"✓ Claimed":unlocked?"Claim reward":"🔒 Locked";
button.disabled=!unlocked||claimed;button.onclick=()=>{if(state.claimedMilestones[reward.level]||state.levelsCompleted<reward.level)return;
state.claimedMilestones[reward.level]=true;state.coins+=reward.coins;gainPetXP(reward.xp);
save();updateStats();msg("🎁 Journey reward claimed! +"+reward.coins+" coins and +"+reward.xp+" XP.");};
item.append(info,button);box.append(item);}}
const challengeDefs=[
{id:"coins_250",name:"🪙 Dedicated Collector",stat:"totalCoinsCollected",target:250,coins:300,xp:60},
{id:"quests_25",name:"🎯 Quest Veteran",stat:"questsCompleted",target:25,coins:450,xp:90},
{id:"stars_10",name:"🌟 Star Explorer",stat:"starTokens",target:10,coins:500,xp:100},
{id:"training_20",name:"🎓 Training Champion",stat:"trainingSessions",target:20,coins:400,xp:120},
{id:"gold_10",name:"🥇 Golden Legend",stat:"goldMedals",target:10,coins:750,xp:150},
{id:"boss_3",name:"👹 Boss Challenger",stat:"bossChallengesWon",target:3,coins:900,xp:180}];
function renderChallenges(){const box=$("challengeList");box.replaceChildren();
for(const challenge of challengeDefs){const progress=Math.max(0,Math.floor(state[challenge.stat]||0));
const unlocked=progress>=challenge.target,claimed=!!state.claimedChallenges[challenge.id];
const item=document.createElement("div");item.className="milestone"+(unlocked?"":" locked");
const info=document.createElement("span");info.textContent=challenge.name+" • "+Math.min(progress,challenge.target)+"/"+challenge.target+
" • 🪙 "+challenge.coins+" • ⭐ "+challenge.xp+" XP";
const button=document.createElement("button");button.textContent=claimed?"✓ Claimed":unlocked?"Claim reward":"🔒 Locked";
button.disabled=claimed||!unlocked;button.onclick=()=>{if(state.claimedChallenges[challenge.id]||(state[challenge.stat]||0)<challenge.target)return;
state.claimedChallenges[challenge.id]=true;state.coins+=challenge.coins;gainPetXP(challenge.xp);
save();updateStats();msg("🏆 "+challenge.name+" completed! +"+challenge.coins+" coins and +"+challenge.xp+" XP.");};
item.append(info,button);box.append(item);}}
const choreChallenges=[
{id:"challenge162",title:"Toy Tamer",ready:()=>state.choreToyWins>=3,reward:12},
{id:"challenge163",title:"Plant Pal",ready:()=>state.chorePlantWins>=3,reward:12},
{id:"challenge164",title:"Five-Star Helper",ready:()=>state.choreTotal>=5,reward:15},
{id:"challenge165",title:"Ten-Task Hero",ready:()=>state.choreTotal>=10,reward:20},
{id:"challenge166",title:"Twenty-Task Champion",ready:()=>state.choreTotal>=20,reward:35},
{id:"challenge167",title:"Fifty-Task Legend",ready:()=>state.choreTotal>=50,reward:75},
{id:"challenge168",title:"Century of Care",ready:()=>state.choreTotal>=100,reward:150},
{id:"challenge169",title:"Toy Organizer Pro",ready:()=>state.choreToyWins>=15,reward:35},
{id:"challenge170",title:"Garden Guardian",ready:()=>state.chorePlantWins>=15,reward:35},
{id:"challenge171",title:"Master Toy Keeper",ready:()=>state.choreToyWins>=50,reward:100},
{id:"challenge172",title:"Master Gardener",ready:()=>state.chorePlantWins>=50,reward:100},
{id:"challenge173",title:"Lightning Helper",ready:()=>state.choreFastWins>=3,reward:15},
{id:"challenge174",title:"Speedy Bunny",ready:()=>state.choreFastWins>=10,reward:30},
{id:"challenge175",title:"Supersonic Team",ready:()=>state.choreFastWins>=30,reward:80},
{id:"challenge176",title:"Comeback Kid",ready:()=>state.choreFailures>=1&&state.choreTotal>=1,reward:15},
{id:"challenge177",title:"Never Give Up",ready:()=>state.choreFailures>=5&&state.choreTotal>=10,reward:30},
{id:"challenge178",title:"Streak Starter",ready:()=>state.bestChoreStreak>=3,reward:12},
{id:"challenge179",title:"Streak Superstar",ready:()=>state.bestChoreStreak>=10,reward:40},
{id:"challenge180",title:"Unstoppable Duo",ready:()=>state.bestChoreStreak>=25,reward:100},
{id:"challenge181",title:"Tidying Apprentice",ready:()=>state.tidyingSkill>=20,reward:20},
{id:"challenge182",title:"Tidying Specialist",ready:()=>state.tidyingSkill>=50,reward:45},
{id:"challenge183",title:"Tidying Master",ready:()=>state.tidyingSkill>=90,reward:100},
{id:"challenge184",title:"Gardening Apprentice",ready:()=>state.gardeningSkill>=20,reward:20},
{id:"challenge185",title:"Gardening Specialist",ready:()=>state.gardeningSkill>=50,reward:45},
{id:"challenge186",title:"Gardening Master",ready:()=>state.gardeningSkill>=90,reward:100},
{id:"challenge187",title:"Balanced Helper",ready:()=>state.tidyingSkill>=25&&state.gardeningSkill>=25,reward:30},
{id:"challenge188",title:"All-Round Home Hero",ready:()=>state.tidyingSkill>=75&&state.gardeningSkill>=75,reward:125},
{id:"challenge189",title:"Clean Sweep",ready:()=>state.cleaningSkill>=30,reward:30},
{id:"challenge190",title:"Cleanliness Expert",ready:()=>state.cleaningSkill>=80,reward:80},
{id:"challenge191",title:"Growing Friendship",ready:()=>state.friendship>=40&&state.choreTotal>=3,reward:20},
{id:"challenge192",title:"Best-Friend Helpers",ready:()=>state.friendship>=85&&state.choreTotal>=10,reward:65},
{id:"challenge193",title:"Happy Home",ready:()=>state.petMood>=90&&state.choreTotal>=5,reward:30},
{id:"challenge194",title:"Energetic Helper",ready:()=>state.petEnergy>=90&&state.choreTotal>=10,reward:35},
{id:"challenge195",title:"Disciplined Assistant",ready:()=>state.petDiscipline>=80&&state.choreTotal>=10,reward:50},
{id:"challenge196",title:"Kind Companion",ready:()=>state.careQuality>=85&&state.choreTotal>=15,reward:60},
{id:"challenge197",title:"Golden Streak",ready:()=>state.bestChoreStreak>=50,reward:200},
{id:"challenge198",title:"Two Hundred Chores",ready:()=>state.choreTotal>=200,reward:250},
{id:"challenge199",title:"Ultimate Caretaker",ready:()=>state.choreTotal>=100&&state.friendship>=90&&state.tidyingSkill>=80&&state.gardeningSkill>=80,reward:300},
{id:"challenge200",title:"TamaCore Home Legend",ready:()=>state.choreTotal>=250&&state.bestChoreStreak>=30&&state.tidyingSkill>=95&&state.gardeningSkill>=95,reward:500},
/*CHORE_CHALLENGES*/
];
function renderChoreChallenges(){const root=$("choreChallenges");if(!root)return;root.replaceChildren();for(const c of choreChallenges){const claimed=state.choreRewardsClaimed.includes(c.id),ready=c.ready();const line=document.createElement("div"),button=document.createElement("button");button.textContent=(claimed?"✅ ":ready?"🎁 ":"🔒 ")+c.title+" • "+c.reward+" coins";button.disabled=claimed||!ready;button.style.opacity=claimed?"0.75":"1";button.onclick=()=>{if(state.choreRewardsClaimed.includes(c.id)||!c.ready())return;state.choreRewardsClaimed.push(c.id);state.coins+=c.reward;state.petMood=clamp(state.petMood+2,0,100);rememberPet("🏆 Challenge: "+c.title);save();updateStats();msg("🏆 "+c.title+"! +"+c.reward+" coins.");};line.appendChild(button);root.appendChild(line);}}
function updateStats(){const g=state.petGarden,age=Date.now()-g.plantedAt;const ready=g.seed&&age>=60000&&g.wateredAt>=g.plantedAt;$("gardenStatus").textContent=g.seed?"🌿 Growing "+g.seed+" • "+(ready?"Ready to harvest!":g.wateredAt>=g.plantedAt?"Growing... "+Math.max(0,Math.ceil((60000-age)/1000))+"s left":"Needs water 💧"):"🌱 Choose a seed to begin!";$("harvestGarden").disabled=!ready;$("waterGarden").disabled=!g.seed||g.wateredAt>=g.plantedAt;$("gardenStatus").textContent+=" • Harvests: "+g.harvests+" • Flowers: "+g.flowers;$("petWellnessStats").textContent="🍲 Meals "+state.petRecipesMade+" • 🛁 Baths "+state.petBaths+" • 🪥 Brushed "+state.petTeethBrushed+" • 🩺 Clinic "+state.petClinicVisits+" • 👩‍🍳 Cooking "+Math.round(state.petCookingSkill)+" • 🧼 Hygiene "+Math.round(state.petHygieneSkill);$("petWellnessTip").textContent=state.petSick?"🤒 Your pet needs care. The clinic can help.":state.petCleanliness<40?"🫧 Time for a bath!":"🐰 A happy pet loves gentle routines.";$("petIdentityStatus").textContent="💖 "+state.petName+" • "+state.petSpecies+" • "+state.petColor+" • called "+state.petNameCalls+" times";$("petWishStatus").textContent=state.petWish?"💭 "+state.petName+" wishes for "+state.petWish+"!":"💤 No special wish right now.";$("petWishHelp").disabled=!state.petWish;$("petWishHistory").textContent="💗 Wishes fulfilled: "+state.petWishCompleted;renderChoreChallenges();$("choreMedalTier").textContent=state.choreTotal>=100?"🏆 Diamond home helper":state.choreTotal>=50?"🥇 Gold home helper":state.choreTotal>=20?"🥈 Silver home helper":state.choreTotal>=5?"🥉 Bronze home helper":"🌱 Rookie home helper";$("choreAccuracy").textContent="🎯 Success rate: "+(state.choreTotal+state.choreFailures?Math.round(state.choreTotal/(state.choreTotal+state.choreFailures)*100):100)+"%";$("choreDetailedStats").textContent="🧸 "+state.choreToyWins+" toy wins • 🪴 "+state.chorePlantWins+" plant wins • ⚡ "+state.choreFastWins+" fast • ⏰ "+state.choreFailures+" timeouts";$("choreOverview").textContent="🏡 Home helper • "+state.choreTotal+" chores • Best streak "+state.bestChoreStreak+" • 🧹 "+Math.round(state.cleaningSkill)+" • 🧸 "+Math.round(state.tidyingSkill)+" • 🪴 "+Math.round(state.gardeningSkill);$("choreEnergyHint").textContent=state.petEnergy<8?"💤 Rest needed before chores":"⚡ Energy available for chores";$("choreFavorite").textContent="💖 Favorite chore: "+(state.favoriteChore==="toy"?"Organizing toys":"Watering plants")+" • Extra mood and friendship";$("choreCelebration").textContent=state.choreStreak>=5?"🎉 Amazing! "+state.choreStreak+" chores in a row!":"";const rank=v=>v>=80?"Master":v>=50?"Skilled":v>=20?"Apprentice":"Beginner";$("choreRanks").textContent="🧸 "+rank(state.tidyingSkill)+" • 🪴 "+rank(state.gardeningSkill);$("choreMoodHint").textContent=state.petMood>=75?"😊 Happy pet: +2 seconds for chores":state.petMood<30?"😴 Low mood: -2 seconds for chores":"🐰 Normal chore pace";$("choreBadges").textContent="🎖️ Badges: "+[state.choreTotal>=1?"First helper":"",state.choreTotal>=10?"Home hero":"",state.choreTotal>=50?"Chore champion":"",state.bestChoreStreak>=5?"Streak star":""].filter(Boolean).join(" • ");$("choreWeeklyStatus").textContent="🏅 Total chores "+state.choreTotal+" • Next milestone "+Math.min(10,state.choreTotal-state.choreWeeklyClaimed)+"/10";$("claimChoreWeekly").disabled=state.choreTotal-state.choreWeeklyClaimed<10;refreshChoreDaily();$("choreDailyStatus").textContent="📅 Daily chores "+state.choreDaily.done+"/3"+(state.choreDaily.claimed?" • Claimed!":"");$("claimChoreDaily").disabled=state.choreDaily.done<3||state.choreDaily.claimed;$("choreStreakStatus").textContent="🔥 Chore streak: "+state.choreStreak+" • Best: "+state.bestChoreStreak;$("choreRetryPanel").hidden=!choreRetryKind;$("choreRetryMessage").textContent=choreRetryKind==="toy"?"⏰ The toys are still scattered. Give it another go!":"⏰ The plant needs more water. Try again!";$("choreRetryButton").textContent=choreRetryKind==="toy"?"🔁 Retry toy sorting":"🔁 Retry watering";$("choreSkills").textContent="🧸 Tidying "+Math.round(state.tidyingSkill)+"/100 • 🪴 Gardening "+Math.round(state.gardeningSkill)+"/100";const choreWait=Math.max(0,30000-(Date.now()-state.lastChoreAt));$("choreCooldown").textContent=choreWait?"⏳ Next chore in "+Math.ceil(choreWait/1000)+"s":"✨ Ready for another chore!";$("tidyToys").disabled=choreWait>0;$("waterPlants").disabled=choreWait>0;$("cleaningSkillStatus").textContent="🧹 Cleaning skill "+Math.round(state.cleaningSkill)+"/100 • "+(state.cleaningSkill>=80?"🌟 Expert helper":state.cleaningSkill>=40?"✨ Helpful cleaner":"🐾 Learning to tidy");if(prankSurprise&&performance.now()>prankSurpriseUntil)prankSurprise="";$("prankInteraction").hidden=!prankSurprise;$("prankInteractionPrompt").textContent=prankSurprise==="toy"?"🧸 Search the bed, box or plant in the room!":prankSurprise==="mess"?"🧹 Collect the four pieces of litter in the room!":"👻 Your pet scared you. Surprise it back!";$("prankInteractionButton").textContent=prankSurprise==="toy"?"🔎 Tap a hiding spot in the room":prankSurprise==="mess"?"🧹 Tap the litter in the room":"👻 Boo! Scare back";$("petHabitsStatus").textContent="🧠 Learned habits • 😈 Pranks "+Math.round(state.humorHabits.prank)+" • 🤡 Clowning "+Math.round(state.humorHabits.clown)+" • 🎩 Manners "+Math.round(state.humorHabits.polite);if(humorPending&&performance.now()>humorPendingUntil)humorPending="";$("humorResponse").hidden=!humorPending;$("humorPrompt").textContent=humorPending==="prank"?"😈 Your pet played a prank! How do you react?":humorPending==="clown"?"🤡 Your pet is clowning around! How do you react?":"🎩 Your pet is acting very proper! How do you react?";$("petHumorStatus").textContent="🎭 Humor style: "+(state.petHumor==="prankster"?"😈 Little prankster":state.petHumor==="clown"?"🤡 Silly clown":"🎩 Polite comedian");const weightMood=state.petWeight>=85?"🎈 Super round!":state.petWeight>=65?"🍩 Chubby cheeks!":state.petWeight<=20?"🪶 Very skinny!":state.petWeight<=35?"🍃 A little thin":"🐰 Just right";$("weightStatus").textContent="⚖️ Pet shape "+Math.round(state.petWeight)+"/100 • "+weightMood;const today=new Date().toLocaleDateString("en-CA");if(state.treatDate!==today){state.treatDate=today;state.treatsToday=0;}$("fullnessStatus").textContent="🍽️ Fullness "+Math.round(state.petFullness)+"/100 • 🍓 Treats "+state.treatsToday+"/3 today"+(state.petFullness>=90?" • Full!":"");updateFoodPreference();renderCelebration();renderPetDiary();updateDayNight();renderRoomShop();$("friendTrick").disabled=state.friendship<30;$("friendPicnic").disabled=state.friendship<60;$("friendDance").disabled=state.friendship<85;dailyProgress();const d=state.dailyCare;
$("dailyCare").textContent="📅 Daily care: "+(d.feed?"✅":"⬜")+" Feed • "+(d.play?"✅":"⬜")+" Play • "+(d.clean?"✅":"⬜")+" Clean • "+(d.rest?"✅":"⬜")+" Rest"+(d.claimed?" • 🎁 Reward claimed":" • Complete all for 75 coins");
$("petPersonality").textContent="💞 Friendship "+Math.round(state.friendship)+"/100 ("+friendshipRank()+") • 🐰 Personality: "+state.petPersonality+(state.petTrait?" • Growing trait: "+state.petTrait:"")+" • Care quality "+Math.round(state.careQuality)+"/100 • "+" • "+(state.petPersonality==="playful"?"Loves games!":state.petPersonality==="gentle"?"Enjoys cuddles!":"Loves discovering things!");careAlert();refreshAchievements();renderMilestones();renderChallenges();const lv=cfg.levels[state.level]||{};
$("hudLevel").textContent="🗺️ "+(state.level+1)+"/"+cfg.levels.length;
$("hudCoins").textContent="🪙 "+state.coins;
$("hudPet").textContent="🐰 "+state.petStage+" • ❤️ "+Math.round(state.petMood);
$("hudPower").textContent=shieldTime>0?"🛡️ Shield":boostTime>0?"⚡ Boost":magnetTime>0?"🧲 Magnet":"💨 Dash "+(dashCooldown>0?Math.ceil(dashCooldown)+"s":"ready");
$("stats").textContent="Level "+(state.level+1)+"/"+cfg.levels.length+"  •  Coins: "+state.coins+
"  •  Collected: "+collected+"/"+Math.min(150,lv.coinCount||0)+"  •  Speed: "+state.speed+
"  •  Pet hunger: "+Math.round(state.petHunger)+"  •  Pet stage: "+state.petStage+
"  •  Medals: 🥇"+state.goldMedals+" 🥈"+state.silverMedals+" 🥉"+state.bronzeMedals+
"  •  Difficulty: "+(state.level>=7?"Hard":state.level>=3?"Medium":"Easy")+
"  •  Boss wins: "+state.bossChallengesWon+"  •  Hazards: "+hazards.length+"  •  🌟 Stars: "+state.starTokens+
(boostTime>0?"  •  ⚡ Speed boost: "+Math.ceil(boostTime)+"s":"")+
(shieldTime>0?"  •  🛡️ Shield: "+Math.ceil(shieldTime)+"s":"")+
(magnetTime>0?"  •  🧲 Magnet: "+Math.ceil(magnetTime)+"s":"");
$("petStatus").textContent="🚽 Mess "+state.petMess+"/5 • 📣 Discipline "+Math.round(state.petDiscipline)+"/100 • "+petLifeStages[Math.min(4,Math.max(0,state.petStage-1))]+(state.petSleeping?" • 🌙 Sleeping":"")+(state.petSick?" • 💊 Sick":"")+" • Hunger "+Math.round(state.petHunger)+"/100 • Energy "+Math.round(state.petEnergy)+"/100 • Mood "+Math.round(state.petMood)+"/100 • Cleanliness "+Math.round(state.petCleanliness)+"/100";
$("petProgress").textContent="Pet evolution: stage "+state.petStage+" • XP "+state.petXP+"/"+(state.petStage*100)+
(state.petStage>=3?" • 🪙 Companion coin helper":" • Coin helper unlocks at stage 3")+
(state.petStage>=5?" • ⚡ Happy speed boost":"")+
" • Training sessions: "+state.trainingSessions+
" • Skill "+state.petSkill+"/3 (next: "+(state.petSkill<3?(100*(state.petSkill+1))+" coins, "+((state.petSkill+1)*3)+" trainings":"MAX")+")";
$("petEmotion").textContent="Pet mood: "+petEmotion()+" • Quests completed: "+state.questsCompleted;}
function gainPetXP(amount){state.petXP+=amount;let evolved=false;
while(state.petStage<5&&state.petXP>=state.petStage*100){state.petXP-=state.petStage*100;state.petStage++;evolved=true;}
if(evolved)msg("✨ Your pet evolved to stage "+state.petStage+"!");save();updateStats();}
function finishLevel(){sound("win");burst(player.x,player.y,"#ffe88b",35);
if((state.level+1)%5===0){burst(player.x,player.y,"#ff7fc4",45);
hearts.push(...Array.from({length:10},(_,i)=>({x:player.x+(i-5)*8,y:player.y-20,vx:(i-5)*12,vy:-50-rand(0,30),life:1.6})));}
const medal=hit===0&&questDone?"gold":hit<=2&&questDone?"silver":"bronze";
const medalBonus=medal==="gold"?100:medal==="silver"?50:20;
state[medal+"Medals"]++;state.levelsCompleted=Math.max(state.levelsCompleted,state.level+1);
const bossChallenge=(state.level+1)%5===0;
const bossBonus=bossChallenge&&hit<=2?250:0;
if(bossBonus)state.bossChallengesWon++;
const reward=50+state.level*25+medalBonus+bossBonus;
gainPetXP(35);state.coins+=reward;
if(state.level+1>=cfg.levels.length){won=true;
$("victorySummary").textContent="You explored "+cfg.levels.length+" levels with your companion! 🪙 "+state.coins+" coins • 🥇 "+state.goldMedals+" gold medals • 🌟 "+state.starTokens+" stars • 🐰 Pet stage "+state.petStage+". Final reward: "+reward+" coins.";
$("victory").hidden=false;burst(player.x,player.y,"#ffe58b",80);
msg("🏆 All levels completed! "+medal.toUpperCase()+" medal, final reward: "+reward+" coins.");updateStats();}
else{state.level++;save();startLevel();msg("Level complete! "+medal.toUpperCase()+" medal • +"+reward+" coins. Next: level "+(state.level+1));}save();}
function renderShop(){const box=$("items");box.replaceChildren();
for(const upgrade of cfg.shop){const b=document.createElement("button");
const id=upgrade.ownedVariable||"Owned_"+upgrade.id,owned=!!state.owned[id];
b.textContent=owned?"✓ "+upgrade.name:upgrade.name+" — "+upgrade.cost+" coins";
b.disabled=owned;b.onclick=()=>{if(state.owned[id])return;
if(state.coins<upgrade.cost){msg("Not enough coins.");return;}
state.coins-=upgrade.cost;state.owned[id]=true;
const effect=upgrade.effect||{};
state.speed+=Number(effect.playerMaxSpeedAdd)||0;
state.coins+=Number(effect.coinsAdd)||0;
state.petMood=clamp(state.petMood+(Number(effect.moodAdd)||0),0,100);
state.petEnergy=clamp(state.petEnergy+(Number(effect.energyAdd)||0),0,100);
state.petCleanliness=clamp(state.petCleanliness+(Number(effect.cleanlinessAdd)||0),0,100);
save();renderShop();updateStats();msg("Purchased "+upgrade.name);};box.appendChild(b);}}
function renderWardrobe(){const box=$("cosmetics");box.replaceChildren();
for(const item of cfg.cosmetics){const owned=!!state.cosmeticsOwned[item.id],equipped=state.equippedCosmetic===item.id;
const b=document.createElement("button");b.textContent=equipped?"✓ "+item.name+" (equipped)":owned?"Wear "+item.name:item.name+" — "+item.price+" coins";
b.onclick=()=>{if(!owned){if(state.coins<item.price){msg("Not enough coins for "+item.name);return;}
state.coins-=item.price;state.cosmeticsOwned[item.id]=true;}
state.equippedCosmetic=item.id;save();renderWardrobe();updateStats();msg("Equipped "+item.name);};box.appendChild(b);}}
$("shopToggle").onclick=()=>{$("shop").classList.toggle("open");renderShop();};
$("victoryClose").onclick=()=>{$("victory").hidden=true;document.getElementById("achievements").scrollIntoView({behavior:"smooth",block:"start"});};
$("victoryRestart").onclick=()=>{$("victory").hidden=true;$("reset").click();};
$("homeToggle").onclick=()=>{homeMode=!homeMode;paused=homeMode;$( "homeToggle").textContent=homeMode?"🎮 Adventure":"🏠 Pet home";$("pause").textContent=paused?"Resume":"Pause";msg(homeMode?"Welcome home! Take care of your bunny.":"Adventure resumed!");};
$("startGame").onclick=()=>{$("welcome").hidden=true;homeMode=true;paused=true;$( "homeToggle").textContent="🎮 Adventure";$("pause").textContent="Pause";msg("Adventure started! Collect coins and protect your bunny.");};
$("pause").textContent="Resume";
$("pause").onclick=()=>{if(!$("welcome").hidden)return;if(homeMode){homeMode=false;$("homeToggle").textContent="🏠 Pet home";}paused=!paused;$("pause").textContent=paused?"Resume":"Pause";msg(paused?"Game paused.":"Game resumed.");};
$("reset").onclick=()=>{if(!confirm("Erase saved progress and restart?"))return;
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;state.petEnergy=75;state.petMood=75;state.petCleanliness=75;hearts=[];petCooldown=0;dashCooldown=0;dashRequested=false;state.questsCompleted=0;state.trainingSessions=0;state.petSkill=0;state.levelsCompleted=0;state.claimedMilestones={};state.claimedChallenges={};state.bossChallengesWon=0;state.starTokens=0;trainingCooldown=0;state.goldMedals=0;state.silverMedals=0;state.bronzeMedals=0;state.totalCoinsCollected=0;state.achievements={};state.petXP=0;state.petStage=1;state.petBornAt=Date.now();state.petPersonality=["playful","gentle","curious"][Math.floor(Math.random()*3)];state.petHumor=["prankster","clown","polite"][Math.floor(Math.random()*3)];state.humorHabits={prank:30,clown:30,polite:30};state.cleaningSkill=0;state.tidyingSkill=0;state.gardeningSkill=0;state.lastChoreAt=0;state.choreStreak=0;state.bestChoreStreak=0;state.choreDaily={date:"",done:0,claimed:false};state.choreTotal=0;state.choreWeeklyClaimed=0;state.favoriteChore="toy";state.petName="Nuppu";state.petSpecies="bunny";state.petColor="mint";state.petWish="";state.petWishAt=0;state.petWishCompleted=0;state.petNameCalls=0;state.petRecipesMade=0;state.petBaths=0;state.petTeethBrushed=0;state.petClinicVisits=0;state.petCookingSkill=0;state.petHygieneSkill=0;state.petGarden={seed:"",plantedAt:0,wateredAt:0,harvests:0,flowers:0};state.choreRewardsClaimed=[];state.choreFailures=0;state.choreFastWins=0;state.choreToyWins=0;state.chorePlantWins=0;state.choreFirstReward=false;humorPending="";humorPendingUntil=0;prankSurprise="";prankSurpriseUntil=0;toySearchTries=0;messPieces=0;messHelperClock=0;messHelperActions=0;choreVisualKind="";choreVisualUntil=0;choreVisualStart=0;choreToyMask=0;choreWaterCount=0;choreDrag=null;choreDifficulty=1;choreGoal=3;choreRetryKind="";state.dailyCare={date:"",feed:0,play:0,clean:0,rest:0,claimed:false};hatchAnimationUntil=0;state.petSleeping=false;state.sleepStartedAt=0;state.dreamKind="";state.lastMorningDate="";state.petSick=false;state.petMess=0;state.petDiscipline=50;state.roomOwned={};state.roomEquipped={wall:"default",floor:"default",furniture:"none",toy:"none"};state.homeSurprise={kind:"",expires:0,nextAt:Date.now()+90000};state.careQuality=65;state.petWeight=50;state.petFullness=45;state.treatsToday=0;state.treatDate="";state.friendship=20;state.favoriteFood=Math.floor(Math.random()*(cfg.foods.length+3));state.dislikedFood=(state.favoriteFood+1+Math.floor(Math.random()*(cfg.foods.length+2)))%(cfg.foods.length+3);state.petMemories=[];state.celebrationsClaimed={};state.petTrait="";state.cosmeticsOwned={};state.equippedCosmetic="";won=false;paused=false;$("victory").hidden=true;$("pause").textContent="Pause";boutiqueSave=normalizeBoutique(null);state.boutique=boutiqueSave;save();try{localStorage.removeItem(boutiqueKey);localStorage.removeItem(KEY+"_expansion_v2");}catch(_){}location.reload();};
$("trainPet").onclick=()=>{if(paused||won){msg("Resume playing to train your companion.");return;}
if(trainingCooldown>0){msg("Your companion needs a break before training again.");return;}
if(state.coins<20){msg("Training costs 20 coins.");return;}
if(state.petEnergy<15||state.petHunger<15){msg("Feed or rest your companion before training.");return;}
state.coins-=20;state.petEnergy=clamp(state.petEnergy-15,0,100);
state.petHunger=clamp(state.petHunger-8,0,100);state.petMood=clamp(state.petMood+6,0,100);
state.trainingSessions++;trainingCooldown=25;
burst(pet.x,pet.y,"#b5eaff",22);gainPetXP(25);save();updateStats();
msg("🎓 Great training! +25 pet XP. Sessions: "+state.trainingSessions);};
$("skillPet").onclick=()=>{if(state.petStage<3){msg("Unlock pet skills at evolution stage 3.");return;}
if(state.petSkill>=3){msg("Your companion's skill is already maxed out.");return;}
const cost=100*(state.petSkill+1);if(state.coins<cost){msg("Skill upgrade costs "+cost+" coins.");return;}
if(state.trainingSessions<(state.petSkill+1)*3){msg("Complete "+((state.petSkill+1)*3)+" training sessions to upgrade.");return;}
state.coins-=cost;state.petSkill++;burst(pet.x,pet.y,"#e4c2ff",25);
save();updateStats();msg("✨ Companion skill upgraded to "+state.petSkill+"/3!");};
function petCompanion(){if((paused&&!homeMode)||won){msg("Resume playing to interact with your pet.");return;}
if(state.petSleeping){msg("Your pet is asleep. Let it rest.");return;}
if(petCooldown>0){msg("Your pet needs a moment before more cuddles.");return;}
petCooldown=4;gainFriendship(3);state.petMood=clamp(state.petMood+(state.petPersonality==="gentle"?15:state.petTrait==="kind"?12:8),0,100);
petReaction("cuddle",state.friendship>=85?"💞 You're my best friend!":state.friendship>=60?"❤️ I love being with you!":state.petPersonality==="gentle"?"❤️ More cuddles!":"💕 Thank you!");
hearts.push(...Array.from({length:6},(_,i)=>({x:pet.x+(i-2.5)*7,y:pet.y-25,vx:(i-2.5)*12,vy:-35-rand(0,25),life:1.3})));
const cuddleXP=state.petPersonality==="gentle"?6:3;gainPetXP(cuddleXP);save();updateStats();msg("❤️ Your companion loves the attention! +"+cuddleXP+" XP.");}
$("petPet").onclick=petCompanion;
canvas.addEventListener("pointerdown",e=>{if(!homeMode||state.petStage===1)return;
const bounds=canvas.getBoundingClientRect(),x=(e.clientX-bounds.left)*W/bounds.width,y=(e.clientY-bounds.top)*H/bounds.height;
if(choreVisualKind&&performance.now()<choreVisualUntil){const i=choreVisualKind==="toy"?choreToyPositions().slice(0,choreGoal).findIndex((v,i)=>!(choreToyMask&(1<<i))&&Math.hypot(x-v,y-H*.79)<45):(Math.hypot(x-W*.52,y-H*.48)<65?0:-1);if(i>=0){choreDrag={id:e.pointerId,index:i,x,y};e.preventDefault();canvas.setPointerCapture(e.pointerId);return;}}
if(prankSurprise==="toy"&&performance.now()<prankSurpriseUntil){const spots=[{x:W*.18,y:H*.76},{x:W*.5,y:H*.83},{x:W*.82,y:H*.76}];const index=spots.findIndex(p=>Math.hypot(x-p.x,y-p.y)<42);if(index>=0){e.preventDefault();searchToySpot(index);return;}}
if(prankSurprise==="mess"&&performance.now()<prankSurpriseUntil){const spots=[{x:W*.16,y:H*.72},{x:W*.37,y:H*.86},{x:W*.65,y:H*.83},{x:W*.85,y:H*.7}];const index=spots.findIndex(p=>Math.hypot(x-p.x,y-p.y)<39);if(index>=0){e.preventDefault();collectMessPiece(index);return;}}
if(Math.abs(x-W/2)<110&&Math.abs(y-(H/2+60))<135)petCompanion();});
canvas.addEventListener("pointermove",e=>{if(!choreDrag||choreDrag.id!==e.pointerId)return;const p=canvasPoint(e);choreDrag.x=p.x;choreDrag.y=p.y;});
function releaseChoreDrag(e){if(!choreDrag||choreDrag.id!==e.pointerId)return;const p=canvasPoint(e),drag=choreDrag;choreDrag=null;if(e.type==="pointercancel")return;const target=choreVisualKind==="toy"?{x:W*.78,y:H*.77}:{x:W*.77,y:H*.75};if(Math.hypot(p.x-target.x,p.y-target.y)<78){interactChore(choreVisualKind==="toy"?choreToyPositions()[drag.index]:W*.52,choreVisualKind==="toy"?H*.79:H*.48);}else msg("🎯 Drop it on the "+(choreVisualKind==="toy"?"basket!":"plant!"));}
canvas.addEventListener("pointerup",releaseChoreDrag);canvas.addEventListener("pointercancel",releaseChoreDrag);
function friendshipRank(){return state.friendship>=85?"Best friends":state.friendship>=60?"Close friends":state.friendship>=30?"Growing bond":"Getting acquainted";}
function rememberPet(text){state.petMemories.push({time:Date.now(),text:String(text).slice(0,140)});state.petMemories=state.petMemories.slice(-30);renderPetDiary();}
function renderPetDiary(){const root=$("diaryEntries");root.replaceChildren();if(!state.petMemories.length){root.textContent="Your adventures together will appear here.";return;}
for(const entry of state.petMemories.slice(-12).reverse()){const p=document.createElement("p");p.textContent=new Date(entry.time).toLocaleString()+" • "+entry.text;root.appendChild(p);}}
function gainFriendship(points){const before=friendshipRank();state.friendship=clamp(state.friendship+points,0,100);const after=friendshipRank();if(before!==after){rememberPet("💞 Friendship reached "+after);msg("💞 Friendship milestone: "+after+"!");}}
function friendshipActivity(required,energyCost,moodGain,bondGain,kind,message){if(state.friendship<required){msg("💞 Unlock this activity at "+required+" friendship.");return;}
if(state.petSleeping||state.petSick){msg("Your pet needs to be awake and healthy.");return;}
if(state.petEnergy<energyCost){msg("Your pet is too tired for this activity.");return;}
state.petEnergy=clamp(state.petEnergy-energyCost,0,100);state.petMood=clamp(state.petMood+moodGain,0,100);
gainFriendship(bondGain);petReaction(kind,message);rememberPet(message);gainPetXP(6+Math.floor(required/10));save();updateStats();msg(message);}
$("friendTrick").onclick=()=>friendshipActivity(30,8,8,2,"trick","🐾 Your pet learned a cute trick!");
$("friendPicnic").onclick=()=>friendshipActivity(60,12,18,3,"picnic","🧺 What a lovely picnic together!");
$("friendDance").onclick=()=>friendshipActivity(85,15,25,4,"dance","💞 Best friends forever!");
const extraFoods=[{name:"🍓 Strawberry treat",price:18,hunger:12,energy:2,mood:18},{name:"🥕 Crunchy carrot",price:12,hunger:22,energy:3,mood:7},{name:"🍪 Sweet cookie",price:15,hunger:10,energy:4,mood:14}];
const allPetFoods=[...cfg.foods,...extraFoods];
function updateFoodPreference(){const favorite=allPetFoods[state.favoriteFood],disliked=allPetFoods[state.dislikedFood];
$("foodPreference").textContent="😋 Favorite: "+(favorite?favorite.name:"Unknown")+" • 😕 Dislikes: "+(disliked?disliked.name:"Unknown");}
function feedPet(){const index=Number($("foodChoice").value),food=allPetFoods[index];if(!food){msg("No food available.");return;}
const day=new Date().toLocaleDateString("en-CA");if(state.treatDate!==day){state.treatDate=day;state.treatsToday=0;}
const isTreat=index>=cfg.foods.length&&index!==cfg.foods.length+1;
const overfed=state.petFullness>=85;
if(state.petFullness>=100){msg("🍽️ Your pet's tummy is completely full! Give it a break.");return;}
if(isTreat&&state.treatsToday>=3){msg("🍓 Enough treats for today. Try a balanced meal!");return;}
if(state.coins<food.price){msg("Not enough coins to feed your pet.");return;}
state.coins-=food.price;state.petHunger=clamp(state.petHunger+(Number(food.hunger)||0),0,100);
state.petFullness=clamp(state.petFullness+(isTreat?12:Math.max(15,Math.round((Number(food.hunger)||0)*.65))),0,100);
state.petEnergy=clamp(state.petEnergy+(Number(food.energy)||0),0,100);
state.petWeight=clamp(state.petWeight+(overfed?7:isTreat?2:state.petHunger>=80?2:0),5,100);
if(overfed)state.petMood=clamp(state.petMood-6,0,100);
if(isTreat)state.treatsToday++;
const liked=index===state.favoriteFood,disliked=index===state.dislikedFood&&!liked;
state.petMood=clamp(state.petMood+(Number(food.mood)||0)+(liked?12:disliked?-8:0),0,100);
feedingVisual={until:performance.now()+3000,emoji:index===cfg.foods.length?"🍓":index===cfg.foods.length+1?"🥕":index===cfg.foods.length+2?"🍪":"🍽️",liked,disliked};
gainFriendship(liked?4:disliked?1:2);gainPetXP(state.petPersonality==="curious"?11:8);recordCare("feed");if(overfed)sound("belly");petReaction(overfed?"belly":"eat",overfed?"🎈 Burp! My tummy is a balloon!":liked?"😍 My favorite!":disliked?"😕 Not my favorite...":"😋 Yummy!");save();updateStats();msg("Fed pet: "+food.name+(liked?" • Favorite food bonus!":disliked?" • Your pet wasn't thrilled.":""));}
for(const [index,food] of allPetFoods.entries()){const option=document.createElement("option");option.value=index;
option.textContent=food.name+" ("+food.price+" coins)";$("foodChoice").appendChild(option);}
$("feed").onclick=feedPet;$("feedSelected").onclick=feedPet;
$("toiletPet").onclick=()=>{if(state.petMess===0){msg("🚽 Everything is already tidy.");return;}
const amount=state.petMess;state.petMess=0;state.petCleanliness=clamp(state.petCleanliness+Math.min(20,amount*5),0,100);
state.petMood=clamp(state.petMood+4,0,100);state.careQuality=clamp(state.careQuality+2,0,100);petReaction("toilet","🚽 All clean!");save();updateStats();msg("🚽 Cleaned up after your pet!");};
$("disciplinePet").onclick=()=>{if(state.petSleeping){msg("Let your pet sleep.");return;}
if(state.petEnergy<10){msg("Your pet is too tired to learn.");return;}
state.petEnergy=clamp(state.petEnergy-5,0,100);state.petDiscipline=clamp(state.petDiscipline+12,0,100);state.careQuality=clamp(state.careQuality+1,0,100);
petReaction("learn","📣 Good manners!");gainPetXP(4);save();updateStats();msg("Your pet learned good manners!");};
$("cleanPet").onclick=()=>{if(state.coins<15){msg("Cleaning costs 15 coins.");return;}
if(state.petCleanliness>=100){msg("Your pet is already clean.");return;}
state.coins-=15;state.petCleanliness=clamp(state.petCleanliness+35,0,100);
state.petMood=clamp(state.petMood+5,0,100);gainFriendship(2);petReaction("clean","🫧 So fresh!");recordCare("clean");gainPetXP(10);save();updateStats();msg("Your pet feels fresh!");};
$("playPet").onclick=()=>{if(state.petEnergy<12){msg("Your pet is too tired. Let it rest.");return;}
state.petEnergy=clamp(state.petEnergy-12,0,100);
state.petMood=clamp(state.petMood+(state.petPersonality==="playful"?28:22)+(state.roomEquipped.toy!=="none"?10:0),0,100);
state.petHunger=clamp(state.petHunger-6,0,100);
state.petCleanliness=clamp(state.petCleanliness-5,0,100);
gainFriendship(5);if(state.petWeight>=75){petReaction("belly","🎈 Boing-boing! Belly bounce!");sound("belly");}else if(state.petWeight<=25){petReaction("skinny","🍃 Whoosh! A tiny breeze!");sound("skinny");}else petReaction("play","🎾 Wheee!");recordCare("play");gainPetXP((state.petPersonality==="playful"?20:15)+(state.roomEquipped.toy==="blocks"?5:0));save();updateStats();msg("Your pet loved playing!");};
$("restPet").onclick=()=>{if(state.petEnergy>=100){msg("Your pet is fully rested.");return;}
state.petEnergy=clamp(state.petEnergy+(state.roomEquipped.furniture==="bed"?45:30),0,100);
state.petHunger=clamp(state.petHunger-5,0,100);
petReaction("rest","💤 Nice nap!");recordCare("rest");gainPetXP(5);save();updateStats();msg("Your pet had a nice nap.");};
$("sleepPet").onclick=()=>{const waking=state.petSleeping;state.petSleeping=!state.petSleeping;
if(waking){const slept=Math.max(0,Date.now()-(state.sleepStartedAt||Date.now()));
if(slept>=60000){const dream=state.dreamKind||"happy";const moodChange=dream==="nightmare"?-4:dream==="adventure"?7:10;
state.petMood=clamp(state.petMood+Math.min(12,Math.floor(slept/60000)*2)+moodChange,0,100);
petReaction("wake",dreamWakeMessage(dream));msg("💭 "+dreamWakeMessage(dream));}
else petReaction("wake","☀️ Good morning!");state.sleepStartedAt=0;state.dreamKind="";}
else{state.sleepStartedAt=Date.now();state.dreamKind=choosePetDream();petReaction("sleep","🌙 Sweet dreams!");}
save();updateStats();msg(state.petSleeping?"🌙 Your pet is sleeping.":"☀️ Your pet woke up!");};
$("healPet").onclick=()=>{if(!state.petSick){msg("Your pet is healthy!");return;}
if(state.coins<25){msg("Medicine costs 25 coins.");return;}
state.coins-=25;state.petSick=false;state.petMood=clamp(state.petMood+10,0,100);petReaction("heal","❤️ Feeling better!");save();updateStats();msg("💊 Your pet feels better!");};
$("dash").onclick=()=>{dashRequested=true;};
addEventListener("keydown",e=>{if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"," "].includes(e.key))e.preventDefault();
if(e.key===" "&&!e.repeat)dashRequested=true;keys.add(e.key.toLowerCase());});
addEventListener("keyup",e=>keys.delete(e.key.toLowerCase()));
addEventListener("blur",()=>keys.clear());
for(const b of document.querySelectorAll("[data-key]")){
const key=b.dataset.key.toLowerCase();
b.addEventListener("pointerdown",e=>{e.preventDefault();b.setPointerCapture(e.pointerId);keys.add(key);});
for(const event of ["pointerup","pointercancel","lostpointercapture"])b.addEventListener(event,()=>keys.delete(key));
}
function circle(x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();}
function drawObstacle(o){const theme=state.level%worlds.length;
ctx.save();ctx.translate(o.x,o.y);ctx.fillStyle="#101c2b77";ctx.beginPath();ctx.ellipse(4,o.r*.7,o.r*1.1,o.r*.43,0,0,Math.PI*2);ctx.fill();
if(theme===0){ctx.fillStyle="#785a42";ctx.fillRect(-o.r*.2,-o.r*.15,o.r*.4,o.r*.95);
for(let j=0;j<3;j++)circle((j-1)*o.r*.35,-o.r*.35-(j%2)*o.r*.25,o.r*.55,j===1?"#6fc184":"#3e996c");
circle(-o.r*.3,-o.r*.65,o.r*.12,"#d5f4aa");}
else if(theme===1){ctx.fillStyle="#483c7e";ctx.beginPath();ctx.ellipse(0,o.r*.3,o.r*.8,o.r*.4,0,0,Math.PI*2);ctx.fill();
for(let j=-1;j<=1;j++){ctx.fillStyle=j===0?"#a9e8ff":"#a88fe9";ctx.beginPath();ctx.moveTo(j*o.r*.5-o.r*.23,o.r*.25);ctx.lineTo(j*o.r*.5,-o.r*(j===0?1.25:.7));ctx.lineTo(j*o.r*.5+o.r*.28,o.r*.25);ctx.closePath();ctx.fill();}}
else if(theme===2){circle(0,0,o.r,"#b7814f");circle(-o.r*.23,-o.r*.22,o.r*.62,"#d8a36a");
ctx.strokeStyle="#8b603f";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-o.r*.4,-o.r*.1);ctx.lineTo(0,o.r*.16);ctx.lineTo(o.r*.3,-o.r*.1);ctx.stroke();}
else{ctx.fillStyle="#a5dbe9";ctx.beginPath();ctx.moveTo(-o.r,o.r*.6);ctx.lineTo(-o.r*.55,-o.r*.6);ctx.lineTo(0,-o.r*1.15);ctx.lineTo(o.r*.8,-o.r*.35);ctx.lineTo(o.r,o.r*.6);ctx.closePath();ctx.fill();
ctx.fillStyle="#e4fbff";ctx.beginPath();ctx.moveTo(-o.r*.55,-o.r*.6);ctx.lineTo(0,-o.r*1.15);ctx.lineTo(o.r*.32,-o.r*.68);ctx.lineTo(0,-o.r*.42);ctx.closePath();ctx.fill();}
ctx.restore();}
function drawTreasure(t){const bob=Math.sin(visualTime*3+t.x*.1)*3;
ctx.save();ctx.translate(t.x,t.y+bob);circle(0,0,20,"#fff8ad22");
const color=t.kind==="gem"?"#7de7ff":t.kind==="magnet"?"#f6c46a":t.kind==="boost"?"#e9b0ff":t.kind==="star"?"#ffe18a":"#9ef7b8";
ctx.fillStyle=color;ctx.strokeStyle="#ffffff";ctx.lineWidth=2;
ctx.beginPath();ctx.moveTo(0,-13);ctx.lineTo(12,-3);ctx.lineTo(8,10);ctx.lineTo(-8,10);ctx.lineTo(-12,-3);ctx.closePath();ctx.fill();ctx.stroke();
ctx.fillStyle="#24354d";ctx.font="bold 16px system-ui";ctx.textAlign="center";ctx.fillText(t.kind==="gem"?"★":t.kind==="magnet"?"M":t.kind==="boost"?"⚡":t.kind==="star"?"★":"✚",0,5);ctx.restore();}
function drawCoin(c){const pulse=1+Math.sin(visualTime*5+c.x*.07)*.1;
const r=c.r*pulse;circle(c.x,c.y,r+6,"#ffd55b33");
const shine=ctx.createRadialGradient(c.x-r*.35,c.y-r*.4,1,c.x,c.y,r);
shine.addColorStop(0,"#fff9bf");shine.addColorStop(.5,"#ffd85c");shine.addColorStop(1,"#d78b28");circle(c.x,c.y,r,shine);
ctx.strokeStyle="#fff0a5";ctx.lineWidth=1.7;ctx.beginPath();ctx.arc(c.x,c.y,r*.7,0,Math.PI*2);ctx.stroke();
ctx.fillStyle="#a86c24";ctx.font="bold "+Math.round(r*1.25)+"px system-ui";ctx.textAlign="center";ctx.fillText("★",c.x,c.y+r*.44);ctx.textAlign="left";}
function drawEnemy(e){ctx.save();ctx.translate(e.x,e.y+Math.sin(visualTime*6+e.x*.02)*2);
circle(2,4,e.r+3,"#511d3d88");const g=ctx.createRadialGradient(-5,-7,1,0,0,e.r+2);
const palette=e.type==="boss"?["#ffddbd","#dc3e61","#631c4b"]:e.type==="guardian"?["#aaf7ec","#3bbaa6","#176a73"]:e.type==="chaser"?["#ffde95","#ef9a3b","#a75226"]:e.type==="sprinter"?["#d7b8ff","#9868df","#633f9b"]:["#ffb0b3","#f45e83","#ac365c"];
g.addColorStop(0,palette[0]);g.addColorStop(.55,palette[1]);g.addColorStop(1,palette[2]);
if(e.type==="boss"){const glow=.25+.18*Math.sin(visualTime*4);
circle(0,0,e.r+14,"rgba(255,70,140,"+glow+")");
ctx.strokeStyle="#ffb5dd";ctx.lineWidth=3;ctx.beginPath();ctx.arc(0,0,e.r+8,visualTime,visualTime+Math.PI*1.25);ctx.stroke();}
circle(0,0,e.r,g);
for(const side of [-1,1]){ctx.fillStyle=e.type==="boss"?"#68204b":e.type==="guardian"?"#217d80":"#a83b65";ctx.beginPath();ctx.moveTo(side*e.r*.55,-e.r*.6);ctx.lineTo(side*e.r*.8,-e.r*1.22);ctx.lineTo(side*e.r*.08,-e.r*.87);ctx.closePath();ctx.fill();}
if(e.type==="boss"){ctx.fillStyle="#ffd36b";ctx.beginPath();ctx.moveTo(-12,-e.r*.8);ctx.lineTo(-7,-e.r-12);ctx.lineTo(0,-e.r*.85);ctx.lineTo(7,-e.r-12);ctx.lineTo(12,-e.r*.8);ctx.closePath();ctx.fill();}
circle(-5,-3,4,"#fff");circle(6,-3,4,"#fff");circle(-4,-3,2,"#28203a");circle(7,-3,2,"#28203a");
ctx.strokeStyle="#802744";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-4,7);ctx.lineTo(4,7);ctx.stroke();
if(e.type==="boss"){ctx.fillStyle="#fff0ba";ctx.font="bold 10px system-ui";ctx.textAlign="center";ctx.fillText("BOSS",0,-e.r-17);}
ctx.restore();}
function drawBunny(x,y,scale,bodyColor,walking,face=1,expression="happy"){
const bounce=walking?Math.abs(Math.sin(visualTime*12))*3:Math.sin(visualTime*2)*1.3;
ctx.save();ctx.translate(x,y-bounce);ctx.scale(scale*face,scale);
ctx.fillStyle="#10242b66";ctx.beginPath();ctx.ellipse(0,19,19,6,0,0,Math.PI*2);ctx.fill();
ctx.fillStyle=bodyColor;
const earSway=Math.sin(visualTime*(walking?10:2.2)+x*.02)*.09;
ctx.save();ctx.rotate(earSway);
const species=state.petSpecies||"bunny";
if(species==="kitten"){ctx.beginPath();ctx.moveTo(-19,-8);ctx.lineTo(-17,-35);ctx.lineTo(-2,-19);ctx.moveTo(19,-8);ctx.lineTo(17,-35);ctx.lineTo(2,-19);ctx.closePath();ctx.fill();ctx.fillStyle="#f4a7bb";ctx.beginPath();ctx.moveTo(-15,-14);ctx.lineTo(-15,-28);ctx.lineTo(-7,-18);ctx.moveTo(15,-14);ctx.lineTo(15,-28);ctx.lineTo(7,-18);ctx.fill();}
else if(species==="puppy"){ctx.beginPath();ctx.ellipse(-21,-12,9,17,-.4,0,Math.PI*2);ctx.ellipse(21,-12,9,17,.4,0,Math.PI*2);ctx.fill();}
else{ctx.beginPath();ctx.ellipse(-9,-23,7,20,-.15,0,Math.PI*2);ctx.ellipse(9,-23,7,20,.15,0,Math.PI*2);ctx.fill();ctx.fillStyle="#f4a7bb";ctx.beginPath();ctx.ellipse(-9,-24,3,13,-.15,0,Math.PI*2);ctx.ellipse(9,-24,3,13,.15,0,Math.PI*2);ctx.fill();}ctx.restore();
// Tiny feet and tail make the character readable at mobile sizes.
const step=walking?Math.sin(visualTime*12)*3:0;
circle(-12,16+step,8,bodyColor);circle(12,16-step,8,bodyColor);
circle(17,9,7,"#ffffffbb");
const fur=ctx.createRadialGradient(-8,-8,2,0,2,25);fur.addColorStop(0,"#ffffffbb");fur.addColorStop(.35,bodyColor);fur.addColorStop(1,bodyColor);
circle(0,1,19,fur);
ctx.fillStyle="#ffffffaa";ctx.beginPath();ctx.ellipse(-5,10,9,6,0,0,Math.PI*2);ctx.fill();
ctx.fillStyle="#ffffff55";ctx.beginPath();ctx.ellipse(-11,-10,5,3,-.5,0,Math.PI*2);ctx.fill();
const blink=expression==="sleepy"||Math.sin(visualTime*1.8+x*.03)>.995;
ctx.fillStyle="#243040";if(blink){ctx.fillRect(-11,-3,7,2);ctx.fillRect(5,-3,7,2);}else{
ctx.beginPath();ctx.ellipse(-8,-3,3.4,4.8,0,0,Math.PI*2);ctx.ellipse(8,-3,3.4,4.8,0,0,Math.PI*2);ctx.fill();
circle(-7,-5,1.3,"#ffffff");circle(9,-5,1.3,"#ffffff");}
circle(0,5,2.7,"#e88099");
ctx.strokeStyle="#75445a";ctx.lineWidth=1.6;ctx.beginPath();
if(expression==="sad"){ctx.arc(0,15,4,Math.PI*1.1,Math.PI*1.9);}else if(expression==="excited"){ctx.arc(0,8,7,0,Math.PI); }else{ctx.arc(0,8,5,.1,Math.PI-.1);}
ctx.stroke();ctx.fillStyle="#ed91a5";circle(-14,6,3,"#ed91a577");circle(14,6,3,"#ed91a577");
// Fine whiskers and cheek highlights.
ctx.strokeStyle="#ffffff99";ctx.lineWidth=.9;
for(const side of [-1,1])for(const angle of [-.24,.14]){ctx.beginPath();ctx.moveTo(side*11,7);
ctx.lineTo(side*26,7+angle*20);ctx.stroke();}
const outfit=boutiqueSelected("outfit");if(outfit){ctx.save();ctx.scale(face,1);ctx.font="22px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";const yOffsets={outfit_sunhat:-36,outfit_bow:-21,outfit_hoodie:13,outfit_glasses:-4,outfit_cape:15,outfit_crown:-36,outfit_pajamas:13,outfit_boots:22};const baseId=outfit.theme?outfit.id.slice(0,-outfit.theme.length-1):outfit.id;Object.assign(yOffsets,{outfit_scarf:8,outfit_cap:-36,outfit_tophat:-38,outfit_dress:17,outfit_shirt:12,outfit_mittens:20,outfit_backpack:15,outfit_headphones:-15});boutiqueThemeEffect(outfit);ctx.fillText(outfit.emoji,0,yOffsets[baseId]??-25);ctx.restore();}for(const [i,id] of boutiqueSave.extraOutfits.entries()){if(outfit&&outfit.id===id)continue;const item=(cfg.collectibles||[]).find(x=>x.id===id);if(item){ctx.save();ctx.scale(face,1);ctx.font="17px system-ui";ctx.textAlign="center";boutiqueThemeEffect(item);ctx.fillText(item.emoji,i===0?-17:17,i===0?-15:12);ctx.restore();}}
ctx.restore();}
const homeWander={x:400,target:400,next:0,step:0};
function advancePetWander(dt){if(state.petSleeping||state.petSick||state.petStage===1)return;if(visualTime>=homeWander.next){homeWander.target=170+Math.random()*450;homeWander.next=visualTime+4+Math.random()*7;}const dx=homeWander.target-homeWander.x;homeWander.step=Math.abs(dx)>3?Math.sign(dx):0;homeWander.x+=homeWander.step*Math.min(Math.abs(dx),dt*(state.petEnergy<25?22:45));}
function frame(t){const dt=Math.min(.05,(t-(frame.last||t))/1000);frame.last=t;
if(document.hidden){requestAnimationFrame(frame);return;}
musicTick(dt);
if(homeMode){visualTime+=dt;advancePetWander(dt);petCooldown=Math.max(0,petCooldown-dt);careTick(dt);}
if(!paused&&!homeMode){visualTime+=dt;petCooldown=Math.max(0,petCooldown-dt);
levelBanner=Math.max(0,levelBanner-dt);hitFlash=Math.max(0,hitFlash-dt);
trainingCooldown=Math.max(0,trainingCooldown-dt);dashCooldown=Math.max(0,dashCooldown-dt);
$("dash").disabled=paused||won||dashCooldown>0;$("dash").textContent=dashCooldown>0?"💨 Dash "+Math.ceil(dashCooldown)+"s":"💨 Dash";
companionCollectCooldown=Math.max(0,companionCollectCooldown-dt);
magnetTime=Math.max(0,magnetTime-dt);shieldTime=Math.max(0,shieldTime-dt);boostTime=Math.max(0,boostTime-dt);
for(const p of particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=90*dt;p.life-=dt;}
particles=particles.filter(p=>p.life>0);
for(const h of hearts){h.x+=h.vx*dt;h.y+=h.vy*dt;h.life-=dt;}
hearts=hearts.filter(h=>h.life>0);}
ctx.clearRect(0,0,W,H);drawWorldBackdrop();
ctx.save();ctx.globalAlpha=.22;ctx.strokeStyle=world().grid;ctx.lineWidth=1;
for(let x=0;x<W;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
for(let y=0;y<H;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
ctx.restore();if(!reducedEffects)drawScenery();
if(homeMode){const phase=petDayPhase();const wallColors={default:"#10253b",mint:"#245b54",peach:"#71445c"},floorColors={default:"#38404e",wood:"#80583c",cloud:"#6e829f"};
const boutiqueWall=boutiqueSelected("wallpaper");const boutiqueWallColors={wallpaper_sky:"#8acbe9",wallpaper_forest:"#497e5d",wallpaper_space:"#302459",wallpaper_candy:"#d890bf",wallpaper_ocean:"#287c9c",wallpaper_snow:"#a8c5d8",wallpaper_sunset:"#b76b49",wallpaper_garden:"#548d63"};
ctx.fillStyle=(boutiqueWall&&boutiqueWallColors[boutiqueWall.id])||wallColors[state.roomEquipped.wall]||wallColors.default;ctx.fillRect(65,90,670,325);
ctx.fillStyle=floorColors[state.roomEquipped.floor]||floorColors.default;ctx.fillRect(65,415,670,100);
const roomTheme=boutiqueSave.roomTheme;
ctx.save();const floor=boutiqueSave.roomFloor;if(floor!=="default"){ctx.fillStyle={oak:"#a9784c",tile:"#78969c",marble:"#c4c6ca"}[floor];ctx.fillRect(65,415,670,100);ctx.strokeStyle="#30304030";ctx.lineWidth=2;for(let x=65;x<735;x+=floor==="oak"?48:85){ctx.beginPath();ctx.moveTo(x,415);ctx.lineTo(x,515);ctx.stroke();}if(floor!=="oak"){ctx.beginPath();ctx.moveTo(65,465);ctx.lineTo(735,465);ctx.stroke();}}
if(boutiqueSave.roomCurtain!=="none"){ctx.fillStyle={rose:"#aa5779",blue:"#456da4",cream:"#e0c49e"}[boutiqueSave.roomCurtain];for(const x of [555,681]){ctx.fillRect(x,165,18,130);ctx.fillStyle="#ffffff33";ctx.fillRect(x+6,165,3,130);ctx.fillStyle={rose:"#aa5779",blue:"#456da4",cream:"#e0c49e"}[boutiqueSave.roomCurtain];}}
if(boutiqueSave.roomLamp!=="none"){ctx.fillStyle="#72604e";ctx.fillRect(716,340,5,72);ctx.fillRect(702,409,32,5);ctx.fillStyle={gold:"#e7bd67",mint:"#85dabb",violet:"#b79ae5"}[boutiqueSave.roomLamp];ctx.beginPath();ctx.moveTo(705,310);ctx.lineTo(732,310);ctx.lineTo(739,340);ctx.lineTo(698,340);ctx.closePath();ctx.fill();}ctx.restore();
ctx.save();if(boutiqueSave.roomWindow!=="default"){ctx.beginPath();if(boutiqueSave.roomWindow==="round")ctx.arc(625,230,55,0,Math.PI*2);else{ctx.moveTo(570,285);ctx.lineTo(570,220);ctx.arc(625,220,55,Math.PI,0);ctx.lineTo(680,285);ctx.closePath();}ctx.fillStyle=phase==="night"?"#19294e":"#90d8ef";ctx.fill();ctx.strokeStyle="#e1c7a1";ctx.lineWidth=7;ctx.stroke();ctx.fillStyle=phase==="night"?"#fff4bc":"#ffe39b";ctx.beginPath();ctx.arc(640,218,15,0,Math.PI*2);ctx.fill();}
if(boutiqueSave.roomClock){ctx.fillStyle="#f6e4c4";ctx.beginPath();ctx.arc(235,220,27,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#784e38";ctx.lineWidth=3;ctx.stroke();const now=new Date();for(const [angle,length] of [[(now.getHours()%12+now.getMinutes()/60)*Math.PI/6,13],[now.getMinutes()*Math.PI/30,20]]){ctx.beginPath();ctx.moveTo(235,220);ctx.lineTo(235+Math.sin(angle)*length,220-Math.cos(angle)*length);ctx.stroke();}}ctx.restore();
ctx.save();if(boutiqueSave.roomPlant!=="none"){ctx.font="60px system-ui";ctx.textAlign="center";ctx.fillText({fern:"🪴",cactus:"🌵",flowers:"💐"}[boutiqueSave.roomPlant],690,410);}if(boutiqueSave.roomArt!=="none"){ctx.fillStyle="#dbb98b";ctx.fillRect(90,200,86,90);ctx.fillStyle="#f6e7cf";ctx.fillRect(97,207,72,76);ctx.font="38px system-ui";ctx.textAlign="center";ctx.fillText({moon:"🌙",mountain:"🏔️",heart:"♥"}[boutiqueSave.roomArt],133,260);}ctx.restore();
if(boutiqueSave.roomRug!=="none"){ctx.save();ctx.fillStyle={round:"#b67b9b",woven:"#bf9963",stars:"#485c96"}[boutiqueSave.roomRug];ctx.beginPath();ctx.ellipse(400,477,155,29,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#ffffff55";ctx.lineWidth=3;ctx.stroke();if(boutiqueSave.roomRug==="stars"){ctx.font="18px system-ui";ctx.fillStyle="#ffe6a1";for(let x=300;x<=500;x+=50)ctx.fillText("✦",x,482);}if(boutiqueSave.roomRug==="woven"){ctx.strokeStyle="#ffffff44";for(let x=280;x<=520;x+=20){ctx.beginPath();ctx.moveTo(x,468);ctx.lineTo(x,486);ctx.stroke();}}ctx.restore();}
if(boutiqueSave.roomLighting!=="auto"){ctx.fillStyle=boutiqueSave.roomLighting==="warm"?"#ffbd6620":"#89cfff20";ctx.fillRect(65,90,670,425);}
ctx.save();
if(roomTheme==="cottage"){ctx.strokeStyle="#936e4b";ctx.lineWidth=12;for(const x of [85,230,570,715]){ctx.beginPath();ctx.moveTo(x,90);ctx.lineTo(x,415);ctx.stroke();}ctx.fillStyle="#936e4b";ctx.fillRect(65,180,670,10);}
if(roomTheme==="loft"){ctx.strokeStyle="#ffffff25";ctx.lineWidth=2;for(let y=155;y<415;y+=32){ctx.beginPath();ctx.moveTo(65,y);ctx.lineTo(735,y);ctx.stroke();for(let x=65+(y%64);x<735;x+=80){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+32);ctx.stroke();}}}
if(roomTheme==="observatory"){ctx.fillStyle="#161d46";ctx.beginPath();ctx.arc(400,270,105,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#b2c9ed";ctx.lineWidth=8;ctx.stroke();ctx.fillStyle="#fff0b4";for(let i=0;i<20;i++){const a=i*2.39996,rad=85*Math.sqrt(i/20);ctx.fillRect(400+Math.cos(a)*rad,270+Math.sin(a)*rad,3,3);}}
ctx.restore();
ctx.fillStyle=phase==="night"?"#07152b99":phase==="evening"?"#b95c4050":"#fff3bd15";ctx.fillRect(65,90,670,425);
ctx.save();ctx.textAlign="center";ctx.font="40px system-ui";ctx.fillText(phase==="night"?"🌙":phase==="evening"?"🌇":"☀️",690,155);ctx.restore();
if(typeof extra!=="undefined"&&extra){const room=extra.room||"cozy",decor=extra.decor||"plant";ctx.save();ctx.textAlign="center";ctx.font="55px system-ui";const roomIcons={cozy:"🛏️",kitchen:"🍳",bathroom:"🛁",playroom:"🧸",garden:"🌿"};ctx.fillText(roomIcons[room]||"🛏️",110,380);const decorIcons={plant:"🪴",lamp:"💡",rug:"🌈",poster:"🖼️",couch:"🛋️"};ctx.fillText(decorIcons[decor]||"🪴",675,385);ctx.font="bold 16px system-ui";ctx.fillStyle="#fff7d5";ctx.fillText(room.toUpperCase()+" • "+decor.toUpperCase(),400,215);ctx.restore();}
ctx.strokeStyle="#ffffff55";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(65,415);ctx.lineTo(735,415);ctx.stroke();
if(state.roomEquipped.furniture==="plant"){ctx.font="75px system-ui";ctx.textAlign="center";ctx.fillText("🪴",640,430);}
if(state.roomEquipped.furniture==="bed"){ctx.font="85px system-ui";ctx.textAlign="center";ctx.fillText("🛏️",610,455);}
if(typeof extra!=="undefined"&&extra&&extra.living){ctx.save();ctx.font="45px system-ui";ctx.textAlign="center";ctx.fillText(({ball:"⚽",plush:"🧸",blocks:"🧱",drum:"🥁",kite:"🪁",robot:"🤖",puzzle:"🧩",train:"🚂"})[extra.living.favoriteToy]||"⚽",homeWander.x+85,455);ctx.restore();}
if(state.roomEquipped.toy!=="none"){ctx.font="54px system-ui";ctx.textAlign="center";ctx.fillText(state.roomEquipped.toy==="ball"?"⚽":"🧩",190,460);}
ctx.save();ctx.textAlign="center";const boutiqueFurniture=boutiqueSelected("furniture"),boutiqueToy=boutiqueSelected("toy");
if(boutiqueFurniture){ctx.save();boutiqueThemeEffect(boutiqueFurniture);ctx.font="85px system-ui";ctx.fillText(boutiqueFurniture.emoji,boutiqueSave.positions.furniture?.x??560,boutiqueSave.positions.furniture?.y??420);ctx.restore();}
for(const [i,id] of boutiqueSave.displayed.entries()){if(boutiqueFurniture&&id===boutiqueFurniture.id)continue;const item=(cfg.collectibles||[]).find(x=>x.id===id);if(item){ctx.save();boutiqueThemeEffect(item);ctx.font="55px system-ui";const pos=boutiqueSave.positions[id];ctx.fillText(item.emoji,pos?.x??125+i*130,pos?.y??395);ctx.restore();}}
if(boutiqueToy){ctx.save();boutiqueThemeEffect(boutiqueToy);ctx.font="48px system-ui";ctx.fillText(boutiqueToy.emoji,boutiqueSave.positions.toy?.x??260,boutiqueSave.positions.toy?.y??475);ctx.restore();}
ctx.restore();
ctx.fillStyle="#ffe9b2";ctx.font="bold 34px system-ui";ctx.textAlign="center";ctx.fillText((state.petSpecies==="kitten"?"🐱":state.petSpecies==="puppy"?"🐶":"🐰")+" "+state.petName.toUpperCase()+"\u0027S HOME",W/2,142);
ctx.font="bold 16px system-ui";ctx.fillText(phase==="night"?"Nighttime":phase==="evening"?"Evening":"Daytime",W/2,164);
const reacting=performance.now()<reactionUntil;
const idle=state.petSleeping?"sleep":state.petSick?"sick":state.petTrait==="mischievous"?"zigzag":state.petTrait==="brave"?"bounce":state.petTrait==="kind"?"sway":state.petPersonality==="playful"?"bounce":state.petPersonality==="curious"?"look":"sway";
const funnyActive=performance.now()<funnyEventUntil;
const petMood=funnyActive&&(funnyEventKind==="trip"||funnyEventKind==="sneeze")?"sad":funnyActive&&funnyEventKind==="toot"?"sleepy":state.petSick||state.petMood<25?"sad":state.petSleeping||state.petEnergy<20?"sleepy":reacting&&reactionKind==="eat"?(feedingVisual.disliked?"sad":"excited"):reacting&&reactionKind==="play"?"excited":state.petHunger<25?"sad":"happy";
ctx.font="bold 23px system-ui";ctx.fillStyle="#fff2bd";ctx.fillText(petLifeStages[Math.min(4,Math.max(0,state.petStage-1))]+" • Age "+petAgeLabel(),W/2,186);
if(state.petStage===1){ctx.save();ctx.translate(W/2,H/2+60);ctx.rotate(Math.sin(visualTime*3)*.045);ctx.fillStyle="#f5e8d4";ctx.beginPath();ctx.ellipse(0,0,52,69,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#f8b7d6";ctx.lineWidth=5;ctx.stroke();ctx.restore();}
else {ctx.save();const widthFactor=state.petWeight>=50?1+(state.petWeight-50)/85:Math.max(.62,1-(50-state.petWeight)/115);ctx.translate(W/2,H/2+60);const chubby=state.petWeight>=70&&!state.petSleeping,skinny=state.petWeight<=30&&!state.petSleeping;
if(funnyActive&&funnyEventKind==="clown")ctx.rotate(Math.sin(visualTime*9)*.13);
if(funnyActive&&funnyEventKind==="prank")ctx.rotate(Math.sin(visualTime*5)*.06);
if(funnyActive&&funnyEventKind==="trip")ctx.rotate(-.22*Math.sin(Math.PI*Math.min(1,(funnyEventUntil-performance.now())/3000)));
if(funnyActive&&funnyEventKind==="hiccup")ctx.scale(1,1+Math.sin(visualTime*18)*.035);
if(funnyActive&&funnyEventKind==="sneeze")ctx.translate(Math.sin(visualTime*22)*5,0);
if(chubby)ctx.rotate(Math.sin(visualTime*2.8)*.065);
if(skinny)ctx.rotate(Math.sin(visualTime*1.3)*.035);
ctx.scale(widthFactor*(chubby?1+Math.sin(visualTime*5)*.025:1),1+(chubby?Math.abs(Math.sin(visualTime*5))*.035:skinny?Math.sin(visualTime*2)*.018:0));ctx.translate(-W/2,-(H/2+60));drawBunny(homeWander.x+(idle==="look"?Math.sin(visualTime*.9)*15:idle==="zigzag"?Math.sin(visualTime*2.8)*28:0),H/2+60+(reacting&&reactionKind==="play"?Math.sin(visualTime*16)*9:idle==="bounce"?Math.abs(Math.sin(visualTime*2.5))*7:idle==="zigzag"?Math.abs(Math.sin(visualTime*4))*4:0)+(chubby?Math.abs(Math.sin(visualTime*3))*5:skinny?Math.sin(visualTime*1.8)*3:0),Math.min(3.3,1.6+state.petStage*.35),({mint:"#f7f2ec",peach:"#ffe0ce",lavender:"#dfd2f6",sky:"#cfeaff"})[state.petColor]||"#f7f2ec",homeWander.step!==0,funnyActive&&funnyEventKind==="toot"?Math.sin(visualTime*4)<0?-1:1:idle==="look"&&Math.sin(visualTime*.9)<-.7?-1:1,petMood);ctx.restore();}
if(!state.petSleeping&&state.petStage>1&&(state.petWeight>=75||state.petWeight<=25)){ctx.save();ctx.textAlign="center";ctx.font="26px system-ui";ctx.fillText(state.petWeight>=75?"🎈":"🍃",W/2+120+Math.sin(visualTime*1.7)*9,H/2-15+Math.sin(visualTime*2.4)*8);ctx.restore();}
if(performance.now()<feedingVisual.until&&!state.petSleeping){const remaining=(feedingVisual.until-performance.now())/3000;ctx.save();ctx.textAlign="center";ctx.font="38px system-ui";ctx.fillText(feedingVisual.emoji,W/2-95+Math.sin(visualTime*5)*8,H/2+65-Math.sin(visualTime*9)*4);ctx.font="27px system-ui";ctx.fillText(feedingVisual.liked?"💖":feedingVisual.disliked?"💧":"✨",W/2+85,H/2-65-Math.sin(visualTime*4)*10);ctx.globalAlpha=Math.min(1,Math.max(0,remaining));ctx.font="20px system-ui";ctx.fillText("•  •  •",W/2,H/2+128);ctx.restore();}
if(state.petSleeping&&state.petStage>1){ctx.save();ctx.globalAlpha=.7+.3*Math.sin(visualTime*1.5)**2;ctx.textAlign="center";ctx.font="bold 26px system-ui";ctx.fillStyle="#dbe9ff";ctx.fillText("Z",W/2+92,H/2-70-Math.sin(visualTime*1.2)*10);ctx.font="bold 18px system-ui";ctx.fillText("z",W/2+120,H/2-100-Math.sin(visualTime*1.2)*15);
ctx.font="23px system-ui";ctx.fillText(state.dreamKind==="nightmare"?"☁️":state.dreamKind==="adventure"?"🚀":"💗",W/2+135,H/2-145-Math.sin(visualTime*.8)*8);ctx.restore();}
if(state.friendship>=85&&!state.petSleeping&&state.petStage>1){ctx.save();ctx.fillStyle="#ff9ecb";ctx.font="bold 19px system-ui";ctx.fillText("♥",W/2-85,H/2-80+Math.sin(visualTime*2)*7);ctx.restore();}
if(state.petTrait==="kind"&&!state.petSleeping){ctx.fillStyle="#ffb9d7";ctx.font="bold 20px system-ui";ctx.fillText("♥",W/2+85,H/2-20+Math.sin(visualTime*2)*8);}
if(state.petTrait==="brave"&&!state.petSleeping){ctx.fillStyle="#ffe08a";ctx.font="bold 22px system-ui";ctx.fillText("★",W/2-92,H/2-10+Math.sin(visualTime*2)*5);}
if(homeMode&&choreVisualKind&&performance.now()<choreVisualUntil){const progress=Math.min(1,(performance.now()-choreVisualStart)/(choreVisualUntil-choreVisualStart));const ease=v=>v*v*(3-2*v);ctx.save();ctx.textAlign="center";ctx.fillStyle="#fff1c4";ctx.font="bold 21px system-ui";ctx.fillText("⭐ Level "+choreDifficulty+" • "+(choreVisualKind==="toy"?"🧸 Put away "+choreGoal+" toys!":"🪴 Water "+choreGoal+" times!"),W/2,H*.21);
if(choreVisualKind==="toy"){const targetX=W*.78,targetY=H*.77;for(let i=0;i<choreGoal;i++){const phase=(choreToyMask&(1<<i))?1:0;const x=choreDrag&&choreVisualKind==="toy"&&choreDrag.index===i?choreDrag.x:choreToyPositions()[i]+(targetX-choreToyPositions()[i])*ease(phase),y=choreDrag&&choreVisualKind==="toy"&&choreDrag.index===i?choreDrag.y:H*.79+(targetY-H*.79)*ease(phase)-Math.sin(phase*Math.PI)*45;ctx.font="33px system-ui";ctx.fillText(["🧸","⚽","🪀","🚂","🎲"][i],x,y);}ctx.font="42px system-ui";ctx.fillText("🧺",targetX,targetY+35);}
else{const x=W*.77,y=H*.75;ctx.font="43px system-ui";ctx.save();ctx.translate(choreDrag&&choreVisualKind==="plant"?choreDrag.x:W*.52,choreDrag&&choreVisualKind==="plant"?choreDrag.y:H*.48);ctx.rotate(-.45-Math.sin(progress*12)*.18);ctx.fillText("🚿",0,0);ctx.restore();for(let i=0;i<7;i++){const fall=(progress*2+i*.16)%1;ctx.globalAlpha=Math.max(0,1-fall);ctx.font="21px system-ui";ctx.fillText("💧",W*.56+i*9+fall*40,H*.48+fall*(H*.25));}ctx.globalAlpha=1;ctx.font=(37+Math.round(progress*10))+"px system-ui";ctx.fillText(choreWaterCount>=2?"🌻":"🪴",x,y);ctx.font="bold 19px system-ui";ctx.fillText("💧 "+choreWaterCount+"/"+choreGoal,x,y+62);}
if(progress>.8){ctx.font="bold 19px system-ui";ctx.fillText("⏳ Finish before time runs out!",W/2,H*.34);}ctx.restore();}
if(performance.now()<prankSurpriseUntil&&prankSurprise){ctx.save();ctx.textAlign="center";const t=(prankSurpriseUntil-performance.now())/5000;
if(prankSurprise==="toy"){const spots=[{x:W*.18,y:H*.76,icon:"🛏️"},{x:W*.5,y:H*.83,icon:"📦"},{x:W*.82,y:H*.76,icon:"🪴"}];ctx.font="bold 21px system-ui";ctx.fillStyle="#fff1c4";ctx.fillText("🔎 Find the hidden toy! Tap a spot",W/2,H*.24);for(let i=0;i<spots.length;i++){const p=spots[i];ctx.fillStyle="rgba(255,255,255,.22)";ctx.beginPath();ctx.arc(p.x,p.y,35,0,Math.PI*2);ctx.fill();ctx.font="35px system-ui";ctx.fillText(p.icon,p.x,p.y+12);}}
else if(prankSurprise==="mess"){const spots=[{x:W*.16,y:H*.72,icon:"🧻"},{x:W*.37,y:H*.86,icon:"🍂"},{x:W*.65,y:H*.83,icon:"📄"},{x:W*.85,y:H*.7,icon:"🧦"}];ctx.font="bold 21px system-ui";ctx.fillStyle="#fff1c4";ctx.fillText("🧹 Tap all the litter to clean up!",W/2,H*.24);for(let i=0;i<spots.length;i++)if(messPieces&(1<<i)){const p=spots[i];ctx.fillStyle="rgba(255,255,255,.2)";ctx.beginPath();ctx.arc(p.x,p.y,32,0,Math.PI*2);ctx.fill();ctx.font="31px system-ui";ctx.fillText(p.icon,p.x,p.y+11);}}
else{ctx.font=(38+Math.round((1-t)*15))+"px system-ui";ctx.fillText("👻 BOO!",W/2,H/2-130-Math.sin(visualTime*8)*8);}
ctx.restore();}
if(funnyActive){ctx.save();const elapsed=3000-(funnyEventUntil-performance.now());ctx.font="36px system-ui";ctx.fillText(funnyEventIcon,W/2+110,H/2+15+Math.sin(visualTime*12)*8);
if(elapsed>1500){ctx.font="bold 22px system-ui";ctx.fillStyle="#ffe3aa";ctx.fillText(funnyEventKind==="toot"?"😇 Who, me?":funnyEventKind==="trip"?"😳 Nobody saw that!":funnyEventKind==="sneeze"?"🥺 Bless me!":funnyEventKind==="prank"?"😇 Innocent!":funnyEventKind==="clown"?"🎪 Encore!":funnyEventKind==="polite"?"🎩 Thank you!":"😅 Hic... okay!",W/2,H/2-105);}
ctx.restore();}
if(reacting){ctx.font="bold 25px system-ui";ctx.fillStyle="#fff1c4";ctx.fillText(reactionText,W/2,245);}
if(performance.now()<hatchAnimationUntil){ctx.fillStyle="#ffedb5";ctx.font="bold 29px system-ui";ctx.fillText("✨ 🐣 HATCHED! ✨",W/2,260);
for(let i=0;i<12;i++){const a=i*Math.PI/6+visualTime*.6,r=95+Math.sin(visualTime*5+i)*12;
ctx.fillStyle=i%2?"#ffe88b":"#ffb5de";ctx.beginPath();ctx.arc(W/2+Math.cos(a)*r,H/2+60+Math.sin(a)*r,5,0,Math.PI*2);ctx.fill();}}
ctx.fillStyle="#e8f5ff";ctx.font="bold 20px system-ui";
ctx.fillText(state.petSick?"💊 I feel sick!":state.petMess>=2?"🚽 Toilet, please!":state.petSleeping?"🌙 Zzz...":state.petHunger<25?"🍽️ I'm hungry!":state.petEnergy<25?"💤 I'm sleepy!":state.petCleanliness<25?"🧼 I need a bath!":state.petMood<25?"🎾 Play with me!":"❤️ I'm happy!",W/2,510);
ctx.textAlign="left";requestAnimationFrame(frame);return;}
if(!won&&!paused){hazardCooldown=Math.max(0,hazardCooldown-dt);
for(const h of hazards){if(hazardCooldown<=0&&invincible<=0&&shieldTime<=0&&Math.hypot(player.x-h.x,player.y-h.y)<player.r+17){
hazardCooldown=2;invincible=1.2;hit++;hitFlash=.35;state.coins=Math.max(0,state.coins-8);
state.petEnergy=clamp(state.petEnergy-3,0,100);burst(player.x,player.y,"#ff9a55",18);
msg("🔥 Hazard! Lost 8 coins and 3 pet energy.");save();updateStats();}}
if(eventTimer>0&&!eventDone){eventTimer=Math.max(0,eventTimer-dt);
if(eventTimer===0)msg("⌛ Special event expired.");updateEvent();}
if(questKind==="survive"){petMoodClock+=dt;
if(petMoodClock>=1){petMoodClock-=1;advanceQuest(1);}}
petWander-=dt;
if(petWander<=0){petWander=rand(1.5,4);petTarget={x:clamp(player.x+rand(-85,85),30,W-30),y:clamp(player.y+rand(-85,85),30,H-30)};}
const followDist=Math.hypot(player.x-pet.x,player.y-pet.y);
if(followDist>125)petTarget={x:player.x+35,y:player.y+35};
const petDx=petTarget.x-pet.x,petDy=petTarget.y-pet.y,petDist=Math.hypot(petDx,petDy);
if(petDist>3){const step=Math.min(petDist,(state.petEnergy<20?55:105)*dt);pet.x+=petDx/petDist*step;pet.y+=petDy/petDist*step;}
careTick(dt);
let dx=Number(keys.has("d")||keys.has("arrowright"))-Number(keys.has("a")||keys.has("arrowleft"));
let dy=Number(keys.has("s")||keys.has("arrowdown"))-Number(keys.has("w")||keys.has("arrowup"));
if(joystick){const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const length=Math.hypot(vx,vy);if(length>8){dx=vx/Math.max(60,length);dy=vy/Math.max(60,length);}}
const len=Math.max(1,Math.hypot(dx,dy));playerMoving=Math.hypot(dx,dy)>.1;
if(Math.abs(dx)>.1)playerFacing=dx>0?1:-1;
if(dashRequested){dashRequested=false;
if(dashCooldown<=0&&playerMoving){moveAroundObstacles(player,dx/len*115,dy/len*115);
invincible=Math.max(invincible,.35);dashCooldown=8;burst(player.x,player.y,"#9deeff",14);
msg("💨 Dash! Briefly dodge attacks.");}
else if(dashCooldown<=0)msg("Move in a direction to dash.");}
const happyBoost=(state.petStage>=5&&state.petMood>=70?1.12:1)*(boostTime>0?1.4:1);
moveAroundObstacles(player,dx/len*state.speed*happyBoost*dt,dy/len*state.speed*happyBoost*dt);
if(state.petStage>=3&&state.petEnergy>=20&&companionCollectCooldown<=0){
const reach=24+state.petSkill*12;
const nearby=targets.findIndex(c=>Math.hypot(pet.x-c.x,pet.y-c.y)<reach);
if(nearby>=0){const c=targets[nearby];burst(c.x,c.y,"#a8f7d0",12);
targets.splice(nearby,1);collected++;state.totalCoinsCollected++;state.coins+=10;eventCollect("coin");
state.petEnergy=clamp(state.petEnergy-1,0,100);companionCollectCooldown=Math.max(.65,2-state.petSkill*.4);
if(questKind==="collect")advanceQuest(1);save();updateStats();msg("🐰 Your companion found a coin!");}}
for(let i=treasures.length-1;i>=0;i--){const t=treasures[i];
if(Math.hypot(player.x-t.x,player.y-t.y)<player.r+15){
burst(t.x,t.y,"#a5f5ff",18);treasures.splice(i,1);sound("power");
if(t.kind==="gem"){eventCollect("gem");state.coins+=75;gainPetXP(12);msg("💎 Rare gem! +75 coins and +12 pet XP.");}
else if(t.kind==="magnet"){magnetTime=12;msg("🧲 Coin magnet active for 12 seconds!");}
else if(t.kind==="shield"){shieldTime=12;msg("🛡️ Shield active for 12 seconds!");}
else if(t.kind==="boost"){boostTime=10;msg("⚡ Speed boost active for 10 seconds!");}
else if(t.kind==="star"){state.starTokens++;state.coins+=100;gainPetXP(25);
msg("🌟 Star token collected! +100 coins and +25 pet XP.");}
save();updateStats();}}
if(magnetTime>0)for(const c of targets){const d=Math.hypot(player.x-c.x,player.y-c.y);
if(d>1&&d<145){const speed=Math.min(d,220*dt);c.x+=(player.x-c.x)/d*speed;c.y+=(player.y-c.y)/d*speed;}}
for(let i=targets.length-1;i>=0;i--)if(Math.hypot(player.x-targets[i].x,player.y-targets[i].y)<player.r+targets[i].r){
burst(targets[i].x,targets[i].y,"#ffe57d",10);targets.splice(i,1);collected++;state.totalCoinsCollected++;state.coins+=10;sound("coin");eventCollect("coin");
if(questKind==="collect")advanceQuest(1);save();updateStats();}
for(const e of enemies){
if(e.type==="chaser"||e.type==="guardian"||e.type==="boss"){const vx=player.x-e.x,vy=player.y-e.y,d=Math.hypot(vx,vy);
if(d>1&&d<(e.type==="boss"?360:e.type==="guardian"?290:210)){const desiredX=vx/d*e.speed,desiredY=vy/d*e.speed;
e.vx+=(desiredX-e.vx)*Math.min(1,dt*1.5);e.vy+=(desiredY-e.vy)*Math.min(1,dt*1.5);}}
e.x+=e.vx*dt;e.y+=e.vy*dt;
if(e.x<e.r||e.x>W-e.r)e.vx*=-1;
if(e.y<e.r||e.y>H-e.r)e.vy*=-1;
e.x=clamp(e.x,e.r,W-e.r);e.y=clamp(e.y,e.r,H-e.r);
if(invincible<=0&&shieldTime<=0&&Math.hypot(player.x-e.x,player.y-e.y)<player.r+e.r){
if(questKind==="survive"&&!questDone){questProgress=0;petMoodClock=0;updateQuest();}
hit++;invincible=1.2;hitFlash=.3;burst(player.x,player.y,"#ff7c96",20);
sound("hit");const penalty=e.type==="boss"?20:e.type==="guardian"?15:5;state.coins=Math.max(0,state.coins-penalty);
if(e.type==="guardian"||e.type==="boss"){state.petMood=clamp(state.petMood-5,0,100);}
msg(e.type==="boss"?"Boss hit! Lost 20 coins and 5 pet mood.":e.type==="guardian"?"Guardian hit! Lost 15 coins and 5 pet mood.":"Enemy hit! Lost 5 coins.");save();updateStats();}}
invincible=Math.max(0,invincible-dt);
if(!targets.length)finishLevel();}
for(const h of hazards){const pulse=.5+.5*Math.sin(visualTime*3+h.phase);
ctx.save();ctx.translate(h.x,h.y);ctx.fillStyle="rgba(255,100,55,"+(.17+pulse*.22)+")";
ctx.beginPath();ctx.arc(0,0,27+pulse*6,0,Math.PI*2);ctx.fill();
ctx.fillStyle="#ff7549";ctx.beginPath();ctx.moveTo(0,-19);ctx.lineTo(17,13);ctx.lineTo(-17,13);ctx.closePath();ctx.fill();
ctx.fillStyle="#ffdb7b";ctx.beginPath();ctx.arc(0,4,6,0,Math.PI*2);ctx.fill();ctx.restore();}
for(const o of obstacles)drawObstacle(o);
for(const c of targets)drawCoin(c);
for(const t of treasures)drawTreasure(t);
drawParticles();
// Companion is decorative and never collides with enemies or collectibles.
drawBunny(pet.x,pet.y,.72+state.petStage*.09,state.petMood<30?"#a9b3cf":"#ffb6d7",!paused&&Math.hypot(petTarget.x-pet.x,petTarget.y-pet.y)>3,1,state.petMood<30?"sad":"happy");
if(state.petEnergy<20){ctx.font="18px system-ui";ctx.fillText("Zzz",pet.x+16,pet.y-30);}
for(const h of hearts){ctx.save();ctx.globalAlpha=Math.min(1,h.life);ctx.font="19px system-ui";ctx.fillText("❤",h.x,h.y);ctx.restore();}
if(joystick){circle(joystick.start.x,joystick.start.y,56,"#365b77");
const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const len=Math.max(1,Math.hypot(vx,vy));circle(joystick.start.x+vx/len*Math.min(48,len),joystick.start.y+vy/len*Math.min(48,len),24,"#9acbdc");}
for(const e of enemies)drawEnemy(e);
drawBunny(player.x,player.y,.9,invincible>0?"#ffffff":"#79e0d0",!paused&&playerMoving,playerFacing);
if(shieldTime>0){ctx.strokeStyle="#a4f9dd";ctx.lineWidth=3;ctx.beginPath();ctx.arc(player.x,player.y,29+Math.sin(visualTime*5)*2,0,Math.PI*2);ctx.stroke();}
if(state.equippedCosmetic){ctx.font="23px system-ui";ctx.fillText("✦",player.x+17,player.y-13);}
ctx.textAlign="left";
ctx.fillStyle="#ffffff";ctx.font="bold 18px system-ui";ctx.fillText(world().name+"  •  Coins left: "+targets.length,16,30);
if(hitFlash>0){ctx.fillStyle="rgba(255,45,85,"+(hitFlash*.3)+")";ctx.fillRect(0,0,W,H);}
if(levelBanner>0&&!won){ctx.save();ctx.globalAlpha=Math.min(1,levelBanner,2.1-levelBanner);
ctx.fillStyle="#14263ddd";ctx.fillRect(W/2-195,H/2-53,390,106);
ctx.strokeStyle="#ffe5a2";ctx.lineWidth=2;ctx.strokeRect(W/2-195,H/2-53,390,106);
ctx.fillStyle="#ffe5a2";ctx.font="bold 30px system-ui";ctx.textAlign="center";ctx.fillText("LEVEL "+(state.level+1),W/2,H/2-7);
ctx.fillStyle="#fff";ctx.font="18px system-ui";ctx.fillText(world().name,W/2,H/2+27);ctx.restore();}
if(paused){ctx.fillStyle="#ffffff";ctx.font="bold 48px system-ui";ctx.textAlign="center";ctx.fillText("PAUSED",W/2,H/2);ctx.textAlign="left";}
if(won){ctx.fillStyle="#ffe58d";ctx.font="bold 44px system-ui";ctx.textAlign="center";
ctx.fillText("YOU WIN!",W/2,H/2);ctx.textAlign="left";}
requestAnimationFrame(frame);}
function plantGarden(seed,cost){if(state.petGarden.seed){msg("🌱 Harvest the current plant first.");return;}if(state.coins<cost){msg("🪙 Not enough coins.");return;}state.coins-=cost;state.petGarden.seed=seed;state.petGarden.plantedAt=Date.now();state.petGarden.wateredAt=0;petReaction("happy","🌱 A little seed!");save();updateStats();}
$("plantCarrot").onclick=()=>plantGarden("carrot",8);$("plantBerry").onclick=()=>plantGarden("berry",10);$("plantFlower").onclick=()=>plantGarden("flower",6);
$("waterGarden").onclick=()=>{const g=state.petGarden;if(!g.seed||g.wateredAt>=g.plantedAt)return;g.wateredAt=Date.now();state.gardeningSkill=clamp(state.gardeningSkill+2,0,100);petReaction("kind","💧 Grow, little plant!");save();updateStats();};
$("harvestGarden").onclick=()=>{const g=state.petGarden;if(!g.seed||Date.now()-g.plantedAt<60000||g.wateredAt<g.plantedAt)return;const kind=g.seed;g.harvests++;if(kind==="flower"){g.flowers++;state.petMood=clamp(state.petMood+10,0,100);gainFriendship(2);}else{state.coins+=kind==="berry"?24:18;state.petHunger=clamp(state.petHunger+8,0,100);}state.gardeningSkill=clamp(state.gardeningSkill+5,0,100);rememberPet("🌻 Harvested "+kind+" in the garden");g.seed="";g.plantedAt=0;g.wateredAt=0;petReaction("happy","🌻 Look what we grew!");save();updateStats();msg("🧺 Garden harvest: "+kind+"!");};
function wellnessAction(kind){if(state.petStage===1){msg("🥚 Wait until your pet hatches!");return;}const cost=kind==="meal"?10:kind==="snack"?12:kind==="clinic"?15:0;if(state.coins<cost){msg("🪙 Not enough coins.");return;}if(state.petSleeping&&kind!=="clinic"){msg("💤 Let your pet wake up first.");return;}state.coins-=cost;if(kind==="meal"){state.petRecipesMade++;state.petCookingSkill=clamp(state.petCookingSkill+4,0,100);state.petHunger=clamp(state.petHunger+18,0,100);state.petFullness=clamp(state.petFullness+16,0,100);state.petMood=clamp(state.petMood+5,0,100);completePetWish("feed");}else if(kind==="snack"){state.petRecipesMade++;state.petCookingSkill=clamp(state.petCookingSkill+3,0,100);state.petHunger=clamp(state.petHunger+8,0,100);state.petFullness=clamp(state.petFullness+10,0,100);state.petMood=clamp(state.petMood+12,0,100);state.petWeight=clamp(state.petWeight+2,5,100);completePetWish("feed");}else if(kind==="bath"){state.petBaths++;state.petHygieneSkill=clamp(state.petHygieneSkill+4,0,100);state.petCleanliness=clamp(state.petCleanliness+30,0,100);state.petMood=clamp(state.petMood+5,0,100);completePetWish("clean");}else if(kind==="teeth"){state.petTeethBrushed++;state.petHygieneSkill=clamp(state.petHygieneSkill+3,0,100);state.petCleanliness=clamp(state.petCleanliness+8,0,100);state.petDiscipline=clamp(state.petDiscipline+2,0,100);}else if(kind==="clinic"){state.petClinicVisits++;state.petSick=false;state.petEnergy=clamp(state.petEnergy+15,0,100);state.petMood=clamp(state.petMood+8,0,100);}gainFriendship(1);rememberPet("🏡 "+state.petName+" enjoyed "+kind+" time");petReaction("happy",kind==="bath"?"🫧 Bubble bubble!":kind==="teeth"?"😁 Sparkly teeth!":kind==="clinic"?"🩺 Feeling better!":"😋 Yummy!");sound("power");save();updateStats();msg("✨ "+state.petName+" enjoyed "+kind+" time!");}
$("cookPetMeal").onclick=()=>wellnessAction("meal");$("cookPetSnack").onclick=()=>wellnessAction("snack");$("bathePet").onclick=()=>wellnessAction("bath");$("brushPetTeeth").onclick=()=>wellnessAction("teeth");$("visitPetClinic").onclick=()=>wellnessAction("clinic");
$("savePetName").onclick=()=>{const name=$("petNameInput").value.trim().replace(/[<>]/g,"").slice(0,24);if(!name){msg("🐰 Choose a name first.");return;}state.petName=name;rememberPet("🐰 My name is "+name);save();updateStats();msg("💖 Hello, "+name+"!");};
$("savePetStyle").onclick=()=>{state.petSpecies=$("petSpeciesSelect").value;state.petColor=$("petColorSelect").value;rememberPet("🎨 Changed my style");save();updateStats();msg("🎨 Pet style saved!");};
$("petNameCall").onclick=()=>{state.petNameCalls++;state.petMood=clamp(state.petMood+1,0,100);petReaction("happy","👋 "+state.petName+" is listening!");save();updateStats();};
$("petWishHelp").onclick=()=>{const kind=state.petWish;if(!kind)return;if(kind==="feed"){state.petHunger=clamp(state.petHunger+12,0,100);state.petFullness=clamp(state.petFullness+8,0,100);}else if(kind==="play"){state.petEnergy=clamp(state.petEnergy-3,0,100);state.petMood=clamp(state.petMood+12,0,100);}else if(kind==="clean")state.petCleanliness=clamp(state.petCleanliness+15,0,100);else if(kind==="rest")state.petEnergy=clamp(state.petEnergy+12,0,100);else state.petMood=clamp(state.petMood+8,0,100);completePetWish(kind);};
$("petNameInput").value=state.petName;$("petSpeciesSelect").value=state.petSpecies;$("petColorSelect").value=state.petColor;

/* TamaCore expansion: mini-games, daily play and keepsakes (261-320) */
const extraKey=KEY+"_expansion_v2";
const extraDefault=()=>({games:{},plays:0,wins:0,streak:0,lastPlay:"",daily:{date:"",done:0,claimed:false},inventory:[],photos:[],room:"cozy",decor:"plant",friends:0,visits:0,expedition:0,storyStep:0,seasonClaim:"",lastGift:""});
let extra=extraDefault();
try{const data=JSON.parse(localStorage.getItem(extraKey)||"null");if(data&&typeof data==="object"){extra={...extra,...data};extra.games=data.games&&typeof data.games==="object"?data.games:{};extra.inventory=Array.isArray(data.inventory)?data.inventory.slice(-100):[];extra.photos=Array.isArray(data.photos)?data.photos.slice(-40):[];}}catch(_){}
const extraSave=()=>{try{localStorage.setItem(extraKey,JSON.stringify(extra));}catch(_){}};
const extraDay=()=>new Date().toLocaleDateString("en-CA");
const extraBox=document.createElement("section");extraBox.id="extraPlay";extraBox.innerHTML='<h3>🎮 Playroom & little adventures</h3><p id="extraStatus"></p><div id="extraGames"></div><p id="extraChallenge"></p><button id="extraDailyClaim">🎁 Claim daily play reward</button><p id="extraGameHistory"></p>';
$("petGarden").before(extraBox);
const extraGames=[
{id:"ball",name:"⚽ Catch the ball",desc:"Tap when the ball is close",win:()=>Math.random()<.7},
{id:"hide",name:"🙈 Hide and seek",desc:"Find your friend",win:()=>Math.random()<.65},
{id:"memory",name:"🧠 Memory match",desc:"Remember the pattern",win:()=>Math.random()<.6},
{id:"dance",name:"💃 Dance together",desc:"Follow the rhythm",win:()=>Math.random()<.75},
{id:"obstacle",name:"🏃 Little obstacle course",desc:"Hop through the course",win:()=>Math.random()<.65},
{id:"fishing",name:"🎣 Tiny fishing trip",desc:"Catch a fish",win:()=>Math.random()<.55},
{id:"treasure",name:"🗝️ Treasure hunt",desc:"Look for hidden treasures",win:()=>Math.random()<.5},
{id:"painting",name:"🎨 Paint a picture",desc:"Make a keepsake",win:()=>Math.random()<.85}
];
function extraDaily(){const day=extraDay();if(!extra.daily||extra.daily.date!==day)extra.daily={date:day,done:0,claimed:false};}
function extraRender(){extraDaily();$("extraStatus").textContent="🎲 Plays "+extra.plays+" • 🏅 Wins "+extra.wins+" • 🔥 Best streak "+extra.streak;$("extraChallenge").textContent="📅 Daily play "+Math.min(3,extra.daily.done)+"/3"+(extra.daily.claimed?" • claimed":"");$("extraDailyClaim").disabled=extra.daily.done<3||extra.daily.claimed;$("extraGameHistory").textContent=extra.inventory.length?"🎁 Recent finds: "+extra.inventory.slice(-5).join(" · "):"🎁 Play to find little keepsakes!";}

const gameArena=document.createElement("div");gameArena.id="gameArena";gameArena.style.cssText="margin:12px 0;padding:12px;border:1px solid #ffffff55;border-radius:12px;background:#12223d";$("extraGames").after(gameArena);
let activeGame=null;
function finishExtraGame(game,success){if(!activeGame||activeGame.id!==game.id)return;activeGame=null;extra.plays++;extra.games[game.id]=(extra.games[game.id]||0)+1;extraDaily();extra.daily.done=Math.min(3,extra.daily.done+1);state.petEnergy=clamp(state.petEnergy-5,0,100);state.petMood=clamp(state.petMood+(success?9:3),0,100);if(success){extra.wins++;extra.streak++;state.coins+=8;gainFriendship(2);if(extra.wins%5===0){extra.inventory.push("🎖️ Play badge "+extra.wins);rememberPet("🎖️ Won "+extra.wins+" little games");}if(game.id==="painting")extra.photos.push({at:Date.now(),caption:"A painting by "+state.petName});}else extra.streak=0;petReaction(success?"play":"kind",success?"🎉 We did it together!":"💖 Let's try again!");gameArena.textContent=success?"🎉 Great job! +8 coins":"🐰 Nice try! Play again soon.";msg(success?"🎉 "+game.name+": +8 coins!":"🐰 "+game.name+": good try!");extraSave();save();updateStats();extraRender();}
const gameIcons={ball:["⚽","🏀","🏐"],hide:["🌳","🪨","🏠"],memory:["🍎","🍓","🥕"],dance:["💃","🕺","🎵"],obstacle:["🐇","🐢","🦊"],fishing:["🐟","🐠","🦀"],treasure:["💎","🗝️","🪙"],painting:["🎨","🖌️","🖼️"]};
for(const game of extraGames){const button=document.createElement("button");button.textContent=game.name;button.title=game.desc;button.onclick=()=>{if(state.petSleeping||state.petSick||state.petStage===1){msg("🐰 Your pet needs to be awake and healthy.");return;}if(state.petEnergy<5){msg("💤 Rest before playing.");return;}if(activeGame){msg("🎮 Finish your current mini-game first.");return;}const icons=gameIcons[game.id],target=Math.floor(Math.random()*3),token={id:game.id};activeGame=token;gameArena.replaceChildren();const p=document.createElement("p");p.textContent=game.name+" • "+game.desc+" • Remember the lucky symbol: "+icons[target];gameArena.appendChild(p);const choices=document.createElement("div");choices.style.cssText="display:flex;gap:8px;flex-wrap:wrap";gameArena.appendChild(choices);const shuffled=[0,1,2].sort(()=>Math.random()-.5);for(const n of shuffled){const c=document.createElement("button");c.textContent=icons[n];c.style.fontSize="28px";c.disabled=true;c.onclick=()=>finishExtraGame(game,n===target);choices.appendChild(c);}setTimeout(()=>{if(activeGame!==token)return;p.textContent=game.name+" • Which symbol did you see?";for(const c of choices.children)c.disabled=false;},1400);};$("extraGames").appendChild(button);}
$("extraDailyClaim").onclick=()=>{extraDaily();if(extra.daily.done<3||extra.daily.claimed)return;extra.daily.claimed=true;state.coins+=25;state.petMood=clamp(state.petMood+10,0,100);rememberPet("🎁 Daily playtime completed");extraSave();save();updateStats();extraRender();msg("🎁 Daily play reward: +25 coins!");};
extraRender();


/* TamaCore expansion: rooms, friends, expeditions and keepsakes */
const townBox=document.createElement("section");townBox.id="townExpansion";townBox.innerHTML='<h3>🏡 Home, friends & the little town</h3><p id="townSummary"></p><div id="roomButtons"></div><div id="decorButtons"></div><div id="townButtons"></div><p id="townInventory"></p><p id="townPhoto"></p>';$("extraPlay").after(townBox);
const rooms=[["cozy","🛏️ Cozy bedroom",0],["kitchen","🍳 Kitchen",90],["bathroom","🛁 Bathroom",90],["playroom","🧸 Playroom",110],["garden","🌳 Garden room",130]];
const decorations=[["plant","🪴 Houseplant",0],["lamp","💡 Star lamp",35],["rug","🌈 Rainbow rug",45],["poster","🖼️ Bunny poster",60],["couch","🛋️ Soft couch",85]];
extra.roomsOwned=Array.isArray(extra.roomsOwned)?extra.roomsOwned:["cozy"];extra.decorsOwned=Array.isArray(extra.decorsOwned)?extra.decorsOwned:["plant"];
function townRender(){$("townSummary").textContent="🏡 "+extra.room+" • "+extra.decor+" • 💞 Friend visits "+extra.friends+" • 🧭 Expeditions "+extra.expedition;$("townInventory").textContent="🎒 Collection ("+extra.inventory.length+"): "+(extra.inventory.slice(-8).join(" · ")||"Empty");$("townPhoto").textContent="🖼️ Memory album: "+extra.photos.length+" moments";}
for(const [id,label,cost] of rooms){const b=document.createElement("button");b.textContent=label+(cost?" · "+cost+" coins":"");b.onclick=()=>{if(!extra.roomsOwned.includes(id)){if(state.coins<cost){msg("🪙 Save more coins to unlock this room.");return;}state.coins-=cost;extra.roomsOwned.push(id);}extra.room=id;state.petMood=clamp(state.petMood+3,0,100);extraSave();save();updateStats();townRender();msg("🏡 Welcome to the "+id+"!");};$("roomButtons").appendChild(b);}
for(const [id,label,cost] of decorations){const b=document.createElement("button");b.textContent=label+(cost?" · "+cost+" coins":"");b.onclick=()=>{if(!extra.decorsOwned.includes(id)){if(state.coins<cost){msg("🪙 Not enough coins.");return;}state.coins-=cost;extra.decorsOwned.push(id);}extra.decor=id;state.petMood=clamp(state.petMood+2,0,100);extraSave();save();updateStats();townRender();msg("🎨 New room decoration: "+id);};$("decorButtons").appendChild(b);}
const townActions=[
["☕ Visit the pet café",()=>{if(state.coins<5){msg("🪙 Café visit costs 5 coins.");return false;}state.coins-=5;state.petMood=clamp(state.petMood+12,0,100);extra.visits++;extra.inventory.push("☕ Café postcard");}],
["🌳 Meet a friend at the park",()=>{state.petEnergy=clamp(state.petEnergy-5,0,100);state.petMood=clamp(state.petMood+12,0,100);extra.friends++;gainFriendship(3);if(extra.friends%5===0)extra.inventory.push("💌 Friendship badge");}],
["🧭 Explore the forest",()=>{if(state.petEnergy<10){msg("💤 Too tired to explore.");return false;}state.petEnergy-=10;extra.expedition++;const loot=["🍄 Forest mushroom","🪶 Pretty feather","🪨 Shiny stone","🌿 Clover"];extra.inventory.push(loot[Math.floor(Math.random()*loot.length)]);state.coins+=6;}],
["🏖️ Visit the beach",()=>{if(state.petEnergy<10){msg("💤 Rest before the beach.");return false;}state.petEnergy-=10;extra.expedition++;extra.inventory.push("🐚 Seashell");state.petMood=clamp(state.petMood+10,0,100);}],
["📸 Take a memory photo",()=>{extra.photos.push({at:Date.now(),caption:state.petName+" at "+extra.room});extra.photos=extra.photos.slice(-40);state.petMood=clamp(state.petMood+3,0,100);}],
["📖 Read a little story",()=>{extra.storyStep++;state.petMood=clamp(state.petMood+7,0,100);if(extra.storyStep%5===0){extra.inventory.push("📖 Story chapter "+extra.storyStep);state.coins+=15;}}]
];
for(const [label,action] of townActions){const b=document.createElement("button");b.textContent=label;b.onclick=()=>{if(state.petSleeping||state.petSick||state.petStage===1){msg("🐰 Your pet needs to be awake and healthy.");return;}if(action()===false)return;extra.inventory=extra.inventory.slice(-100);extraSave();save();updateStats();townRender();msg("✨ "+label+" with "+state.petName+"!");};$("townButtons").appendChild(b);}townRender();


/* TamaCore expansion: progression, long-term goals and events */
const goalsBox=document.createElement("section");goalsBox.id="longTermGoals";goalsBox.innerHTML='<h3>🏆 Goals & seasonal celebrations</h3><p id="goalSummary"></p><div id="goalButtons"></div><p id="seasonInfo"></p><button id="seasonReward">🎊 Claim seasonal gift</button><p id="skillTreeInfo"></p><button id="skillTreeTrain">🌟 Train a special trick · 20 coins</button>';
$("townExpansion").after(goalsBox);
extra.goalClaims=Array.isArray(extra.goalClaims)?extra.goalClaims:[];
extra.trickLevel=Number.isFinite(extra.trickLevel)?Math.max(0,Math.min(50,extra.trickLevel)):0;
const goalList=[
["First playmate",()=>extra.plays>=1,10],["Little champion",()=>extra.wins>=10,25],["Game master",()=>extra.wins>=50,100],
["Friendly face",()=>extra.friends>=5,25],["Social butterfly",()=>extra.friends>=25,100],
["Forest explorer",()=>extra.expedition>=10,40],["Wanderer",()=>extra.expedition>=50,125],
["Room collector",()=>extra.roomsOwned.length>=3,40],["Interior designer",()=>extra.decorsOwned.length>=4,40],
["Photographer",()=>extra.photos.length>=10,35],["Storyteller",()=>extra.storyStep>=20,75],
["Careful gardener",()=>state.petGarden.harvests>=10,50],["Skilled cook",()=>state.petCookingSkill>=50,50],
["Happy companion",()=>state.friendship>=90,80],["Master of tricks",()=>extra.trickLevel>=10,100],
["Lifetime helper",()=>state.choreTotal>=100,150]
];
function goalsRender(){extraDaily();$("goalSummary").textContent="🏆 "+extra.goalClaims.length+"/"+goalList.length+" goals claimed • ⭐ Trick level "+extra.trickLevel;const month=new Date().getMonth();const seasons=["❄️ Winter","🌷 Spring","☀️ Summer","🍂 Autumn"];const season=seasons[Math.floor(month/3)%4];const key=new Date().getFullYear()+"-"+Math.floor(month/3);$("seasonInfo").textContent=season+" • "+(extra.seasonClaim===key?"Gift claimed":"Seasonal gift available");$("seasonReward").disabled=extra.seasonClaim===key;$("skillTreeInfo").textContent="🌟 Special trick level "+extra.trickLevel+" • Every level makes your pet happier.";}
for(let i=0;i<goalList.length;i++){const [name,ready,reward]=goalList[i],b=document.createElement("button");b.textContent="🏅 "+name+" · "+reward+" coins";b.onclick=()=>{if(extra.goalClaims.includes(i)||!ready())return;extra.goalClaims.push(i);state.coins+=reward;state.petMood=clamp(state.petMood+4,0,100);rememberPet("🏅 Goal completed: "+name);extraSave();save();updateStats();goalsRender();msg("🏅 "+name+"! +"+reward+" coins.");};$("goalButtons").appendChild(b);}
$("seasonReward").onclick=()=>{const key=new Date().getFullYear()+"-"+Math.floor(new Date().getMonth()/3);if(extra.seasonClaim===key)return;extra.seasonClaim=key;state.coins+=50;extra.inventory.push("🎊 Seasonal keepsake "+key);extraSave();save();updateStats();goalsRender();townRender();msg("🎊 Seasonal gift! +50 coins.");};
$("skillTreeTrain").onclick=()=>{if(extra.trickLevel>=50){msg("🌟 All tricks mastered!");return;}if(state.coins<20){msg("🪙 Need 20 coins to train.");return;}if(state.petEnergy<8||state.petSleeping){msg("💤 Your pet needs energy to learn.");return;}state.coins-=20;state.petEnergy-=8;extra.trickLevel++;state.petMood=clamp(state.petMood+Math.min(15,4+Math.floor(extra.trickLevel/5)),0,100);gainFriendship(2);if(extra.trickLevel%5===0)rememberPet("🌟 Learned trick level "+extra.trickLevel);extraSave();save();updateStats();goalsRender();msg("🌟 New trick learned!");};
goalsRender();


/* TamaCore expansion: accessibility, backup and player-friendly controls */
const settingsBox=document.createElement("section");settingsBox.id="extraSettings";settingsBox.innerHTML='<h3>⚙️ Comfort & game settings</h3><label><input type="checkbox" id="extraLargeText"> 🔎 Large text</label><label><input type="checkbox" id="extraReducedMotion"> 🌿 Reduced motion</label><label><input type="checkbox" id="extraHighContrast"> 🌗 High contrast</label><p id="extraBackupHint">💾 Back up your pet, home and extra progress together.</p><button id="extraExport">⬇️ Download complete save</button><label for="extraImport">📂 Import complete save</label><input id="extraImport" type="file" accept=".json,application/json"><p id="extraSettingsStatus" aria-live="polite"></p>';
$("longTermGoals").after(settingsBox);
extra.preferences=extra.preferences&&typeof extra.preferences==="object"?extra.preferences:{large:false,motion:false,contrast:false};
const comfortStyle=document.createElement("style");comfortStyle.id="extraComfortStyle";document.head.appendChild(comfortStyle);
function comfortApply(){comfortStyle.textContent=(extra.preferences.large?"body{font-size:19px!important}button{font-size:1.05rem!important}":"")+(extra.preferences.motion?"*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important;scroll-behavior:auto!important}":"")+(extra.preferences.contrast?"body{background:#080b15!important;color:#fff!important}button{border:2px solid #fff!important}":"");$("extraLargeText").checked=!!extra.preferences.large;$("extraReducedMotion").checked=!!extra.preferences.motion;$("extraHighContrast").checked=!!extra.preferences.contrast;$("extraSettingsStatus").textContent="💾 Settings saved on this device.";}
for(const [id,key] of [["extraLargeText","large"],["extraReducedMotion","motion"],["extraHighContrast","contrast"]])$(id).onchange=e=>{extra.preferences[key]=e.target.checked;extraSave();comfortApply();};
$("extraExport").onclick=()=>{const payload={format:"tamacore-complete-save",version:2,exportedAt:new Date().toISOString(),progress:state,expansion:extra};const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="TamaCore_complete_save.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);};
$("extraImport").onchange=async e=>{const file=e.target.files&&e.target.files[0];if(!file)return;try{if(file.size>2000000)throw Error("File is too large");const data=JSON.parse(await file.text());if(data.format!=="tamacore-complete-save"||data.version!==2||!data.progress||!data.expansion||typeof data.progress!=="object"||typeof data.expansion!=="object")throw Error("Invalid TamaCore save format");if(!confirm("Replace current progress with the imported save?"))return;localStorage.setItem(KEY,JSON.stringify(data.progress));localStorage.setItem(extraKey,JSON.stringify(data.expansion));location.reload();}catch(err){$("extraSettingsStatus").textContent="⚠️ Import failed: "+String(err.message||err);}};
comfortApply();


/* TamaCore: Pet-led living room, interactive care and collectible toys */
const living=document.createElement("section");living.id="livingExpansion";living.innerHTML='<h3>🐾 Living with your pet</h3><p id="livingMood"></p><p id="livingNarrative" aria-live="polite"></p><div id="livingActions"></div><h4>🧸 Toy collection</h4><div id="livingToys"></div><p id="livingProgress"></p>';
$("petIdentity").after(living);
extra.living=extra.living&&typeof extra.living==="object"?extra.living:{bondMoments:0,walks:0,stories:0,napTimes:0,petting:0,playedToys:0,toys:["ball"],favoriteToy:"ball",lastAction:0};
const toyCatalog=[["ball","⚽ Bouncy ball",0],["plush","🧸 Plush bear",35],["blocks","🧱 Building blocks",45],["drum","🥁 Tiny drum",55],["kite","🪁 Rainbow kite",70],["robot","🤖 Mini robot",100],["puzzle","🧩 Puzzle set",120],["train","🚂 Toy train",150]];
const livingActs=[
["🤗 Give a cuddle","cuddle",()=>{state.petMood=clamp(state.petMood+7,0,100);gainFriendship(3);extra.living.petting++;}],
["🐾 Take a little walk","walk",()=>{state.petEnergy=clamp(state.petEnergy-7,0,100);state.petMood=clamp(state.petMood+11,0,100);state.petWeight=clamp(state.petWeight-.7,5,100);extra.living.walks++;}],
["📚 Read a bedtime story","story",()=>{state.petMood=clamp(state.petMood+5,0,100);state.petEnergy=clamp(state.petEnergy+4,0,100);extra.living.stories++;}],
["🎵 Sing a silly song","sing",()=>{state.petMood=clamp(state.petMood+9,0,100);state.petDiscipline=clamp(state.petDiscipline+1,0,100);}],
["🫶 Teach a high-five","highfive",()=>{state.petMood=clamp(state.petMood+5,0,100);state.petDiscipline=clamp(state.petDiscipline+2,0,100);extra.living.bondMoments++;}],
["😴 Take a calm nap","nap",()=>{state.petEnergy=clamp(state.petEnergy+14,0,100);state.petMood=clamp(state.petMood+2,0,100);extra.living.napTimes++;}]
];
function livingRender(){const l=extra.living;$("livingMood").textContent="🐰 "+state.petName+" • Mood "+Math.round(state.petMood)+" • Energy "+Math.round(state.petEnergy)+" • Bond "+Math.round(state.friendship);$("livingProgress").textContent="💞 Cuddles "+l.petting+" • 🚶 Walks "+l.walks+" • 📚 Stories "+l.stories+" • 🧸 Toy games "+l.playedToys+" • Toys "+l.toys.length+"/"+toyCatalog.length;}
for(const [label,kind,action] of livingActs){const b=document.createElement("button");b.textContent=label;b.onclick=()=>{if(state.petSleeping||state.petSick||state.petStage===1){msg("🐰 Wake up and feel better first.");return;}if(Date.now()-extra.living.lastAction<8000){msg("⏳ Give your pet a little moment between activities.");return;}if(kind==="walk"&&state.petEnergy<8){msg("💤 Too tired for a walk.");return;}extra.living.lastAction=Date.now();action();if(kind==="cuddle")completePetWish("cuddle");if(kind==="walk"||kind==="sing")completePetWish("play");if(kind==="nap")completePetWish("rest");$("livingNarrative").textContent=["💗 "+state.petName+" wiggles happily!","🐾 What a lovely moment together!","✨ "+state.petName+" looks up at you with a smile!"][Math.floor(Math.random()*3)];petReaction("happy",$("livingNarrative").textContent);extraSave();save();updateStats();livingRender();};$("livingActions").appendChild(b);}
for(const [id,label,cost] of toyCatalog){const b=document.createElement("button");b.textContent=label+(cost?" · "+cost+" coins":"");b.onclick=()=>{const l=extra.living;if(!l.toys.includes(id)){if(state.coins<cost){msg("🪙 Not enough coins for this toy.");return;}state.coins-=cost;l.toys.push(id);extraSave();save();updateStats();msg("🧸 New toy unlocked!");return;}if(state.petSleeping||state.petSick||state.petEnergy<5){msg("💤 Your pet cannot play right now.");return;}if(Date.now()-l.lastAction<8000){msg("⏳ Wait a little before playing again.");return;}l.lastAction=Date.now();l.favoriteToy=id;l.playedToys++;state.petEnergy=clamp(state.petEnergy-5,0,100);state.petMood=clamp(state.petMood+8,0,100);gainFriendship(2);completePetWish("play");$("livingNarrative").textContent="🎉 "+state.petName+" plays with "+label+"!";petReaction("play",$("livingNarrative").textContent);extraSave();save();updateStats();livingRender();};$("livingToys").appendChild(b);}
livingRender();


/* TamaCore: Weekly rhythm and compassionate return rewards */
const rhythmBox=document.createElement("section");rhythmBox.id="rhythmExpansion";rhythmBox.innerHTML='<h3>🌞 Our little routine</h3><p id="rhythmGreeting"></p><p id="rhythmTasks"></p><div id="rhythmButtons"></div><p id="rhythmWeekly"></p><button id="rhythmClaim">🎀 Claim weekly friendship gift</button>';
$("livingExpansion").after(rhythmBox);
extra.rhythm=extra.rhythm&&typeof extra.rhythm==="object"?extra.rhythm:{day:"",fed:0,played:0,cleaned:0,rested:0,weekly:{week:"",days:[],claimed:false},lastVisit:0,welcomes:0};
function rhythmWeek(){const d=new Date();const u=new Date(d.getFullYear(),d.getMonth(),d.getDate());u.setDate(u.getDate()-(u.getDay()+6)%7);return u.getFullYear()+"-"+String(u.getMonth()+1).padStart(2,"0")+"-"+String(u.getDate()).padStart(2,"0");}
function rhythmSync(){const r=extra.rhythm,day=extraDay(),week=rhythmWeek();if(r.day!==day){r.day=day;r.fed=0;r.played=0;r.cleaned=0;r.rested=0;}if(!r.weekly||r.weekly.week!==week)r.weekly={week,days:[],claimed:false};}
function rhythmRender(){rhythmSync();const r=extra.rhythm;const hour=new Date().getHours();$("rhythmGreeting").textContent=(hour<11?"🌅 Good morning, ":hour<18?"☀️ Hello, ":"🌙 Good evening, ")+state.petName+"! We can enjoy today at our own pace.";$("rhythmTasks").textContent="🍎 Food "+Math.min(1,r.fed)+"/1 • 🧸 Play "+Math.min(1,r.played)+"/1 • 🫧 Clean "+Math.min(1,r.cleaned)+"/1 • 💤 Rest "+Math.min(1,r.rested)+"/1";$("rhythmWeekly").textContent="💖 Caring days this week: "+r.weekly.days.length+"/3 • No streaks to lose.";$("rhythmClaim").disabled=r.weekly.days.length<3||r.weekly.claimed;}
function rhythmDo(kind){rhythmSync();const r=extra.rhythm;if(state.petStage===1||state.petSleeping&&kind!=="rest"){msg("🐰 Your pet needs a little time.");return;}if(kind==="feed"){if(state.petHunger>=95){msg("🍎 Your pet is already full.");return;}state.petHunger=clamp(state.petHunger+14,0,100);state.petFullness=clamp(state.petFullness+12,0,100);r.fed=1;completePetWish("feed");}if(kind==="play"){if(state.petEnergy<8){msg("💤 Rest before playing.");return;}state.petEnergy-=8;state.petMood=clamp(state.petMood+10,0,100);r.played=1;completePetWish("play");}if(kind==="clean"){state.petCleanliness=clamp(state.petCleanliness+18,0,100);r.cleaned=1;completePetWish("clean");}if(kind==="rest"){state.petEnergy=clamp(state.petEnergy+12,0,100);r.rested=1;completePetWish("rest");}if(r.fed&&r.played&&r.cleaned&&r.rested&&!r.weekly.days.includes(r.day)){r.weekly.days.push(r.day);state.coins+=12;gainFriendship(3);rememberPet("💗 A caring day together");msg("💗 Caring day complete! +12 coins.");}else msg("💗 "+state.petName+" enjoyed "+kind+" time!");petReaction("happy","💖 Thank you for caring!");extraSave();save();updateStats();rhythmRender();}
for(const [label,kind] of [["🍎 Give a healthy bite","feed"],["🧸 Play together","play"],["🫧 Freshen up","clean"],["💤 Quiet rest","rest"]]){const b=document.createElement("button");b.textContent=label;b.onclick=()=>rhythmDo(kind);$("rhythmButtons").appendChild(b);}
$("rhythmClaim").onclick=()=>{rhythmSync();const w=extra.rhythm.weekly;if(w.days.length<3||w.claimed)return;w.claimed=true;state.coins+=60;state.petMood=clamp(state.petMood+12,0,100);extra.inventory.push("🎀 Friendship ribbon "+w.week);rememberPet("🎀 Weekly friendship gift");extraSave();save();updateStats();rhythmRender();townRender();msg("🎀 A lovely week together! +60 coins.");};
rhythmSync();if(extra.rhythm.lastVisit&&Date.now()-extra.rhythm.lastVisit>86400000){extra.rhythm.welcomes++;state.petMood=clamp(state.petMood+3,0,100);$("rhythmGreeting").textContent="💞 Welcome back! "+state.petName+" is happy to see you. No missed-day penalty.";}extra.rhythm.lastVisit=Date.now();extraSave();rhythmRender();


/* Keep the pet visible and advanced systems discoverable without a wall of buttons. */
const optionalPanels=[
["petWellness","🍳 Kitchen & wellness"],
["petGarden","🌱 Little garden"],
["extraPlay","🎮 Playroom & mini-games"],
["townExpansion","🏡 Rooms, town & friends"],
["longTermGoals","🏆 Achievements & mastery"],
["extraSettings","⚙️ Comfort & backups"],
["rhythmExpansion","🌞 Daily care routine"]
];
for(const [id,title] of optionalPanels){const panel=$(id);if(!panel)continue;const details=document.createElement("details");details.className="tamapanel";const summary=document.createElement("summary");summary.textContent=title;details.appendChild(summary);panel.before(details);details.appendChild(panel);const heading=panel.querySelector("h3");if(heading)heading.hidden=true;}
const panelStyle=document.createElement("style");panelStyle.textContent=".tamapanel{margin:8px 0;border:1px solid #ffffff45;border-radius:14px;overflow:hidden}.tamapanel>summary{cursor:pointer;padding:13px 16px;background:#203858;color:#fff4d3;font-weight:700;list-style-position:inside;touch-action:manipulation}.tamapanel[open]>summary{background:#315279}.tamapanel>section{margin:0!important;border-radius:0!important;box-shadow:none!important}";document.head.appendChild(panelStyle);

// Collectible boutique: soft currency only. No fake billing or premium entitlements.
const boutiqueKey="tamacore_boutique_v1";
function normalizeBoutique(input){
 const result={owned:{},equipped:{},claimed:{},positions:{},displayed:[],layouts:{},wishlist:[],roomTheme:"classic",roomLighting:"auto",roomRug:"none",roomPlant:"none",roomArt:"none",roomWindow:"default",roomClock:false,roomFloor:"default",roomCurtain:"none",roomLamp:"none",roomAwards:{},extraOutfits:[],favorites:[]};
 if(!input||typeof input!=="object")return result;
 for(const item of cfg.collectibles||[]){
   if(input.owned&&Object.prototype.hasOwnProperty.call(input.owned,item.id)&&input.owned[item.id]===true)result.owned[item.id]=true;
   if(result.owned[item.id]&&input.equipped&&input.equipped[item.category]===item.id)result.equipped[item.category]=item.id;
 }
 for(const category of ["furniture","toy"]){const pos=input.positions&&input.positions[category];if(pos&&Number.isFinite(pos.x))result.positions[category]={x:Math.max(130,Math.min(670,pos.x)),y:Number.isFinite(pos.y)?Math.max(355,Math.min(495,pos.y)):(category==="furniture"?420:475)};}
 if(Array.isArray(input.displayed))result.displayed=[...new Set(input.displayed)].filter(id=>result.owned[id]&&(cfg.collectibles||[]).some(item=>item.id===id&&item.category==="furniture")).slice(0,3);
 for(const id of result.displayed){const pos=input.positions&&input.positions[id];if(pos&&Number.isFinite(pos.x)&&Number.isFinite(pos.y))result.positions[id]={x:Math.max(130,Math.min(670,pos.x)),y:Math.max(355,Math.min(495,pos.y))};}
 for(const theme of ["pastel","royal","winter","garden"])if(input.claimed&&input.claimed[theme]===true)result.claimed[theme]=true;
 for(const slot of ["1","2","3"]){const layout=input.layouts&&input.layouts[slot];if(layout&&typeof layout==="object"){const clean=normalizeBoutique({owned:result.owned,equipped:layout.equipped,positions:layout.positions,displayed:layout.displayed,roomTheme:layout.roomTheme,roomLighting:layout.roomLighting,roomRug:layout.roomRug,roomPlant:layout.roomPlant,roomArt:layout.roomArt,roomWindow:layout.roomWindow,roomClock:layout.roomClock,roomFloor:layout.roomFloor,roomCurtain:layout.roomCurtain,roomLamp:layout.roomLamp,extraOutfits:layout.extraOutfits});result.layouts[slot]={equipped:clean.equipped,positions:clean.positions,displayed:clean.displayed,roomTheme:clean.roomTheme,roomLighting:clean.roomLighting,roomRug:clean.roomRug,roomPlant:clean.roomPlant,roomArt:clean.roomArt,roomWindow:clean.roomWindow,roomClock:clean.roomClock,roomFloor:clean.roomFloor,roomCurtain:clean.roomCurtain,roomLamp:clean.roomLamp,extraOutfits:clean.extraOutfits};}}
 if(Array.isArray(input.wishlist))result.wishlist=[...new Set(input.wishlist)].filter(id=>(cfg.collectibles||[]).some(item=>item.id===id)&&!result.owned[id]);
 if(["classic","cottage","loft","observatory"].includes(input.roomTheme))result.roomTheme=input.roomTheme;
 if(["auto","warm","cool"].includes(input.roomLighting))result.roomLighting=input.roomLighting;
 if(["none","round","woven","stars"].includes(input.roomRug))result.roomRug=input.roomRug;
 if(["none","fern","cactus","flowers"].includes(input.roomPlant))result.roomPlant=input.roomPlant;
 if(["none","moon","mountain","heart"].includes(input.roomArt))result.roomArt=input.roomArt;
 if(["default","round","arched"].includes(input.roomWindow))result.roomWindow=input.roomWindow;
 result.roomClock=input.roomClock===true;
 if(["default","oak","tile","marble"].includes(input.roomFloor))result.roomFloor=input.roomFloor;
 if(["none","rose","blue","cream"].includes(input.roomCurtain))result.roomCurtain=input.roomCurtain;
 if(["none","gold","mint","violet"].includes(input.roomLamp))result.roomLamp=input.roomLamp;
 for(const id of ["firstItem","decorator","collector","stylist","designer"])if(input.roomAwards&&input.roomAwards[id]===true)result.roomAwards[id]=true;
 if(Array.isArray(input.extraOutfits))result.extraOutfits=[...new Set(input.extraOutfits)].filter(id=>result.owned[id]&&(cfg.collectibles||[]).some(item=>item.id===id&&item.category==="outfit")).slice(0,2);
 if(Array.isArray(input.favorites))result.favorites=[...new Set(input.favorites)].filter(id=>result.owned[id]&&(cfg.collectibles||[]).some(item=>item.id===id));
 return result;
}
let boutiqueSave=normalizeBoutique(state.boutique);
if(!state.boutique){try{boutiqueSave=normalizeBoutique(JSON.parse(localStorage.getItem(boutiqueKey)||"{}"));}catch(_error){}}
state.boutique=boutiqueSave;
function boutiqueThemeEffect(item){
 const colors={pastel:"#efb9df",royal:"#e8ca77",winter:"#a9dfef",garden:"#a4d5a3"};
 ctx.shadowColor=colors[item.theme]||"transparent";ctx.shadowBlur=item.theme?12:0;
}
function boutiqueSelected(category){const id=boutiqueSave.equipped[category];return (cfg.collectibles||[]).find(item=>item.id===id&&item.category===category&&boutiqueSave.owned[id]===true);}
let boutiqueCategory="outfit";
const boutiqueCategories=["outfit","furniture","wallpaper","toy"];
function boutiqueCollections(){
 const all=cfg.collectibles||[];
 return ["pastel","royal","winter","garden"].map(theme=>{
   const items=all.filter(item=>item.theme===theme);
   return {theme,total:items.length,owned:items.filter(item=>boutiqueSave.owned[item.id]).length};
 });
}
function boutiqueRender(){
  const balance=document.getElementById("boutiqueBalance");
  if(!balance)return;
  balance.textContent="🪙 Available coins: "+Math.floor(state.coins);
  const tabs=document.getElementById("boutiqueTabs");tabs.replaceChildren();
  boutiqueCategories.forEach(category=>{const btn=document.createElement("button");btn.textContent=category===boutiqueCategory?"✓ "+category:category;btn.onclick=()=>{boutiqueCategory=category;boutiqueRender()};tabs.appendChild(btn)});
  const grid=document.getElementById("boutiqueItems");grid.replaceChildren();
  const query=document.getElementById("boutiqueSearch").value.trim().toLowerCase();
  const theme=document.getElementById("boutiqueTheme").value;
  const ownedOnly=document.getElementById("boutiqueOwnedOnly").checked;
  const results=(cfg.collectibles||[]).filter(item=>item.category===boutiqueCategory&&(!query||item.name.toLowerCase().includes(query))&&(!theme||(item.theme||"classic")===theme)&&(!ownedOnly||boutiqueSave.owned[item.id])&&(!document.getElementById("boutiqueWishlist").checked||boutiqueSave.wishlist.includes(item.id))&&(!document.getElementById("boutiqueFavorites").checked||boutiqueSave.favorites.includes(item.id)));
  const sort=document.getElementById("boutiqueSort").value;if(sort==="cheap")results.sort((a,b)=>a.coinPrice-b.coinPrice);if(sort==="expensive")results.sort((a,b)=>b.coinPrice-a.coinPrice);if(sort==="name")results.sort((a,b)=>a.name.localeCompare(b.name));
  document.getElementById("boutiqueCount").textContent=results.length+" items • "+(cfg.collectibles||[]).filter(item=>boutiqueSave.owned[item.id]).length+" collected";
  const allItems=cfg.collectibles||[];
  const collected=allItems.filter(item=>boutiqueSave.owned[item.id]).length;
  const progress=document.createElement("progress");progress.max=Math.max(1,allItems.length);progress.value=collected;progress.style.width="100%";progress.setAttribute("aria-label","Collection completion");
  document.getElementById("boutiqueCount").append(" / "+allItems.length+" · "+Math.floor(100*collected/Math.max(1,allItems.length))+"%",progress);
  document.getElementById("boutiqueCount").append(" · "+boutiqueSave.favorites.length+" favorites");
  const wishItems=(cfg.collectibles||[]).filter(item=>boutiqueSave.wishlist.includes(item.id)&&!boutiqueSave.owned[item.id]);
  if(wishItems.length){const total=wishItems.reduce((sum,item)=>sum+item.coinPrice,0);const summary=document.createElement("p");summary.textContent="Wishlist: "+wishItems.length+" items · "+total+" coins total";const goal=document.createElement("span");goal.dataset.goal=String(total);goal.textContent=state.coins>=total?"Affordable":Math.ceil(total-state.coins)+" more coins needed";summary.append(" · ",goal);document.getElementById("boutiqueCount").appendChild(summary);}
  const roomChoice=document.createElement("select");roomChoice.setAttribute("aria-label","Home architecture");for(const [id,name] of [["classic","Classic home"],["cottage","Wooden cottage"],["loft","City loft"],["observatory","Star observatory"]]){const option=document.createElement("option");option.value=id;option.textContent=name;roomChoice.appendChild(option);}roomChoice.value=boutiqueSave.roomTheme;roomChoice.onchange=()=>{boutiqueSave.roomTheme=roomChoice.value;save();};document.getElementById("boutiqueCount").append("Home style: ",roomChoice);
  for(const [key,label,options] of [["roomLighting","Lighting",[["auto","Automatic"],["warm","Warm"],["cool","Cool"]]],["roomRug","Rug",[["none","None"],["round","Round"],["woven","Woven"],["stars","Stars"]]],["roomPlant","Plant",[["none","None"],["fern","Fern"],["cactus","Cactus"],["flowers","Flowers"]]],["roomArt","Wall art",[["none","None"],["moon","Moon"],["mountain","Mountain"],["heart","Heart"]]]]){const select=document.createElement("select");select.setAttribute("aria-label",label);for(const [id,name] of options){const option=document.createElement("option");option.value=id;option.textContent=name;select.appendChild(option);}select.value=boutiqueSave[key];select.onchange=()=>{boutiqueSave[key]=select.value;save();};document.getElementById("boutiqueCount").append(" "+label+": ",select);}
  const windowSelect=document.createElement("select");windowSelect.setAttribute("aria-label","Window style");for(const [id,name] of [["default","Default"],["round","Round"],["arched","Arched"]]){const option=document.createElement("option");option.value=id;option.textContent=name;windowSelect.append(option);}windowSelect.value=boutiqueSave.roomWindow;windowSelect.onchange=()=>{boutiqueSave.roomWindow=windowSelect.value;save();};const clockLabel=document.createElement("label"),clock=document.createElement("input");clock.type="checkbox";clock.checked=boutiqueSave.roomClock;clock.onchange=()=>{boutiqueSave.roomClock=clock.checked;save();};clockLabel.append(clock," Wall clock");document.getElementById("boutiqueCount").append(" Window: ",windowSelect,clockLabel);
  for(const [key,label,options] of [["roomFloor","Floor",["default","oak","tile","marble"]],["roomCurtain","Curtains",["none","rose","blue","cream"]],["roomLamp","Lamp",["none","gold","mint","violet"]]]){const select=document.createElement("select");select.setAttribute("aria-label",label);for(const id of options){const opt=document.createElement("option");opt.value=id;opt.textContent=id;select.append(opt);}select.value=boutiqueSave[key];select.onchange=()=>{boutiqueSave[key]=select.value;save();};document.getElementById("boutiqueCount").append(" "+label+": ",select);}
  const stylePresets={
    cozy:{roomTheme:"cottage",roomLighting:"warm",roomRug:"woven",roomPlant:"fern",roomArt:"heart",roomWindow:"arched",roomClock:true,roomFloor:"oak",roomCurtain:"cream",roomLamp:"gold"},
    cosmic:{roomTheme:"observatory",roomLighting:"cool",roomRug:"stars",roomPlant:"none",roomArt:"moon",roomWindow:"round",roomClock:false,roomFloor:"tile",roomCurtain:"blue",roomLamp:"violet"},
    modern:{roomTheme:"loft",roomLighting:"auto",roomRug:"round",roomPlant:"cactus",roomArt:"mountain",roomWindow:"default",roomClock:true,roomFloor:"marble",roomCurtain:"none",roomLamp:"mint"},
    garden:{roomTheme:"cottage",roomLighting:"auto",roomRug:"round",roomPlant:"flowers",roomArt:"heart",roomWindow:"arched",roomClock:false,roomFloor:"oak",roomCurtain:"rose",roomLamp:"mint"}
  };
  const presetBar=document.createElement("div");presetBar.append("Quick home designs: ");
  for(const [name,preset] of Object.entries(stylePresets)){const button=document.createElement("button");button.textContent=name[0].toUpperCase()+name.slice(1);button.onclick=()=>{Object.assign(boutiqueSave,preset);save();boutiqueRender();};presetBar.append(button);}
  const resetDecor=document.createElement("button");resetDecor.textContent="Reset decor";resetDecor.onclick=()=>{const defaults=normalizeBoutique(null);for(const key of Object.keys(stylePresets.cozy))boutiqueSave[key]=defaults[key];save();boutiqueRender();};presetBar.append(resetDecor);document.getElementById("boutiqueCount").append(presetBar);
  const achievements=document.createElement("div");achievements.append("Home milestones: "+Object.keys(boutiqueSave.roomAwards).filter(id=>boutiqueSave.roomAwards[id]===true).length+"/5 completed · ");
  const milestones=[
    ["firstItem","First purchase",collected>=1,25],
    ["decorator","Three furniture items",allItems.filter(item=>item.category==="furniture"&&boutiqueSave.owned[item.id]).length>=3,75],
    ["collector","25 collectibles",collected>=25,150],
    ["stylist","10 outfits",allItems.filter(item=>item.category==="outfit"&&boutiqueSave.owned[item.id]).length>=10,100],
    ["designer","Three saved room styles",Object.keys(boutiqueSave.layouts).length===3,100]
  ];
  const remainingRewards=milestones.filter(([id])=>!boutiqueSave.roomAwards[id]).reduce((sum,entry)=>sum+entry[3],0);
  const availableRewards=milestones.filter(([id,name,ready])=>ready&&!boutiqueSave.roomAwards[id]);
  const rewardSummary=document.createElement("span");rewardSummary.textContent=remainingRewards+" coins remaining · "+availableRewards.length+" ready";achievements.append(rewardSummary);
  const claimAll=document.createElement("button");claimAll.textContent="Claim all ready rewards";claimAll.disabled=availableRewards.length===0;claimAll.onclick=()=>{let total=0;for(const [id,name,ready,coins] of availableRewards){if(ready&&!boutiqueSave.roomAwards[id]){boutiqueSave.roomAwards[id]=true;total+=coins;}}if(!total)return;state.coins+=total;save();updateStats();boutiqueRender();msg("Rewards collected! +"+total+" coins");};achievements.append(claimAll);
  for(const [id,name,ready,coins] of milestones){const button=document.createElement("button");const claimed=boutiqueSave.roomAwards[id];button.textContent=name+" · "+(claimed?"✓":coins+" coins");button.title=claimed?"Reward already collected":ready?"Claim your reward":"Complete this milestone to unlock the reward";button.setAttribute("aria-label",name+": "+button.title);button.disabled=claimed||!ready;button.onclick=()=>{if(!ready||boutiqueSave.roomAwards[id])return;boutiqueSave.roomAwards[id]=true;state.coins+=coins;save();updateStats();boutiqueRender();msg(name+" completed! +"+coins+" coins");};achievements.append(button);}
  document.getElementById("boutiqueCount").append(achievements);
  const layouts=document.createElement("div");layouts.style.cssText="display:flex;gap:5px;flex-wrap:wrap";layouts.append("Saved room styles: ");
  for(const slot of ["1","2","3"]){
    const store=document.createElement("button"),load=document.createElement("button");
    store.textContent="Save "+slot;load.textContent="Load "+slot;load.disabled=!boutiqueSave.layouts[slot];
    store.onclick=()=>{if(boutiqueSave.layouts[slot]&&!confirm("Replace saved style "+slot+"?"))return;const copy=JSON.parse(JSON.stringify({equipped:boutiqueSave.equipped,positions:boutiqueSave.positions,displayed:boutiqueSave.displayed,roomTheme:boutiqueSave.roomTheme,roomLighting:boutiqueSave.roomLighting,roomRug:boutiqueSave.roomRug,roomPlant:boutiqueSave.roomPlant,roomArt:boutiqueSave.roomArt,roomWindow:boutiqueSave.roomWindow,roomClock:boutiqueSave.roomClock,roomFloor:boutiqueSave.roomFloor,roomCurtain:boutiqueSave.roomCurtain,roomLamp:boutiqueSave.roomLamp,extraOutfits:boutiqueSave.extraOutfits}));boutiqueSave.layouts[slot]=copy;save();boutiqueRender();};
    load.onclick=()=>{const clean=normalizeBoutique({...boutiqueSave.layouts[slot],owned:boutiqueSave.owned});boutiqueSave.equipped=clean.equipped;boutiqueSave.positions=clean.positions;boutiqueSave.displayed=clean.displayed;boutiqueSave.roomTheme=clean.roomTheme;boutiqueSave.roomLighting=clean.roomLighting;boutiqueSave.roomRug=clean.roomRug;boutiqueSave.roomPlant=clean.roomPlant;boutiqueSave.roomArt=clean.roomArt;boutiqueSave.roomWindow=clean.roomWindow;boutiqueSave.roomClock=clean.roomClock;boutiqueSave.roomFloor=clean.roomFloor;boutiqueSave.roomCurtain=clean.roomCurtain;boutiqueSave.roomLamp=clean.roomLamp;boutiqueSave.extraOutfits=clean.extraOutfits;save();boutiqueRender();};
    const remove=document.createElement("button");remove.textContent="Clear "+slot;remove.disabled=!boutiqueSave.layouts[slot];remove.onclick=()=>{if(!confirm("Delete saved style "+slot+"?"))return;delete boutiqueSave.layouts[slot];save();boutiqueRender();};layouts.append(store,load,remove);
  }
  document.getElementById("boutiqueCount").appendChild(layouts);
  const collections=document.createElement("div");collections.style.cssText="display:flex;gap:8px;flex-wrap:wrap";
  for(const set of boutiqueCollections()){
    const label=document.createElement("button");label.textContent=set.theme[0].toUpperCase()+set.theme.slice(1)+" "+set.owned+"/"+set.total+(set.total&&set.owned===set.total?" ★":"");
    label.onclick=()=>{document.getElementById("boutiqueTheme").value=set.theme;document.getElementById("boutiqueSearch").value="";document.getElementById("boutiqueOwnedOnly").checked=false;boutiqueRender();};
    collections.appendChild(label);
    if(set.total>0&&set.owned===set.total){
      const reward=document.createElement("button");const claimed=boutiqueSave.claimed[set.theme]===true;
      reward.textContent=claimed?"Reward claimed":"Claim 500 coins";reward.disabled=claimed;
      reward.onclick=()=>{if(boutiqueSave.claimed[set.theme])return;const current=boutiqueCollections().find(x=>x.theme===set.theme);if(!current||!current.total||current.owned!==current.total)return;boutiqueSave.claimed[set.theme]=true;state.coins+=500;save();updateStats();boutiqueRender();msg("Collection complete! +500 coins");};
      collections.appendChild(reward);
    }
  }
  document.getElementById("boutiqueCount").appendChild(collections);
  if(!results.length){const empty=document.createElement("p");empty.textContent="No matching items. Try a different search or collection.";grid.appendChild(empty);}
  if(["furniture","toy"].includes(boutiqueCategory)&&boutiqueSelected(boutiqueCategory)){
    const category=boutiqueCategory;
    const controls=document.createElement("label");controls.textContent="Position in home";
    const range=document.createElement("input");range.type="range";range.min="130";range.max="670";range.step="10";range.value=String(boutiqueSave.positions[category]?.x??(category==="furniture"?560:260));
    const vertical=document.createElement("input");vertical.type="range";vertical.min="355";vertical.max="495";vertical.step="5";vertical.value=String(boutiqueSave.positions[category]?.y??(category==="furniture"?420:475));vertical.setAttribute("aria-label","Vertical position");range.setAttribute("aria-label","Horizontal position");
    const move=()=>{boutiqueSave.positions[category]={x:Number(range.value),y:Number(vertical.value)};save();};
    range.oninput=move;vertical.oninput=move;
    controls.append(" Horizontal ",range," Vertical ",vertical);
    const reset=document.createElement("button");reset.textContent="Reset position";reset.onclick=()=>{delete boutiqueSave.positions[category];save();boutiqueRender();};controls.appendChild(reset);grid.appendChild(controls);
  }

  results.forEach(item=>{
    const card=document.createElement("div");card.style.cssText="padding:10px;background:#223b5a;border:1px solid #5b7d9e;border-radius:12px";
    const themeColors={pastel:"#efb9df",royal:"#e8ca77",winter:"#a9dfef",garden:"#a4d5a3"};
    const art=document.createElement("div");art.textContent=item.emoji;art.style.cssText="font-size:48px;text-align:center;padding:12px;border-radius:9px;margin-bottom:8px;background:linear-gradient(145deg,"+(themeColors[item.theme]||"#8199bc")+",#233b5b);";card.appendChild(art);
    const title=document.createElement("strong");title.textContent=item.name;card.appendChild(title);
    const detail=document.createElement("p");detail.textContent=boutiqueSave.owned[item.id]?"Owned forever":"🪙 "+item.coinPrice+" coins";card.appendChild(detail);if(!boutiqueSave.owned[item.id]){const remaining=document.createElement("small");remaining.dataset.goal=String(item.coinPrice);remaining.textContent=state.coins>=item.coinPrice?"Affordable":Math.ceil(item.coinPrice-state.coins)+" more coins needed";card.appendChild(remaining);}
    const btn=document.createElement("button");const owned=Boolean(boutiqueSave.owned[item.id]);btn.textContent=owned?(boutiqueSave.equipped[item.category]===item.id?"✓ Equipped":"Equip"):"Buy with coins";
    if(!owned)btn.dataset.price=String(item.coinPrice);
    btn.disabled=!owned&&state.coins<item.coinPrice;
    btn.onclick=()=>{
      if(!boutiqueSave.owned[item.id]){
        if(state.coins<item.coinPrice)return;
        state.coins-=item.coinPrice;boutiqueSave.owned[item.id]=true; boutiqueSave.wishlist=boutiqueSave.wishlist.filter(id=>id!==item.id);
      }
      boutiqueSave.equipped[item.category]=item.id;
      state.boutique=boutiqueSave;
      save();
      if(typeof updateStats==="function")updateStats();boutiqueRender();
    };card.appendChild(btn);
    if(!owned){const wish=document.createElement("button");wish.textContent=boutiqueSave.wishlist.includes(item.id)?"♥ Saved":"♡ Wishlist";wish.onclick=()=>{if(boutiqueSave.wishlist.includes(item.id))boutiqueSave.wishlist=boutiqueSave.wishlist.filter(id=>id!==item.id);else boutiqueSave.wishlist.push(item.id);save();boutiqueRender();};card.appendChild(wish);}
    if(owned&&boutiqueSave.equipped[item.category]===item.id){
      const remove=document.createElement("button");remove.textContent="Unequip";remove.onclick=()=>{delete boutiqueSave.equipped[item.category];save();boutiqueRender();};card.appendChild(remove);
    }
    if(owned){const favorite=document.createElement("button");favorite.textContent=boutiqueSave.favorites.includes(item.id)?"★ Favorite":"☆ Favorite";favorite.onclick=()=>{if(boutiqueSave.favorites.includes(item.id))boutiqueSave.favorites=boutiqueSave.favorites.filter(id=>id!==item.id);else boutiqueSave.favorites.push(item.id);save();boutiqueRender();};card.appendChild(favorite);}
    if(owned&&item.category==="outfit"){
      const accessory=document.createElement("button");const added=boutiqueSave.extraOutfits.includes(item.id);accessory.textContent=added?"Remove accessory":"Add accessory";accessory.disabled=!added&&boutiqueSave.extraOutfits.length>=2;accessory.onclick=()=>{if(boutiqueSave.extraOutfits.includes(item.id))boutiqueSave.extraOutfits=boutiqueSave.extraOutfits.filter(id=>id!==item.id);else if(boutiqueSave.extraOutfits.length<2)boutiqueSave.extraOutfits.push(item.id);save();boutiqueRender();};card.appendChild(accessory);
    }
    if(owned&&item.category==="furniture"){
      const display=document.createElement("button");const shown=boutiqueSave.displayed.includes(item.id);
      display.textContent=shown?"Remove from display":"Add to display";display.disabled=!shown&&boutiqueSave.displayed.length>=3;
      display.onclick=()=>{if(boutiqueSave.displayed.includes(item.id))boutiqueSave.displayed=boutiqueSave.displayed.filter(id=>id!==item.id);else if(boutiqueSave.displayed.length<3)boutiqueSave.displayed.push(item.id);save();boutiqueRender();};card.appendChild(display);
      if(shown){
        const i=boutiqueSave.displayed.indexOf(item.id);
        const pos=boutiqueSave.positions[item.id]||{x:125+i*130,y:395};
        const x=document.createElement("input"),y=document.createElement("input");
        for(const [el,min,max,value,label] of [[x,130,670,pos.x,"Horizontal"],[y,355,495,pos.y,"Vertical"]]){el.type="range";el.min=String(min);el.max=String(max);el.value=String(value);el.step="5";el.setAttribute("aria-label",label+" position for "+item.name);card.append(label,el);}
        x.oninput=y.oninput=()=>{boutiqueSave.positions[item.id]={x:Number(x.value),y:Number(y.value)};save();};
      }
    }
    const preview=document.createElement("button");preview.textContent="Try preview";preview.onclick=()=>{const ids={outfit:"boutiquePreviewOutfit",furniture:"boutiquePreviewFurniture",toy:"boutiquePreviewToy"};if(ids[item.category]){const el=document.getElementById(ids[item.category]);el.textContent=item.emoji;el.style.filter=item.theme?"drop-shadow(0 0 9px "+themeColors[item.theme]+")":"none";}else{const colors={wallpaper_sky:"#8acbe9",wallpaper_forest:"#497e5d",wallpaper_space:"#302459",wallpaper_candy:"#d890bf",wallpaper_ocean:"#287c9c",wallpaper_snow:"#a8c5d8",wallpaper_sunset:"#b76b49",wallpaper_garden:"#548d63"};document.getElementById("boutiquePreviewWallpaper").style.background=colors[item.id]||"transparent";}msg("Preview only: "+item.name);};card.appendChild(preview);
    grid.appendChild(card)
  });
  const equipped=document.getElementById("boutiqueEquipped");
  equipped.textContent="Equipped: "+Object.entries(boutiqueSave.equipped).map(([cat,id])=>{const item=(cfg.collectibles||[]).find(x=>x.id===id);return cat+": "+(item?item.name:id)}).join(" · ");
  const selected=category=>{const id=boutiqueSave.equipped[category];return (cfg.collectibles||[]).find(item=>item.id===id&&boutiqueSave.owned[id])};
  const outfit=selected("outfit"),furniture=selected("furniture"),wallpaper=selected("wallpaper"),toy=selected("toy");
  document.getElementById("boutiquePreviewOutfit").textContent=outfit?outfit.emoji:"";
  document.getElementById("boutiquePreviewFurniture").textContent=furniture?furniture.emoji:"🏠";
  document.getElementById("boutiquePreviewToy").textContent=toy?toy.emoji:"";
  const palette={pastel:"#efb9df",royal:"#e8ca77",winter:"#a9dfef",garden:"#a4d5a3"};
  for(const [id,item] of [["boutiquePreviewOutfit",outfit],["boutiquePreviewFurniture",furniture],["boutiquePreviewToy",toy]]){
    const element=document.getElementById(id);element.style.filter=item&&item.theme?"drop-shadow(0 0 9px "+palette[item.theme]+")":"none";
  }
  const wall=document.getElementById("boutiquePreviewWallpaper");
  const backgrounds={wallpaper_sky:"linear-gradient(#b5e6ff,#fefefe)",wallpaper_forest:"linear-gradient(#70b992,#d5f6aa)",wallpaper_space:"linear-gradient(#252550,#784ea1)",wallpaper_candy:"linear-gradient(#ffaacc,#b6e9ff)",wallpaper_ocean:"linear-gradient(#53badb,#176a9c)",wallpaper_snow:"linear-gradient(#c8e6ff,#ffffff)",wallpaper_sunset:"linear-gradient(#ffb86a,#c56b92)",wallpaper_garden:"linear-gradient(#a9de91,#f9c1d8)"};
  wall.style.background=wallpaper?backgrounds[wallpaper.id]||"transparent":"transparent";

}
for(const id of ["boutiqueSearch","boutiqueTheme","boutiqueOwnedOnly","boutiqueWishlist","boutiqueSort","boutiqueFavorites"]){document.getElementById(id).addEventListener("input",boutiqueRender);}
setInterval(()=>{const balance=document.getElementById("boutiqueBalance");if(balance)balance.textContent="🪙 Available coins: "+Math.floor(state.coins);for(const btn of document.querySelectorAll("#boutiqueItems button[data-price]"))btn.disabled=state.coins<Number(btn.dataset.price);for(const goal of document.querySelectorAll("#boutiqueItems [data-goal],#boutiqueCount [data-goal]"))goal.textContent=state.coins>=Number(goal.dataset.goal)?"Affordable":Math.ceil(Number(goal.dataset.goal)-state.coins)+" more coins needed";},1000);
boutiqueRender();
updatePetGrowth();startLevel();renderShop();renderWardrobe();updateStats();requestAnimationFrame(frame);
</script></body></html>
'''
