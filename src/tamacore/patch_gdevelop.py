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

    # Ensure objects + instances exist
    _ensure_objects(scene, project)
    _ensure_instances(scene)

    # Ensure controls
    _ensure_player_controls(scene)

    # Ensure variables + events
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
        inst.setdefault("angle", 0)
        inst["layer"] = layer
        inst["zOrder"] = z
        inst.setdefault("x", x)
        inst.setdefault("y", y)
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


# ---------------- behaviors ----------------

def _detect_anchor_behavior_type(project: Dict[str, Any]) -> str:
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
                "ignoreDefaultControls": False,  # keyboard ON
                "defaultControls": True,
            }
        )

    # Touch mapper (requires SpriteMultitouchJoystick extension in template)
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
    HUD + Menus + Settings + Pause/Shop + Enemies
    (Text-only UI to avoid needing extra assets)
    """
    anchor_type = _detect_anchor_behavior_type(project)

    def ensure_text(name: str, text: str, size: int, color: Dict[str, int], anchor: Optional[Dict[str, str]] = None) -> None:
        if _find_object(scene, name) is not None:
            return
        obj: Dict[str, Any] = {
            "name": name,
            "type": "Text",
            "string": text,
            "fontSize": size,
            "bold": True,
            "italic": False,
            "underlined": False,
            "smoothed": True,
            "font": "",
            "color": color,
            "behaviors": [],
            "effects": [],
        }
        if anchor:
            _ensure_anchor(
                obj,
                anchor.get("behaviorName", f"Anchor_{name}"),
                anchor_type,
                anchor.get("top", "None"),
                anchor.get("left", "None"),
                anchor.get("bottom", "None"),
                anchor.get("right", "None"),
            )
        _scene_objects(scene).append(obj)

    # --- HUD (top-left) ---
    ensure_text(
        "HUD",
        "Score: 0 | High: 0",
        28,
        {"r": 245, "g": 245, "b": 250},
        anchor={"behaviorName": "AnchorHUD", "top": "WindowTop", "left": "WindowLeft", "bottom": "None", "right": "None"},
    )
    ensure_text(
        "HPHud",
        "HP: 3",
        26,
        {"r": 245, "g": 245, "b": 250},
        anchor={"behaviorName": "AnchorHP", "top": "WindowTop", "left": "WindowLeft", "bottom": "None", "right": "None"},
    )
    ensure_text(
        "StaminaHud",
        "STA: 100%",
        24,
        {"r": 245, "g": 245, "b": 250},
        anchor={"behaviorName": "AnchorSTA", "top": "WindowTop", "left": "WindowLeft", "bottom": "None", "right": "None"},
    )
    ensure_text(
        "StaminaBar",
        "██████████",
        22,
        {"r": 90, "g": 220, "b": 120},
        anchor={"behaviorName": "AnchorSTABAR", "top": "WindowTop", "left": "WindowLeft", "bottom": "None", "right": "None"},
    )

    # --- Overlay (pause/menu) ---
    ensure_text("OverlayDim", "████████████████████████████", 80, {"r": 0, "g": 0, "b": 0})
    ensure_text("TitleTxt", "TamaCore", 72, {"r": 245, "g": 245, "b": 250})
    ensure_text("StartBtn", "START", 54, {"r": 245, "g": 245, "b": 250})
    ensure_text("SettingsBtn", "SETTINGS", 44, {"r": 245, "g": 245, "b": 250})
    ensure_text("BackBtn", "BACK", 44, {"r": 245, "g": 245, "b": 250})
    ensure_text("SoundBtn", "SOUND: ON", 40, {"r": 245, "g": 245, "b": 250})
    ensure_text("VibeBtn", "VIBRATION: ON", 40, {"r": 245, "g": 245, "b": 250})

    # --- Pause + Shop ---
    ensure_text(
        "PauseBtn",
        "II",
        42,
        {"r": 245, "g": 245, "b": 250},
        anchor={"behaviorName": "AnchorPause", "top": "WindowTop", "left": "None", "bottom": "None", "right": "WindowRight"},
    )
    ensure_text("ResumeBtn", "RESUME", 48, {"r": 245, "g": 245, "b": 250})
    ensure_text("ShopBtn", "SHOP", 44, {"r": 245, "g": 245, "b": 250})
    ensure_text("Upgrade1Btn", "+HP (cost 10)", 36, {"r": 245, "g": 245, "b": 250})
    ensure_text("Upgrade2Btn", "+Max STA (cost 10)", 36, {"r": 245, "g": 245, "b": 250})
    ensure_text("Upgrade3Btn", "+Speed (cost 10)", 36, {"r": 245, "g": 245, "b": 250})
    ensure_text("ShopBackBtn", "BACK", 40, {"r": 245, "g": 245, "b": 250})

    # --- Game Over ---
    ensure_text("GameOverTxt", "GAME OVER", 64, {"r": 245, "g": 70, "b": 70})
    ensure_text("RestartBtn", "RESTART", 48, {"r": 245, "g": 245, "b": 250})

    # --- Sprint button (bottom-right) ---
    ensure_text("SprintBtn", "SPRINT", 34, {"r": 245, "g": 245, "b": 250})

    # --- Enemy sprites (use coin resource name by default; ok if missing image, user can swap later) ---
    if _find_object(scene, "Enemy") is None:
        _scene_objects(scene).append(_make_enemy_sprite("Enemy", image_name="coin"))
    if _find_object(scene, "Enemy2") is None:
        _scene_objects(scene).append(_make_enemy_sprite("Enemy2", image_name="coin"))
    if _find_object(scene, "Enemy3") is None:
        _scene_objects(scene).append(_make_enemy_sprite("Enemy3", image_name="coin"))


def _make_enemy_sprite(name: str, image_name: str) -> Dict[str, Any]:
    return {
        "name": name,
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
                                "image": image_name,
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


def _ensure_instances(scene: Dict[str, Any]) -> None:
    # HUD cluster (top-left stack)
    _ensure_instance(scene, "HUD", 20, 20, "UI", 2000)
    _ensure_instance(scene, "HPHud", 20, 55, "UI", 2000)
    _ensure_instance(scene, "StaminaHud", 20, 88, "UI", 2000)
    _ensure_instance(scene, "StaminaBar", 20, 118, "UI", 2000)

    # Pause + Sprint
    _ensure_instance(scene, "PauseBtn", 920, 18, "UI", 2100)
    _ensure_instance(scene, "SprintBtn", 820, 520, "UI", 2100)

    # Menu overlay + buttons (centered-ish; we toggle opacity)
    _ensure_instance(scene, "OverlayDim", 0, 0, "UI", 2900)
    _ensure_instance(scene, "TitleTxt", 320, 110, "UI", 3000)
    _ensure_instance(scene, "StartBtn", 420, 220, "UI", 3000)
    _ensure_instance(scene, "SettingsBtn", 390, 300, "UI", 3000)

    _ensure_instance(scene, "BackBtn", 420, 460, "UI", 3000)
    _ensure_instance(scene, "SoundBtn", 340, 230, "UI", 3000)
    _ensure_instance(scene, "VibeBtn", 300, 300, "UI", 3000)

    # Pause overlay buttons
    _ensure_instance(scene, "ResumeBtn", 420, 220, "UI", 3050)
    _ensure_instance(scene, "ShopBtn", 440, 290, "UI", 3050)

    # Shop
    _ensure_instance(scene, "Upgrade1Btn", 360, 210, "UI", 3060)
    _ensure_instance(scene, "Upgrade2Btn", 300, 270, "UI", 3060)
    _ensure_instance(scene, "Upgrade3Btn", 330, 330, "UI", 3060)
    _ensure_instance(scene, "ShopBackBtn", 420, 420, "UI", 3060)

    # Game over
    _ensure_instance(scene, "GameOverTxt", 290, 180, "UI", 3100)
    _ensure_instance(scene, "RestartBtn", 420, 300, "UI", 3100)

    # Enemies (layer base)
    _ensure_instance(scene, "Enemy", 700, 260, "", 10)
    _ensure_instance(scene, "Enemy2", 2000, 2000, "", 10)  # start offscreen
    _ensure_instance(scene, "Enemy3", 2000, 2000, "", 10)


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

    # Game state:
    # 0 = MainMenu, 1 = Playing, 2 = Paused, 3 = Settings, 4 = Shop, 5 = GameOver
    if not has("GameState"):
        add_num("GameState", "0")

    if not has("Score"):
        add_num("Score", "0")
    if not has("HighScore"):
        add_num("HighScore", "0")

    if not has("HP"):
        add_num("HP", "3")
    if not has("MaxHP"):
        add_num("MaxHP", "3")

    if not has("Stamina"):
        add_num("Stamina", "100")
    if not has("MaxStamina"):
        add_num("MaxStamina", "100")

    if not has("IsSprinting"):
        add_num("IsSprinting", "0")

    if not has("EnemySpeed"):
        add_num("EnemySpeed", "60")

    # Settings
    if not has("SoundOn"):
        add_num("SoundOn", "1")
    if not has("VibrationOn"):
        add_num("VibrationOn", "1")


# ---------------- events ----------------

def _events(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    ev = scene.get("events")
    if not isinstance(ev, list):
        ev = []
        scene["events"] = ev
    return ev


def _ensure_events(scene: Dict[str, Any]) -> None:
    evs = _events(scene)

    if any(isinstance(e, dict) and e.get("name") == "TAMACORE_AUTOGEN_V2" for e in evs):
        return

    # Helpers: show/hide sets via opacity
    def set_op(name: str, op: int) -> Dict[str, Any]:
        return {"type": "BuiltinCommonInstructions::SetObjectOpacity", "parameters": [name, str(op)]}

    def hud_update_expr() -> str:
        return "\"Score: \" + ToString(Variable(Score)) + \" | High: \" + ToString(Variable(HighScore))"

    def hp_update_expr() -> str:
        return "\"HP: \" + ToString(Variable(HP)) + \"/\" + ToString(Variable(MaxHP))"

    def sta_percent_expr() -> str:
        return "floor(100 * Variable(Stamina) / max(1, Variable(MaxStamina)))"

    def sta_text_expr() -> str:
        return "\"STA: \" + ToString(" + sta_percent_expr() + ") + \"%\""

    def sta_bar_expr() -> str:
        # 10 blocks
        return (
            "SubStr(\"██████████\", 0, floor(10*Variable(Stamina)/max(1,Variable(MaxStamina))))"
            " + SubStr(\"..........\", 0, 10-floor(10*Variable(Stamina)/max(1,Variable(MaxStamina))))"
        )

    block: Dict[str, Any] = {
        "type": "BuiltinCommonInstructions::Group",
        "name": "TAMACORE_AUTOGEN_V2",
        "events": [],
    }

    # --- INIT (load settings + highscore, go menu) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Once"}],
            "actions": [
                {"type": "Storage::ReadNumber", "parameters": ["tamacore", "highscore", "HighScore"]},
                {"type": "Storage::ReadNumber", "parameters": ["tamacore", "sound", "SoundOn"]},
                {"type": "Storage::ReadNumber", "parameters": ["tamacore", "vibration", "VibrationOn"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["SoundOn", "=", "max(0, min(1, Variable(SoundOn)))"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["VibrationOn", "=", "max(0, min(1, Variable(VibrationOn)))"]},

                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["MaxHP", "=", "3"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "Variable(MaxHP)"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["MaxStamina", "=", "100"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "Variable(MaxStamina)"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["EnemySpeed", "=", "60"]},

                {"type": "TextObject::SetString", "parameters": ["HUD", hud_update_expr()]},
                {"type": "TextObject::SetString", "parameters": ["HPHud", hp_update_expr()]},
                {"type": "TextObject::SetString", "parameters": ["StaminaHud", sta_text_expr()]},
                {"type": "TextObject::SetString", "parameters": ["StaminaBar", sta_bar_expr()]},

                # Default: show main menu overlay
                set_op("OverlayDim", 180),
                set_op("TitleTxt", 255),
                set_op("StartBtn", 255),
                set_op("SettingsBtn", 255),

                # Hide settings
                set_op("SoundBtn", 0),
                set_op("VibeBtn", 0),
                set_op("BackBtn", 0),

                # Hide pause/shop
                set_op("ResumeBtn", 0),
                set_op("ShopBtn", 0),
                set_op("Upgrade1Btn", 0),
                set_op("Upgrade2Btn", 0),
                set_op("Upgrade3Btn", 0),
                set_op("ShopBackBtn", 0),

                # Hide gameover
                set_op("GameOverTxt", 0),
                set_op("RestartBtn", 0),
            ],
            "events": [],
        }
    )

    # --- UI text reflect toggles (each frame) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "TextObject::SetString", "parameters": ["SoundBtn", "\"SOUND: \" + (Variable(SoundOn)=1?\"ON\":\"OFF\")"]},
                {"type": "TextObject::SetString", "parameters": ["VibeBtn", "\"VIBRATION: \" + (Variable(VibrationOn)=1?\"ON\":\"OFF\")"]},
            ],
            "events": [],
        }
    )

    # --- MAIN MENU: Start click ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "0"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["StartBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "1"]},
                set_op("OverlayDim", 0),
                set_op("TitleTxt", 0),
                set_op("StartBtn", 0),
                set_op("SettingsBtn", 0),
                # reset run
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "Variable(MaxHP)"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "Variable(MaxStamina)"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Player", "200"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Player", "240"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy", "700"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy", "260"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy2", "2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy2", "2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy3", "2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy3", "2000"]},
            ],
            "events": [],
        }
    )

    # --- MAIN MENU: Settings click ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "0"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["SettingsBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "3"]},
                # hide menu buttons, show settings
                set_op("TitleTxt", 255),
                set_op("StartBtn", 0),
                set_op("SettingsBtn", 0),
                set_op("SoundBtn", 255),
                set_op("VibeBtn", 255),
                set_op("BackBtn", 255),
            ],
            "events": [],
        }
    )

    # --- SETTINGS: toggle sound ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "3"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["SoundBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["SoundOn", "=", "1-Variable(SoundOn)"]},
                {"type": "Storage::WriteNumber", "parameters": ["tamacore", "sound", "Variable(SoundOn)"]},
            ],
            "events": [],
        }
    )

    # --- SETTINGS: toggle vibration ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "3"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["VibeBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["VibrationOn", "=", "1-Variable(VibrationOn)"]},
                {"type": "Storage::WriteNumber", "parameters": ["tamacore", "vibration", "Variable(VibrationOn)"]},
            ],
            "events": [],
        }
    )

    # --- SETTINGS: back ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "3"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["BackBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "0"]},
                set_op("SoundBtn", 0),
                set_op("VibeBtn", 0),
                set_op("BackBtn", 0),
                set_op("StartBtn", 255),
                set_op("SettingsBtn", 255),
            ],
            "events": [],
        }
    )

    # --- PAUSE toggle (only while playing) ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["PauseBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "2"]},
                set_op("OverlayDim", 180),
                set_op("ResumeBtn", 255),
                set_op("ShopBtn", 255),
            ],
            "events": [],
        }
    )

    # --- RESUME ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "2"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ResumeBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "1"]},
                set_op("OverlayDim", 0),
                set_op("ResumeBtn", 0),
                set_op("ShopBtn", 0),
                # hide shop if open
                set_op("Upgrade1Btn", 0),
                set_op("Upgrade2Btn", 0),
                set_op("Upgrade3Btn", 0),
                set_op("ShopBackBtn", 0),
            ],
            "events": [],
        }
    )

    # --- SHOP open ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "2"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ShopBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "4"]},
                set_op("ResumeBtn", 0),
                set_op("ShopBtn", 0),
                set_op("Upgrade1Btn", 255),
                set_op("Upgrade2Btn", 255),
                set_op("Upgrade3Btn", 255),
                set_op("ShopBackBtn", 255),
            ],
            "events": [],
        }
    )

    # --- SHOP back ---
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "4"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["ShopBackBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "2"]},
                set_op("Upgrade1Btn", 0),
                set_op("Upgrade2Btn", 0),
                set_op("Upgrade3Btn", 0),
                set_op("ShopBackBtn", 0),
                set_op("ResumeBtn", 255),
                set_op("ShopBtn", 255),
            ],
            "events": [],
        }
    )

    # --- SHOP: upgrades (cost 10 score) ---
    def upgrade_event(btn: str, action_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "4"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Score", ">=", "10"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": [btn, "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "Variable(Score) - 10"]},
                *action_list,
            ],
            "events": [],
        }

    block["events"].append(
        upgrade_event(
            "Upgrade1Btn",
            [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["MaxHP", "=", "Variable(MaxHP) + 1"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "Variable(MaxHP)"]},
            ],
        )
    )
    block["events"].append(
        upgrade_event(
            "Upgrade2Btn",
            [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["MaxStamina", "=", "Variable(MaxStamina) + 20"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "Variable(MaxStamina)"]},
            ],
        )
    )
    block["events"].append(
        upgrade_event(
            "Upgrade3Btn",
            [
                {"type": "TopDownMovementBehavior::SetMaxSpeed", "parameters": ["Player", "TopDownMovement", "min(650, TopDownMovement::MaxSpeed() + 40)"]},
            ],
        )
    )

    # --- PLAYING loop (only when GameState==1) ---
    # Movement enable/disable
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::ActivateBehavior", "parameters": ["Player", "TouchMapper"]},
            ],
            "events": [],
        }
    )
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "!=", "1"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TopDownMovement"]},
                {"type": "BuiltinCommonInstructions::DeactivateBehavior", "parameters": ["Player", "TouchMapper"]},
            ],
            "events": [],
        }
    )

    # Sprint logic (pressed on SprintBtn)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["SprintBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["Stamina", ">", "0"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["IsSprinting", "=", "1"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "max(0, Variable(Stamina) - 60 * TimeDelta())"]},
            ],
            "events": [],
        }
    )
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["IsSprinting", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "min(Variable(MaxStamina), Variable(Stamina) + 30 * TimeDelta())"]},
            ],
            "events": [],
        }
    )
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["IsSprinting", "=", "1"]}],
            "actions": [{"type": "TopDownMovementBehavior::SetMaxSpeed", "parameters": ["Player", "TopDownMovement", "520"]}],
            "events": [],
        }
    )
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["IsSprinting", "=", "0"]}],
            "actions": [{"type": "TopDownMovementBehavior::SetMaxSpeed", "parameters": ["Player", "TopDownMovement", "300"]}],
            "events": [],
        }
    )

    # Bounds clamp
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Player", "clamp(Player.X(), 0, 960)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Player", "clamp(Player.Y(), 0, 540)"]},
            ],
            "events": [],
        }
    )

    # Camera follow
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [{"type": "Scene::CenterCameraOnObject", "parameters": ["Player", "", "0", "0"]}],
            "events": [],
        }
    )

    # Score collect coin
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]},
                {"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Coin"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "Variable(Score) + 1"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Coin", "RandomInRange(80, 900)"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Coin", "RandomInRange(120, 520)"]},
            ],
            "events": [],
        }
    )

    # Difficulty scaling: enemy speed increases with score, unlock more enemies
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["EnemySpeed", "=", "60 + min(240, Variable(Score) * 4)"]},
                # unlock Enemy2 at 10, Enemy3 at 20
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy2", "Variable(Score) >= 10 ? Enemy2.X() : 2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy2", "Variable(Score) >= 10 ? Enemy2.Y() : 2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": ["Enemy3", "Variable(Score) >= 20 ? Enemy3.X() : 2000"]},
                {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": ["Enemy3", "Variable(Score) >= 20 ? Enemy3.Y() : 2000"]},
            ],
            "events": [],
        }
    )

    # Enemy movement (chase)
    for enemy in ["Enemy", "Enemy2", "Enemy3"]:
        block["events"].append(
            {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]}],
                "actions": [
                    {"type": "BuiltinCommonInstructions::SetObjectAngle", "parameters": [enemy, f"AngleBetweenPositions({enemy}.X(), {enemy}.Y(), Player.X(), Player.Y())"]},
                    {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": [enemy, f"{enemy}.X() + cos({enemy}.Angle()) * Variable(EnemySpeed) * TimeDelta()"]},
                    {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": [enemy, f"{enemy}.Y() + sin({enemy}.Angle()) * Variable(EnemySpeed) * TimeDelta()"]},
                ],
                "events": [],
            }
        )

    # Collision with enemies -> HP-- (trigger once per enemy)
    for enemy in ["Enemy", "Enemy2", "Enemy3"]:
        block["events"].append(
            {
                "type": "BuiltinCommonInstructions::Standard",
                "conditions": [
                    {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]},
                    {"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", enemy]},
                    {"type": "BuiltinCommonInstructions::TriggerOnce"},
                ],
                "actions": [
                    {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "max(0, Variable(HP) - 1)"]},
                    {"type": "BuiltinCommonInstructions::SetObjectX", "parameters": [enemy, "RandomInRange(80, 900)"]},
                    {"type": "BuiltinCommonInstructions::SetObjectY", "parameters": [enemy, "RandomInRange(120, 520)"]},
                ],
                "events": [],
            }
        )

    # Game over when HP==0
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["HP", "=", "0"]},
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "5"]},
                set_op("OverlayDim", 180),
                set_op("GameOverTxt", 255),
                set_op("RestartBtn", 255),
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HighScore", "=", "max(Variable(HighScore), Variable(Score))"]},
                {"type": "Storage::WriteNumber", "parameters": ["tamacore", "highscore", "Variable(HighScore)"]},
            ],
            "events": [],
        }
    )

    # Restart click
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [
                {"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "5"]},
                {"type": "Mouse::IsButtonPressed", "parameters": ["Left"]},
                {"type": "BuiltinCommonInstructions::CursorOnObject", "parameters": ["RestartBtn", "", ""]},
                {"type": "BuiltinCommonInstructions::TriggerOnce"},
            ],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["GameState", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Score", "=", "0"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "Variable(MaxHP)"]},
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["Stamina", "=", "Variable(MaxStamina)"]},
                set_op("GameOverTxt", 0),
                set_op("RestartBtn", 0),
                # show main menu UI
                set_op("OverlayDim", 180),
                set_op("TitleTxt", 255),
                set_op("StartBtn", 255),
                set_op("SettingsBtn", 255),
            ],
            "events": [],
        }
    )

    # HUD refresh (always)
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "TextObject::SetString", "parameters": ["HUD", hud_update_expr()]},
                {"type": "TextObject::SetString", "parameters": ["HPHud", hp_update_expr()]},
                {"type": "TextObject::SetString", "parameters": ["StaminaHud", sta_text_expr()]},
                {"type": "TextObject::SetString", "parameters": ["StaminaBar", sta_bar_expr()]},
            ],
            "events": [],
        }
    )

    # Hide/show menu groups depending on state (simple opacity gates)
    # Main menu visible when GameState==0
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "0"]}],
            "actions": [
                set_op("OverlayDim", 180),
                set_op("TitleTxt", 255),
                set_op("StartBtn", 255),
                set_op("SettingsBtn", 255),
                set_op("SoundBtn", 0),
                set_op("VibeBtn", 0),
                set_op("BackBtn", 0),
            ],
            "events": [],
        }
    )
    # Settings visible when GameState==3
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "3"]}],
            "actions": [
                set_op("OverlayDim", 180),
                set_op("TitleTxt", 255),
                set_op("StartBtn", 0),
                set_op("SettingsBtn", 0),
                set_op("SoundBtn", 255),
                set_op("VibeBtn", 255),
                set_op("BackBtn", 255),
            ],
            "events": [],
        }
    )
    # Playing visible when GameState==1
    block["events"].append(
        {
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::CompareNumberVariable", "parameters": ["GameState", "=", "1"]}],
            "actions": [
                set_op("OverlayDim", 0),
                set_op("TitleTxt", 0),
                set_op("StartBtn", 0),
                set_op("SettingsBtn", 0),
                set_op("SoundBtn", 0),
                set_op("VibeBtn", 0),
                set_op("BackBtn", 0),
                set_op("ResumeBtn", 0),
                set_op("ShopBtn", 0),
                set_op("Upgrade1Btn", 0),
                set_op("Upgrade2Btn", 0),
                set_op("Upgrade3Btn", 0),
                set_op("ShopBackBtn", 0),
                set_op("GameOverTxt", 0),
                set_op("RestartBtn", 0),
            ],
            "events": [],
        }
    )

    evs.append(block)
