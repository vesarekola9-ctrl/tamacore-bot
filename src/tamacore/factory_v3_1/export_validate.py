from __future__ import annotations

from pathlib import Path
from typing import List

from ..utils import read_json


def validate_exports(export_dir: Path) -> List[str]:
    errors: List[str] = []

    manifest_path = export_dir / "export_manifest.json"
    report_path = export_dir / "EXPORT_REPORT.txt"

    if not manifest_path.exists():
        errors.append("Missing file: export_manifest.json")
        return errors

    if not report_path.exists():
        errors.append("Missing file: EXPORT_REPORT.txt")
        return errors

    data = read_json(manifest_path)
    if not isinstance(data, dict):
        errors.append("export_manifest.json: must be an object")
        return errors

    exports = data.get("exports")
    if not isinstance(exports, dict):
        errors.append("export_manifest.json: exports missing")
        return errors

    if exports.get("web") is True:
        if not (export_dir / "web").exists():
            errors.append("Missing export folder: web")
        if not (export_dir / "web" / "index.html").exists():
            errors.append("Missing export file: web/index.html")

    if exports.get("zip") is True:
        if not (export_dir / "game.zip").exists():
            errors.append("Missing export file: game.zip")

    if exports.get("android") is True:
        if not (export_dir / "ANDROID_EXPORT.txt").exists():
            errors.append("Missing export file: ANDROID_EXPORT.txt")

    return errors
