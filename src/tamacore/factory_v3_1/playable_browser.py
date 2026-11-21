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
<div id="foodMenu"><h2>🐰 Tamagotchi pet care</h2><p id="careHint">Your pet needs food, play, sleep and cleaning even between adventures.</p><label for="foodChoice">Food: </label><select id="foodChoice"></select><button id="feedSelected">Feed selected food</button><div id="careActions"><button id="cleanPet">🧼 Clean (15 coins)</button><button id="playPet">🎾 Play</button><button id="restPet">💤 Rest</button><button id="sleepPet">🌙 Sleep / Wake</button><button id="healPet">💊 Medicine (25 coins)</button><button id="petPet">❤️ Pet companion</button><button id="trainPet">🎓 Train (20 coins)</button><button id="skillPet">✨ Upgrade skill (100 coins)</button></div><p id="petStatus"></p><p id="petProgress"></p><p id="petEmotion" aria-live="polite"></p><p id="questStatus"></p><p id="eventStatus" aria-live="polite"></p></div><section id="achievements"><h2>🏅 Achievements</h2><div id="achievementList"></div></section><section id="milestones"><h2>🎁 Journey rewards</h2><div id="milestoneList"></div></section><section id="challenges"><h2>🏆 Long-term challenges</h2><div id="challengeList"></div></section>
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
const state={coins:250,speed:200,level:0,owned:{},petHunger:75,petEnergy:75,petMood:75,petCleanliness:75,cosmeticsOwned:{},equippedCosmetic:"",petXP:0,petStage:1,questsCompleted:0,goldMedals:0,silverMedals:0,bronzeMedals:0,totalCoinsCollected:0,achievements:{},trainingSessions:0,petSkill:0,levelsCompleted:0,claimedMilestones:{},starTokens:0,claimedChallenges:{},bossChallengesWon:0,petSleeping:false,petSick:false,petBornAt:Date.now()};
try{const saved=JSON.parse(localStorage.getItem(KEY)||"null");if(saved&&typeof saved==="object"){
for(const k of ["coins","speed","level","petHunger","petEnergy","petMood","petCleanliness","petXP","petStage","questsCompleted","goldMedals","silverMedals","bronzeMedals","totalCoinsCollected","trainingSessions","petSkill","levelsCompleted","starTokens","bossChallengesWon"])if(Number.isFinite(saved[k]))state[k]=saved[k];
if(saved.owned&&typeof saved.owned==="object")state.owned=saved.owned;
if(saved.achievements&&typeof saved.achievements==="object")state.achievements=saved.achievements;
if(saved.claimedMilestones&&typeof saved.claimedMilestones==="object")state.claimedMilestones=saved.claimedMilestones;
if(saved.claimedChallenges&&typeof saved.claimedChallenges==="object")state.claimedChallenges=saved.claimedChallenges;
if(saved.cosmeticsOwned&&typeof saved.cosmeticsOwned==="object")state.cosmeticsOwned=saved.cosmeticsOwned;
if(typeof saved.equippedCosmetic==="string")state.equippedCosmetic=saved.equippedCosmetic;
if(typeof saved.petSleeping==="boolean")state.petSleeping=saved.petSleeping;
if(typeof saved.petSick==="boolean")state.petSick=saved.petSick;
if(Number.isFinite(saved.petBornAt)&&saved.petBornAt>0&&saved.petBornAt<=Date.now())state.petBornAt=saved.petBornAt;
}}catch(_){}
state.level=clamp(Math.floor(state.level),0,Math.max(0,cfg.levels.length-1));
let reactionUntil=0,reactionText="",reactionKind="",lastCareAlert="";
function careAlert(){let notice="";
if(state.petSick)notice="💊 Your pet is sick! Give medicine.";
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
msg(wasEgg?"🐣 Your egg hatched!":"✨ Your pet grew into "+petLifeStages[stage-1]+"!");save();updateStats();}}
function petAgeLabel(){const minutes=Math.floor(petAgeMinutes());return minutes<60?minutes+" min":Math.floor(minutes/60)+" h "+minutes%60+" min";}
const careStampKey="tamacore_last_care_v1";
try{const now=Date.now(),last=Number(localStorage.getItem(careStampKey))||now;
const elapsed=Math.min(48*60*60,Math.max(0,now-last)),ticks=Math.floor(elapsed/(20*60*1000));
if(ticks>0){state.petHunger=clamp(state.petHunger-ticks*2,0,100);
state.petEnergy=clamp(state.petEnergy+(state.petSleeping?ticks*3:-ticks),0,100);
state.petCleanliness=clamp(state.petCleanliness-ticks,0,100);
if(state.petHunger<25||state.petCleanliness<25)state.petMood=clamp(state.petMood-Math.min(ticks,30),0,100);
if(ticks>=3&&(state.petHunger<15||state.petCleanliness<15))state.petSick=true;}
localStorage.setItem(careStampKey,String(now));}catch(_){}
function careTick(dt){updatePetGrowth();careClock+=dt;if(careClock<20)return;careClock=0;
state.petHunger=clamp(state.petHunger-1,0,100);state.petEnergy=clamp(state.petEnergy+(state.petSleeping?3:-1),0,100);
state.petCleanliness=clamp(state.petCleanliness-1,0,100);
if(state.petHunger<20||state.petCleanliness<20)state.petMood=clamp(state.petMood-1,0,100);
if(state.petHunger<10||state.petCleanliness<10)state.petSick=true;
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
function updateStats(){careAlert();refreshAchievements();renderMilestones();renderChallenges();const lv=cfg.levels[state.level]||{};
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
$("petStatus").textContent=petLifeStages[Math.min(4,Math.max(0,state.petStage-1))]+(state.petSleeping?" • 🌙 Sleeping":"")+(state.petSick?" • 💊 Sick":"")+" • Hunger "+Math.round(state.petHunger)+"/100 • Energy "+Math.round(state.petEnergy)+"/100 • Mood "+Math.round(state.petMood)+"/100 • Cleanliness "+Math.round(state.petCleanliness)+"/100";
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
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;state.petEnergy=75;state.petMood=75;state.petCleanliness=75;hearts=[];petCooldown=0;dashCooldown=0;dashRequested=false;state.questsCompleted=0;state.trainingSessions=0;state.petSkill=0;state.levelsCompleted=0;state.claimedMilestones={};state.claimedChallenges={};state.bossChallengesWon=0;state.starTokens=0;trainingCooldown=0;state.goldMedals=0;state.silverMedals=0;state.bronzeMedals=0;state.totalCoinsCollected=0;state.achievements={};state.petXP=0;state.petStage=1;state.petBornAt=Date.now();hatchAnimationUntil=0;state.petSleeping=false;state.petSick=false;state.cosmeticsOwned={};state.equippedCosmetic="";won=false;paused=false;$("victory").hidden=true;$("pause").textContent="Pause";save();startLevel();renderShop();renderWardrobe();};
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
function petCompanion(){if(paused||won){msg("Resume playing to interact with your pet.");return;}
if(petCooldown>0){msg("Your pet needs a moment before more cuddles.");return;}
petCooldown=4;state.petMood=clamp(state.petMood+8,0,100);
hearts.push(...Array.from({length:6},(_,i)=>({x:pet.x+(i-2.5)*7,y:pet.y-25,vx:(i-2.5)*12,vy:-35-rand(0,25),life:1.3})));
gainPetXP(3);save();updateStats();msg("❤️ Your companion loves the attention! +3 XP.");}
$("petPet").onclick=petCompanion;
function feedPet(){const food=cfg.foods[Number($("foodChoice").value)];if(!food){msg("No food available.");return;}
if(state.coins<food.price){msg("Not enough coins to feed your pet.");return;}
state.coins-=food.price;state.petHunger=clamp(state.petHunger+(Number(food.hunger)||0),0,100);
state.petEnergy=clamp(state.petEnergy+(Number(food.energy)||0),0,100);
state.petMood=clamp(state.petMood+(Number(food.mood)||0),0,100);
gainPetXP(8);petReaction("eat","😋 Yummy!");save();updateStats();msg("Fed pet: "+food.name);}
for(const [index,food] of cfg.foods.entries()){const option=document.createElement("option");option.value=index;
option.textContent=food.name+" ("+food.price+" coins)";$("foodChoice").appendChild(option);}
$("feed").onclick=feedPet;$("feedSelected").onclick=feedPet;
$("cleanPet").onclick=()=>{if(state.coins<15){msg("Cleaning costs 15 coins.");return;}
if(state.petCleanliness>=100){msg("Your pet is already clean.");return;}
state.coins-=15;state.petCleanliness=clamp(state.petCleanliness+35,0,100);
state.petMood=clamp(state.petMood+5,0,100);petReaction("clean","🫧 So fresh!");gainPetXP(10);save();updateStats();msg("Your pet feels fresh!");};
$("playPet").onclick=()=>{if(state.petEnergy<12){msg("Your pet is too tired. Let it rest.");return;}
state.petEnergy=clamp(state.petEnergy-12,0,100);
state.petMood=clamp(state.petMood+22,0,100);
state.petHunger=clamp(state.petHunger-6,0,100);
state.petCleanliness=clamp(state.petCleanliness-5,0,100);
petReaction("play","🎾 Wheee!");gainPetXP(15);save();updateStats();msg("Your pet loved playing!");};
$("restPet").onclick=()=>{if(state.petEnergy>=100){msg("Your pet is fully rested.");return;}
state.petEnergy=clamp(state.petEnergy+30,0,100);
state.petHunger=clamp(state.petHunger-5,0,100);
petReaction("rest","💤 Nice nap!");gainPetXP(5);save();updateStats();msg("Your pet had a nice nap.");};
$("sleepPet").onclick=()=>{state.petSleeping=!state.petSleeping;petReaction("sleep",state.petSleeping?"🌙 Sweet dreams!":"☀️ Good morning!");save();updateStats();msg(state.petSleeping?"🌙 Your pet is sleeping.":"☀️ Your pet woke up!");};
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
if(homeMode)careTick(dt);
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
if(homeMode){ctx.fillStyle="#10253bbb";ctx.fillRect(65,90,670,425);
ctx.fillStyle="#ffe9b2";ctx.font="bold 34px system-ui";ctx.textAlign="center";ctx.fillText("🐰 YOUR PET HOME",W/2,142);
const reacting=performance.now()<reactionUntil;
const petMood=state.petSick||state.petMood<25?"sad":state.petSleeping||state.petEnergy<20?"sleepy":reacting&&reactionKind==="play"?"excited":state.petHunger<25?"sad":"happy";
ctx.font="bold 23px system-ui";ctx.fillStyle="#fff2bd";ctx.fillText(petLifeStages[Math.min(4,Math.max(0,state.petStage-1))]+" • Age "+petAgeLabel(),W/2,186);
if(state.petStage===1){ctx.save();ctx.translate(W/2,H/2+60);ctx.rotate(Math.sin(visualTime*3)*.045);ctx.fillStyle="#f5e8d4";ctx.beginPath();ctx.ellipse(0,0,52,69,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#f8b7d6";ctx.lineWidth=5;ctx.stroke();ctx.restore();}
else drawBunny(W/2,H/2+60+(reacting&&reactionKind==="play"?Math.sin(visualTime*16)*9:0),Math.min(3.3,1.6+state.petStage*.35),"#f7f2ec",false,1,petMood);
if(reacting){ctx.font="bold 25px system-ui";ctx.fillStyle="#fff1c4";ctx.fillText(reactionText,W/2,245);}
if(performance.now()<hatchAnimationUntil){ctx.fillStyle="#ffedb5";ctx.font="bold 29px system-ui";ctx.fillText("✨ 🐣 HATCHED! ✨",W/2,260);
for(let i=0;i<12;i++){const a=i*Math.PI/6+visualTime*.6,r=95+Math.sin(visualTime*5+i)*12;
ctx.fillStyle=i%2?"#ffe88b":"#ffb5de";ctx.beginPath();ctx.arc(W/2+Math.cos(a)*r,H/2+60+Math.sin(a)*r,5,0,Math.PI*2);ctx.fill();}}
ctx.fillStyle="#e8f5ff";ctx.font="bold 20px system-ui";
ctx.fillText(state.petSick?"💊 I feel sick!":state.petSleeping?"🌙 Zzz...":state.petHunger<25?"🍽️ I'm hungry!":state.petEnergy<25?"💤 I'm sleepy!":state.petCleanliness<25?"🧼 I need a bath!":state.petMood<25?"🎾 Play with me!":"❤️ I'm happy!",W/2,510);
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
