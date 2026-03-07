from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..utils import write_text


def write_batch_report(out_root: Path, summary: Dict[str, Any]) -> None:
    results = summary.get("results", [])
    if not isinstance(results, list):
        results = []

    lines: List[str] = [
        "TamaCore Batch Report",
        "=====================",
        "",
        f"Packs root: {summary.get('packsRoot', '')}",
        f"Template dir: {summary.get('templateDir', '')}",
        f"Out root: {summary.get('outRoot', '')}",
        f"Export root: {summary.get('exportRoot', '')}",
        f"Bundle root: {summary.get('bundleRoot', '')}",
        "",
        "Summary",
        "-------",
        f"Count: {summary.get('count', 0)}",
        f"OK: {summary.get('okCount', 0)}",
        f"Failed: {summary.get('failedCount', 0)}",
        "",
        "Results",
        "-------",
    ]

    for item in results:
        if not isinstance(item, dict):
            continue
        lines.append(
            f"- {item.get('pack', 'unknown')}: "
            f"ok={item.get('ok', False)}, "
            f"build={item.get('buildOk', False)}, "
            f"export={item.get('exportOk', False)}, "
            f"bundle={item.get('bundleOk', False)}"
        )
        errs = item.get("errors", [])
        if isinstance(errs, list):
            for err in errs:
                lines.append(f"  - ERROR: {err}")

    write_text(out_root / "BATCH_REPORT.txt", "\n".join(lines))
