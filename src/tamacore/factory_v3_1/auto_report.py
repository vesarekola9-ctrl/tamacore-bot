from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..utils import write_json, write_text


def write_auto_report(workspace_dir: Path, result: Dict[str, Any]) -> None:
    summary = result.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    lines = [
        "TamaCore Auto Report",
        "====================",
        "",
        f"Workspace: {workspace_dir}",
        f"Pack dir: {result.get('packDir', '')}",
        f"Game dir: {result.get('gameDir', '')}",
        f"Export dir: {result.get('exportDir', '')}",
        f"Bundle dir: {result.get('bundleDir', '')}",
        "",
        "Generated",
        "---------",
        f"Pet: {result.get('pet', '')}",
        f"Shop upgrades: {result.get('shopUpgrades', 0)}",
        f"Levels: {result.get('levelCount', 0)}",
        f"Foods: {result.get('foodCount', 0)}",
        f"Cosmetics: {result.get('cosmeticCount', 0)}",
        "",
        "Summary",
        "-------",
        f"Total packs: {summary.get('count', 0)}",
        f"OK: {summary.get('okCount', 0)}",
        f"Failed: {summary.get('failedCount', 0)}",
        "",
        "Results",
        "-------",
    ]

    for item in summary.get("results", []) if isinstance(summary.get("results"), list) else []:
        if not isinstance(item, dict):
            continue
        lines.append(
            f"- {item.get('pack', 'unknown')}: "
            f"ok={item.get('ok', False)}, "
            f"build={item.get('buildOk', False)}, "
            f"export={item.get('exportOk', False)}, "
            f"bundle={item.get('bundleOk', False)}"
        )
        for err in item.get("errors", []) if isinstance(item.get("errors"), list) else []:
            lines.append(f"  - ERROR: {err}")

    write_text(workspace_dir / "AUTO_REPORT.txt", "\n".join(lines))
    write_json(workspace_dir / "AUTO_REPORT.json", result)
