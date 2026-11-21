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
#touch button{min-width:64px;min-height:50px}small{color:#b8c9dc}#stats{background:#ffffff0b;border:1px solid #ffffff20;border-radius:12px;padding:10px 12px;font-weight:650;line-height:1.5}#foodMenu,#wardrobe{margin-top:16px;padding:14px;background:#ffffff09;border:1px solid #ffffff1c;border-radius:14px}#foodMenu h2,#wardrobe h2,#shop h2{font-size:19px;margin:0 0 12px;color:#ffe5aa}#foodChoice{background:#233c5f;color:#fff;border:1px solid #7f9dbb;border-radius:10px;padding:10px;max-width:100%;margin:0 8px 8px 0}#petStatus{line-height:1.7}#message{font-weight:650}#game{box-shadow:0 12px 32px #0005}#touch{gap:10px;flex-wrap:wrap}#careActions{display:flex;gap:6px;flex-wrap:wrap}#careActions button{flex:1 1 130px}@media(max-width:600px){#touch button{min-width:52px;padding:10px}#touch>div{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;flex:1}#touch>button{flex:1}header>div{display:flex;gap:5px;flex-wrap:wrap}header button{padding:9px}#panel{padding:12px}}
</style></head><body><main><header><h1 id="title">TamaCore</h1><div>
<button id="shopToggle">Shop</button><button id="pause">Pause</button><button id="reset">New game</button></div></header>
<div id="stats" aria-live="polite"></div>
<canvas id="game" width="800" height="600" aria-label="Playable game field"></canvas>
<div id="touch"><div><button data-key="ArrowLeft">◀</button><button data-key="ArrowUp">▲</button><button data-key="ArrowDown">▼</button><button data-key="ArrowRight">▶</button></div><button id="feed">Feed pet</button></div>
<div id="panel"><div id="message">Collect gold coins, avoid red enemies, and finish every level.</div>
<div id="shop"><h2>Shop</h2><div id="items"></div></div>
<div id="wardrobe"><h2>Wardrobe</h2><div id="cosmetics"></div></div>
<div id="foodMenu"><h2>Pet care</h2><label for="foodChoice">Food: </label><select id="foodChoice"></select><button id="feedSelected">Feed selected food</button><div id="careActions"><button id="cleanPet">🧼 Clean (15 coins)</button><button id="playPet">🎾 Play</button><button id="restPet">💤 Rest</button><button id="petPet">❤️ Pet companion</button></div><p id="petStatus"></p><p id="petProgress"></p><p id="petEmotion" aria-live="polite"></p><p id="questStatus"></p></div>
<small>Move: WASD / arrow keys or touch buttons. Collect yellow coins. Avoid red enemies. Progress saves automatically in this browser.</small></div>
</main><script id="config" type="application/json">__GAME_CONFIG__</script><script>
"use strict";
const cfg=JSON.parse(document.getElementById("config").textContent);
const canvas=document.getElementById("game"),ctx=canvas.getContext("2d");
const W=canvas.width,H=canvas.height,KEY="tamacore_browser_save_v1";
const $=id=>document.getElementById(id);
$("title").textContent=cfg.name;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const rand=(a,b)=>a+Math.random()*(b-a);
const state={coins:250,speed:200,level:0,owned:{},petHunger:75,petEnergy:75,petMood:75,petCleanliness:75,cosmeticsOwned:{},equippedCosmetic:"",petXP:0,petStage:1,questsCompleted:0};
try{const saved=JSON.parse(localStorage.getItem(KEY)||"null");if(saved&&typeof saved==="object"){
for(const k of ["coins","speed","level","petHunger","petEnergy","petMood","petCleanliness","petXP","petStage","questsCompleted"])if(Number.isFinite(saved[k]))state[k]=saved[k];
if(saved.owned&&typeof saved.owned==="object")state.owned=saved.owned;
if(saved.cosmeticsOwned&&typeof saved.cosmeticsOwned==="object")state.cosmeticsOwned=saved.cosmeticsOwned;
if(typeof saved.equippedCosmetic==="string")state.equippedCosmetic=saved.equippedCosmetic;
}}catch(_){}
state.level=clamp(Math.floor(state.level),0,Math.max(0,cfg.levels.length-1));
let player={x:W/2,y:H/2,r:17},targets=[],enemies=[],obstacles=[],collected=0,hit=0,invincible=0,won=false;
let questProgress=0,questTarget=5,questKind="collect";
let scenery=[],visualTime=0,playerMoving=false,playerFacing=1,hearts=[],petCooldown=0,particles=[],levelBanner=0,hitFlash=0,treasures=[],magnetTime=0,shieldTime=0;
let joystick=null,paused=false,careClock=0,pet={x:W/2+65,y:H/2+35},petMoodClock=0,petWander=0,petTarget={x:W/2+65,y:H/2+35};
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
function burst(x,y,color,count=12){for(let i=0;i<count;i++){const angle=i*Math.PI*2/count+rand(-.15,.15),speed=rand(45,145);
particles.push({x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-25,life:rand(.35,.85),maxLife:.85,r:rand(2,5),color});}
if(particles.length>220)particles.splice(0,particles.length-220);}
function drawParticles(){for(const p of particles){ctx.save();ctx.globalAlpha=clamp(p.life/p.maxLife,0,1);
circle(p.x,p.y,p.r*p.life/p.maxLife,p.color);ctx.restore();}}
function startLevel(){const lv=cfg.levels[state.level];if(!lv){won=true;msg("Game complete!");return;}
player.x=W/2;player.y=H/2;levelBanner=2.1;generateScenery();beginQuest();pet.x=player.x+65;pet.y=player.y+35;petTarget={x:pet.x,y:pet.y};collected=0;hit=0;invincible=0;
obstacles=[];
for(let i=0;i<Math.min(14,3+state.level);i++){
const p=point(rand(20,32));if(Math.hypot(p.x-W/2,p.y-H/2)>115&&!blocked(p.x,p.y,p.r))obstacles.push(p);}
targets=Array.from({length:Math.min(150,Math.max(0,lv.coinCount||0))},()=>safePoint(10));
treasures=Array.from({length:Math.min(5,1+Math.floor(state.level/3))},(_,i)=>({...safePoint(14),kind:["gem","magnet","shield"][((state.level+i)%3)]}));
magnetTime=0;shieldTime=0;
enemies=Array.from({length:Math.min(50,Math.max(0,lv.enemyCount||0))},(_,i)=>{
const type=(state.level>=4&&i%5===0)?"chaser":(state.level>=2&&i%3===0)?"sprinter":"wanderer";
const speed=type==="sprinter"?rand(115,155):rand(45,90);
const angle=rand(0,Math.PI*2);return {...safePoint(16),vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,type,speed};});
msg(world().name+" • Level "+(state.level+1)+": collect "+targets.length+" coins and avoid enemies.");
updateStats();}
function beginQuest(){questKind=state.level%2===0?"collect":"survive";questProgress=0;
questTarget=questKind==="collect"?Math.min(8,3+state.level):15+state.level*3;
updateQuest();}
function updateQuest(){$("questStatus").textContent="🎯 Quest: "+(questKind==="collect"?"Collect coins":"Survive")+" "+Math.min(questProgress,questTarget)+"/"+questTarget+(questKind==="survive"?" sec":"");}
function advanceQuest(amount){if(questProgress>=questTarget)return;
questProgress=Math.min(questTarget,questProgress+amount);updateQuest();
if(questProgress>=questTarget){const bonus=30+state.level*10;state.coins+=bonus;state.questsCompleted++;
gainPetXP(20);save();updateStats();msg("🎉 Quest complete! +"+bonus+" coins and +20 pet XP.");}}
function petEmotion(){if(state.petHunger<20)return "🍽️ Hungry";
if(state.petEnergy<20)return "💤 Sleepy";
if(state.petCleanliness<20)return "🛁 Needs a bath";
if(state.petMood<30)return "😢 Sad";
if(state.petMood>80)return "🥰 Happy";return "🙂 Content";}
function updateStats(){const lv=cfg.levels[state.level]||{};
$("stats").textContent="Level "+(state.level+1)+"/"+cfg.levels.length+"  •  Coins: "+state.coins+
"  •  Collected: "+collected+"/"+Math.min(150,lv.coinCount||0)+"  •  Speed: "+state.speed+
"  •  Pet hunger: "+Math.round(state.petHunger)+"  •  Pet stage: "+state.petStage;
$("petStatus").textContent="Hunger "+Math.round(state.petHunger)+"/100 • Energy "+Math.round(state.petEnergy)+"/100 • Mood "+Math.round(state.petMood)+"/100 • Cleanliness "+Math.round(state.petCleanliness)+"/100";
$("petProgress").textContent="Pet evolution: stage "+state.petStage+" • XP "+state.petXP+"/"+(state.petStage*100);
$("petEmotion").textContent="Pet mood: "+petEmotion()+" • Quests completed: "+state.questsCompleted;}
function gainPetXP(amount){state.petXP+=amount;let evolved=false;
while(state.petStage<5&&state.petXP>=state.petStage*100){state.petXP-=state.petStage*100;state.petStage++;evolved=true;}
if(evolved)msg("✨ Your pet evolved to stage "+state.petStage+"!");save();updateStats();}
function finishLevel(){burst(player.x,player.y,"#ffe88b",35);const reward=50+state.level*25;gainPetXP(35);state.coins+=reward;
if(state.level+1>=cfg.levels.length){won=true;msg("🏆 All levels completed! Final reward: "+reward+" coins.");updateStats();}
else{state.level++;save();startLevel();msg("Level complete! Bonus: "+reward+" coins. Next: level "+(state.level+1));}save();}
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
$("pause").onclick=()=>{paused=!paused;$("pause").textContent=paused?"Resume":"Pause";msg(paused?"Game paused.":"Game resumed.");};
$("reset").onclick=()=>{if(!confirm("Erase saved progress and restart?"))return;
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;state.petEnergy=75;state.petMood=75;state.petCleanliness=75;hearts=[];petCooldown=0;state.questsCompleted=0;state.petXP=0;state.petStage=1;state.cosmeticsOwned={};state.equippedCosmetic="";won=false;paused=false;$("pause").textContent="Pause";save();startLevel();renderShop();renderWardrobe();};
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
gainPetXP(8);save();updateStats();msg("Fed pet: "+food.name);}
for(const [index,food] of cfg.foods.entries()){const option=document.createElement("option");option.value=index;
option.textContent=food.name+" ("+food.price+" coins)";$("foodChoice").appendChild(option);}
$("feed").onclick=feedPet;$("feedSelected").onclick=feedPet;
$("cleanPet").onclick=()=>{if(state.coins<15){msg("Cleaning costs 15 coins.");return;}
if(state.petCleanliness>=100){msg("Your pet is already clean.");return;}
state.coins-=15;state.petCleanliness=clamp(state.petCleanliness+35,0,100);
state.petMood=clamp(state.petMood+5,0,100);gainPetXP(10);save();updateStats();msg("Your pet feels fresh!");};
$("playPet").onclick=()=>{if(state.petEnergy<12){msg("Your pet is too tired. Let it rest.");return;}
state.petEnergy=clamp(state.petEnergy-12,0,100);
state.petMood=clamp(state.petMood+22,0,100);
state.petHunger=clamp(state.petHunger-6,0,100);
state.petCleanliness=clamp(state.petCleanliness-5,0,100);
gainPetXP(15);save();updateStats();msg("Your pet loved playing!");};
$("restPet").onclick=()=>{if(state.petEnergy>=100){msg("Your pet is fully rested.");return;}
state.petEnergy=clamp(state.petEnergy+30,0,100);
state.petHunger=clamp(state.petHunger-5,0,100);
gainPetXP(5);save();updateStats();msg("Your pet had a nice nap.");};
addEventListener("keydown",e=>{if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"," "].includes(e.key))e.preventDefault();keys.add(e.key.toLowerCase());});
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
const color=t.kind==="gem"?"#7de7ff":t.kind==="magnet"?"#f6c46a":"#9ef7b8";
ctx.fillStyle=color;ctx.strokeStyle="#ffffff";ctx.lineWidth=2;
ctx.beginPath();ctx.moveTo(0,-13);ctx.lineTo(12,-3);ctx.lineTo(8,10);ctx.lineTo(-8,10);ctx.lineTo(-12,-3);ctx.closePath();ctx.fill();ctx.stroke();
ctx.fillStyle="#24354d";ctx.font="bold 16px system-ui";ctx.textAlign="center";ctx.fillText(t.kind==="gem"?"★":t.kind==="magnet"?"M":"✚",0,5);ctx.restore();}
function drawCoin(c){const pulse=1+Math.sin(visualTime*5+c.x*.07)*.1;
const r=c.r*pulse;circle(c.x,c.y,r+6,"#ffd55b33");
const shine=ctx.createRadialGradient(c.x-r*.35,c.y-r*.4,1,c.x,c.y,r);
shine.addColorStop(0,"#fff9bf");shine.addColorStop(.5,"#ffd85c");shine.addColorStop(1,"#d78b28");circle(c.x,c.y,r,shine);
ctx.strokeStyle="#fff0a5";ctx.lineWidth=1.7;ctx.beginPath();ctx.arc(c.x,c.y,r*.7,0,Math.PI*2);ctx.stroke();
ctx.fillStyle="#a86c24";ctx.font="bold "+Math.round(r*1.25)+"px system-ui";ctx.textAlign="center";ctx.fillText("★",c.x,c.y+r*.44);ctx.textAlign="left";}
function drawEnemy(e){ctx.save();ctx.translate(e.x,e.y+Math.sin(visualTime*6+e.x*.02)*2);
circle(2,4,e.r+3,"#511d3d88");const g=ctx.createRadialGradient(-5,-7,1,0,0,e.r+2);
const palette=e.type==="chaser"?["#ffde95","#ef9a3b","#a75226"]:e.type==="sprinter"?["#d7b8ff","#9868df","#633f9b"]:["#ffb0b3","#f45e83","#ac365c"];
g.addColorStop(0,palette[0]);g.addColorStop(.55,palette[1]);g.addColorStop(1,palette[2]);circle(0,0,e.r,g);
for(const side of [-1,1]){ctx.fillStyle="#a83b65";ctx.beginPath();ctx.moveTo(side*e.r*.55,-e.r*.6);ctx.lineTo(side*e.r*.8,-e.r*1.22);ctx.lineTo(side*e.r*.08,-e.r*.87);ctx.closePath();ctx.fill();}
circle(-5,-3,4,"#fff");circle(6,-3,4,"#fff");circle(-4,-3,2,"#28203a");circle(7,-3,2,"#28203a");
ctx.strokeStyle="#802744";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-4,7);ctx.lineTo(4,7);ctx.stroke();ctx.restore();}
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
const blink=Math.sin(visualTime*1.8+x*.03)>.995;
ctx.fillStyle="#243040";if(blink){ctx.fillRect(-11,-3,7,2);ctx.fillRect(5,-3,7,2);}else{
ctx.beginPath();ctx.ellipse(-8,-3,3.4,4.8,0,0,Math.PI*2);ctx.ellipse(8,-3,3.4,4.8,0,0,Math.PI*2);ctx.fill();
circle(-7,-5,1.3,"#ffffff");circle(9,-5,1.3,"#ffffff");}
circle(0,5,2.7,"#e88099");
ctx.strokeStyle="#75445a";ctx.lineWidth=1.6;ctx.beginPath();
if(expression==="sad"){ctx.arc(0,15,4,Math.PI*1.1,Math.PI*1.9);}else{ctx.arc(0,8,5,.1,Math.PI-.1);}
ctx.stroke();ctx.fillStyle="#ed91a5";circle(-14,6,3,"#ed91a577");circle(14,6,3,"#ed91a577");
// Fine whiskers and cheek highlights.
ctx.strokeStyle="#ffffff99";ctx.lineWidth=.9;
for(const side of [-1,1])for(const angle of [-.24,.14]){ctx.beginPath();ctx.moveTo(side*11,7);
ctx.lineTo(side*26,7+angle*20);ctx.stroke();}
ctx.restore();}
function frame(t){const dt=Math.min(.05,(t-(frame.last||t))/1000);frame.last=t;
if(!paused){visualTime+=dt;petCooldown=Math.max(0,petCooldown-dt);
levelBanner=Math.max(0,levelBanner-dt);hitFlash=Math.max(0,hitFlash-dt);
magnetTime=Math.max(0,magnetTime-dt);shieldTime=Math.max(0,shieldTime-dt);
for(const p of particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=90*dt;p.life-=dt;}
particles=particles.filter(p=>p.life>0);
for(const h of hearts){h.x+=h.vx*dt;h.y+=h.vy*dt;h.life-=dt;}
hearts=hearts.filter(h=>h.life>0);}
ctx.clearRect(0,0,W,H);drawWorldBackdrop();
ctx.save();ctx.globalAlpha=.22;ctx.strokeStyle=world().grid;ctx.lineWidth=1;
for(let x=0;x<W;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
for(let y=0;y<H;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
ctx.restore();drawScenery();
if(!won&&!paused){if(questKind==="survive"){petMoodClock+=dt;
if(petMoodClock>=1){petMoodClock-=1;advanceQuest(1);}}
petWander-=dt;
if(petWander<=0){petWander=rand(1.5,4);petTarget={x:clamp(player.x+rand(-85,85),30,W-30),y:clamp(player.y+rand(-85,85),30,H-30)};}
const followDist=Math.hypot(player.x-pet.x,player.y-pet.y);
if(followDist>125)petTarget={x:player.x+35,y:player.y+35};
const petDx=petTarget.x-pet.x,petDy=petTarget.y-pet.y,petDist=Math.hypot(petDx,petDy);
if(petDist>3){const step=Math.min(petDist,(state.petEnergy<20?55:105)*dt);pet.x+=petDx/petDist*step;pet.y+=petDy/petDist*step;}
careClock+=dt;
if(careClock>=20){careClock=0;
state.petHunger=clamp(state.petHunger-1,0,100);
state.petEnergy=clamp(state.petEnergy-1,0,100);
state.petCleanliness=clamp(state.petCleanliness-1,0,100);
if(state.petHunger<20||state.petCleanliness<20)state.petMood=clamp(state.petMood-1,0,100);
save();updateStats();}
let dx=Number(keys.has("d")||keys.has("arrowright"))-Number(keys.has("a")||keys.has("arrowleft"));
let dy=Number(keys.has("s")||keys.has("arrowdown"))-Number(keys.has("w")||keys.has("arrowup"));
if(joystick){const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const length=Math.hypot(vx,vy);if(length>8){dx=vx/Math.max(60,length);dy=vy/Math.max(60,length);}}
const len=Math.max(1,Math.hypot(dx,dy));playerMoving=Math.hypot(dx,dy)>.1;
if(Math.abs(dx)>.1)playerFacing=dx>0?1:-1;
moveAroundObstacles(player,dx/len*state.speed*dt,dy/len*state.speed*dt);
for(let i=treasures.length-1;i>=0;i--){const t=treasures[i];
if(Math.hypot(player.x-t.x,player.y-t.y)<player.r+15){
burst(t.x,t.y,"#a5f5ff",18);treasures.splice(i,1);
if(t.kind==="gem"){state.coins+=75;gainPetXP(12);msg("💎 Rare gem! +75 coins and +12 pet XP.");}
else if(t.kind==="magnet"){magnetTime=12;msg("🧲 Coin magnet active for 12 seconds!");}
else{shieldTime=12;msg("🛡️ Shield active for 12 seconds!");}
save();updateStats();}}
if(magnetTime>0)for(const c of targets){const d=Math.hypot(player.x-c.x,player.y-c.y);
if(d>1&&d<145){const speed=Math.min(d,220*dt);c.x+=(player.x-c.x)/d*speed;c.y+=(player.y-c.y)/d*speed;}}
for(let i=targets.length-1;i>=0;i--)if(Math.hypot(player.x-targets[i].x,player.y-targets[i].y)<player.r+targets[i].r){
burst(targets[i].x,targets[i].y,"#ffe57d",10);targets.splice(i,1);collected++;state.coins+=10;
if(questKind==="collect")advanceQuest(1);save();updateStats();}
for(const e of enemies){
if(e.type==="chaser"){const vx=player.x-e.x,vy=player.y-e.y,d=Math.hypot(vx,vy);
if(d>1&&d<210){const desiredX=vx/d*e.speed,desiredY=vy/d*e.speed;
e.vx+=(desiredX-e.vx)*Math.min(1,dt*1.5);e.vy+=(desiredY-e.vy)*Math.min(1,dt*1.5);}}
e.x+=e.vx*dt;e.y+=e.vy*dt;
if(e.x<e.r||e.x>W-e.r)e.vx*=-1;
if(e.y<e.r||e.y>H-e.r)e.vy*=-1;
e.x=clamp(e.x,e.r,W-e.r);e.y=clamp(e.y,e.r,H-e.r);
if(invincible<=0&&shieldTime<=0&&Math.hypot(player.x-e.x,player.y-e.y)<player.r+e.r){
if(questKind==="survive"){questProgress=0;petMoodClock=0;updateQuest();}
hit++;invincible=1.2;hitFlash=.3;burst(player.x,player.y,"#ff7c96",20);state.coins=Math.max(0,state.coins-5);msg("Enemy hit! Lost 5 coins.");updateStats();}}
invincible=Math.max(0,invincible-dt);
if(!targets.length)finishLevel();}
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
startLevel();renderShop();renderWardrobe();requestAnimationFrame(frame);
</script></body></html>
'''
