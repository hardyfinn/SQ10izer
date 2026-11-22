# SQ10izer

A VCV Rack module by Haer (20 HP). It takes a clock and a V/OCT pitch, and on
every clock adds a small, unquantised offset (up to ±40 cents) from one of 16 steps. A perfectly
quantised sequencer then plays slightly out of tune in a repeating way, like an
early analogue step sequencer where every step's pitch was dialled in by hand
and no two steps were ever quite in tune.

![panel](panel-preview.png)

## The panel

| Part | What it does |
|---|---|
| **Steps 1–16** | One knob per step, from −100% (full left, flat) through in tune (noon) to +100% (full right, sharp). How many cents 100% means is set by STRENGTH. Hover a knob to read its offset in % and cents; double-click to put it back in tune. The light under each knob shows the playing step; steps inside the loop glow faintly. |
| **LENGTH** + CV | Where the pattern loops, 1 to 16 steps. The CV adds 1.5 steps per volt. |
| **STRENGTH** + CV | How far the whole pattern pulls away from in tune: a step at full turn shifts the pitch by this much, 0 to 40 cents (starts at 20). It acts live on all 16 steps at once, so turning it down fades the wobble out and turning it up makes the same pattern wilder. At 5 cents you get a faint shimmer, at 40 a properly drunk sequencer. The CV adds 4 cents per volt. |
| **RANDOMISE** button + TRIG | Sets all 16 step knobs to new random positions. The knobs really move, so you can then fine-tune any step by hand. |
| **CLOCK** | Each trigger moves on one step. Use the same clock as the sequencer feeding V/OCT IN. |
| **RESET** | Back to the start: the next clock plays step 1. |
| **V/OCT IN** | The pitch to wobble. Polyphonic is fine: every voice gets the same offset. Nothing plugged in = the offsets on their own. |
| **OFFSET** | Just the step offset as a voltage (no input pitch added). |
| **OUT** | V/OCT IN plus the step offset. |

Rack's own **Randomize** (Ctrl/Cmd-R) also randomises the steps but leaves STRENGTH and LENGTH alone. Rack's **Initialize** puts every step back in tune.

## Patch ideas

1. **Basic SQ wobble.** Clock into your sequencer and into SQ10izer's CLOCK. Sequencer pitch into V/OCT IN, OUT into the oscillator. STRENGTH around 10 to 20 cents, press RANDOMISE until it sounds right, then nudge single steps.
2. **Out-of-phase loops.** Set LENGTH to something that doesn't match the sequence (sequence 16, SQ10izer 7 or 5). The same notes come round with a different tuning each time, which slowly shifts the feel without changing the melody.
3. **Drift over a track.** Slow LFO or envelope into STRENGTH CV: start in tune, let the wobble creep in during a breakdown, take it out again for the drop. The pattern stays the same, only its depth changes.
4. **Mutating pattern.** A slow clock divider (every 8 or 16 bars) into RANDOMISE TRIG: the tuning pattern re-rolls now and then while the notes stay put.
5. **Chords that beat.** Poly chord into V/OCT IN: the whole chord moves together. For a looser chord, use OFFSET into a second oscillator's fine-tune or FM input instead.

## Building

```
python3 res/make_panel.py        # panel -> res/SQ10izer.svg (needs fonttools + Inter)
python3 tools/preview.py out.png # mock-up picture of the panel
make dist RACK_DIR=...           # or let GitHub Actions build it
```

The version stays 2.x: Rack 2 skips plugins numbered 3.x.

## Licence

MIT (see `LICENSE.txt`): you're free to use, change, port (VST/CLAP, other platforms, hardware) and share this code, as long as the copyright notice and licence text come along. Fonts on the panel (Inter, Climate Crisis) are under the SIL Open Font Licence.
