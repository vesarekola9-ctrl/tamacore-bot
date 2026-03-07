from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from ..utils import write_json, write_text


def write_export_report(export_dir: Path, exported: Dict[str, bool]) -> None:
    lines: List[str] = [
        "TamaCore Export Report",
        "======================",
        "",
        f"Export dir: {export_dir}",
        "",
        "Exports",
        "-------",
    ]

    for key in ["web", "zip", "android"]:
        lines.append(f"- {key}: {'OK' if exported.get(key, False) else 'SKIPPED'}")

    write_text(export_dir / "EXPORT_REPORT.txt", "\n".join(lines))
    write_json(
        export_dir / "export_manifest.json",
        {
            "exports": exported,
        },
    )
