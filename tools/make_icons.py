#!/usr/bin/env python3
"""Draws the icon packs shipped with the official themes into icons/<theme id>/<key>.png.

Each icon is a white glyph on a transparent 96x96 canvas. The app recolours it with the theme's icon colour
(icons.packTint = true), so one drawing works with any accent. Needs Pillow:  pip install pillow
Usage:  python3 tools/make_icons.py
"""
import math, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIZE, SS = 96, 4            # final size, supersampling factor (drawn big, shrunk for smooth edges)

# stroke = line width in final pixels, filled = solid glyphs, round = round caps/corners
STYLES = {
    "aurora-night":   dict(stroke=7, filled=False, round=True),
    "cyber-pop":      dict(stroke=8, filled=True,  round=False),
    "midnight-black": dict(stroke=4, filled=False, round=True),
    "solar-flare":    dict(stroke=10, filled=True, round=True),
}
KEYS = ["play", "pause", "next", "previous", "shuffle", "repeat", "favorite", "favorite_border",
        "home", "search", "library", "settings"]
WHITE = (255, 255, 255, 255)


class Pen:
    def __init__(self, style):
        self.st = style
        self.img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.w = style["stroke"] * SS

    def p(self, x, y):  # design units (0..96) -> big canvas
        return (x * SS, y * SS)

    def dot(self, q, r):
        self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=WHITE)

    def line(self, pts):
        big = [self.p(*q) for q in pts]
        self.d.line(big, fill=WHITE, width=int(self.w), joint="curve")
        if self.st["round"]:
            self.dot(big[0], self.w / 2)
            self.dot(big[-1], self.w / 2)

    def poly(self, pts, filled, soften=True):
        big = [self.p(*q) for q in pts]
        if filled:
            self.d.polygon(big, fill=WHITE)
            if self.st["round"] and soften:  # round the corners with a thin round-joined outline
                w = self.w * 0.6
                self.d.line(big + [big[0]], fill=WHITE, width=int(w), joint="curve")
                for q in big:
                    self.dot(q, w / 2)
        else:
            self.line(pts + [pts[0]])

    def circle(self, c, r, filled):
        x, y = self.p(*c)
        R = r * SS
        if filled:
            self.d.ellipse([x - R, y - R, x + R, y + R], fill=WHITE)
        else:
            self.d.ellipse([x - R, y - R, x + R, y + R], outline=WHITE, width=int(self.w))

    def rect(self, x0, y0, x1, y1, radius):
        rad = radius * SS if self.st["round"] else 0
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], rad, fill=WHITE)

    def hole(self, c, r):
        x, y = self.p(*c)
        R = r * SS
        self.d.ellipse([x - R, y - R, x + R, y + R], fill=(0, 0, 0, 0))

    def done(self):
        return self.img.resize((SIZE, SIZE), Image.LANCZOS)


def heart_points(cx=48, cy=50, n=60):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * 1.9, cy - y * 1.9))
    return pts


def gear_points(cx=48, cy=48, teeth=8, r_out=36, r_in=27):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        r = r_out if (i % 4) in (0, 1) else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw(key, style):
    g = Pen(style)
    filled = style["filled"]
    if key == "play":
        g.poly([(30, 20), (30, 76), (76, 48)], filled)
    elif key == "pause":
        g.rect(26, 20, 42, 76, 5)
        g.rect(54, 20, 70, 76, 5)
    elif key == "next":
        g.poly([(22, 22), (22, 74), (60, 48)], filled)
        g.rect(66, 22, 76, 74, 3)
    elif key == "previous":
        g.poly([(74, 22), (74, 74), (36, 48)], filled)
        g.rect(20, 22, 30, 74, 3)
    elif key == "shuffle":
        g.line([(14, 28), (34, 28), (58, 68), (76, 68)])
        g.line([(14, 68), (34, 68), (42, 56)])
        g.line([(50, 40), (58, 28), (76, 28)])
        g.poly([(72, 18), (86, 28), (72, 38)], True)
        g.poly([(72, 58), (86, 68), (72, 78)], True)
    elif key == "repeat":
        g.line([(22, 42), (22, 32), (30, 24), (68, 24)])
        g.poly([(64, 14), (80, 24), (64, 34)], True)
        g.line([(74, 54), (74, 64), (66, 72), (28, 72)])
        g.poly([(32, 62), (16, 72), (32, 82)], True)
    elif key == "favorite":
        g.poly(heart_points(), True, soften=False)
    elif key == "favorite_border":
        g.poly(heart_points(), False)
    elif key == "home":
        g.poly([(12, 46), (48, 14), (84, 46)], False)
        g.poly([(22, 42), (22, 80), (74, 80), (74, 42)], filled)
        if filled:
            g.hole((48, 66), 7)
    elif key == "search":
        g.circle((42, 42), 22, False)
        g.line([(58, 58), (80, 80)])
    elif key == "library":
        g.circle((30, 68), 12, True)
        g.circle((62, 60), 10, True)
        g.line([(42, 68), (42, 22), (72, 30), (72, 60)])
    elif key == "settings":
        g.poly(gear_points(), filled, soften=False)
        if filled:
            g.hole((48, 48), 11)
        else:
            g.circle((48, 48), 11, False)
    return g.done()


def main():
    for theme, style in STYLES.items():
        out = ROOT / "icons" / theme
        out.mkdir(parents=True, exist_ok=True)
        for key in KEYS:
            draw(key, style).save(out / f"{key}.png", optimize=True)
        print(f"{theme}: {len(KEYS)} icons")


main()
