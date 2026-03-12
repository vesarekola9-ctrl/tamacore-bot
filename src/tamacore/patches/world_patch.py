def apply_world_patch(project):

    if "variables" not in project:
        project["variables"] = []

    project["variables"].append({
        "name": "world_day",
        "type": "number",
        "value": 1
    })

    project["variables"].append({
        "name": "world_time",
        "type": "number",
        "value": 0
    })

    project["variables"].append({
        "name": "world_zone",
        "type": "string",
        "value": "home"
    })
