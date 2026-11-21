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
    for resource in resources:
        if not isinstance(resource, dict):
            errors.append("Malformed resource entry")
            continue
        filename = resource.get("file")
        if not filename or not isinstance(filename, str):
            errors.append(f"Resource {resource.get('name', '?')} has no file")
            continue
        if not (project_file.parent / filename).is_file():
            errors.append(f"Missing resource: {filename}")
    for scene in layouts:
        name = scene.get("name", "?")
        if not scene.get("objects") and not scene.get("instances"):
            errors.append(f"Scene {name} has no objects or instances")
        if not scene.get("events"):
            errors.append(f"Scene {name} has no events")
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
