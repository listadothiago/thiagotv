#!/usr/bin/env python3
"""Draw ThiagoTV's app icons.

The set is drawn on a small grid and scaled up with nearest-neighbour, so the
icon is genuinely pixelated rather than a smooth illustration shrunk down — the
same logic as the cabinet on the page, which is built from whole blocks.

Icons are generated rather than committed as hand-made art so the palette can
follow the site's if it ever changes.

Usage:
    python3 scripts/make_icons.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "icons"

BG_DEEP = (7, 15, 34)
BG_MID = (18, 36, 74)
WOOD_LIT = (138, 90, 52)
WOOD = (107, 68, 37)
WOOD_MID = (87, 53, 23)
WOOD_DARK = (59, 35, 16)
WOOD_DEEP = (36, 20, 8)
BRASS = (224, 179, 86)
SCREEN = (12, 26, 40)
SCREEN_LIT = (36, 74, 104)
METAL = (170, 180, 190)

GRID = 32  # the icon is designed at 32x32 and scaled up


def draw_set(d, *, with_background):
    """Draw the television on a GRID x GRID canvas."""
    if with_background:
        d.rectangle([0, 0, GRID, GRID], fill=BG_MID)
        # A soft-ish vignette, done in two steps so it stays blocky.
        d.rectangle([0, 0, GRID, 3], fill=BG_DEEP)
        d.rectangle([0, GRID - 4, GRID, GRID], fill=BG_DEEP)

    # Antenna: two diagonals of single pixels, drawn by stepping.
    for i in range(6):
        d.point((14 - i, 5 - 0 + i), fill=METAL)
        d.point((17 + i, 5 - 0 + i), fill=METAL)
    d.point((8, 10), fill=BRASS)
    d.point((23, 10), fill=BRASS)
    d.rectangle([14, 10, 17, 11], fill=WOOD_DARK)

    # Cabinet, with the corner blocks knocked out.
    d.rectangle([3, 11, 28, 27], fill=WOOD)
    d.rectangle([3, 11, 28, 12], fill=WOOD_LIT)      # lit top edge
    d.rectangle([3, 25, 28, 27], fill=WOOD_MID)      # shaded lower deck
    for x, y in [(3, 11), (28, 11), (3, 27), (28, 27)]:
        d.point((x, y), fill=BG_MID if with_background else (0, 0, 0, 0))

    # Screen well and glass.
    d.rectangle([5, 13, 26, 23], fill=WOOD_DEEP)
    d.rectangle([6, 14, 25, 22], fill=SCREEN)
    # A lit band across the tube so it reads as switched on.
    d.rectangle([7, 16, 24, 19], fill=SCREEN_LIT)
    d.rectangle([7, 15, 24, 15], fill=(24, 50, 72))

    # Speaker grille and two knobs on the lower deck.
    for x in range(6, 15, 2):
        d.point((x, 25), fill=WOOD_DEEP)
        d.point((x + 1, 26), fill=WOOD_DEEP)
    d.rectangle([19, 24, 21, 26], fill=WOOD_DEEP)
    d.rectangle([23, 24, 25, 26], fill=WOOD_DEEP)
    d.point((20, 25), fill=BRASS)
    d.point((24, 25), fill=BRASS)

    # Feet.
    d.rectangle([6, 28, 9, 28], fill=WOOD_DARK)
    d.rectangle([22, 28, 25, 28], fill=WOOD_DARK)


def render(size, *, with_background=True, padding=0):
    """Render at GRID and scale up with nearest neighbour to keep hard edges."""
    mode = "RGB" if with_background else "RGBA"
    base = Image.new(mode, (GRID, GRID), BG_MID if with_background else (0, 0, 0, 0))
    draw_set(ImageDraw.Draw(base), with_background=with_background)
    icon = base.resize((size, size), Image.NEAREST)

    if padding:
        # Maskable icons get cropped to a circle by the launcher, so the artwork
        # has to sit inside a safe zone with room to spare at the edges.
        inner = int(size * (1 - padding * 2))
        shrunk = base.resize((inner, inner), Image.NEAREST)
        canvas = Image.new("RGB", (size, size), BG_MID)
        canvas.paste(shrunk, ((size - inner) // 2, (size - inner) // 2))
        icon = canvas
    return icon


def main():
    ICON_DIR.mkdir(exist_ok=True)
    outputs = [
        ("icon-192.png", render(192)),
        ("icon-512.png", render(512)),
        ("icon-maskable-512.png", render(512, padding=0.14)),
        ("apple-touch-icon.png", render(180)),
        ("favicon-32.png", render(32)),
    ]
    for name, img in outputs:
        img.save(ICON_DIR / name)
        print(f"  {name:<26} {img.size[0]}x{img.size[1]}")
    print(f"\nWrote {len(outputs)} icons to {ICON_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
