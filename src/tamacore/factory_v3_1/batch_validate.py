from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import read_json, write_json
from .export_validate import validate_exports
from .validate import validate_build_output


def validate_batch_output(
    out_root: Path,
    export_root: Path,
    bundle_root: Path,
) -> List[str]:
    errors: List[str] = []

    report_path = out_root / "BATCH_REPORT.json"
    if not report_path.exists():
        return [f"Missing file: {report_path}"]

    data = read_json(report_path)
    if not isinstance(data, dict):
        return ["BATCH_REPORT.json: must be an object"]

    results = data.get("results")
    if not isinstance(results, list):
        return ["BATCH_REPORT.json: results missing"]

    for item in results:
        if not isinstance(item, dict):
            errors.append("BATCH_REPORT.json: invalid result item")
            continue

        pack = str(item.get("pack", "")).strip()
        if not pack:
            errors.append("BATCH_REPORT.json: result missing pack")
            continue

        if bool(item.get("buildOk")):
            build_errors = validate_build_output(out_root / pack)
            for err in build_errors:
                errors.append(f"{pack}: {err}")

        if bool(item.get("exportOk")):
            export_errors = validate_exports(export_root / pack)
            for err in export_errors:
                errors.append(f"{pack}: {err}")

        if bool(item.get("bundleOk")):
            bundle_dir = bundle_root / pack
            if not bundle_dir.exists():
                errors.append(f"{pack}: missing bundle dir")
            if not (bundle_dir / "README_RELEASE.txt").exists():
                errors.append(f"{pack}: missing bundle README_RELEASE.txt")
            if not bundle_dir.with_suffix(".zip").exists():
                errors.append(f"{pack}: missing bundle zip")

    write_json(
        out_root / "BATCH_VALIDATE_REPORT.json",
        {
            "ok": len(errors) == 0,
            "errors": errors,
        },
    )

    return errors
