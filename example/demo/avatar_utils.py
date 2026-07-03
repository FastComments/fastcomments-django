"""Pixel-identicon avatar generation for the demo users.

The identicon logic is a port of the FastComments demo avatar generator (main
app util/demo-user-utils.ts renderDemoAvatarSvg): a mirrored 8x8 grid filled
from a per-scheme palette by a Mulberry32 PRNG seeded from an FNV-1a hash.

Output is PNG (not SVG): FastComments accepts `data:image/png` avatars in SSO
but rejects `data:image/svg+xml` data URIs for security, and a data URI keeps the
avatar self-contained (works on the page and inside the widget's iframe). PNGs
are encoded with the stdlib (zlib) - no image library needed.

The generated PNGs are committed under ./avatars/. Regenerate them with
`python demo/avatar_utils.py`.
"""

import base64
import struct
import zlib
from collections.abc import Callable
from pathlib import Path

SCHEME_PALETTES: dict[str, list[str]] = {
    "green": ["#0e4d24", "#1a7d3a", "#2db958", "#7be087", "#c5f5cc"],
    "red": ["#5c0d0d", "#a51e1e", "#e63b3b", "#f57878", "#fcc7c7"],
    "blue": ["#0a2a5c", "#1a4fb0", "#3b7ee6", "#7eaef5", "#c7dcfc"],
    "purple": ["#3a0d5c", "#6b1ea5", "#9d3be6", "#c47ef5", "#e8c7fc"],
    "orange": ["#5c2a0d", "#a55b1e", "#e6873b", "#f5b07e", "#fcd9c7"],
    "teal": ["#0d5c5c", "#1ea5a5", "#3be6e6", "#7ef5f5", "#c7fcfc"],
    "pink": ["#5c0d3a", "#a51e6b", "#e63b9d", "#f57ec4", "#fcc7e8"],
    "amber": ["#5c4d0d", "#a58a1e", "#e6c43b", "#f5dd7e", "#fcefc7"],
}

GRID = 8
BLOCK = 16

# seed -> palette scheme for each demo user's committed avatar.
AVATARS: dict[str, str] = {"user-1": "purple", "user-2": "teal", "user-3": "amber"}

_AVATAR_DIR = Path(__file__).resolve().parent / "avatars"
_MASK32 = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & _MASK32


def _hash_seed(seed: str) -> int:
    h = 2166136261
    for ch in seed:
        h = _imul(h ^ ord(ch), 16777619)
    return h & _MASK32


def _mulberry32(seed_num: int) -> Callable[[], float]:
    state = seed_num & _MASK32

    def nxt() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & _MASK32
        r = state
        r = _imul(r ^ (r >> 15), r | 1)
        r = (r ^ ((r + _imul(r ^ (r >> 7), r | 61)) & _MASK32)) & _MASK32
        return ((r ^ (r >> 14)) & _MASK32) / 4294967296

    return nxt


def _cells(seed: str, scheme: str) -> list[bytes]:
    """Return GRID*GRID cells as RGB byte-triples, mirrored left-to-right."""
    palette = [bytes.fromhex(c[1:]) for c in SCHEME_PALETTES.get(scheme, SCHEME_PALETTES["blue"])]
    rng = _mulberry32(_hash_seed(seed))
    cells: list[bytes] = [b""] * (GRID * GRID)
    half = (GRID + 1) // 2
    for y in range(GRID):
        for x in range(half):
            color = palette[int(rng() * len(palette))]
            cells[y * GRID + x] = color
            cells[y * GRID + (GRID - 1 - x)] = color
    return cells


def _png(width: int, height: int, rows: list[bytes]) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & _MASK32)

    raw = b"".join(b"\x00" + row for row in rows)  # filter byte 0 (none) per scanline
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit truecolor RGB
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def render_png(seed: str, scheme: str) -> bytes:
    cells = _cells(seed, scheme)
    dim = GRID * BLOCK
    rows: list[bytes] = []
    for py in range(dim):
        gy = py // BLOCK
        row = bytearray()
        for px in range(dim):
            row += cells[gy * GRID + (px // BLOCK)]
        rows.append(bytes(row))
    return _png(dim, dim, rows)


_CACHE: dict[str, str] = {}


def data_uri(name: str) -> str:
    """Return the committed PNG avatar as an inline data URI (works everywhere)."""
    if name not in _CACHE:
        png = (_AVATAR_DIR / f"{name}.png").read_bytes()
        _CACHE[name] = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    return _CACHE[name]


def generate() -> None:
    _AVATAR_DIR.mkdir(exist_ok=True)
    for name, scheme in AVATARS.items():
        (_AVATAR_DIR / f"{name}.png").write_bytes(render_png(name, scheme))
        print(f"wrote {name}.png ({scheme})")


if __name__ == "__main__":
    generate()
