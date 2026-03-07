from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json


@dataclass
class DisplayCfg:
    mode: str = "portrait"
    virtualWidth: int = 720
    virtualHeight: int = 1280


@dataclass
class WorldBoundsCfg:
    xMin: int = 0
    yMin: int = 0
    xMax: int = 720
    yMax: int = 1280


@dataclass
class CameraCfg:
    followObject: str = "Player"
    lerp: float = 0.12


@dataclass
class HudCfg:
    objectName: str = "HUD"
    anchor: str = "top-left"
    marginX: int = 24
    marginY: int = 24


@dataclass
class JoystickCfg:
    objectName: str = "TouchJoystick"
    anchor: str = "bottom-left"
    marginX: int = 36
    marginY: int = 36


@dataclass
class UiCfg:
    layer: str = "UI"
    hud: HudCfg = field(default_factory=HudCfg)
    joystick: JoystickCfg = field(default_factory=JoystickCfg)


@dataclass
class SpawnCfg:
    objectName: str
    count: int = 0
    enabled: bool = True
    respawnOnCollect: bool = False
    minDistanceFromPlayer: int = 0


@dataclass
class LevelsCfg:
    count: int = 1
    coinBase: int = 8
    coinStep: int = 2
    enemyBase: int = 0
    enemyStep: int = 1
    seed: int = 1337


@dataclass
class ShopUpgrade:
    id: str
    name: str
    cost: int
    effect: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShopCfg:
    currencyVariable: str = "Coins"
    upgrades: List[ShopUpgrade] = field(default_factory=list)


@dataclass
class PackCfg:
    name: str = "TamaCore Pack"
    version: str = "1.0.0"
    scene: str = "Main"
    display: DisplayCfg = field(default_factory=DisplayCfg)
    worldBounds: WorldBoundsCfg = field(default_factory=WorldBoundsCfg)
    camera: CameraCfg = field(default_factory=CameraCfg)
    ui: UiCfg = field(default_factory=UiCfg)
    coinSpawn: SpawnCfg = field(default_factory=lambda: SpawnCfg(objectName="Coin", count=8, enabled=True, respawnOnCollect=True, minDistanceFromPlayer=120))
    enemySpawn: SpawnCfg = field(default_factory=lambda: SpawnCfg(objectName="Enemy", count=0, enabled=False, respawnOnCollect=False, minDistanceFromPlayer=180))
    levels: LevelsCfg = field(default_factory=LevelsCfg)
    shop: ShopCfg = field(default_factory=ShopCfg)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in {"1", "true", "yes", "on"}:
            return True
        if low in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _to_str(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _read_pack_json(pack_dir: Path) -> Dict[str, Any]:
    path = pack_dir / "pack.json"
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid pack.json in {pack_dir}")
    return data


def _parse_display(data: Dict[str, Any]) -> DisplayCfg:
    return DisplayCfg(
        mode=_to_str(data.get("mode"), "portrait"),
        virtualWidth=_to_int(data.get("virtualWidth"), 720),
        virtualHeight=_to_int(data.get("virtualHeight"), 1280),
    )


def _parse_world_bounds(data: Dict[str, Any], display: DisplayCfg) -> WorldBoundsCfg:
    return WorldBoundsCfg(
        xMin=_to_int(data.get("xMin"), 0),
        yMin=_to_int(data.get("yMin"), 0),
        xMax=_to_int(data.get("xMax"), display.virtualWidth),
        yMax=_to_int(data.get("yMax"), display.virtualHeight),
    )


def _parse_camera(data: Dict[str, Any]) -> CameraCfg:
    return CameraCfg(
        followObject=_to_str(data.get("followObject"), "Player"),
        lerp=_to_float(data.get("lerp"), 0.12),
    )


def _parse_hud(data: Dict[str, Any]) -> HudCfg:
    return HudCfg(
        objectName=_to_str(data.get("objectName"), "HUD"),
        anchor=_to_str(data.get("anchor"), "top-left"),
        marginX=_to_int(data.get("marginX"), 24),
        marginY=_to_int(data.get("marginY"), 24),
    )


def _parse_joystick(data: Dict[str, Any]) -> JoystickCfg:
    return JoystickCfg(
        objectName=_to_str(data.get("objectName"), "TouchJoystick"),
        anchor=_to_str(data.get("anchor"), "bottom-left"),
        marginX=_to_int(data.get("marginX"), 36),
        marginY=_to_int(data.get("marginY"), 36),
    )


def _parse_ui(data: Dict[str, Any]) -> UiCfg:
    return UiCfg(
        layer=_to_str(data.get("layer"), "UI"),
        hud=_parse_hud(_as_dict(data.get("hud"))),
        joystick=_parse_joystick(_as_dict(data.get("joystick"))),
    )


def _parse_spawn(data: Dict[str, Any], default_name: str, default_count: int, default_enabled: bool, default_respawn: bool, default_min_dist: int) -> SpawnCfg:
    return SpawnCfg(
        objectName=_to_str(data.get("objectName"), default_name),
        count=max(0, _to_int(data.get("count"), default_count)),
        enabled=_to_bool(data.get("enabled"), default_enabled),
        respawnOnCollect=_to_bool(data.get("respawnOnCollect"), default_respawn),
        minDistanceFromPlayer=max(0, _to_int(data.get("minDistanceFromPlayer"), default_min_dist)),
    )


def _parse_levels(data: Dict[str, Any]) -> LevelsCfg:
    return LevelsCfg(
        count=max(1, _to_int(data.get("count"), 1)),
        coinBase=max(0, _to_int(data.get("coinBase"), 8)),
        coinStep=max(0, _to_int(data.get("coinStep"), 2)),
        enemyBase=max(0, _to_int(data.get("enemyBase"), 0)),
        enemyStep=max(0, _to_int(data.get("enemyStep"), 1)),
        seed=_to_int(data.get("seed"), 1337),
    )


def _parse_upgrade(data: Dict[str, Any], index: int) -> ShopUpgrade:
    upgrade_id = _to_str(data.get("id"), f"upgrade_{index + 1}")
    name = _to_str(data.get("name"), upgrade_id.replace("_", " ").title())
    cost = max(0, _to_int(data.get("cost"), 0))
    effect = _as_dict(data.get("effect"))
    return ShopUpgrade(id=upgrade_id, name=name, cost=cost, effect=effect)


def _parse_shop(data: Dict[str, Any]) -> ShopCfg:
    upgrades = [
        _parse_upgrade(_as_dict(item), index)
        for index, item in enumerate(_as_list(data.get("upgrades")))
        if isinstance(item, dict)
    ]
    return ShopCfg(
        currencyVariable=_to_str(data.get("currencyVariable"), "Coins"),
        upgrades=upgrades,
    )


def load_pack_cfg(pack_dir: Path) -> PackCfg:
    raw = _read_pack_json(pack_dir)

    display = _parse_display(_as_dict(raw.get("display")))
    cfg = PackCfg(
        name=_to_str(raw.get("name"), "TamaCore Pack"),
        version=_to_str(raw.get("version"), "1.0.0"),
        scene=_to_str(raw.get("scene"), "Main"),
        display=display,
        worldBounds=_parse_world_bounds(_as_dict(raw.get("worldBounds")), display),
        camera=_parse_camera(_as_dict(raw.get("camera"))),
        ui=_parse_ui(_as_dict(raw.get("ui"))),
        coinSpawn=_parse_spawn(_as_dict(raw.get("coinSpawn")), "Coin", 8, True, True, 120),
        enemySpawn=_parse_spawn(_as_dict(raw.get("enemySpawn")), "Enemy", 0, False, False, 180),
        levels=_parse_levels(_as_dict(raw.get("levels"))),
        shop=_parse_shop(_as_dict(raw.get("shop"))),
    )
    return cfg
