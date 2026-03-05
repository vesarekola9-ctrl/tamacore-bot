from __future__ import annotations

from pathlib import Path
from tamacore.patches.shop_v321 import apply_shop_v321
from tamacore.utils import read_json, write_json

GAME_JSON = Path(r"..\tamacore-game\game.json")

def main() -> None:
    project = read_json(GAME_JSON)
    changed = apply_shop_v321(project, scene_name="Main")
    if changed:
        write_json(GAME_JSON, project)
        print("[OK] Shop v3.2.1 patched into:", GAME_JSON)
    else:
        print("[OK] No changes (already patched or layout missing):", GAME_JSON)

if __name__ == "__main__":
    main()
