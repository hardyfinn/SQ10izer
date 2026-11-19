#!/usr/bin/env python3
# Draws res/SQ10izer.svg. VCV Rack can't draw SVG <text>, so every label is
# turned into outline paths with fontTools. Positions are in mm and must match
# src/SQ10izer.cpp (the numbers in the LAYOUT block are the same in both).
#   pip install fonttools
#   python3 res/make_panel.py
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.environ.get("PANEL_FONT_BOLD", "/usr/share/fonts/opentype/inter/Inter-Bold.otf")
FONT_MED = os.environ.get("PANEL_FONT_MED", "/usr/share/fonts/opentype/inter/Inter-Medium.otf")

W, H = 101.6, 128.5  # 20 HP

BG = "#24211E"
BG_DARK = "#181614"
LINE = "#3A3631"
INK = "#F1E9DA"
SOFT = "#A39B8E"
AMBER = "#F2A541"

# ---- LAYOUT (same numbers in src/SQ10izer.cpp) ----
STEP_X0, STEP_DX = 10.55, 11.5
ROW_Y = [28.0, 50.0]
LIGHT_DY = 6.6
X_STRENGTH, X_LENGTH, X_RAND, X_CLOCK = 38.0, 14.0, 62.0, 87.0
CTRL_Y, CV_Y = 75.0, 92.0
BOT_Y = 113.0
X_IN, X_OFFSET, X_OUT = 14.0, 60.0, 86.0

CONTROL = 3.2   # control label size (project standard)
JACK = 2.9      # jack label size (project standard)

fonts = {}


def text(s, x, y, size, font=FONT_BOLD, fill=INK, anchor="middle", spacing=0.04):
    """SVG path for string s; (x, y) is the baseline point in mm."""
    if font not in fonts:
        f = TTFont(font)
        fonts[font] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    f, gs, cmap, upm = fonts[font]
    scale = size / upm
    track = spacing * upm
    names = [cmap[ord(c)] for c in s]
    width = sum(gs[n].width + track for n in names) - track
    x0 = {"middle": x - width * scale / 2, "end": x - width * scale}.get(anchor, x)
    pen = SVGPathPen(gs)
    cx = 0.0
    for n in names:
        gs[n].draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + cx * scale, y)))
        cx += gs[n].width + track
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>'


parts = []
add = parts.append

add(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

# title, with a little stepped line next to it
add(text("SQ10izer", 6.0, 11.4, 4.8, FONT_BOLD, INK, anchor="start", spacing=0.06))
wx, wy = 33.5, 9.8
add(f'<path d="M{wx} {wy} h2.2 v-1.3 h2.2 v2.1 h2.2 v-0.6 h2.2 v-1.9 h2.2 v1.4 h2.2" '
    f'stroke="{AMBER}" stroke-width="0.55" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
add(text("unquantised step offsets", W - 6.0, 11.0, 2.6, FONT_MED, SOFT, anchor="end"))

# step area: a darker band per row, step numbers above each knob
for r, y in enumerate(ROW_Y):
    add(f'<rect x="3.5" y="{y - 10.9}" width="{W - 7.0}" height="{LIGHT_DY + 13.6}" rx="1.4" fill="{BG_DARK}"/>')
    for i in range(8):
        x = STEP_X0 + i * STEP_DX
        add(text(str(r * 8 + i + 1), x, y - 6.6, CONTROL, FONT_BOLD, INK))

# controls
add(f'<line x1="3.5" y1="62.6" x2="{W - 3.5}" y2="62.6" stroke="{LINE}" stroke-width="0.35"/>')
LBL_Y = CTRL_Y - 8.0
add(text("STRENGTH", X_STRENGTH, LBL_Y, CONTROL))
add(text("LENGTH", X_LENGTH, LBL_Y, CONTROL))
add(text("RANDOMISE", X_RAND, LBL_Y, CONTROL))
add(text("CLOCK", X_CLOCK, LBL_Y, JACK))
JL_Y = CV_Y - 6.4
add(text("CV", X_STRENGTH, JL_Y, JACK))
add(text("CV", X_LENGTH, JL_Y, JACK))
add(text("TRIG", X_RAND, JL_Y, JACK))
add(text("RESET", X_CLOCK, JL_Y, JACK))
# small scale marks under the RANGE and LENGTH knobs
add(text("0", X_STRENGTH - 5.6, CTRL_Y + 6.6, 2.4, FONT_MED, SOFT))
add(text("40c", X_STRENGTH + 6.2, CTRL_Y + 6.6, 2.4, FONT_MED, SOFT))
add(text("1", X_LENGTH - 5.6, CTRL_Y + 6.6, 2.4, FONT_MED, SOFT))
add(text("16", X_LENGTH + 5.8, CTRL_Y + 6.6, 2.4, FONT_MED, SOFT))

# bottom: IN --(+)--> OUT, with the OFFSET tap
add(f'<line x1="3.5" y1="99.4" x2="{W - 3.5}" y2="99.4" stroke="{LINE}" stroke-width="0.35"/>')
add(f'<rect x="{X_OFFSET - 7.0}" y="102.2" width="{X_OUT - X_OFFSET + 14.0}" height="17.6" rx="1.4" fill="{BG_DARK}"/>')
BL_Y = BOT_Y - 6.6
add(text("V/OCT IN", X_IN, BL_Y, JACK))
add(text("OFFSET", X_OFFSET, BL_Y, JACK))
add(text("OUT", X_OUT, BL_Y, JACK, fill=AMBER))
PX = (X_IN + X_OFFSET) / 2 + 2.0
add(f'<line x1="{X_IN + 5.0}" y1="{BOT_Y}" x2="{PX - 2.2}" y2="{BOT_Y}" stroke="{SOFT}" stroke-width="0.45"/>')
add(f'<circle cx="{PX}" cy="{BOT_Y}" r="2.2" fill="none" stroke="{AMBER}" stroke-width="0.45"/>')
add(f'<path d="M{PX - 1.2} {BOT_Y} h2.4 M{PX} {BOT_Y - 1.2} v2.4" stroke="{AMBER}" stroke-width="0.45"/>')
add(f'<line x1="{PX + 2.2}" y1="{BOT_Y}" x2="{X_OFFSET - 7.6}" y2="{BOT_Y}" stroke="{SOFT}" stroke-width="0.45"/>')
add(text("steps", PX, BOT_Y + 6.4, 2.4, FONT_MED, SOFT))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">\n'
       + "\n".join(parts) + "\n</svg>\n")
open(os.path.join(HERE, "SQ10izer.svg"), "w").write(svg)
print("ok")

# --- Haer maker logo (res/haer_logo.py) on the bottom rail
import sys as _sys
_sys.path.insert(0, HERE)
import haer_logo
haer_logo.add_to_file(os.path.join(HERE, "SQ10izer.svg"), x=W / 2, y=126.0, cap=3.0, bg=BG)
