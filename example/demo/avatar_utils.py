"""Pixel-identicon avatar generation for the demo users.

Port of the FastComments demo avatar generator (main app
util/demo-user-utils.ts renderDemoAvatarSvg): a mirrored 8x8 grid filled from a
per-scheme palette by a Mulberry32 PRNG seeded from an FNV-1a hash of the seed.

The generated SVGs are committed under ./avatars/. Run this module directly to
regenerate them: `python demo/avatar_utils.py`.
"""

import base64
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


def render_svg(seed: str, scheme: str) -> str:
    palette = SCHEME_PALETTES.get(scheme, SCHEME_PALETTES["blue"])
    rng = _mulberry32(_hash_seed(seed))
    cells: list[str] = [""] * (GRID * GRID)
    half = (GRID + 1) // 2
    for y in range(GRID):
        for x in range(half):
            color = palette[int(rng() * len(palette))]
            cells[y * GRID + x] = color
            cells[y * GRID + (GRID - 1 - x)] = color
    rects = "".join(
        f'<rect x="{x * BLOCK}" y="{y * BLOCK}" width="{BLOCK}" height="{BLOCK}" fill="{cells[y * GRID + x]}"/>'
        for y in range(GRID)
        for x in range(GRID)
    )
    dim = GRID * BLOCK
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{dim}" height="{dim}" '
        f'viewBox="0 0 {dim} {dim}" shape-rendering="crispEdges">{rects}</svg>'
    )


_CACHE: dict[str, str] = {}


def data_uri(name: str) -> str:
    """Return the committed SVG avatar as an inline data URI (works everywhere)."""
    if name not in _CACHE:
        svg = (_AVATAR_DIR / f"{name}.svg").read_text(encoding="utf-8")
        encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        _CACHE[name] = f"data:image/svg+xml;base64,{encoded}"
    return _CACHE[name]


def generate() -> None:
    _AVATAR_DIR.mkdir(exist_ok=True)
    for name, scheme in AVATARS.items():
        (_AVATAR_DIR / f"{name}.svg").write_text(render_svg(name, scheme), encoding="utf-8")
        print(f"wrote {name}.svg ({scheme})")


if __name__ == "__main__":
    generate()
