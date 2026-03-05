from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import read_json


@dataclass
class DisplayCfg:
    mode: str  # "landscape" | "portrait"
    virtualWidth: int
    virtualHeight: int


@dataclass
class Bounds:
    xMin: int
    yMin: int
    xMax: int
    yMax: int


@dataclass
class CameraCfg:
    followObject: str
    lerp: float


@dataclass
class UIAnchorCfg:
    objectName: str
    anchor: str  # top-left, top-right, bottom-left, bottom-right
    marginX: int
    marginY: int


@dataclass
class UICfg:
    layer: str
    hud: UIAnchorCfg
    joystick: UIAnchorCfg


@dataclass
class SpawnCfg:
    objectName: str
    count: int
    enabled: bool = True
    respawnOnCollect: bool = False
    minDistanceFromPlayer: int = 0


@dataclass
class ShopUpgrade:
    id: str
    name: str
    cost: int
    effect: Dict[str, Any]


@dataclass
class ShopCfg:
    currencyVariable: str
    upgrades: List[ShopUpgrade]


@dataclass
class LevelsCfg:
    mode: str  # "procedural" | "static"
    seed: int
    count: int


@dataclass
class PackCfg:
    name: str
    version: str
    scene: str
    display: DisplayCfg
    worldBounds: Bounds
    camera: CameraCfg
    ui: UICfg
    coinSpawn: SpawnCfg
    enemySpawn: SpawnCfg
    levels: LevelsCfg
    shop: ShopCfg


def _get(d: Dict[str, Any], path: str, default: Any) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def load_pack_cfg(pack_dir: Path) -> PackCfg:
    data = read_json(pack_dir / "pack.json")
    if not isinstance(data, dict):
        raise ValueError("pack.json must be an object")

    name = str(data.get("name", pack_dir.name))
    version = str(data.get("version", "0.0.0"))
    scene = str(data.get("scene", "Main"))

    display = DisplayCfg(
        mode=str(_get(data, "display.mode", "landscape")),
        virtualWidth=int(_get(data, "display.virtualWidth", 960)),
        virtualHeight=int(_get(data, "display.virtualHeight", 540)),
    )

    wb = _get(data, "world.bounds", {})
    if not isinstance(wb, dict):
        wb = {}
    bounds = Bounds(
        xMin=int(wb.get("xMin", 0)),
        yMin=int(wb.get("yMin", 0)),
        xMax=int(wb.get("xMax", 2000)),
        yMax=int(wb.get("yMax", 1200)),
    )

    camera = CameraCfg(
        followObject=str(_get(data, "camera.followObject", "Player")),
        lerp=float(_get(data, "camera.lerp", 0.08)),
    )

    ui_layer = str(_get(data, "ui.layer", "UI"))

    hud = UIAnchorCfg(
        objectName=str(_get(data, "ui.hud.objectName", "HUD")),
        anchor=str(_get(data, "ui.hud.anchor", "top-left")),
        marginX=int(_get(data, "ui.hud.marginX", 20)),
        marginY=int(_get(data, "ui.hud.marginY", 20)),
    )

    joystick = UIAnchorCfg(
        objectName=str(_get(data, "ui.joystick.objectName", "TouchJoystick")),
        anchor=str(_get(data, "ui.joystick.anchor", "bottom-left")),
        marginX=int(_get(data, "ui.joystick.marginX", 140)),
        marginY=int(_get(data, "ui.joystick.marginY", 140)),
    )

    ui = UICfg(layer=ui_layer, hud=hud, joystick=joystick)

    coin = _get(data, "spawns.coin", {})
    if not isinstance(coin, dict):
        coin = {}
    coinSpawn = SpawnCfg(
        objectName=str(coin.get("objectName", "Coin")),
        count=int(coin.get("count", 1)),
        enabled=True,
        respawnOnCollect=bool(coin.get("respawnOnCollect", True)),
        minDistanceFromPlayer=int(coin.get("minDistanceFromPlayer", 250)),
    )

    enemy = _get(data, "spawns.enemy", {})
    if not isinstance(enemy, dict):
        enemy = {}
    enemySpawn = SpawnCfg(
        objectName=str(enemy.get("objectName", "Enemy")),
        count=int(enemy.get("count", 1)),
        enabled=bool(enemy.get("enabled", True)),
        respawnOnCollect=False,
        minDistanceFromPlayer=int(enemy.get("minDistanceFromPlayer", 350)),
    )

    levels_d = _get(data, "levels", {})
    if not isinstance(levels_d, dict):
        levels_d = {}
    levels = LevelsCfg(
        mode=str(levels_d.get("mode", "procedural")),
        seed=int(levels_d.get("seed", 1337)),
        count=int(levels_d.get("count", 1)),
    )

    shop_d = _get(data, "shop", {})
    if not isinstance(shop_d, dict):
        shop_d = {}
    upgrades_d = shop_d.get("upgrades", [])
    upgrades: List[ShopUpgrade] = []
    if isinstance(upgrades_d, list):
        for u in upgrades_d:
            if not isinstance(u, dict):
                continue
            upgrades.append(
                ShopUpgrade(
                    id=str(u.get("id", "")),
                    name=str(u.get("name", "")),
                    cost=int(u.get("cost", 0)),
                    effect=u.get("effect", {}) if isinstance(u.get("effect"), dict) else {},
                )
            )
    shop = ShopCfg(currencyVariable=str(shop_d.get("currencyVariable", "Coins")), upgrades=upgrades)

    return PackCfg(
        name=name,
        version=version,
        scene=scene,
        display=display,
        worldBounds=bounds,
        camera=camera,
        ui=ui,
        coinSpawn=coinSpawn,
        enemySpawn=enemySpawn,
        levels=levels,
        shop=shop,
    )
