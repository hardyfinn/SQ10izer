#!/usr/bin/env python3
# Mock-up picture of the panel with knobs, jacks and lights drawn in, so the
# layout can be checked without Rack.  python3 tools/preview.py out.png
import os, sys, math, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
svg = open(os.path.join(HERE, "..", "res", "SQ10izer.svg")).read()
L = {}
src = open(os.path.join(HERE, "..", "res", "make_panel.py")).read()
exec(src.split("# ---- LAYOUT")[1].split("CONTROL =")[0].split("\n", 1)[1], L)
g = []
def jack(x, y):
    g.append(f'<circle cx="{x}" cy="{y}" r="4.1" fill="#C9CCD1"/><circle cx="{x}" cy="{y}" r="3.1" fill="#7C8088"/><circle cx="{x}" cy="{y}" r="1.9" fill="#0B0B0C"/>')
def knob(x, y, a, r=4.0):
    g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#26272B" stroke="#3A3C42" stroke-width="0.5"/>')
    ang = math.radians(-135 + 270 * a)
    g.append(f'<line x1="{x}" y1="{y}" x2="{x + (r-0.8)*math.sin(ang):.2f}" y2="{y - (r-0.8)*math.cos(ang):.2f}" stroke="#EEE" stroke-width="0.7" stroke-linecap="round"/>')
def light(x, y, b):
    g.append(f'<circle cx="{x}" cy="{y}" r="1.0" fill="#3a3320"/><circle cx="{x}" cy="{y}" r="1.0" fill="#FFD23C" fill-opacity="{b}"/>')
random.seed(4)
for i in range(16):
    x = L["STEP_X0"] + (i % 8) * L["STEP_DX"]; y = L["ROW_Y"][i // 8]
    knob(x, y, 0.5 + random.uniform(-0.5, 0.5))
    light(x, y + L["LIGHT_DY"], 1.0 if i == 5 else (0.12 if i < 12 else 0))
knob(L["X_STRENGTH"], L["CTRL_Y"], 0.5, 5.0); knob(L["X_LENGTH"], L["CTRL_Y"], 11/15, 5.0)
g.append(f'<circle cx="{L["X_RAND"]}" cy="{L["CTRL_Y"]}" r="3.4" fill="#2B2D33"/><circle cx="{L["X_RAND"]}" cy="{L["CTRL_Y"]}" r="2.4" fill="#4a4126"/>')
for x, y in [(L["X_CLOCK"], L["CTRL_Y"]), (L["X_STRENGTH"], L["CV_Y"]), (L["X_LENGTH"], L["CV_Y"]), (L["X_RAND"], L["CV_Y"]), (L["X_CLOCK"], L["CV_Y"]),
             (L["X_IN"], L["BOT_Y"]), (L["X_OFFSET"], L["BOT_Y"]), (L["X_OUT"], L["BOT_Y"])]:
    jack(x, y)
W = 101.6
for x in (7.6, W - 7.6 - 0):
    for y in (2.5, 126.0): g.append(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#8A8D93"/>')
svg = svg.replace("</svg>", "\n".join(g) + "\n</svg>")
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "preview.png")
tmp = out + ".svg"; open(tmp, "w").write(svg)
pw, ph = 508, 643
open(tmp + ".html", "w").write(f'<html><body style="margin:0;background:#111"><img src="{os.path.basename(tmp)}" style="width:{pw}px;height:{ph}px"></body></html>')
js = f"""const {{chromium}} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage({{viewport: {{width: {pw}, height: {ph}}}, deviceScaleFactor: 2}});
await p.goto('file://{tmp}.html'); await p.waitForTimeout(300);
await p.screenshot({{path: '{out}'}}); await b.close(); }})();"""
open(out + ".js", "w").write(js)
subprocess.run(["node", out + ".js"], check=True, cwd="/tmp")
os.remove(out + ".js"); os.remove(tmp); os.remove(tmp + ".html")
print("wrote", out)
