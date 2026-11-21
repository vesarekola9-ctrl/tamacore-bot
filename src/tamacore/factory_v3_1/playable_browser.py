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
*{box-sizing:border-box}body{margin:0;background:#0b1224;color:#fff;font:16px system-ui,sans-serif}
main{max-width:850px;margin:auto;padding:12px}header{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
h1{font-size:23px;margin:8px 0}button{background:#334c7e;color:#fff;border:1px solid #6783ad;border-radius:10px;padding:10px 14px;cursor:pointer}
button:hover{background:#4967a0}#stats{margin:8px 0;color:#bfe6ff}canvas{display:block;width:100%;height:auto;max-height:65vh;aspect-ratio:4/3;border:2px solid #4c7b9e;border-radius:16px;background:#142b3d;touch-action:none}
#panel{background:#182841;border-radius:12px;padding:12px;margin-top:10px}#shop{display:none}#shop.open{display:block}
#shop button,#careActions button{margin:4px}#message{min-height:24px;color:#ffe68c}#touch{display:flex;justify-content:space-between;margin-top:10px}
#touch button{min-width:64px;min-height:50px}small{color:#b8c9dc}
</style></head><body><main><header><h1 id="title">TamaCore</h1><div>
<button id="shopToggle">Shop</button><button id="pause">Pause</button><button id="reset">New game</button></div></header>
<div id="stats" aria-live="polite"></div>
<canvas id="game" width="800" height="600" aria-label="Playable game field"></canvas>
<div id="touch"><div><button data-key="ArrowLeft">◀</button><button data-key="ArrowUp">▲</button><button data-key="ArrowDown">▼</button><button data-key="ArrowRight">▶</button></div><button id="feed">Feed pet</button></div>
<div id="panel"><div id="message">Collect gold coins, avoid red enemies, and finish every level.</div>
<div id="shop"><h2>Shop</h2><div id="items"></div></div>
<div id="wardrobe"><h2>Wardrobe</h2><div id="cosmetics"></div></div>
<div id="foodMenu"><h2>Pet care</h2><label for="foodChoice">Food: </label><select id="foodChoice"></select><button id="feedSelected">Feed selected food</button><div id="careActions"><button id="cleanPet">🧼 Clean (15 coins)</button><button id="playPet">🎾 Play</button><button id="restPet">💤 Rest</button></div><p id="petStatus"></p><p id="petProgress"></p><p id="petEmotion" aria-live="polite"></p><p id="questStatus"></p></div>
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
let scenery=[],visualTime=0,playerMoving=false,playerFacing=1;
let joystick=null,paused=false,careClock=0,pet={x:W/2+65,y:H/2+35},petMoodClock=0,petWander=0,petTarget={x:W/2+65,y:H/2+35};
function canvasPoint(e){const rect=canvas.getBoundingClientRect();return{x:(e.clientX-rect.left)*W/rect.width,y:(e.clientY-rect.top)*H/rect.height};}
canvas.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse")return;
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
function drawScenery(){const theme=state.level%worlds.length;
for(const d of scenery){ctx.save();ctx.translate(d.x,d.y);ctx.globalAlpha=.25+(Math.sin(visualTime*1.3+d.phase)+1)*.12;
if(theme===0){ctx.fillStyle=d.kind%2?"#b0e8a2":"#f6c0e2";
for(let j=0;j<5;j++){ctx.beginPath();ctx.ellipse(Math.cos(j*1.256)*d.size*.5,Math.sin(j*1.256)*d.size*.5,d.size*.36,d.size*.55,j*1.256,0,Math.PI*2);ctx.fill();}
circle(0,0,d.size*.22,"#ffdf87");}
else if(theme===1){ctx.fillStyle=d.kind%2?"#9ad9f8":"#d6a9ff";ctx.beginPath();ctx.moveTo(0,-d.size);ctx.lineTo(d.size*.65,0);ctx.lineTo(0,d.size);ctx.lineTo(-d.size*.65,0);ctx.closePath();ctx.fill();}
else if(theme===2){ctx.strokeStyle="#efc184";ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,d.size,0,Math.PI);ctx.stroke();}
else{ctx.fillStyle="#d8f6ff";for(let j=0;j<3;j++){ctx.save();ctx.rotate(j*Math.PI/3);ctx.fillRect(-1,-d.size,2,d.size*2);ctx.restore();}}
ctx.restore();}}
function startLevel(){const lv=cfg.levels[state.level];if(!lv){won=true;msg("Game complete!");return;}
player.x=W/2;player.y=H/2;generateScenery();beginQuest();pet.x=player.x+65;pet.y=player.y+35;petTarget={x:pet.x,y:pet.y};collected=0;hit=0;invincible=0;
obstacles=[];
for(let i=0;i<Math.min(14,3+state.level);i++){
const p=point(rand(20,32));if(Math.hypot(p.x-W/2,p.y-H/2)>115&&!blocked(p.x,p.y,p.r))obstacles.push(p);}
targets=Array.from({length:Math.min(150,Math.max(0,lv.coinCount||0))},()=>safePoint(10));
enemies=Array.from({length:Math.min(50,Math.max(0,lv.enemyCount||0))},()=>({...safePoint(16),vx:rand(-90,90),vy:rand(-90,90)}));
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
function finishLevel(){const reward=50+state.level*25;gainPetXP(35);state.coins+=reward;
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
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;state.petEnergy=75;state.petMood=75;state.petCleanliness=75;state.questsCompleted=0;state.petXP=0;state.petStage=1;state.cosmeticsOwned={};state.equippedCosmetic="";won=false;paused=false;$("pause").textContent="Pause";save();startLevel();renderShop();renderWardrobe();};
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
function drawBunny(x,y,scale,bodyColor,walking,face=1,expression="happy"){
const bounce=walking?Math.abs(Math.sin(visualTime*12))*3:Math.sin(visualTime*2)*1.3;
ctx.save();ctx.translate(x,y-bounce);ctx.scale(scale*face,scale);
ctx.fillStyle="#10242b66";ctx.beginPath();ctx.ellipse(0,19,19,6,0,0,Math.PI*2);ctx.fill();
ctx.fillStyle=bodyColor;
ctx.beginPath();ctx.ellipse(-9,-23,7,20,-.15,0,Math.PI*2);ctx.ellipse(9,-23,7,20,.15,0,Math.PI*2);ctx.fill();
ctx.fillStyle="#f4a7bb";ctx.beginPath();ctx.ellipse(-9,-24,3,13,-.15,0,Math.PI*2);ctx.ellipse(9,-24,3,13,.15,0,Math.PI*2);ctx.fill();
circle(0,1,19,bodyColor);
ctx.fillStyle="#ffffffaa";ctx.beginPath();ctx.ellipse(-5,10,9,6,0,0,Math.PI*2);ctx.fill();
const blink=Math.sin(visualTime*1.8+x*.03)>.995;
ctx.fillStyle="#243040";if(blink){ctx.fillRect(-11,-3,7,2);ctx.fillRect(5,-3,7,2);}else{
ctx.beginPath();ctx.ellipse(-8,-3,3.4,4.8,0,0,Math.PI*2);ctx.ellipse(8,-3,3.4,4.8,0,0,Math.PI*2);ctx.fill();
circle(-7,-5,1.3,"#ffffff");circle(9,-5,1.3,"#ffffff");}
circle(0,5,2.7,"#e88099");
ctx.strokeStyle="#75445a";ctx.lineWidth=1.6;ctx.beginPath();
if(expression==="sad"){ctx.arc(0,15,4,Math.PI*1.1,Math.PI*1.9);}else{ctx.arc(0,8,5,.1,Math.PI-.1);}
ctx.stroke();ctx.fillStyle="#ed91a5";circle(-14,6,3,"#ed91a577");circle(14,6,3,"#ed91a577");
ctx.restore();}
function frame(t){const dt=Math.min(.05,(t-(frame.last||t))/1000);frame.last=t;
if(!paused)visualTime+=dt;
ctx.clearRect(0,0,W,H);ctx.fillStyle=world().floor;ctx.fillRect(0,0,W,H);
ctx.strokeStyle=world().grid;ctx.lineWidth=1;
for(let x=0;x<W;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
for(let y=0;y<H;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
drawScenery();
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
for(let i=targets.length-1;i>=0;i--)if(Math.hypot(player.x-targets[i].x,player.y-targets[i].y)<player.r+targets[i].r){
targets.splice(i,1);collected++;state.coins+=10;
if(questKind==="collect")advanceQuest(1);save();updateStats();}
for(const e of enemies){e.x+=e.vx*dt;e.y+=e.vy*dt;
if(e.x<e.r||e.x>W-e.r)e.vx*=-1;
if(e.y<e.r||e.y>H-e.r)e.vy*=-1;
e.x=clamp(e.x,e.r,W-e.r);e.y=clamp(e.y,e.r,H-e.r);
if(invincible<=0&&Math.hypot(player.x-e.x,player.y-e.y)<player.r+e.r){
if(questKind==="survive"){questProgress=0;petMoodClock=0;updateQuest();}
hit++;invincible=1.2;state.coins=Math.max(0,state.coins-5);msg("Enemy hit! Lost 5 coins.");updateStats();}}
invincible=Math.max(0,invincible-dt);
if(!targets.length)finishLevel();}
for(const o of obstacles){circle(o.x+3,o.y+5,o.r+3,"#172331");circle(o.x,o.y,o.r,world().obstacle);
circle(o.x-o.r*.2,o.y-o.r*.2,o.r*.32,"#ffffff25");}
for(const c of targets){const pulse=1+Math.sin(visualTime*5+c.x*.07)*.12;
circle(c.x,c.y,c.r*pulse+5,"#e5b54844");circle(c.x,c.y,c.r*pulse,"#ffd35a");
ctx.fillStyle="#fff1aa";ctx.fillRect(c.x-1.5,c.y-5,3,10);}
// Companion is decorative and never collides with enemies or collectibles.
drawBunny(pet.x,pet.y,.72+state.petStage*.09,state.petMood<30?"#a9b3cf":"#ffb6d7",!paused&&petDist>3,1,state.petMood<30?"sad":"happy");
if(state.petEnergy<20){ctx.font="18px system-ui";ctx.fillText("Zzz",pet.x+16,pet.y-30);}
if(joystick){circle(joystick.start.x,joystick.start.y,56,"#365b77");
const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const len=Math.max(1,Math.hypot(vx,vy));circle(joystick.start.x+vx/len*Math.min(48,len),joystick.start.y+vy/len*Math.min(48,len),24,"#9acbdc");}
for(const e of enemies){circle(e.x,e.y,e.r+3,"#9e3447");circle(e.x,e.y,e.r,"#fb6570");
circle(e.x-5,e.y-3,3,"#fff");circle(e.x+5,e.y-3,3,"#fff");
circle(e.x-4,e.y-3,1.5,"#222");circle(e.x+6,e.y-3,1.5,"#222");}
drawBunny(player.x,player.y,.9,invincible>0?"#ffffff":"#79e0d0",!paused&&playerMoving,playerFacing);
if(state.equippedCosmetic){ctx.font="23px system-ui";ctx.fillText("✦",player.x+17,player.y-13);}
ctx.textAlign="left";
ctx.fillStyle="#ffffff";ctx.font="bold 18px system-ui";ctx.fillText(world().name+"  •  Coins left: "+targets.length,16,30);
if(paused){ctx.fillStyle="#ffffff";ctx.font="bold 48px system-ui";ctx.textAlign="center";ctx.fillText("PAUSED",W/2,H/2);ctx.textAlign="left";}
if(won){ctx.fillStyle="#ffe58d";ctx.font="bold 44px system-ui";ctx.textAlign="center";
ctx.fillText("YOU WIN!",W/2,H/2);ctx.textAlign="left";}
requestAnimationFrame(frame);}
startLevel();renderShop();renderWardrobe();requestAnimationFrame(frame);
</script></body></html>
'''
