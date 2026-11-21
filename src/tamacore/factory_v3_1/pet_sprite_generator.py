"""Deterministic, dependency-free RGBA pet sprite generation for GDevelop.

Generated sprites are original procedural pixel-art, not AI-rendered images.
Existing artist-provided frames are never overwritten.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 128
COLORS = {
    "bunny": ((222, 218, 235), (245, 179, 196)),
    "rabbit": ((222, 218, 235), (245, 179, 196)),
    "cat": ((240, 174, 106), (248, 207, 166)),
    "dog": ((181, 145, 109), (227, 193, 153)),
}
STATES = ("idle", "walk", "sleep", "eat", "play")


def _ellipse(pixels: bytearray, cx: int, cy: int, rx: int, ry: int, color: tuple[int, ...]) -> None:
    if rx <= 0 or ry <= 0:
        return
    for y in range(max(0, cy - ry), min(SIZE, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(SIZE, cx + rx + 1)):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                i = (y * SIZE + x) * 4
                pixels[i:i + 4] = bytes((*color[:3], color[3] if len(color) > 3 else 255))


def _png(pixels: bytearray) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    scanlines = b"".join(b"\x00" + pixels[y * SIZE * 4:(y + 1) * SIZE * 4] for y in range(SIZE))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(scanlines, 9)) + chunk(b"IEND", b""))


def render_pet(species: str, state: str, frame: int) -> bytes:
    species = species.lower()
    if species not in COLORS:
        species = "bunny"
    base, accent = COLORS[species]
    pixels = bytearray(SIZE * SIZE * 4)
    moving = state in ("walk", "play")
    offset = (-3 if frame == 0 else 3) if moving else (0 if frame == 0 else -2)
    sleeping = state == "sleep"
    dark = (67, 58, 72)
    _ellipse(pixels, 64, 114, 38, 6, (50, 41, 67, 45))
    _ellipse(pixels, 64 + offset, 87, 30, 27, base)
    if species in ("bunny", "rabbit"):
        for x, tilt in ((46, -2), (80, 2)):
            _ellipse(pixels, x + offset + tilt, 37, 11, 29, base)
            _ellipse(pixels, x + offset + tilt, 37, 5, 21, accent)
    elif species == "cat":
        for x in (43, 85):
            _ellipse(pixels, x + offset, 43, 13, 18, base)
            _ellipse(pixels, x + offset, 44, 6, 10, accent)
    else:
        for x in (30, 98):
            _ellipse(pixels, x + offset, 57, 12, 24, accent)
    _ellipse(pixels, 64 + offset, 67, 37, 33, base)
    _ellipse(pixels, 64 + offset, 83, 20, 12, accent)
    if sleeping:
        for x in (49, 79):
            _ellipse(pixels, x + offset, 67, 9, 2, dark)
    else:
        for x in (49, 79):
            _ellipse(pixels, x + offset, 64, 5, 7, dark)
            _ellipse(pixels, x + offset - 1, 62, 2, 2, (255, 255, 255))
    _ellipse(pixels, 64 + offset, 79, 5, 4, (147, 91, 106))
    for x in (45, 83):
        _ellipse(pixels, x + offset, 81, 7, 4, (245, 153, 172, 135))
    _ellipse(pixels, 47 + offset + (5 if moving and frame else 0), 106, 12, 8, base)
    _ellipse(pixels, 81 + offset - (5 if moving and frame else 0), 106, 12, 8, base)
    if state == "eat":
        _ellipse(pixels, 64 + offset, 101, 8, 13, (242, 132, 49))
        _ellipse(pixels, 66 + offset, 89, 4, 6, (91, 166, 86))
    elif state == "play":
        _ellipse(pixels, 102, 104 - (8 if frame else 0), 10, 10, (100, 179, 237))
        _ellipse(pixels, 99, 100 - (8 if frame else 0), 3, 3, (255, 255, 255))
    return _png(pixels)


def generate_pet_sprites(game_dir: Path, species: str = "bunny") -> list[Path]:
    target = Path(game_dir) / "assets" / "generated" / "player"
    target.mkdir(parents=True, exist_ok=True)
    result = []
    for state in STATES:
        for frame in (1, 2):
            path = target / f"player_{state}_{frame:02d}.png"
            if not path.exists():
                path.write_bytes(render_pet(species, state, frame - 1))
            result.append(path)
    return result
