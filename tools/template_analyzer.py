from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

OUT_REPORTS = Path("output") / "reports"
OUT_SCAFFOLD = Path("output") / "scaffold"

def main():
    OUT_REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_SCAFFOLD.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": "ok",
        "message": "Template analyzer placeholder (v1)"
    }

    conventions = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "naming": {},
        "scenes": [],
        "objects": []
    }

    (OUT_REPORTS / "template_analysis.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    (OUT_SCAFFOLD / "template_conventions.json").write_text(
        json.dumps(conventions, indent=2), encoding="utf-8"
    )

    print("[✓] Analyzer outputs created")

if __name__ == "__main__":
    main()
