from __future__ import annotations

from pathlib import Path
from typing import List

from ..utils import read_json


def validate_auto_workspace(workspace_dir: Path) -> List[str]:
    errors: List[str] = []

    report_txt = workspace_dir / "AUTO_REPORT.txt"
    report_json = workspace_dir / "AUTO_REPORT.json"
    packs_dir = workspace_dir / "packs"
    games_dir = workspace_dir / "games"
    exports_dir = workspace_dir / "exports"
    bundles_dir = workspace_dir / "bundles"

    for path in [report_txt, report_json, packs_dir, games_dir, exports_dir, bundles_dir]:
        if not path.exists():
            errors.append(f"Missing: {path}")

    if errors:
        return errors

    data = read_json(report_json)
    if not isinstance(data, dict):
        return ["AUTO_REPORT.json: must be an object"]

    summary = data.get("summary")
    if not isinstance(summary, dict):
        return ["AUTO_REPORT.json: summary missing"]

    results = summary.get("results")
    if not isinstance(results, list):
        return ["AUTO_REPORT.json: results missing"]

    for item in results:
        if not isinstance(item, dict):
            errors.append("AUTO_REPORT.json: invalid result item")
            continue

        pack = str(item.get("pack", "")).strip()
        if not pack:
            errors.append("AUTO_REPORT.json: result missing pack")
            continue

        if bool(item.get("ok")):
            if not (games_dir / pack / "game.json").exists():
                errors.append(f"Missing built game for pack: {pack}")
            if not (exports_dir / pack / "EXPORT_REPORT.txt").exists():
                errors.append(f"Missing export report for pack: {pack}")
            if not (bundles_dir / pack / "README_RELEASE.txt").exists():
                errors.append(f"Missing bundle for pack: {pack}")

    text = report_txt.read_text(encoding="utf-8")
    if "TamaCore Auto Report" not in text:
        errors.append("AUTO_REPORT.txt: invalid header")

    return errors
