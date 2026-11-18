#!/usr/bin/env python3
"""Regenerates the app icon (icon.png / icon.ico / icon.icns) in this folder.

Only needed when changing the design; the generated files are committed so builds
don't depend on Pillow. Usage: pip install Pillow && python3 assets/make_icon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

S = 1024 * 4  # drawn at 4x and downscaled for smooth (anti-aliased) edges
BG = "#1F6AA5"  # CustomTkinter's default blue, so the icon matches the app
FG = "white"
ACCENT = "#F5A623"
OUT = Path(__file__).resolve().parent

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((S * 0.06, S * 0.06, S * 0.94, S * 0.94), radius=S * 0.2, fill=BG)

w = int(S * 0.05)  # stroke width
r = S * 0.08  # node radius
x_main, x_branch = S * 0.37, S * 0.65
y_top, y_bot, y_branch = S * 0.28, S * 0.72, S * 0.40

# Main line plus a branch curving off it: the "multi-profile" fork.
d.line((x_main, y_top, x_main, y_bot), fill=FG, width=w)
# Quadratic Bezier from low on the main line up to the branch node.
p0, p1, p2 = (x_main, y_bot - S * 0.05), (x_branch, y_bot - S * 0.05), (x_branch, y_branch)
curve = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
          (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / 64 for i in range(65))]
d.line(curve, fill=FG, width=w, joint="curve")
for x, y in ((x_main, y_top), (x_main, y_bot)):  # hollow commit rings
    d.ellipse((x - r, y - r, x + r, y + r), fill=FG)
    d.ellipse((x - r + w, y - r + w, x + r - w, y + r - w), fill=BG)
d.ellipse((x_branch - r, y_branch - r, x_branch + r, y_branch + r), fill=ACCENT)

icon = img.resize((1024, 1024), Image.LANCZOS)
icon.resize((512, 512), Image.LANCZOS).save(OUT / "icon.png")
icon.save(OUT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
icon.save(OUT / "icon.icns")
print("Wrote icon.png, icon.ico, icon.icns to", OUT)
