from pathlib import Path
import json

def main() -> None:
    p = Path("_ci_game/game.json")
    if not p.exists():
        print("[WARN] _ci_game/game.json not found.")
        return

    data = json.loads(p.read_text(encoding="utf-8"))
    assert "layouts" in data and isinstance(data["layouts"], list), "Missing layouts"
    assert any(isinstance(l, dict) and l.get("name") == "Main" for l in data["layouts"]), "Missing Main scene"
    print("[OK] game.json basic structure validated")

if __name__ == "__main__":
    main()
