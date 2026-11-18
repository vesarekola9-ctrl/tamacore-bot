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

    try:
        data = read_json(manifest_path)
    except (OSError, ValueError) as exc:
        return [f"export_manifest.json: invalid JSON ({exc})"]
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
        if not (export_dir / "web" / "index.html").is_file():
            errors.append("Missing export file: web/index.html")
        if not (export_dir / "web" / "game.json").is_file() and not any((export_dir / "web").glob("*.js")):
            errors.append("web: compiled GDevelop runtime files missing")

    if exports.get("zip") is True:
        zip_path = export_dir / "game.zip"
        if not zip_path.is_file():
            errors.append("Missing export file: game.zip")
        else:
            from zipfile import BadZipFile, ZipFile
            try:
                with ZipFile(zip_path) as archive:
                    if archive.testzip() is not None:
                        errors.append("game.zip: corrupted archive member")
                    if "game.json" not in archive.namelist():
                        errors.append("game.zip: missing game.json")
            except (BadZipFile, OSError) as exc:
                errors.append(f"game.zip: invalid ZIP archive ({exc})")

    if exports.get("android") is True:
        if not (export_dir / "ANDROID_EXPORT.txt").exists():
            errors.append("Missing export file: ANDROID_EXPORT.txt")

    return errors
