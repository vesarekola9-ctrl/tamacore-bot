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
#shop button{margin:4px}#message{min-height:24px;color:#ffe68c}#touch{display:flex;justify-content:space-between;margin-top:10px}
#touch button{min-width:64px;min-height:50px}small{color:#b8c9dc}
</style></head><body><main><header><h1 id="title">TamaCore</h1><div>
<button id="shopToggle">Shop</button><button id="reset">New game</button></div></header>
<div id="stats" aria-live="polite"></div>
<canvas id="game" width="800" height="600" aria-label="Playable game field"></canvas>
<div id="touch"><div><button data-key="ArrowLeft">◀</button><button data-key="ArrowUp">▲</button><button data-key="ArrowDown">▼</button><button data-key="ArrowRight">▶</button></div><button id="feed">Feed pet</button></div>
<div id="panel"><div id="message">Collect gold coins, avoid red enemies, and finish every level.</div>
<div id="shop"><h2>Shop</h2><div id="items"></div></div>
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
const state={coins:250,speed:200,level:0,owned:{},petHunger:75};
try{const saved=JSON.parse(localStorage.getItem(KEY)||"null");if(saved&&typeof saved==="object"){
for(const k of ["coins","speed","level","petHunger"])if(Number.isFinite(saved[k]))state[k]=saved[k];
if(saved.owned&&typeof saved.owned==="object")state.owned=saved.owned;
}}catch(_){}
state.level=clamp(Math.floor(state.level),0,Math.max(0,cfg.levels.length-1));
let player={x:W/2,y:H/2,r:17},targets=[],enemies=[],collected=0,hit=0,invincible=0,won=false;
let joystick=null;
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
function startLevel(){const lv=cfg.levels[state.level];if(!lv){won=true;msg("Game complete!");return;}
player.x=W/2;player.y=H/2;collected=0;hit=0;invincible=0;
targets=Array.from({length:Math.min(150,Math.max(0,lv.coinCount||0))},()=>point(10));
enemies=Array.from({length:Math.min(50,Math.max(0,lv.enemyCount||0))},()=>({...point(16),vx:rand(-90,90),vy:rand(-90,90)}));
msg("Level "+(state.level+1)+": collect "+targets.length+" coins and avoid enemies.");
updateStats();}
function updateStats(){const lv=cfg.levels[state.level]||{};
$("stats").textContent="Level "+(state.level+1)+"/"+cfg.levels.length+"  •  Coins: "+state.coins+
"  •  Collected: "+collected+"/"+Math.min(150,lv.coinCount||0)+"  •  Speed: "+state.speed+
"  •  Pet hunger: "+Math.round(state.petHunger);}
function finishLevel(){if(state.level+1>=cfg.levels.length){won=true;msg("🏆 All levels completed! Open New game to play again.");}
else{state.level++;save();startLevel();}save();}
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
state.petHunger=clamp(state.petHunger+(Number(effect.moodAdd)||0),0,100);
save();renderShop();updateStats();msg("Purchased "+upgrade.name);};box.appendChild(b);}}
$("shopToggle").onclick=()=>{$("shop").classList.toggle("open");renderShop();};
$("reset").onclick=()=>{if(!confirm("Erase saved progress and restart?"))return;
state.coins=250;state.speed=200;state.level=0;state.owned={};state.petHunger=75;won=false;save();startLevel();renderShop();};
$("feed").onclick=()=>{const food=cfg.foods[0];if(!food){msg("No food available.");return;}
if(state.coins<food.price){msg("Not enough coins to feed your pet.");return;}
state.coins-=food.price;state.petHunger=clamp(state.petHunger+food.hunger,0,100);
save();updateStats();msg("Fed pet: "+food.name);};
addEventListener("keydown",e=>{if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"," "].includes(e.key))e.preventDefault();keys.add(e.key.toLowerCase());});
addEventListener("keyup",e=>keys.delete(e.key.toLowerCase()));
addEventListener("blur",()=>keys.clear());
for(const b of document.querySelectorAll("[data-key]")){
const key=b.dataset.key.toLowerCase();
b.addEventListener("pointerdown",e=>{e.preventDefault();b.setPointerCapture(e.pointerId);keys.add(key);});
for(const event of ["pointerup","pointercancel","lostpointercapture"])b.addEventListener(event,()=>keys.delete(key));
}
function circle(x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();}
function frame(t){const dt=Math.min(.05,(t-(frame.last||t))/1000);frame.last=t;
ctx.clearRect(0,0,W,H);ctx.fillStyle="#17384b";ctx.fillRect(0,0,W,H);
ctx.strokeStyle="#234b60";ctx.lineWidth=1;
for(let x=0;x<W;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
for(let y=0;y<H;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
if(!won){let dx=Number(keys.has("d")||keys.has("arrowright"))-Number(keys.has("a")||keys.has("arrowleft"));
let dy=Number(keys.has("s")||keys.has("arrowdown"))-Number(keys.has("w")||keys.has("arrowup"));
if(joystick){const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const length=Math.hypot(vx,vy);if(length>8){dx=vx/Math.max(60,length);dy=vy/Math.max(60,length);}}
const len=Math.max(1,Math.hypot(dx,dy));player.x=clamp(player.x+dx/len*state.speed*dt,player.r,W-player.r);
player.y=clamp(player.y+dy/len*state.speed*dt,player.r,H-player.r);
for(let i=targets.length-1;i>=0;i--)if(Math.hypot(player.x-targets[i].x,player.y-targets[i].y)<player.r+targets[i].r){
targets.splice(i,1);collected++;state.coins+=10;save();updateStats();}
for(const e of enemies){e.x+=e.vx*dt;e.y+=e.vy*dt;
if(e.x<e.r||e.x>W-e.r)e.vx*=-1;
if(e.y<e.r||e.y>H-e.r)e.vy*=-1;
e.x=clamp(e.x,e.r,W-e.r);e.y=clamp(e.y,e.r,H-e.r);
if(invincible<=0&&Math.hypot(player.x-e.x,player.y-e.y)<player.r+e.r){
hit++;invincible=1.2;state.coins=Math.max(0,state.coins-5);msg("Enemy hit! Lost 5 coins.");updateStats();}}
invincible=Math.max(0,invincible-dt);
if(!targets.length)finishLevel();}
for(const c of targets)circle(c.x,c.y,c.r,"#ffd35a");
if(joystick){circle(joystick.start.x,joystick.start.y,56,"#365b77");
const vx=joystick.now.x-joystick.start.x,vy=joystick.now.y-joystick.start.y;
const len=Math.max(1,Math.hypot(vx,vy));circle(joystick.start.x+vx/len*Math.min(48,len),joystick.start.y+vy/len*Math.min(48,len),24,"#9acbdc");}
for(const e of enemies)circle(e.x,e.y,e.r,"#fb6570");
circle(player.x,player.y,player.r,invincible>0?"#ffffff":"#79e0d0");
ctx.font="30px system-ui";ctx.textAlign="center";ctx.fillText("🐾",player.x,player.y+10);ctx.textAlign="left";
ctx.fillStyle="#ffffff";ctx.font="bold 18px system-ui";ctx.fillText("Coins left: "+targets.length,16,30);
if(won){ctx.fillStyle="#ffe58d";ctx.font="bold 44px system-ui";ctx.textAlign="center";
ctx.fillText("YOU WIN!",W/2,H/2);ctx.textAlign="left";}
requestAnimationFrame(frame);}
startLevel();renderShop();requestAnimationFrame(frame);
</script></body></html>
'''
