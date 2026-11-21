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

    # GDevelop's current project schema also uses 'variables'. Keep the
    # canonical Pet_State available to event conditions in that format.
    canonical = game_data.setdefault("variables", [])
    if isinstance(canonical, list):
        names = {item.get("name") for item in canonical if isinstance(item, dict)}
        if "Pet_State" not in names:
            canonical.append({
                "name": "Pet_State", "type": "string", "value": "Idle",
                "children": [],
            })
    return game_data
