from __future__ import annotations

from pathlib import Path

from ..utils import ensure_dir, write_text


def generate_placeholder_assets(pack_dir: Path) -> None:
    assets = pack_dir / "assets"

    ensure_dir(assets / "background")
    ensure_dir(assets / "player")
    ensure_dir(assets / "coin")
    ensure_dir(assets / "enemy")
    ensure_dir(assets / "ui")

    _write_if_missing(
        assets / "background" / "background.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="720" height="1280" fill="url(#bg)"/>
  <circle cx="580" cy="160" r="120" fill="#38bdf8" opacity="0.15"/>
  <circle cx="140" cy="1080" r="140" fill="#22c55e" opacity="0.10"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "player" / "player_idle_01.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="108" rx="28" ry="10" fill="#000" opacity="0.18"/>
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <circle cx="52" cy="48" r="5" fill="#0f172a"/>
  <circle cx="76" cy="48" r="5" fill="#0f172a"/>
  <path d="M49 66 Q64 76 79 66" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
  <rect x="44" y="84" width="40" height="22" rx="11" fill="#f59e0b"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "player" / "player_idle_02.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="108" rx="28" ry="10" fill="#000" opacity="0.18"/>
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <circle cx="52" cy="49" r="5" fill="#0f172a"/>
  <circle cx="76" cy="49" r="5" fill="#0f172a"/>
  <path d="M50 67 Q64 73 78 67" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
  <rect x="42" y="83" width="44" height="24" rx="12" fill="#f59e0b"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "player" / "player_walk_01.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="108" rx="28" ry="10" fill="#000" opacity="0.18"/>
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <circle cx="52" cy="48" r="5" fill="#0f172a"/>
  <circle cx="76" cy="48" r="5" fill="#0f172a"/>
  <path d="M48 66 Q64 78 80 66" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
  <rect x="40" y="84" width="42" height="22" rx="11" fill="#f59e0b"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "player" / "player_walk_02.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="108" rx="28" ry="10" fill="#000" opacity="0.18"/>
  <circle cx="64" cy="54" r="34" fill="#fbbf24"/>
  <circle cx="52" cy="48" r="5" fill="#0f172a"/>
  <circle cx="76" cy="48" r="5" fill="#0f172a"/>
  <path d="M50 67 Q64 74 78 67" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
  <rect x="46" y="84" width="42" height="22" rx="11" fill="#f59e0b"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "coin" / "coin.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">
  <circle cx="48" cy="48" r="34" fill="#fde047"/>
  <circle cx="48" cy="48" r="28" fill="#facc15"/>
  <text x="48" y="56" text-anchor="middle" font-family="Arial" font-size="28" font-weight="700" fill="#854d0e">C</text>
</svg>
""",
    )

    _write_if_missing(
        assets / "enemy" / "enemy.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <ellipse cx="64" cy="110" rx="30" ry="10" fill="#000" opacity="0.18"/>
  <circle cx="64" cy="56" r="34" fill="#ef4444"/>
  <circle cx="52" cy="48" r="6" fill="#fff"/>
  <circle cx="76" cy="48" r="6" fill="#fff"/>
  <circle cx="52" cy="48" r="2.5" fill="#0f172a"/>
  <circle cx="76" cy="48" r="2.5" fill="#0f172a"/>
  <path d="M48 74 L56 66 L64 74 L72 66 L80 74" fill="none" stroke="#7f1d1d" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "ui" / "touch_joystick.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">
  <circle cx="80" cy="80" r="62" fill="#94a3b8" opacity="0.20"/>
  <circle cx="80" cy="80" r="46" fill="#cbd5e1" opacity="0.28"/>
  <circle cx="80" cy="80" r="22" fill="#e2e8f0" opacity="0.55"/>
</svg>
""",
    )

    _write_if_missing(
        assets / "ui" / "hud_label.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" width="320" height="80" viewBox="0 0 320 80">
  <rect x="4" y="4" width="312" height="72" rx="18" fill="#0f172a" opacity="0.68" stroke="#334155" stroke-width="2"/>
  <text x="20" y="49" font-family="Arial" font-size="28" font-weight="700" fill="#f8fafc">HUD</text>
</svg>
""",
    )


def _write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        write_text(path, content)
