"""GDevelop event-sheet pet care controls, HUD and timed needs decay.

These are source-project events; compiling and previewing requires GDevelop.
"""
from __future__ import annotations

from typing import Any

CARE = (
    ("Feed", "Eat", "Pet_Hunger", 15, "RUOKI", "f"),
    ("Play", "Play", "Pet_Happiness", 12, "LEIKI", "p"),
    ("Sleep", "Sleep", "Pet_Energy", 20, "NUKU", "s"),
    ("Walk", "Walk", "Pet_Energy", -5, "KAVELE", "w"),
    ("Idle", "Idle", None, 0, "LEPAA", "i"),
)
STATS = ("Pet_Hunger", "Pet_Happiness", "Pet_Energy")


def _instruction(name: str, parameters: list[str]) -> dict[str, Any]:
    return {"type": {"value": name}, "parameters": parameters}


def _event(name: str, conditions: list[dict], actions: list[dict]) -> dict:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "name": name,
        "conditions": conditions,
        "actions": actions,
        "events": [],
        "disabled": False,
        "folded": False,
    }


def _button(name: str, caption: str) -> dict:
    return {
        "name": name,
        "type": "TextObject::Text",
        "assetStoreId": "",
        "tags": "",
        "variables": [],
        "behaviors": [],
        "content": {
            "font": "", "size": 23, "bold": True, "italic": False,
            "underlined": False, "color": "255;255;255", "string": caption,
            "alignment": "center", "verticalAlignment": "center",
            "wrapping": False,
        },
        "effects": [],
    }


def apply_pet_care_events(scene: dict, *, width: int = 720, height: int = 1280) -> None:
    """Add visible clickable care controls, HUD and a periodic decay tick.

    Repeated application does not duplicate objects, instances or events.
    Keyboard actions are provided separately by character_builder.
    """
    objects = scene.setdefault("objects", [])
    if not any(isinstance(obj, dict) and obj.get("name") == "Player" for obj in objects):
        return
    instances = scene.setdefault("instances", [])
    events = scene.setdefault("events", [])
    object_names = {obj.get("name") for obj in objects if isinstance(obj, dict)}
    instance_names = {inst.get("objectName", inst.get("name")) for inst in instances if isinstance(inst, dict)}
    event_names = {event.get("name") for event in events if isinstance(event, dict)}

    for index, (verb, state, stat, delta, caption, _key) in enumerate(CARE):
        name = f"PetCareButton_{verb}"
        if name not in object_names:
            objects.append(_button(name, caption))
            object_names.add(name)
        if name not in instance_names:
            instances.append({
                "name": name, "objectName": name, "layer": "UI",
                "x": max(0, min(width - 1, 16 + index * max(60, min(125, (width - 32) // 5)))),
                "y": max(0, height - 100), "angle": 0, "zOrder": 2900,
                "locked": False, "persistentUuid": "",
                "customSize": False, "width": 0, "height": 0,
            })
            instance_names.add(name)
        marker = f"TamaCorePetClick_{verb}"
        if marker not in event_names:
            actions = [_instruction("SetStringVariable", ["Pet_State", "=", f'"{state}"'])]
            if stat:
                actions.append(_instruction("SetNumberVariable", [
                    stat, "=", f"min(100, max(0, GlobalVariable({stat}) + ({delta})))"
                ]))
            events.append(_event(marker, [
                _instruction("CursorOnObject", [name, "", ""]),
                _instruction("MouseButtonReleased", ["Left"]),
            ], actions))
            event_names.add(marker)

    # Needs decrease once per 60 seconds rather than once per rendered
    # frame. The tick is bounded at zero.
    marker = "TamaCorePetNeedsDecay"
    if marker not in event_names:
        events.append(_event(marker, [
            _instruction("Timer", ["60", '"TamaCoreNeeds"']),
        ], [
            _instruction("SetNumberVariable", [
                stat, "=", f"max(0, GlobalVariable({stat}) - 1)"
            ]) for stat in STATS
        ] + [_instruction("ResetTimer", ['"TamaCoreNeeds"'])]))
        event_names.add(marker)

    # Text-object status labels are refreshed every frame.
    for index, (stat, label) in enumerate((
        ("Pet_Hunger", "Hunger"), ("Pet_Happiness", "Happy"),
        ("Pet_Energy", "Energy"),
    )):
        name = f"PetCareStatus_{label}"
        if name not in object_names:
            objects.append(_button(name, label))
            object_names.add(name)
        if name not in instance_names:
            instances.append({
                "name": name, "objectName": name, "layer": "UI",
                "x": max(0, min(width - 1, 16 + index * max(90, width // 3))),
                "y": max(0, height - 160), "angle": 0, "zOrder": 2900,
                "locked": False, "persistentUuid": "",
                "customSize": False, "width": 0, "height": 0,
            })
            instance_names.add(name)
        marker = f"TamaCorePetStatus_{label}"
        if marker not in event_names:
            events.append(_event(marker, [], [
                _instruction("TextObject::String", [
                    name, "=", f'"{label}: " + ToString(GlobalVariable({stat}))'
                ]),
            ]))
            event_names.add(marker)
