#!/usr/bin/env python3
# Builds the SQ10izer user guide (HTML), then prints it to A4 PDF with Playwright.
#   python3 docs/make_guide.py out.pdf
import os, sys, subprocess, json, random, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "SQ10izer-Guide.pdf")

AMBER, INK, QUIET, PAPER, TEAL = "#d98a1f", "#26262a", "#8a847a", "#efe9de", "#1f8fa0"

# one fixed "randomised" pattern used all through the guide
r = random.Random(10)
PATTERN = [round(r.uniform(-1, 1), 2) for _ in range(16)]


def bars(values, strength, length=16, play=None, title="", maxc=40):
    """Bar chart of the 16 steps in cents, scaled by strength. Grey = outside LENGTH."""
    cw, gap, h = 22, 5, 120
    w = 46 + 16 * (cw + gap)
    mid = 18 + h / 2
    out = [f'<svg viewBox="0 0 {w} {h + 44}" width="100%" font-family="Inter, Helvetica" font-size="10">']
    for c in (-40, -20, 0, 20, 40):
        y = mid - c / maxc * h / 2
        out.append(f'<line x1="40" y1="{y}" x2="{w}" y2="{y}" stroke="{"#bdb5a6" if c == 0 else "#e6e0d4"}" stroke-width="{1.2 if c == 0 else 0.8}"/>')
        out.append(f'<text x="34" y="{y + 3.5}" text-anchor="end" fill="{QUIET}">{c:+d}c</text>' if c else f'<text x="34" y="{y + 3.5}" text-anchor="end" fill="{QUIET}">0</text>')
    for i, v in enumerate(values):
        x = 46 + i * (cw + gap)
        cents = v * strength
        y0, y1 = mid, mid - cents / maxc * h / 2
        inside = i < length
        col = AMBER if inside else "#d6cfc2"
        if play == i:
            col = "#b4561a"
        out.append(f'<rect x="{x}" y="{min(y0, y1):.1f}" width="{cw}" height="{max(abs(y1 - y0), 1):.1f}" rx="2" fill="{col}"/>')
        out.append(f'<text x="{x + cw / 2}" y="{h + 34}" text-anchor="middle" fill="{INK if inside else "#bdb5a6"}" font-weight="700">{i + 1}</text>')
        if length < 16 and i == length - 1:
            out.append(f'<path d="M{x + cw + gap / 2} 10 V{h + 24}" stroke="{TEAL}" stroke-width="1.6" stroke-dasharray="4 3"/>')
            out.append(f'<text x="{x + cw + gap / 2 + 4}" y="14" fill="{TEAL}" font-weight="700">loops here</text>')
    out.append("</svg>")
    cap = f'<div class="gcap"><b>{title}</b></div>' if title else ""
    return f'<div class="grid">{cap}{"".join(out)}</div>'


def box(x, y, w, h, title, sub="", fill="#2b2c31", ink="#f3efe8"):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}"/>'
    s += f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 4)}" text-anchor="middle" fill="{ink}" font-weight="700" font-size="12" dominant-baseline="middle">{title}</text>'
    if sub:
        s += f'<text x="{x + w / 2}" y="{y + h / 2 + 11}" text-anchor="middle" fill="#bdb5a6" font-size="9.5" dominant-baseline="middle">{sub}</text>'
    return s


def cable(pts, col, label="", lx=None, ly=None):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    s = f'<path d="{d}" stroke="{col}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    x, y = pts[-1]
    s += f'<circle cx="{x}" cy="{y}" r="4.5" fill="{col}"/>'
    if label:
        s += f'<text x="{lx}" y="{ly}" fill="{col}" font-size="10" font-weight="700">{label}</text>'
    return s


def patch_basic():
    g = ['<svg viewBox="0 0 640 250" width="100%" font-family="Inter, Helvetica">']
    g.append(box(20, 20, 130, 50, "CLOCK", "e.g. Long Form, Clocked"))
    g.append(box(230, 20, 160, 50, "SEQUENCER", "quantised pitch + gate"))
    g.append(box(230, 150, 160, 70, "SQ10izer", "CLOCK · V/OCT IN → OUT", fill="#3a332a"))
    g.append(box(470, 20, 150, 50, "OSCILLATOR", "V/OCT"))
    g.append(box(470, 150, 150, 70, "ENVELOPE / VCA", "gate → envelope"))
    g.append(cable([(150, 45), (230, 45)], "#c94b4b", "clock", 168, 38))
    g.append(cable([(90, 70), (90, 170), (230, 170)], "#c94b4b", "same clock", 98, 120))
    g.append(cable([(310, 70), (310, 150)], "#3f86c9", "pitch", 318, 115))
    g.append(cable([(390, 185), (440, 185), (440, 60), (470, 60)], AMBER, "OUT", 446, 120))
    g.append(cable([(390, 35), (410, 35), (410, 120), (545, 120), (545, 150)], "#4fa36b", "gate", 480, 114))
    g.append("</svg>")
    return "".join(g)


def patch_rig():
    g = ['<svg viewBox="0 0 640 170" width="100%" font-family="Inter, Helvetica">']
    g.append(box(10, 20, 140, 54, "METROPOLIX", "pitch CV + clock"))
    g.append(box(190, 20, 130, 54, "disting NT", "inputs (DC)"))
    g.append(box(360, 20, 120, 54, "VCV: SQ10izer", "via Audio module", fill="#3a332a"))
    g.append(box(510, 20, 120, 54, "disting NT", "output → Mangrove"))
    g.append(cable([(150, 40), (190, 40)], "#3f86c9"))
    g.append(cable([(150, 56), (190, 56)], "#c94b4b"))
    g.append(cable([(320, 47), (360, 47)], "#6b6660"))
    g.append(cable([(480, 47), (510, 47)], AMBER))
    g.append('<text x="10" y="110" font-size="10.5" fill="#26262a">Pitch and clock come in through two NT inputs, which show up as inputs on VCV\'s Audio module.</text>')
    g.append('<text x="10" y="126" font-size="10.5" fill="#26262a">SQ10izer\'s OUT goes back to an NT output and on to the oscillator (Mangrove, Three Sisters, Just Friends).</text>')
    g.append('<text x="10" y="142" font-size="10.5" fill="#6b6660">The NT is DC-coupled, so it passes pitch CV. Check the tuning once by ear: the audio path can add a small offset.</text>')
    g.append("</svg>")
    return "".join(g)


# numbered callouts on the panel picture: (n, x mm, y mm)
CALLOUTS = [(1, 3.0, 24.0), (2, 5.5, 75.0), (3, 29.5, 75.0), (4, 54.5, 75.0), (5, 79.0, 75.0),
            (6, 79.0, 92.0), (7, 5.5, 113.0), (8, 51.5, 113.0), (9, 77.5, 113.0)]


def panel_with_callouts():
    dots = "".join(
        f'<div class="co" style="left:{x / 101.6 * 100:.2f}%;top:{y / 128.5 * 100:.2f}%">{n}</div>' for n, x, y in CALLOUTS)
    return f'<div class="pwrap"><img src="panel.png">{dots}</div>'


P = []
P.append(f"""
<section class="page cover">
  <div>
    <div class="kicker">Haer · VCV Rack module · 20 HP · version 2.1</div>
    <h1>SQ10izer</h1>
    <p class="lead">Sixteen steps of small, unquantised pitch offsets, added to any V/OCT signal on each clock.
    It gives a perfectly quantised sequencer the hand-tuned, never-quite-in-tune character of an early
    analogue step sequencer such as the Korg SQ-10, where every step's pitch was set by hand on a knob and no two steps were ever quite in tune.</p>
  </div>
  <div class="two" style="align-items:flex-end">
    <div style="flex:0 0 72mm"><img src="panel.png" style="width:72mm;border-radius:1mm;box-shadow:0 .6mm 2mm rgba(0,0,0,.18)"></div>
    <div>
      <h3>In this guide</h3>
      <ol class="toc">
        <li>The idea in one picture</li>
        <li>The panel</li>
        <li>STRENGTH and LENGTH</li>
        <li>First patch, cable by cable</li>
        <li>Using it with your rig</li>
        <li>Patch ideas</li>
        <li>Reference</li>
      </ol>
      <p class="small">Plugin file: SQ10izer-2.1.0-mac-arm64.vcvplugin. Drop it into Rack's plugins folder (or double-click it) and restart Rack.</p>
    </div>
  </div>
</section>
""")

P.append(f"""
<section class="page">
  <h2>1 · The idea in one picture</h2>
  <p>Your sequencer sends notes that sit exactly on the grid. SQ10izer keeps its own row of 16 small pitch
  offsets and moves through them on every clock. On each step it adds that step's offset to the incoming pitch, so the same
  melody comes out a little sharp here and a little flat there, in a pattern that repeats.</p>
  {bars(PATTERN, 20, title="A randomised pattern at STRENGTH 20 cents. Each bar is how far that step is pulled off pitch.")}
  <div class="box">
    <h3>How big is a cent?</h3>
    <p>100 cents is one semitone. The offsets here are much smaller than that, so you never hear a wrong note, just a note that leans.
    Roughly: <b>under 5 cents</b> is felt more than heard (warmth, chorus-like movement between voices);
    <b>10 to 20 cents</b> sounds clearly analogue and a bit loose; <b>30 to 40 cents</b> is seasick and lo-fi, great for hooks you want to sound unstable.</p>
    <p class="small">In volts: 1 V per octave means 1 cent ≈ 0.83 mV, so 40 cents is about 33 mV.</p>
  </div>
  <h3>Why not just add a random LFO?</h3>
  <p>An LFO drifts smoothly and never repeats. SQ10izer gives each step its <i>own</i> fixed tuning that comes back every loop,
  which is what made the SQ-10 sound the way it did: the third note of the riff is always a bit flat, the seventh always a bit sharp.
  Your ear hears it as character, not as a fault.</p>
</section>
""")

P.append(f"""
<section class="page">
  <h2>2 · The panel</h2>
  <div class="two">
    <div style="flex:0 0 74mm">{panel_with_callouts()}</div>
    <div>
      <table>
        <tr><th>#</th><th>Part</th><th>What it does</th></tr>
        <tr><td>1</td><td>Steps 1–16</td><td>One knob per step. Noon is in tune, full left −100%, full right +100% of STRENGTH. The light underneath shows the playing step; steps inside the loop glow faintly. Hover to read % and cents; double-click puts a step back in tune.</td></tr>
        <tr><td>2</td><td>LENGTH + CV</td><td>Where the pattern loops, 1 to 16 steps. CV adds 1.5 steps per volt.</td></tr>
        <tr><td>3</td><td>STRENGTH + CV</td><td>How many cents +100% means: 0 to 40, starts at 20. Scales all 16 steps live. CV adds 4 cents per volt.</td></tr>
        <tr><td>4</td><td>RANDOMISE + TRIG</td><td>Gives all 16 step knobs new random positions. The knobs really move, so you can fine-tune by hand afterwards.</td></tr>
        <tr><td>5</td><td>CLOCK</td><td>Each trigger moves on one step. Use the same clock as your sequencer.</td></tr>
        <tr><td>6</td><td>RESET</td><td>Back to the start: the next clock plays step 1.</td></tr>
        <tr><td>7</td><td>V/OCT IN</td><td>The pitch to bend. Polyphonic works: every voice gets the same offset.</td></tr>
        <tr><td>8</td><td>OFFSET</td><td>Just the current offset, as a voltage, with no input pitch added.</td></tr>
        <tr><td>9</td><td>OUT</td><td>V/OCT IN plus the current offset.</td></tr>
      </table>
    </div>
  </div>
  <div class="box"><b>The signal path is simple:</b> OUT = V/OCT IN + (step knob × STRENGTH). Nothing is quantised, smoothed or delayed,
  and the offset changes the instant the clock arrives, so it lines up with your sequencer's note change.</div>
</section>
""")

P.append(f"""
<section class="page">
  <h2>3 · STRENGTH and LENGTH</h2>
  <h3>STRENGTH turns the whole pattern up or down</h3>
  <p>The step knobs hold the <i>shape</i> of the pattern; STRENGTH sets its <i>size</i>. Here is the same pattern at three settings:</p>
  {bars(PATTERN, 8, title="STRENGTH 8 cents: subtle")}
  {bars(PATTERN, 20, title="STRENGTH 20 cents: clearly loose")}
  {bars(PATTERN, 40, title="STRENGTH 40 cents: seasick")}
  <p>Because it is live, STRENGTH is a performance control: turn it to 0 and you are perfectly in tune, bring it up and the same wobble returns.
  An LFO or envelope into STRENGTH CV does this for you.</p>
</section>
<section class="page">
  <h2>3 · STRENGTH and LENGTH, continued</h2>
  <h3>LENGTH sets where the pattern loops</h3>
  {bars(PATTERN, 20, length=7, title="LENGTH 7: steps 1–7 repeat, steps 8–16 are kept but not played")}
  <p>If LENGTH matches your sequence (16 and 16, or 8 and 8) every note always gets the same tuning. If it does not match,
  the tuning slides against the melody:</p>
  <div class="box">
    <p><b>Sequence 16 steps, SQ10izer LENGTH 7.</b> Note 1 of the riff gets offset 1 on the first pass, offset 3 on the second
    (because 16 ÷ 7 leaves 2), offset 5 on the third, and so on. The riff only lines up with the tuning again after 7 bars.
    You hear the same notes with a slowly changing accent, the kind of slow, self-shifting pattern Autechre are good at.</p>
  </div>
  <p>Good LENGTH values against a 16-step sequence: <b>15</b> (shifts by one each bar, very gradual), <b>12</b> (lines up every 3 bars),
  <b>7, 5 or 11</b> (long, irregular cycles). LENGTH CV lets a slow ramp or a Long Form lane change this between sections.</p>
  <h3>RANDOMISE</h3>
  <p>The button and the TRIG jack give all 16 steps new random positions, spread evenly between −100% and +100%.
  Then listen, and turn back any step that is too far out. Steps past LENGTH are randomised too, so if you lengthen the loop later they are ready.</p>
</section>
""")

P.append(f"""
<section class="page">
  <h2>4 · First patch, cable by cable</h2>
  <div class="fig">{patch_basic()}</div>
  <div class="step"><span class="num">1</span><div>Put a clock, your sequencer, SQ10izer, an oscillator and an envelope + VCA in the rack.</div></div>
  <div class="step"><span class="num">2</span><div>Clock out → sequencer CLOCK, and the <b>same</b> clock → SQ10izer <span class="jack">CLOCK</span>. (Use a stackable cable or a mult.)</div></div>
  <div class="step"><span class="num">3</span><div>Sequencer pitch (V/OCT or CV) → SQ10izer <span class="jack">V/OCT IN</span>.</div></div>
  <div class="step"><span class="num">4</span><div>SQ10izer <span class="jack">OUT</span> → oscillator V/OCT. Sequencer gate → envelope, envelope → VCA as usual.</div></div>
  <div class="step"><span class="num">5</span><div>If your sequencer has a reset out, send it to SQ10izer <span class="jack">RESET</span> so step 1 always lands on the first note.</div></div>
  <div class="step"><span class="num">6</span><div>Turn STRENGTH to 0 and tune the oscillator. Then bring STRENGTH to about 15, press <span class="k">RANDOMISE</span> until you like it, and nudge any steps that sound wrong.</div></div>
  <div class="box">
    <h3>Variations to try</h3>
    <ul>
      <li>Set LENGTH to 7 or 15 so the tuning drifts against the riff (section 3).</li>
      <li>Send a slow triangle LFO (64 to 128 bars) into STRENGTH CV, with the knob at about 10.</li>
      <li>Use a second SQ10izer with a different LENGTH on the bassline, so bass and lead drift apart.</li>
    </ul>
  </div>
</section>
""")

P.append(f"""
<section class="page">
  <h2>5 · Using it with your rig</h2>
  <p>SQ10izer lives in VCV, but it works just as well on hardware sequences, with the disting NT as the bridge.</p>
  <div class="fig">{patch_rig()}</div>
  <ol>
    <li>In VCV, add an <b>Audio</b> module set to the disting NT. Patch the NT input carrying Metropolix pitch → SQ10izer V/OCT IN, and the NT input carrying the clock → SQ10izer CLOCK.</li>
    <li>SQ10izer OUT → an Audio module output → an NT output → your oscillator's V/OCT.</li>
    <li>Set STRENGTH to 0 and check the oscillator still tracks properly. If notes are a touch flat or sharp overall, fix that with the oscillator's fine tune, not with SQ10izer.</li>
    <li>Then bring in STRENGTH as normal.</li>
  </ol>
  <div class="box">
    <h3>With chords from the Hapax</h3>
    <p>Chords coming into VCV as polyphonic V/OCT (through VCV's MIDI-CV module, polyphony set to 4 or more) can go straight into V/OCT IN.
    Every voice moves together, so the chord keeps its shape but the whole thing leans. For chords that beat against themselves,
    send <b>OFFSET</b> into just one oscillator's fine tune or FM input instead.</p>
  </div>
  <div class="box">
    <h3>With Long Form</h3>
    <p>Long Form's lanes make good controllers for SQ10izer: one lane into STRENGTH CV (in tune for the intro, loose in the breakdown),
    and an ACT change into RANDOMISE TRIG so each new section gets a new tuning pattern.</p>
  </div>
</section>
""")

P.append(f"""
<section class="page">
  <h2>6 · Patch ideas</h2>
  <h3>Detroit strings that lean</h3>
  <p>Pad chords from the Hapax, poly into V/OCT IN, STRENGTH 8 to 12, LENGTH 4 so each chord change has its own small lean.
  Feels like an old string machine that never quite stayed in tune. Variation: LENGTH 3 against 4-chord loops.</p>
  <h3>Drunk acid line</h3>
  <p>A 16-step bass sequence with slides, STRENGTH 25 to 35, LENGTH 16. Randomise until two or three notes stick out, then leave it.
  Variation: STRENGTH CV from an envelope triggered by accents, so accented notes are the ones that go off pitch.</p>
  <h3>Self-mutating loop</h3>
  <p>A clock divider (every 8 or 16 bars) into RANDOMISE TRIG. The melody stays put but its tuning pattern re-rolls now and then,
  so the loop never goes stale. Variation: a Bernoulli gate or Marbles t-output into TRIG, so re-rolls happen only sometimes.</p>
  <h3>Fade in, fade out</h3>
  <p>A slow LFO or envelope into STRENGTH CV with the knob at 0: in tune for the drop, wobbling through the breakdown.
  The pattern stays the same, only its depth changes, so it feels like the same instrument drifting rather than a new effect.</p>
  <h3>Two voices, one riff</h3>
  <p>Mult your sequencer pitch into two SQ10izers with different LENGTHs (16 and 15), each driving its own oscillator.
  The two voices play the same notes but tune differently on each pass, which gives a slow, shifting chorus.</p>
  <h3>Not just pitch</h3>
  <p>OFFSET is a small stepped voltage that repeats with LENGTH. Turn STRENGTH up and use OFFSET on a filter cutoff, a wavefolder
  or a delay time for a subtle, repeating per-step variation.</p>
</section>
""")

P.append(f"""
<section class="page">
  <h2>7 · Reference</h2>
  <table>
    <tr><th>Control / jack</th><th>Range</th><th>Notes</th></tr>
    <tr><td>Step 1–16</td><td>−100% to +100%</td><td>Default 0 (in tune). Offset = position × STRENGTH.</td></tr>
    <tr><td>STRENGTH</td><td>0 to 40 cents</td><td>Default 20. Applies live to every step.</td></tr>
    <tr><td>STRENGTH CV</td><td>+1 V = +4 cents</td><td>Added to the knob, total kept between 0 and 40.</td></tr>
    <tr><td>LENGTH</td><td>1 to 16 steps</td><td>Default 16.</td></tr>
    <tr><td>LENGTH CV</td><td>+1 V = +1.5 steps</td><td>Added to the knob, rounded, kept between 1 and 16. If the loop shrinks past the playing step, it jumps back to step 1.</td></tr>
    <tr><td>RANDOMISE / TRIG</td><td>trigger above 1 V</td><td>All 16 steps get new, evenly spread random positions. The button lights briefly.</td></tr>
    <tr><td>CLOCK</td><td>trigger above 1 V</td><td>One step per rising edge.</td></tr>
    <tr><td>RESET</td><td>trigger above 1 V</td><td>Next clock plays step 1. A clock in the same millisecond as a reset is ignored, so reset and clock can arrive together.</td></tr>
    <tr><td>V/OCT IN</td><td>any, poly up to 16</td><td>Unplugged: OUT gives the offsets on their own.</td></tr>
    <tr><td>OUT</td><td>poly, same channels as IN</td><td>IN + offset.</td></tr>
    <tr><td>OFFSET</td><td>mono, ±33 mV max</td><td>The offset alone.</td></tr>
  </table>
  <h3>Rack menu commands</h3>
  <ul>
    <li><b>Initialize</b> (Ctrl/Cmd-I): every step back to in tune, STRENGTH 20, LENGTH 16.</li>
    <li><b>Randomize</b> (Ctrl/Cmd-R): randomises the step knobs but leaves STRENGTH and LENGTH alone.</li>
    <li><b>Bypass</b> (Ctrl/Cmd-E): V/OCT IN passes straight to OUT, in tune.</li>
  </ul>
  <h3>Good to know</h3>
  <ul>
    <li>The playing step is saved with the patch.</li>
    <li>Patches saved with version 2.0 load with the steps in the wrong places (that version stored cents, this one stores %). Press RANDOMISE or re-dial them.</li>
    <li>The version number stays 2.x, because Rack 2 skips plugins numbered 3.x.</li>
  </ul>
</section>
""")

EXTRA = """
.pwrap { position: relative; width: 74mm; }
.pwrap img { width: 100%; border-radius: 1mm; display: block; }
.co { position: absolute; transform: translate(-50%, -50%); width: 5.2mm; height: 5.2mm; border-radius: 50%;
      background: #d98a1f; color: #fff; font-weight: 700; font-size: 8pt; line-height: 5.2mm; text-align: center;
      box-shadow: 0 0 0 .5mm #fff; }
.grid svg { display: block; }
"""
CSS = open(os.path.join(HERE, "guide.css")).read() + EXTRA
doc = f"<!doctype html><html><head><meta charset='utf-8'><title>SQ10izer user guide</title><style>{CSS}</style></head><body>{''.join(P)}</body></html>"
build = os.path.join(HERE, "build")
os.makedirs(build, exist_ok=True)
open(os.path.join(build, "guide.html"), "w").write(doc)
shutil.copy(os.path.join(ROOT, "panel-preview.png"), os.path.join(build, "panel.png"))
js = f"""const {{chromium}} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{os.path.join(build, "guide.html")}'); await p.waitForTimeout(400);
await p.pdf({{path: {json.dumps(OUT)}, format: 'A4', printBackground: true, preferCSSPageSize: true}});
await b.close(); }})();"""
open(os.path.join(build, "pdf.js"), "w").write(js)
subprocess.run(["node", os.path.join(build, "pdf.js")], check=True, cwd="/tmp")
print("wrote", OUT)
