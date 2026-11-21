"""TamaCore pet runtime defaults for generated GDevelop projects.

The legacy implementation injected an uninstantiated PetObject with missing
stage1.png/apple.png/ultimate.png sprites. The real player sprite is built by
character_builder, so keep one canonical visual object instead.
"""


def apply_pet_runtime(game_data: dict) -> dict:
    variables = game_data.setdefault("globalVariables", [])
    if not isinstance(variables, list):
        variables = []
        game_data["globalVariables"] = variables

    defaults = {
        "Pet_Name": "Tama",
        "Pet_Hunger": "100",
        "Pet_Energy": "100",
        "Pet_Happiness": "100",
        "Pet_Health": "100",
        "Pet_State": "Idle",
        "Pet_CurrentAnimation": "Idle",
    }
    existing = {item.get("name") for item in variables if isinstance(item, dict)}
    for name, value in defaults.items():
        if name not in existing:
            variables.append({"name": name, "value": value})

    # Define every pet care variable in GDevelop's typed project schema.
    canonical = game_data.setdefault("variables", [])
    if isinstance(canonical, list):
        by_name = {item.get("name"): item for item in canonical if isinstance(item, dict)}
        for name, value in defaults.items():
            kind = "number" if name in ("Pet_Hunger", "Pet_Energy", "Pet_Happiness", "Pet_Health") else "string"
            if name not in by_name:
                canonical.append({"name": name, "type": kind,
                                  "value": int(value) if kind == "number" else value,
                                  "children": []})
            else:
                by_name[name].setdefault("type", kind)
                by_name[name].setdefault("children", [])
    return game_data
