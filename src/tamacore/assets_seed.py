from __future__ import annotations

from pathlib import Path


def ensure_assets_exist(assets_dir: Path) -> None:
    """
    Ensures the assets folder exists. We keep this minimal on purpose:
    - your repo can ship default assets under assets/
    - or you can drop your own PNGs there
    """
    assets_dir.mkdir(parents=True, exist_ok=True)

    # If user has nothing yet, keep pipeline still runnable (no crash).
    # The patcher will handle empty maps gracefully.
