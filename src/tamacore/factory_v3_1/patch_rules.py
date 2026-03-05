from __future__ import annotations

from typing import Any, Dict, List

from .schema import PackCfg


def apply_v3_1_rules(project: Dict[str, Any], scene: Dict[str, Any], pack: PackCfg) -> None:
    """
    Adds:
      - global vars: Coins, HP, CurrentLevel
      - camera follow + lerp
      - clamp player to world bounds
      - coin respawn logic using level spawn area (reads variables)
      - UI anchoring using camera center (keeps HUD fixed)
    """
    ensure_global_var(project, "Coins", "number", "0")
    ensure_global_var(project, "HP", "number", "3")
    ensure_global_var(project, "CurrentLevel", "string", "level_001")

    # Ensure scene vars to store spawn rectangles (set on start from level file later)
    ensure_scene_var(scene, "CoinAreaX", "number", "200")
    ensure_scene_var(scene, "CoinAreaY", "number", "200")
    ensure_scene_var(scene, "CoinAreaW", "number", "800")
    ensure_scene_var(scene, "CoinAreaH", "number", "500")

    ensure_scene_var(scene, "EnemyAreaX", "number", "300")
    ensure_scene_var(scene, "EnemyAreaY", "number", "300")
    ensure_scene_var(scene, "EnemyAreaW", "number", "900")
    ensure_scene_var(scene, "EnemyAreaH", "number", "650")

    events = scene.get("events")
    if not isinstance(events, list):
        return

    # Prevent duplicates
    if any(isinstance(e, dict) and e.get("comment") == "FACTORY_V3_1_BOOT" for e in events):
        return

    # BOOT: set camera follow + anchor UI positions relative to camera
    events.append(
        {
            "comment": "FACTORY_V3_1_BOOT",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                # Camera follows Player (layer "")
                {"type": "BuiltinCommonInstructions::CameraCenterOnObject", "parameters": ["", "Player", "0", "0"]},
                # HUD text init shows Coins/HP
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP))"]},
                # Spawn initial coin/enemy inside area
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(Variable(CoinAreaX), Variable(CoinAreaX)+Variable(CoinAreaW))"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(Variable(CoinAreaY), Variable(CoinAreaY)+Variable(CoinAreaH))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy", "RandomInRange(Variable(EnemyAreaX), Variable(EnemyAreaX)+Variable(EnemyAreaW))"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy", "RandomInRange(Variable(EnemyAreaY), Variable(EnemyAreaY)+Variable(EnemyAreaH))"]},
            ],
            "events": [],
        }
    )

    # EVERY FRAME: camera lerp to player + UI anchor recalculation
    # (Simple approach: keep HUD and joystick at camera top-left/bottom-left positions)
    events.append(
        {
            "comment": "FACTORY_V3_1_CAMERA_UI",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                # Camera smooth follow
                {
                    "type": "BuiltinCommonInstructions::SetCameraX",
                    "parameters": ["", "CameraX(\"\") + (" + _f(pack.camera.lerp) + ")*(Player.X()-CameraX(\"\"))"],
                },
                {
                    "type": "BuiltinCommonInstructions::SetCameraY",
                    "parameters": ["", "CameraY(\"\") + (" + _f(pack.camera.lerp) + ")*(Player.Y()-CameraY(\"\"))"],
                },

                # UI anchoring:
                # Top-left HUD: camera position + offset
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["HUD", "CameraX(\"\") - " + str(pack.display.virtualWidth//2) + " + " + str(pack.ui.hud.marginX)]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["HUD", "CameraY(\"\") - " + str(pack.display.virtualHeight//2) + " + " + str(pack.ui.hud.marginY)]},

                # Bottom-left joystick: camera pos + offset from bottom
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["TouchJoystick", "CameraX(\"\") - " + str(pack.display.virtualWidth//2) + " + " + str(pack.ui.joystick.marginX)]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["TouchJoystick", "CameraY(\"\") + " + str(pack.display.virtualHeight//2) + " - " + str(pack.ui.joystick.marginY)]},
            ],
            "events": [],
        }
    )

    # Clamp player to world bounds
    b = pack.worldBounds
    events.append(
        {
            "comment": "FACTORY_V3_1_CLAMP",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Player", f"clamp(Player.X(), {b.xMin}, {b.xMax})"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Player", f"clamp(Player.Y(), {b.yMin}, {b.yMax})"]},
            ],
            "events": [],
        }
    )

    # Coin collect -> Coins++ and respawn within area, update HUD
    events.append(
        {
            "comment": "FACTORY_V3_1_COIN_COLLECT",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Coin"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Coins", "=", "Variable(Coins)+1"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(Variable(CoinAreaX), Variable(CoinAreaX)+Variable(CoinAreaW))"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(Variable(CoinAreaY), Variable(CoinAreaY)+Variable(CoinAreaH))"]},
            ],
            "events": [],
        }
    )

    # Enemy collision -> HP--, reset player, update HUD
    events.append(
        {
            "comment": "FACTORY_V3_1_ENEMY_HIT",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Enemy"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "max(0, Variable(HP)-1)"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Coins: \" + ToString(Variable(Coins)) + \"  HP: \" + ToString(Variable(HP))"]},
                {"type": "BuiltinCommonInstructions::SetObjectPosition", "parameters": ["Player", "200", "240"]},
            ],
            "events": [],
        }
    )


def ensure_global_var(project: Dict[str, Any], name: str, vtype: str, value: str) -> None:
    vars_ = project.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        project["variables"] = vars_
    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            v["type"] = vtype
            v["value"] = value
            v.setdefault("children", [])
            return
    vars_.append({"name": name, "type": vtype, "value": value, "children": []})


def ensure_scene_var(scene: Dict[str, Any], name: str, vtype: str, value: str) -> None:
    vars_ = scene.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        scene["variables"] = vars_
    for v in vars_:
        if isinstance(v, dict) and v.get("name") == name:
            v["type"] = vtype
            v["value"] = value
            v.setdefault("children", [])
            return
    vars_.append({"name": name, "type": vtype, "value": value, "children": []})


def _f(x: float) -> str:
    # stable formatting for GDevelop expressions
    return f"{x:.4f}"
