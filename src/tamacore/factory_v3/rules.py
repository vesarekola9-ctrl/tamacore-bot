from __future__ import annotations

from typing import Any, Dict, List


def factory_rules_patch(project: Dict[str, Any], scene: Dict[str, Any]) -> None:
    """
    Adds:
      - global HP variable
      - if Enemy exists, add simple chase behavior by events
      - collision Player<->Enemy reduces HP and resets player pos
    """
    ensure_global_variable(project, "HP", "number", "3")

    objects = scene.get("objects")
    if not isinstance(objects, list):
        return

    has_player = any(isinstance(o, dict) and o.get("name") == "Player" for o in objects)
    has_enemy = any(isinstance(o, dict) and o.get("name") == "Enemy" for o in objects)
    if not (has_player and has_enemy):
        return

    events = scene.get("events")
    if not isinstance(events, list):
        return

    # Prevent duplicates by checking for our marker variable set
    if any(isinstance(e, dict) and e.get("comment") == "FACTORY_V3_ENEMY_AI" for e in events):
        return

    # Every frame: move Enemy toward Player
    events.append(
        {
            "comment": "FACTORY_V3_ENEMY_AI",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetObjectAngle", "parameters": ["Enemy", "AngleBetweenPositions(Enemy.X(), Enemy.Y(), Player.X(), Player.Y())"]},
                {"type": "BuiltinCommonInstructions::AddForcePolar", "parameters": ["Enemy", "Enemy.Angle()", "120", "0"]},
            ],
            "events": [],
        }
    )

    # Collision reduces HP and resets Player
    events.append(
        {
            "comment": "FACTORY_V3_ENEMY_COLLISION",
            "type": "BuiltinCommonInstructions::Standard",
            "conditions": [{"type": "BuiltinCommonInstructions::Collision", "parameters": ["Player", "Enemy"]}],
            "actions": [
                {"type": "BuiltinCommonInstructions::SetNumberVariable", "parameters": ["HP", "=", "max(0, Variable(HP)-1)"]},
                {"type": "BuiltinCommonInstructions::SetObjectPosition", "parameters": ["Player", "200", "240"]},
            ],
            "events": [],
        }
    )


def ensure_global_variable(project: Dict[str, Any], name: str, vtype: str, value: str) -> None:
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
