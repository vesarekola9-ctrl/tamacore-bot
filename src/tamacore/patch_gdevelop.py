from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import read_json, write_json

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def copy_assets_into_game(assets_dir: Path, game_dir: Path) -> Dict[str, str]:
    out_dir = game_dir / "assets" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping: Dict[str, str] = {}
    for p in sorted(assets_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMG_EXTS:
            continue
        dst = out_dir / p.name
        shutil.copy2(p, dst)
        mapping[p.stem.lower()] = "assets/generated/" + dst.name
    return mapping


def patch_project(game_json_path: Path, image_map: Dict[str, str]) -> None:
    project = read_json(game_json_path)

    _upsert_resources(project, image_map)

    scene = _get_scene(project, preferred_name="Main")
    if scene is None:
        write_json(game_json_path, project)
        return

    _ensure_ui_layer(scene)

    # Ensure core objects exist (UI buttons/texts + enemy placeholder)
    _ensure_objects(scene, project)

    # Ensure instances are positioned/layered
    _ensure_instances(scene)

    # Ensure Player controls: keyboard + touch mapper
    _ensure_player_controls(scene)

    # Ensure variables & events: score, stamina, hp, highscore, pause, gameover, camera, bounds, enemy
    _ensure_variables(scene)
    _ensure_events(scene)

    write_json(game_json_path, project)


# ---------------- helpers: scene/template ----------------

def _get_scene(project: Dict[str, Any], preferred_name: str) -> Optional[Dict[str, Any]]:
    layouts = project.get("layouts", [])
    if not isinstance(layouts, list) or not layouts:
        return None
    for l in layouts:
        if isinstance(l, dict) and l.get("name") == preferred_name:
            return l
    return layouts[0] if isinstance(layouts[0], dict) else None


def _ensure_ui_layer(scene: Dict[str, Any]) -> None:
    layers = scene.get("layers")
    if not isinstance(layers, list):
        layers = []
        scene["layers"] = layers
    if not any(isinstance(l, dict) and l.get("name") == "UI" for l in layers):
        layers.append({"name": "UI", "visibility": True, "effects": []})


def _scene_objects(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    objs = scene.get("objects")
    if not isinstance(objs, list):
        objs = []
        scene["objects"] = objs
    return objs


def _find_object(scene: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    for o in _scene_objects(scene):
        if isinstance(o, dict) and o.get("name") == name:
            return o
    return None


def _instances(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    inst = scene.get("instances")
    if not isinstance(inst, list):
        inst = []
        scene["instances"] = inst
    return inst


def _find_instance(scene: Dict[str, Any], object_name: str) -> Optional[Dict[str, Any]]:
    for i in _instances(scene):
        if not isinstance(i, dict):
            continue
        if i.get("objectName") == object_name or i.get("name") == object_name:
            return i
    return None


def _ensure_instance(scene: Dict[str, Any], object_name: str, x: int, y: int, layer: str, z: int) -> Dict[str, Any]:
    inst = _find_instance(scene, object_name)
    if inst is None:
        inst = {
            "objectName": object_name,
            "name": object_name,
            "x": x,
            "y": y,
            "angle": 0,
            "layer": layer,
            "zOrder": z,
        }
        _instances(scene).append(inst)
    else:
        inst["layer"] = layer
        inst["zOrder"] = z
        inst.setdefault("angle", 0)
    return inst


# ---------------- resources ----------------

def _upsert_resources(project: Dict[str, Any], image_map: Dict[str, str]) -> None:
    project.setdefault("resources", {})
    res_root = project["resources"]
    if not isinstance(res_root, dict):
        project["resources"] = {}
        res_root = project["resources"]

    res_list = res_root.get("resources")
    if not isinstance(res_list, list):
        res_list = []
        res_root["resources"] = res_list

    res_root.setdefault("resourceFolders", [])
    res_root.setdefault("resourcesFolderStructure", {"folderName": "__ROOT"})

    for name, rel in image_map.items():
        _upsert_image_resource(res_list, name=name, rel_path=rel)


def _upsert_image_resource(res_list: List[Dict[str, Any]], name: str, rel_path: str) -> None:
    for r in res_list:
        if isinstance(r, dict) and r.get("name") == name:
            r["kind"] = "image"
            r["file"] = rel_path
            r.setdefault("metadata", "")
            r.setdefault("userAdded", True)
            r.setdefault("alwaysLoaded", False)
            r.setdefault("smoothed", True)
            return
    res_list.append(
        {
            "name": name,
            "kind": "image",
            "file": rel_path,
            "metadata": "",
            "userAdded": True,
            "alwaysLoaded": False,
            "smoothed": True,
        }
    )


# ---------------- behaviors (Anchor + controls) ----------------

def _detect_anchor_behavior_type(project: Dict[str, Any]) -> str:
    # If anchor exists anywhere, reuse its type string.
    layouts = project.get("layouts", [])
    if isinstance(layouts, list):
        for l in layouts:
            if not isinstance(l, dict):
                continue
            objs = l.get("objects")
            if not isinstance(objs, list):
                continue
            for o in objs:
                if not isinstance(o, dict):
                    continue
                beh = o.get("behaviors")
                if not isinstance(beh, list):
                    continue
                for b in beh:
                    if isinstance(b, dict) and "Anchor" in str(b.get("type", "")):
                        t = b.get("type")
                        if isinstance(t, str) and t.strip():
                            return t
    return "AnchorBehavior::AnchorBehavior"


def _ensure_anchor(obj: Dict[str, Any], name: str, anchor_type: str,
                   top: str, left: str, bottom: str, right: str) -> None:
    behaviors = obj.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        obj["behaviors"] = behaviors

    if any(isinstance(b, dict) and b.get("name") == name for b in behaviors):
        return

    behaviors.append(
        {
            "name": name,
            "type": anchor_type,
            "topEdgeAnchor": top,
            "leftEdgeAnchor": left,
            "rightEdgeAnchor": right,
            "bottomEdgeAnchor": bottom,
            "relativeToOriginalWindowSize": True,
            "useLegacyBottomAndRightAnchors": False,
        }
    )


def _ensure_player_controls(scene: Dict[str, Any]) -> None:
    player = _find_object(scene, "Player")
    if player is None:
        return

    behaviors = player.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
        player["behaviors"] = behaviors

    def has(n: str) -> bool:
        return any(isinstance(b, dict) and b.get("name") == n for b in behaviors)

    # TopDownMovement
    if not has("TopDownMovement"):
        behaviors.append(
            {
                "name": "TopDownMovement",
                "type": "TopDownMovementBehavior::TopDownMovementBehavior",
                "allowDiagonals": True,
                "acceleration": 1000,
                "deceleration": 1200,
                "maxSpeed": 300,
                "angularMaxSpeed": 0,
                "rotateObject": False,
                "ignoreDefaultControls": False,  # keyboard ON by default
                "defaultControls": True,
            }
        )

    # Touch mapper (SpriteMultitouchJoystick extension must exist in template)
    if not has("TouchMapper"):
        behaviors.append(
            {
                "name": "TouchMapper",
                "type": "SpriteMultitouchJoystick::TopDownMultitouchMapper",
                "ControllerIdentifier": 1,
                "JoystickIdentifier": "Primary",
                "StickMode": "Analog",
                "TopDownMovement": "TopDownMovement",
            }
        )


# ---------------- object creation ----------------

def _ensure_objects(scene: Dict[str, Any], project: Dict[str, Any]) -> None:
    """
    Create missing UI objects + Enemy placeholder.
    We keep it lightweight: Text objects for UI; Enemy uses existing 'coin' image if available.
    """
    anchor_type = _detect_anchor_behavior_type(project)

    # HUD text should already exist in your template, but ensure it.
    if _find_object(scene, "HUD") is None:
        _scene_objects(scene).append(
            {
                "name": "HUD",
                "type": "Text",
                "string": "Score: 0  |  High: 0",
                "fontSize": 28,
                "bold": True,
                "italic": False,
                "underlined": False,
                "smoothed": True,
                "font": "",
                "color": {"r": 245, "g": 245, "b": 250},
                "behaviors": [],
                "effects": [],
            }
        )

    hud = _find_object(scene, "HUD")
    if hud is not None:
        _ensure_anchor(hud, "AnchorHUD", anchor_type, "WindowTop", "WindowLeft", "None", "None")

    # Pause button top-right
    if _find_object(scene, "PauseBtn") is None:
        obj = {
            "name": "PauseBtn",
            "type": "Text",
            "string": "II",
            "fontSize": 42,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        }
        _ensure_anchor(obj, "AnchorPauseBtn", anchor_type, "WindowTop", "None", "None", "WindowRight")
        _scene_objects(scene).append(obj)

    # Resume button center (UI)
    if _find_object(scene, "ResumeBtn") is None:
        obj = {
            "name": "ResumeBtn",
            "type": "Text",
            "string": "RESUME",
            "fontSize": 44,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)

    # GameOver text
    if _find_object(scene, "GameOverTxt") is None:
        obj = {
            "name": "GameOverTxt",
            "type": "Text",
            "string": "GAME OVER",
            "fontSize": 64,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 70, "b": 70},
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)

    # Restart button
    if _find_object(scene, "RestartBtn") is None:
        obj = {
            "name": "RestartBtn",
            "type": "Text",
            "string": "RESTART",
            "fontSize": 44,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)

    # Sprint button bottom-right
    if _find_object(scene, "SprintBtn") is None:
        obj = {
            "name": "SprintBtn",
            "type": "Text",
            "string": "SPRINT",
            "fontSize": 36,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)

    # Stamina text bottom-left (above joystick area)
    if _find_object(scene, "StaminaTxt") is None:
        obj = {
            "name": "StaminaTxt",
            "type": "Text",
            "string": "STA: 100",
            "fontSize": 26,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": {"r": 245, "g": 245, "b": 250},
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)

    # Enemy sprite (use coin image if exists; else player; else just create sprite with missing image ref and user can swap)
    if _find_object(scene, "Enemy") is None:
        enemy_image = "coin"
        # We can only reference resource names; pick safest existing among your usual names.
        # If coin doesn't exist, GDevelop will show missing image but still lets you set later.
        obj = {
            "name": "Enemy",
            "type": "Sprite",
            "updateIfNotVisible": False,
            "animations": [
                {
                    "name": "Idle",
                    "directionType": "LeftRight",
                    "useMultipleDirections": False,
                    "loop": True,
                    "speed": 5,
                    "directions": [
                        {
                            "sprites": [
                                {
                                    "image": enemy_image,
                                    "originPoint": {"x": 0, "y": 0},
                                    "centerPoint": {"x": 0, "y": 0},
                                    "points": [],
                                    "hasCustomCollisionMask": False,
                                    "customCollisionMask": [],
                                }
                            ]
                        }
                    ],
                }
            ],
            "behaviors": [],
            "effects": [],
        }
        _scene_objects(scene).append(obj)


def _ensure_instances(scene: Dict[str, Any]) -> None:
    # HUD top-left
    _ensure_instance(scene, "HUD", x=20, y=20, layer="UI", z=2000)

    # Pause top-right (place roughly, anchor handles)
    _ensure_instance(scene, "PauseBtn", x=920, y=20, layer="UI", z=2001)

    # Sprint bottom-right
    _ensure_instance(scene, "SprintBtn", x=820, y=520, layer="UI", z=2001)

    # Stamina bottom-left-ish
    _ensure_instance(scene, "StaminaTxt", x=20, y=520, layer="UI", z=2001)

    # Centered menu items (we toggle visibility via events)
    _ensure_instance(scene, "ResumeBtn", x=420, y=220, layer="UI", z=3000)
    _ensure_instance(scene, "GameOverTxt", x=320, y=180, layer="UI", z=3001)
    _ensure_instance(scene, "RestartBtn", x=420, y=300, layer="UI", z=3002)

    # Enemy spawn start (will be moved by events)
    _ensure_instance(scene, "Enemy", x=700, y=260, layer="", z=5)


# ---------------- variables ----------------

def _ensure_variables(scene: Dict[str, Any]) -> None:
    vars_ = scene.get("variables")
    if not isinstance(vars_, list):
        vars_ = []
        scene["variables"] = vars_

    def has(n: str) -> bool:
        return any(isinstance(v, dict) and v.get("name") == n for v in vars_)

    def add_num(name: str, value: str) -> None:
        vars_.append({"name": name, "type": "number", "value": value, "children": []})

    if not has("Score"):
        add_num("Score", "0")
    if not has("HighScore"):
        add_num("HighScore", "0")
    if not has("HP"):
        add_num("HP", "3")
    if not has("Paused"):
        add_num("Paused", "0")
    if not has("GameOver"):
        add_num("GameOver", "0")
    if not has("Stamina"):
        add_num("Stamina", "100")
    if not has("IsSprinting"):
        add_num("IsSprinting", "0")


# ---------------- events ----------------

def _events(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    ev = scene.get("events")
    if not isinstance(ev, list):
        ev = []
        scene["events"] = ev
    return ev


def _ensure_events(scene: Dict[str, Any]) -> None:
    evs = _events(scene)

    # avoid duplicating our block
    if any(isinstance(e, dict) and e.get("name") == "TAMACORE_AUTOGEN_V1" for e in evs):
        return

    block: Dict[str, Any] = {
        "type": "BuiltinCommonInstructions::Group",
        "name": "TAMACORE_AUTOGEN_V1",
        "events": [],
    }

    # --- INIT (load highscore, reset vars, hide menus) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                # Load highscore (Storage). If storage ext missing, it will simply do nothing in editor until you add it.
                {"type": "Storage::ReadNumber", "parameters": ["tamacore", "highscore", "HighScore"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "3"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameOver", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "100"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["IsSprinting", "=", "0"]},
                # Hide menu texts initially (use opacity as "visibility" fallback)
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: 0 | High: \" + ToString(Variable(HighScore)) + \" | HP: 3\""]},
                {"type": "TextObject::SetString", "parameters": ["StaminaTxt", "\"STA: 100\""]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["ResumeBtn", "0"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["GameOverTxt", "0"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["RestartBtn", "0"]},
            ],
            "events": [],
        }
    )

    # --- PAUSE TOGGLE (PauseBtn click/touch) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["PauseBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Paused", "=", "1 - Variable(Paused)"]},
            ],
            "events": [],
        }
    )

    # When paused: disable movement + show Resume
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "1"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TouchMapper"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["ResumeBtn", "255"]},
            ],
            "events": [],
        }
    )

    # When unpaused: enable movement + hide Resume (if not gameover)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TouchMapper"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["ResumeBtn", "0"]},
            ],
            "events": [],
        }
    )

    # Resume click
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ResumeBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "1"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Paused", "=", "0"]},
            ],
            "events": [],
        }
    )

    # --- SPRINT (hold click/touch on SprintBtn) ---
    # If pressed and stamina > 0 => sprinting
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["SprintBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Stamina", ">", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["IsSprinting", "=", "1"]},
                # drain stamina
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "max(0, Variable(Stamina) - 60 * TimeDelta())"]},
            ],
            "events": [],
        }
    )

    # If not pressed => not sprinting (regen stamina)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["IsSprinting", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "min(100, Variable(Stamina) + 30 * TimeDelta())"]},
                {"type": "TextObject::SetString", "parameters": ["StaminaTxt", "\"STA: \" + ToString(floor(Variable(Stamina)))"]},
            ],
            "events": [],
        }
    )

    # Apply sprint speed (if sprinting)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["IsSprinting", "=", "1"]}],
            "actions": [
                {"type": "TopDownMovementBehavior::SetMaxSpeed", "parameters": ["Player", "TopDownMovement", "520"]},
            ],
            "events": [],
        }
    )
    # Normal speed (if not sprinting)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["IsSprinting", "=", "0"]}],
            "actions": [
                {"type": "TopDownMovementBehavior::SetMaxSpeed", "parameters": ["Player", "TopDownMovement", "300"]},
            ],
            "events": [],
        }
    )

    # --- BOUNDS clamp (keep player within playfield) ---
    # Use a simple fixed playfield size that matches your current template-ish.
    # You can later parameterize this.
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Player", "clamp(Player.X(), 0, 960)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Player", "clamp(Player.Y(), 0, 540)"]},
            ],
            "events": [],
        }
    )

    # --- CAMERA follow Player ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "Scene::CenterCameraOnObject", "parameters": ["Player", "", "0", "0"]},
            ],
            "events": [],
        }
    )

    # --- COIN collect (score++) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
                {"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Coin"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "Variable(Score) + 1"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score)) + \" | High: \" + ToString(Variable(HighScore)) + \" | HP: \" + ToString(Variable(HP))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(80, 900)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(120, 520)"]},
            ],
            "events": [],
        }
    )

    # --- ENEMY basic chase + damage ---
    # Make enemy slowly move toward player.
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetObjectAngle", "parameters": ["Enemy", "AngleBetweenPositions(Enemy.X(), Enemy.Y(), Player.X(), Player.Y())"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy", "Enemy.X() + cos(Enemy.Angle()) * 60 * TimeDelta()"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy", "Enemy.Y() + sin(Enemy.Angle()) * 60 * TimeDelta()"]},
            ],
            "events": [],
        }
    )

    # Collision Player/Enemy => HP-- (trigger once)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
                {"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Enemy"]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "max(0, Variable(HP) - 1)"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score)) + \" | High: \" + ToString(Variable(HighScore)) + \" | HP: \" + ToString(Variable(HP))"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy", "RandomInRange(80, 900)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy", "RandomInRange(120, 520)"]},
            ],
            "events": [],
        }
    )

    # --- GAME OVER handling ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["HP", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameOver", "=", "1"]},
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TouchMapper"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["GameOverTxt", "255"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["RestartBtn", "255"]},
                # update highscore if needed
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HighScore", "=", "max(Variable(HighScore), Variable(Score))"]},
                {"type": "Storage::WriteNumber", "parameters": ["tamacore", "highscore", "Variable(HighScore)"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: \" + ToString(Variable(Score)) + \" | High: \" + ToString(Variable(HighScore)) + \" | HP: \" + ToString(Variable(HP))"]},
            ],
            "events": [],
        }
    )

    # Restart click
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["RestartBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameOver", "=", "1"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "3"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Paused", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameOver", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["GameOverTxt", "0"]},
                {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": ["RestartBtn", "0"]},
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TouchMapper"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Player", "200"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Player", "240"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy", "700"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy", "260"]},
                {"type": "TextObject::SetString", "parameters": ["HUD", "\"Score: 0 | High: \" + ToString(Variable(HighScore)) + \" | HP: 3\""]},
            ],
            "events": [],
        }
    )

    evs.append(block)
