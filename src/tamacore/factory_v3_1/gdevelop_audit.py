"""Audit generated GDevelop projects for missing resources and empty gameplay.

This does not replace opening the project in GDevelop and testing its preview.
"""
from __future__ import annotations

import json
from pathlib import Path


def audit_project(project_file: Path) -> list[str]:
    project_file = Path(project_file)
    project = json.loads(project_file.read_text(encoding="utf-8"))
    errors = []
    layouts = project.get("layouts", [])
    if not isinstance(layouts, list) or not layouts:
        errors.append("Project has no scenes (layouts)")
        layouts = []
    resources = project.get("resources", {}).get("resources", [])
    seen_missing = set()

    def check_file(filename: str, label: str) -> None:
        # Reject paths that could escape the project directory.
        if Path(filename).is_absolute() or ".." in Path(filename).parts:
            errors.append(f"Unsafe resource path: {filename}")
            return
        if not (project_file.parent / filename).is_file():
            key = (label, filename)
            if key not in seen_missing:
                errors.append(f"{label}: {filename}")
                seen_missing.add(key)
    for resource in resources:
        if not isinstance(resource, dict):
            errors.append("Malformed resource entry")
            continue
        filename = resource.get("file")
        if not filename or not isinstance(filename, str):
            errors.append(f"Resource {resource.get('name', '?')} has no file")
            continue
        check_file(filename, "Missing resource")
    # Sprite animation images are referenced by objects, not always by
    # top-level resource entries. Audit both locations.
    for scene in layouts:
        name = scene.get("name", "?")
        if not scene.get("objects") and not scene.get("instances"):
            errors.append(f"Scene {name} has no objects or instances")
        if not scene.get("events"):
            errors.append(f"Scene {name} has no events")
        # Named TamaCore generated events must be unique. Duplicates would
        # apply pet care rewards or decay more than once per interaction.
        generated_names = [
            event.get("name") for event in scene.get("events", [])
            if isinstance(event, dict)
            and isinstance(event.get("name"), str)
            and event["name"].startswith("TamaCore")
        ]
        for event_name in sorted({item for item in generated_names if generated_names.count(item) > 1}):
            errors.append(f"Scene {name} has duplicate TamaCore event: {event_name}")
        # Catch broken scene instances and accidental duplicate object names.
        objects = [obj for obj in scene.get("objects", []) if isinstance(obj, dict)]
        object_names = [obj.get("name") for obj in objects if isinstance(obj.get("name"), str)]
        duplicates = {item for item in object_names if object_names.count(item) > 1}
        for duplicate in sorted(duplicates):
            errors.append(f"Scene {name} has duplicate object: {duplicate}")
        known = set(object_names)
        for instance in scene.get("instances", []):
            if not isinstance(instance, dict):
                continue
            target = instance.get("name") or instance.get("objectName")
            if target and target not in known:
                errors.append(f"Scene {name} instance references missing object: {target}")
        for obj in scene.get("objects", []):
            if not isinstance(obj, dict):
                continue
            for animation in obj.get("animations", []):
                if not isinstance(animation, dict):
                    continue
                for direction in animation.get("directions", []):
                    if not isinstance(direction, dict):
                        continue
                    for sprite in direction.get("sprites", []):
                        if not isinstance(sprite, dict):
                            continue
                        image = sprite.get("image")
                        if isinstance(image, str) and image:
                            check_file(image, "Missing animation frame")
    return errors


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Audit a generated TamaCore GDevelop project")
    parser.add_argument("project", type=Path, help="Path to generated game.json")
    args = parser.parse_args()
    problems = audit_project(args.project)
    if problems:
        for problem in problems:
            print("ERROR:", problem)
        return 1
    print("GDevelop structural audit passed (runtime behavior not verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
