"""Generate a self-contained playable browser edition from a TamaCore pack.

This is a browser game, not a compiled GDevelop export.
"""
from __future__ import annotations

import json
from pathlib import Path


def write_playable_browser_game(game_dir: Path, pack: dict, levels: list, shop: dict) -> Path:
    """Write a playable HTML game next to game.json for immediate testing."""
    config = {
        "name": pack.get("name", "TamaCore"),
        "levels": levels,
        "shop": shop.get("upgrades", []),
        "foods": pack.get("foods", []),
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
</style></head><body><div id="victory" role="dialog" aria-modal="true" aria-labelledby="victoryTitle" hidden><div id="victoryCard"><div style="font-size:64px">🏆🐰🎉</div><h2 id="victoryTitle">Adventure Complete!</h2><p id="victorySummary"></p><button id="victoryClose">✨ View my achievements</button><button id="victoryRestart">🔄 Start a new adventure</button></div></div><div id="welcome" role="dialog" aria-modal="true" aria-labelledby="welcomeTitle"><div id="welcomeCard"><div style="font-size:58px">🐰✨</div><h2 id="welcomeTitle">Welcome to TamaCore!</h2><p>Collect coins, dodge enemies and explore new worlds with your bunny companion. Feed, train and evolve your pet as you play.</p><p><strong>Move:</strong> WASD, arrow keys or touch controls<br><strong>Dash:</strong> Space or 💨 button<br><strong>Pet:</strong> Tap your bunny companion</p><button id="startGame">▶ Start adventure</button></div></div><main><header><h1 id="title">TamaCore</h1><div>
<button id="soundToggle" aria-pressed="false">🔇 Sound off</button><button id="musicToggle" aria-pressed="false">🎵 Music off</button><button id="effectsToggle" aria-pressed="false">✨ Full effects</button><button id="homeToggle">🏠 Pet home</button><button id="shopToggle">Shop</button><button id="pause">Pause</button><button id="exportSave">💾 Export save</button><button id="importSave">📂 Import save</button><input id="saveFile" type="file" accept=".json,application/json" hidden><button id="reset">New game</button></div></header>
<div id="careAlert" role="status" aria-live="polite" hidden></div><div id="stats" aria-live="polite"></div><div id="quickHud" aria-label="Game status"><span id="hudLevel"></span><span id="hudCoins"></span><span id="hudPet"></span><span id="hudPower"></span></div>
<canvas id="game" width="800" height="600" aria-label="Playable game field"></canvas>
<div id="touch"><div><button data-key="ArrowLeft">◀</button><button data-key="ArrowUp">▲</button><button data-key="ArrowDown">▼</button><button data-key="ArrowRight">▶</button></div><button id="feed">Feed pet</button><button id="dash">💨 Dash</button></div>
<div id="panel"><div id="message">Collect gold coins, avoid red enemies, and finish every level.</div>
<div id="shop"><h2>Shop</h2><div id="items"></div></div>
<div id="wardrobe"><h2>Wardrobe</h2><div id="cosmetics"></div></div>
<div id="foodMenu"><h2>🐰 Tamagotchi pet care</h2><section id="roomDecor"><h3>🏠 Decorate your pet's room</h3><p id="roomStatus"></p><div id="roomButtons"></div></section><p id="careHint">Your pet needs food, play, sleep and cleaning even between adventures.</p><p id="dayNightStatus" aria-live="polite"></p><p id="foodPreference"></p><p id="fullnessStatus" aria-live="polite"></p><p id="weightStatus" aria-live="polite"></p><label for="foodChoice">Food: </label><select id="foodChoice"></select><button id="feedSelected">Feed selected food</button><div id="careActions"><button id="cleanPet">🧼 Clean (15 coins)</button><button id="toiletPet">🚽 Toilet</button><button id="disciplinePet">📣 Teach manners</button><button id="playPet">🎾 Play</button><button id="restPet">💤 Rest</button><button id="sleepPet">🌙 Sleep / Wake</button><button id="healPet">💊 Medicine (25 coins)</button><button id="petPet">❤️ Pet companion</button><button id="friendTrick">🐾 Teach a trick (30 friendship)</button><button id="friendPicnic">🧺 Friendship picnic (60 friendship)</button><button id="friendDance">💞 Best-friend dance (85 friendship)</button><button id="trainPet">🎓 Train (20 coins)</button><button id="skillPet">✨ Upgrade skill (100 coins)</button></div><div id="homeSurprise" hidden role="status" aria-live="polite"><p id="surpriseText"></p><button id="surpriseAccept">✨ Join your pet</button><button id="surpriseDismiss">Later</button></div><section id="petCelebrations"><h3>🎂 Birthdays & milestones</h3><p id="celebrationStatus"></p><button id="celebratePet" hidden>🎉 Celebrate together</button></section><section id="petDiary"><h3>📖 Pet memories</h3><div id="diaryEntries" aria-live="polite"></div></section><p id="dailyCare" aria-live="polite"></p><p id="petPersonality"></p><p id="petStatus"></p><p id="petProgress"></p><p id="petEmotion" aria-live="polite"></p><p id="questStatus"></p><p id="eventStatus" aria-live="polite"></p></div><section id="achievements"><h2>🏅 Achievements</h2><div id="achievementList"></div></section><section id="milestones"><h2>🎁 Journey rewards</h2><div id="milestoneList"></div></section><section id="challenges"><h2>🏆 Long-term challenges</h2><div id="challengeList"></div></section>
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
const now=audioCtx.currentTime;const notes=kind==="coin"?[[880,.06],[1175,.09]]:kind==="hit"?[[210,.13],[125,.16]]:kind==="win"?[[523,.12],[659,.12],[784,.16],[1047,.3]]:kind==="power"?[[440,.09],[660,.09],[880,.15]]:[[620,.08]];
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
const state={coins:250,speed:200,level:0,owned:{},petHunger:75,petWeight:50,petFullness:45,treatsToday:0,treatDate:"",petEnergy:75,petMood:75,petCleanliness:75,cosmeticsOwned:{},equippedCosmetic:"",petXP:0,petStage:1,questsCompleted:0,goldMedals:0,silverMedals:0,bronzeMedals:0,totalCoinsCollected:0,achievements:{},trainingSessions:0,petSkill:0,levelsCompleted:0,claimedMilestones:{},starTokens:0,claimedChallenges:{},bossChallengesWon:0,petSleeping:false,sleepStartedAt:0,dreamKind:"",lastMorningDate:"",petSick:false,petBornAt:Date.now(),petDiscipline:50,petMess:0,careQuality:65,friendship:20,favoriteFood:0,dislikedFood:1,petMemories:[],celebrationsClaimed:{},petTrait:"",petPersonality:"",roomOwned:{},roomEquipped:{wall:"default",floor:"default",furniture:"none",toy:"none"},homeSurprise:{kind:"",expires:0,nextAt:Date.now()+90000},dailyCare:{date:"",feed:0,play:0,clean:0,rest:0,claimed:false}};
try{const saved=JSON.parse(localStorage.getItem(KEY)||"null");if(saved&&typeof saved==="object"){
for(const k of ["coins","speed","level","petHunger","petWeight","petFullness","petEnergy","petMood","petCleanliness","petXP","petStage","questsCompleted","goldMedals","silverMedals","bronzeMedals","totalCoinsCollected","trainingSessions","petSkill","levelsCompleted","starTokens","bossChallengesWon"])if(Number.isFinite(saved[k]))state[k]=saved[k];
if(saved.owned&&typeof saved.owned==="object")state.owned=saved.owned;
if(saved.achievements&&typeof saved.achievements==="object")state.achievements=saved.achievements;
if(saved.claimedMilestones&&typeof saved.claimedMilestones==="object")state.claimedMilestones=saved.claimedMilestones;
if(saved.claimedChallenges&&typeof saved.claimedChallenges==="object")state.claimedChallenges=saved.claimedChallenges;
if(saved.cosmeticsOwned&&typeof saved.cosmeticsOwned==="object")state.cosmeticsOwned=saved.cosmeticsOwned;
if(typeof saved.equippedCosmetic==="string")state.equippedCosmetic=saved.equippedCosmetic;
if(typeof saved.petSleeping==="boolean")state.petSleeping=saved.petSleeping;
if(typeof saved.petSick==="boolean")state.petSick=saved.petSick;
if(Number.isFinite(saved.petDiscipline))state.petDiscipline=clamp(saved.petDiscipline,0,100);
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
let reactionUntil=0,reactionText="",reactionKind="",lastCareAlert="",feedingVisual={until:0,emoji:"",liked:false,disliked:false};
if(!state.petPersonality)state.petPersonality=["playful","gentle","curious"][Math.floor(state.petBornAt/1000)%3];
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
function careTick(dt){updatePetGrowth();morningTick();surpriseTick();careClock+=dt;if(careClock<20)return;careClock=0;
state.petHunger=clamp(state.petHunger-1,0,100);state.petFullness=clamp(state.petFullness-2,0,100);
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
function updateStats(){const weightMood=state.petWeight>=85?"🎈 Super round!":state.petWeight>=65?"🍩 Chubby cheeks!":state.petWeight<=20?"🪶 Very skinny!":state.petWeight<=35?"🍃 A little thin":"🐰 Just right";$("weightStatus").textContent="⚖️ Pet shape "+Math.round(state.petWeight)+"/100 • "+weightMood;const today=new Date().toLocaleDateString("en-CA");if(state.treatDate!==today){state.treatDate=today;state.treatsToday=0;}$("fullnessStatus").textContent="🍽️ Fullness "+Math.round(state.petFullness)+"/100 • 🍓 Treats "+state.treatsToday+"/3 today"+(state.petFullness>=90?" • Full!":"");updateFoodPreference();renderCelebration();renderPetDiary();updateDayNight();renderRoomShop();$("friendTrick").disabled=state.friendship<30;$("friendPicnic").disabled=state.friendship<60;$("friendDance").disabled=state.friendship<85;dailyProgress();const d=state.dailyCare;
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
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;state.petEnergy=75;state.petMood=75;state.petCleanliness=75;hearts=[];petCooldown=0;dashCooldown=0;dashRequested=false;state.questsCompleted=0;state.trainingSessions=0;state.petSkill=0;state.levelsCompleted=0;state.claimedMilestones={};state.claimedChallenges={};state.bossChallengesWon=0;state.starTokens=0;trainingCooldown=0;state.goldMedals=0;state.silverMedals=0;state.bronzeMedals=0;state.totalCoinsCollected=0;state.achievements={};state.petXP=0;state.petStage=1;state.petBornAt=Date.now();state.petPersonality=["playful","gentle","curious"][Math.floor(Math.random()*3)];state.dailyCare={date:"",feed:0,play:0,clean:0,rest:0,claimed:false};hatchAnimationUntil=0;state.petSleeping=false;state.sleepStartedAt=0;state.dreamKind="";state.lastMorningDate="";state.petSick=false;state.petMess=0;state.petDiscipline=50;state.roomOwned={};state.roomEquipped={wall:"default",floor:"default",furniture:"none",toy:"none"};state.homeSurprise={kind:"",expires:0,nextAt:Date.now()+90000};state.careQuality=65;state.petWeight=50;state.petFullness=45;state.treatsToday=0;state.treatDate="";state.friendship=20;state.favoriteFood=Math.floor(Math.random()*(cfg.foods.length+3));state.dislikedFood=(state.favoriteFood+1+Math.floor(Math.random()*(cfg.foods.length+2)))%(cfg.foods.length+3);state.petMemories=[];state.celebrationsClaimed={};state.petTrait="";state.cosmeticsOwned={};state.equippedCosmetic="";won=false;paused=false;$("victory").hidden=true;$("pause").textContent="Pause";save();startLevel();renderShop();renderWardrobe();};
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
if(Math.abs(x-W/2)<110&&Math.abs(y-(H/2+60))<135)petCompanion();});
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
gainFriendship(liked?4:disliked?1:2);gainPetXP(state.petPersonality==="curious"?11:8);recordCare("feed");petReaction(overfed?"belly":"eat",overfed?"🎈 Burp! My tummy is a balloon!":liked?"😍 My favorite!":disliked?"😕 Not my favorite...":"😋 Yummy!");save();updateStats();msg("Fed pet: "+food.name+(liked?" • Favorite food bonus!":disliked?" • Your pet wasn't thrilled.":""));}
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
gainFriendship(5);petReaction("play","🎾 Wheee!");recordCare("play");gainPetXP((state.petPersonality==="playful"?20:15)+(state.roomEquipped.toy==="blocks"?5:0));save();updateStats();msg("Your pet loved playing!");};
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
ctx.beginPath();ctx.ellipse(-9,-23,7,20,-.15,0,Math.PI*2);ctx.ellipse(9,-23,7,20,.15,0,Math.PI*2);ctx.fill();
ctx.fillStyle="#f4a7bb";ctx.beginPath();ctx.ellipse(-9,-24,3,13,-.15,0,Math.PI*2);ctx.ellipse(9,-24,3,13,.15,0,Math.PI*2);ctx.fill();ctx.restore();
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
ctx.restore();}
function frame(t){const dt=Math.min(.05,(t-(frame.last||t))/1000);frame.last=t;
if(document.hidden){requestAnimationFrame(frame);return;}
musicTick(dt);
if(homeMode){visualTime+=dt;petCooldown=Math.max(0,petCooldown-dt);careTick(dt);}
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
ctx.fillStyle=wallColors[state.roomEquipped.wall]||wallColors.default;ctx.fillRect(65,90,670,325);
ctx.fillStyle=floorColors[state.roomEquipped.floor]||floorColors.default;ctx.fillRect(65,415,670,100);
ctx.fillStyle=phase==="night"?"#07152b99":phase==="evening"?"#b95c4050":"#fff3bd15";ctx.fillRect(65,90,670,425);
ctx.save();ctx.textAlign="center";ctx.font="40px system-ui";ctx.fillText(phase==="night"?"🌙":phase==="evening"?"🌇":"☀️",690,155);ctx.restore();
ctx.strokeStyle="#ffffff55";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(65,415);ctx.lineTo(735,415);ctx.stroke();
if(state.roomEquipped.furniture==="plant"){ctx.font="75px system-ui";ctx.textAlign="center";ctx.fillText("🪴",640,430);}
if(state.roomEquipped.furniture==="bed"){ctx.font="85px system-ui";ctx.textAlign="center";ctx.fillText("🛏️",610,455);}
if(state.roomEquipped.toy!=="none"){ctx.font="54px system-ui";ctx.textAlign="center";ctx.fillText(state.roomEquipped.toy==="ball"?"⚽":"🧩",190,460);}
ctx.fillStyle="#ffe9b2";ctx.font="bold 34px system-ui";ctx.textAlign="center";ctx.fillText("🐰 YOUR PET HOME",W/2,142);
ctx.font="bold 16px system-ui";ctx.fillText(phase==="night"?"Nighttime":phase==="evening"?"Evening":"Daytime",W/2,164);
const reacting=performance.now()<reactionUntil;
const idle=state.petSleeping?"sleep":state.petSick?"sick":state.petTrait==="mischievous"?"zigzag":state.petTrait==="brave"?"bounce":state.petTrait==="kind"?"sway":state.petPersonality==="playful"?"bounce":state.petPersonality==="curious"?"look":"sway";
const petMood=state.petSick||state.petMood<25?"sad":state.petSleeping||state.petEnergy<20?"sleepy":reacting&&reactionKind==="eat"?(feedingVisual.disliked?"sad":"excited"):reacting&&reactionKind==="play"?"excited":state.petHunger<25?"sad":"happy";
ctx.font="bold 23px system-ui";ctx.fillStyle="#fff2bd";ctx.fillText(petLifeStages[Math.min(4,Math.max(0,state.petStage-1))]+" • Age "+petAgeLabel(),W/2,186);
if(state.petStage===1){ctx.save();ctx.translate(W/2,H/2+60);ctx.rotate(Math.sin(visualTime*3)*.045);ctx.fillStyle="#f5e8d4";ctx.beginPath();ctx.ellipse(0,0,52,69,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#f8b7d6";ctx.lineWidth=5;ctx.stroke();ctx.restore();}
else {ctx.save();const widthFactor=state.petWeight>=50?1+(state.petWeight-50)/85:Math.max(.62,1-(50-state.petWeight)/115);ctx.translate(W/2,H/2+60);ctx.scale(widthFactor,1);ctx.translate(-W/2,-(H/2+60));drawBunny(W/2+(idle==="look"?Math.sin(visualTime*.9)*15:idle==="zigzag"?Math.sin(visualTime*2.8)*28:0),H/2+60+(reacting&&reactionKind==="play"?Math.sin(visualTime*16)*9:idle==="bounce"?Math.abs(Math.sin(visualTime*2.5))*7:idle==="zigzag"?Math.abs(Math.sin(visualTime*4))*4:0),Math.min(3.3,1.6+state.petStage*.35),"#f7f2ec",false,idle==="look"&&Math.sin(visualTime*.9)<-.7?-1:1,petMood);ctx.restore();}
if(performance.now()<feedingVisual.until&&!state.petSleeping){const remaining=(feedingVisual.until-performance.now())/3000;ctx.save();ctx.textAlign="center";ctx.font="38px system-ui";ctx.fillText(feedingVisual.emoji,W/2-95+Math.sin(visualTime*5)*8,H/2+65-Math.sin(visualTime*9)*4);ctx.font="27px system-ui";ctx.fillText(feedingVisual.liked?"💖":feedingVisual.disliked?"💧":"✨",W/2+85,H/2-65-Math.sin(visualTime*4)*10);ctx.globalAlpha=Math.min(1,Math.max(0,remaining));ctx.font="20px system-ui";ctx.fillText("•  •  •",W/2,H/2+128);ctx.restore();}
if(state.petSleeping&&state.petStage>1){ctx.save();ctx.globalAlpha=.7+.3*Math.sin(visualTime*1.5)**2;ctx.textAlign="center";ctx.font="bold 26px system-ui";ctx.fillStyle="#dbe9ff";ctx.fillText("Z",W/2+92,H/2-70-Math.sin(visualTime*1.2)*10);ctx.font="bold 18px system-ui";ctx.fillText("z",W/2+120,H/2-100-Math.sin(visualTime*1.2)*15);
ctx.font="23px system-ui";ctx.fillText(state.dreamKind==="nightmare"?"☁️":state.dreamKind==="adventure"?"🚀":"💗",W/2+135,H/2-145-Math.sin(visualTime*.8)*8);ctx.restore();}
if(state.friendship>=85&&!state.petSleeping&&state.petStage>1){ctx.save();ctx.fillStyle="#ff9ecb";ctx.font="bold 19px system-ui";ctx.fillText("♥",W/2-85,H/2-80+Math.sin(visualTime*2)*7);ctx.restore();}
if(state.petTrait==="kind"&&!state.petSleeping){ctx.fillStyle="#ffb9d7";ctx.font="bold 20px system-ui";ctx.fillText("♥",W/2+85,H/2-20+Math.sin(visualTime*2)*8);}
if(state.petTrait==="brave"&&!state.petSleeping){ctx.fillStyle="#ffe08a";ctx.font="bold 22px system-ui";ctx.fillText("★",W/2-92,H/2-10+Math.sin(visualTime*2)*5);}
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
updatePetGrowth();startLevel();renderShop();renderWardrobe();updateStats();requestAnimationFrame(frame);
</script></body></html>
'''
