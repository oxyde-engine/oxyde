# Super effects

MUGEN's answer to "a super is happening" is two things: the screen dims, and
`SuperPause` puts one small charge animation over the fighter. Everything else
is the character's — a cut-in, a backdrop, an `EnvColor`, a palette flash —
and a fighter whose author drew none of it gets a grey screen and a pause at
the most dramatic moment in the game.

Oxyde draws that moment itself. This page is what it draws, the three settings
that decide how much of it, how AUTO decides, and what a sweep of the whole
roster found about the characters' own super art — including whether it fills
a widescreen display.

## What it looks like

Over the dimmed picture and under the character's foreground art (its `ontop`
explods, the `SuperPause` charge animation, hit sparks), in Oxyde's palette —
ember `#FF7A1A`, cold steel, a white-hot core:

1. **The impact.** One white-hot bloom from the fighter who called the super on
   the opening ticks, gone in a tenth of a second. One per super: nothing in
   the effect brightens the screen a second time, so it cannot strobe, and a
   character that flashes the screen itself on those ticks (a short `EnvColor`
   or `BGPalFX`) gets no second flash from the engine.
2. **The burst.** Two layers of rays from the caller, turning against each
   other: a far layer of thin cold steel rays for depth and a near layer of
   broad ember rays with white-hot cores. Each near ray's red edge is a little
   wider than its blue edge — the chromatic fringe of something genuinely hot.
3. **The rings.** Hexagonal shock fronts — the Oxyde mark — crossing the
   screen: a crisp white front, a thin cold line just outside it and an ember
   wake behind. **One ring per bar the super cost**: the super's level is shown
   by the effect itself rather than by a label over somebody's art. The bars
   are read off the drop in the caller's power when the freeze starts.
4. **The streaks.** Speed lines sliding in towards the caller from the outer
   part of the screen, so the middle of the picture stays readable.
5. **The sparks.** Embers thrown out of the caller, streaking as they fly and
   drifting up as they cool.
6. **The grade.** Everything but the caller goes cold — warm channels down
   more than blue — and the corners darken, so the burst is the only warm
   thing on the screen.
7. **The rim.** The caller's outline traced in white-hot light, and the burst
   kept off their body, so the fighter who called the super is the clearest
   thing in the picture rather than lost in it.

It runs for about three quarters of a second (44 ticks, six more per extra
bar) at the start of any screen freeze long enough to be a super — a
`SuperPause`, or a plain `Pause` of 20 ticks or more — and a longer freeze gets
the rest of its time back for the character's own art.

## The three settings

OPTIONS, PRESENTATION, **SUPER EFFECTS**, written to `[Game] superfx`:

| Value | What you get |
|---|---|
| `OFF` | MUGEN: the character's art and the plain dimming, nothing else |
| `AUTO` (default) | the effect in full when the character brings little super art of its own; an accent when its own art already fills the screen |
| `ALWAYS` | the effect in full on every super, under the character's foreground art |

`superfx = 0` and `superfx = 1`, written by every `oxyde.cfg` from before the
setting had three values, still read as OFF and AUTO.

**The engine never hides, recolours or reorders anything a character draws.**
The effect is composited after MUGEN's darkening and before the foreground,
whatever the setting; it only adds light and shade of its own. AUTO goes
further and stays out of the way of the author's art where it is.

### How AUTO decides

On every frame of the freeze the renderer measures what the caller is drawing
for itself (`Scene::probe_art`): its explods, helpers, projectiles and
afterimage trails — not its own body — rasterised on a coarse grid of the
screen, about 160 cells across, twice: once over black and once over white.
Where the two agree the author's picture replaced what was underneath; where
they differ by the whole range the author drew nothing. The difference is an
opacity that is right for every blend mode at once — an opaque plate counts in
full, an additive glow by how bright it is, a subtractive shadow by how dark. A
cell at least a quarter covered counts as covered. An `EnvColor`, or a
`BGPalFX` strong enough to repaint the stage, held through the pause covers the
whole screen; one over within a few ticks is the author's flash, not its
backdrop, and is not counted.

The share of the screen covered sets the strength:

| Caller's own art covers | AUTO plays |
|---|---|
| under 30% of the screen | the full effect |
| 30% to 60% | a smooth ramp between the two |
| over 60% | the accent: the impact, a light burst and the rings at about a quarter, no streaks, sparks or grade |

and the same grid holds the effect back locally — to 15% where the author's
art covers a cell — so what light there is shows round the art rather than
over it. The measurement is a function of the frame alone, so a screenshot of
a frame is the same however it was reached, and the ramp is continuous, so art
that flickers across a threshold makes the effect breathe rather than blink.

The thresholds come from the roster: see [the audit](#the-roster-audit) below.

## Cost

The effect is drawn on the CPU renderer, so it is built to be cheap:

- Everything soft — the burst, the glow, the flash, the vignette, the grade
  and the rings' wakes — is evaluated on a grid of about 240 rows at any
  window size (every 2 pixels at 480 lines, 3 at 720, 5 at 1080) and spread
  over the frame by interpolation; everything crisp — the ring fronts, the
  streaks, the rim and the sparks — is drawn afterwards at full resolution,
  only where it is.
- The distance and angle of every grid point from a centre are computed once
  per window size, for one quadrant, and mirrored; per frame there are only
  tables over angle and over distance, a few thousand entries each.
- The pass over the frame is fixed point, with no lookups or branches in the
  loop that touches every pixel, and runs on up to four threads, started once
  per frame for both halves; the picture is identical at any thread count.
- When the super darkens the screen, the darkening is applied by the effect's
  own pass instead of the wash painting the frame first — the same picture,
  one full-screen pass fewer.

Measured on the development machine — a shared 12-core QEMU virtual machine
at 2 GHz exposing only SSE2, under a load average of 7 to 15 from other work,
so the numbers are pessimistic and noisy:

| | 640x480 | 960x720 | 1280x720 | 1920x1080 |
|---|---|---|---|---|
| the effect alone, one thread (`superfx_bench`) | 3.5 ms | 5.7 ms | 7.3 ms | 12.5 ms |
| MUGEN's darkening wash, for scale | 0.4 ms | 0.9 ms | 1.1 ms | 2.6 ms |
| extra drawing time per frame a super holds, in the game | | | +5 to +10 ms | +8 to +18 ms |
| the effect it replaces, same measure | | | about +90 ms | about +210 ms |

The in-game row is `oxyde --headless` with `OXYDE_RENDER_EVERY=1`, Kung Fu Man
against Kung Fu Man at `--seed 5`, the median of the 90 frames held by supers
against the same run with `superfx = off`; the summary line `freezes` reports
it. It includes AUTO's measurement (about 0.1 ms) and the caller's outline
(about 0.2 ms). The targets set for this work — 3 ms extra at 1280x720 and
6 ms at 1080p — are not met on this machine; the effect costs about six
darkening washes at 720p, a tenth of what the effect it replaces cost, and on
a desktop processor a fraction of a frame. The pass is written to vectorise
and to split across cores, and neither helps much on this host, where four
threads started per frame bought little under contention.

## The roster audit

`oxtool superfx-audit <game-root>` ([TOOLS.md](TOOLS.md)) fought all 2,412
characters of the test roster against Kung Fu Man with a full meter, at 4:3
(640x480, 320-unit playfield) and at 16:9 (854x480, 427 units), up to two
supers each, and measured every frame of player one's supers. It took 20
minutes on eight cores; the results are in `metrics/superfx-audit/`
(`superfx-audit.tsv`, one row per character, and `summary.txt`).

**1,940 characters threw at least one super** in the time given; 472 did not
and are not counted below.

**78% bring super art of their own.** 1,517 of the 1,940 cover at least a
tenth of the screen with their own explods, helpers and trails, or hold an
`EnvColor` (428 do). Peak coverage of the screen by the character's own art:

| Peak coverage | Characters |
|---|---|
| under 5% | 314 |
| 5% to 10% | 113 |
| 10% to 30% | 279 |
| 30% to 60% | 225 |
| 60% to 95% | 80 |
| 95% and over | 929 |

That distribution is where AUTO's thresholds come from. Below 30% is a charge
aura, a cut-in portrait, a fireball — 706 characters whose supers look like a
grey pause without the engine's effect. Over 60% is a backdrop or a screen
wash — 1,009 characters that already have their moment and get the accent.
The few between are ramped. AUTO dropped to the accent on at least one frame
for 958 characters.

**166 characters' super art stops short of a 16:9
screen** — a full-height backdrop with a bare strip down one side or both, at
16:9 and not at 4:3. Almost all of them are 320x240 plates placed from a
screen edge (`postype = left`, `right`, `front` or `back`): drawn at their
authored size on a 427-unit screen they cover the left three quarters and
leave a quarter of the width showing the stage — MvC-style backdrops such as
Hulk's, Morrigan's, Omega Red's and the Powerpuff Girls', KOF and Saint Seiya
supers, and others. Ten more have a gap at 4:3 as well; that is how their art
was drawn.

**FIT SUPER ART TO SCREEN closes 158 of the 166.** The fit already existed,
unconditionally, as a rule growing any screen-anchored explod at least seven
tenths of the window in both directions. The audit found two faults in that
rule, and it is replaced:

- In a 4:3 window it altered the art of **120 characters** at the shape MUGEN
  draws them at — re-centring tiles and enlarging strips an author drew at
  their own size. It now does nothing unless the window is wider than 4:3:
  **no character's art is changed at 4:3** (re-measured: 0).
- It measured against the window, so a 254-unit strip was grown at 4:3 and
  left alone at 16:9: one character's backdrop filled the screen at one shape
  and stopped short at the other. It now grows only a plate that fills
  MUGEN's 4:3 screen — nineteen twentieths of it in both directions — and
  draws everything smaller exactly as authored.

At 16:9 the fit now changes the picture for 264 characters, uniformly scaled
and centred, so nothing is stretched out of shape. Eight gaps remain, and are
left: five are partial plates (`Ken_MvC`, `MissMarvel`, `Banshee_MvC` — a
254-unit strip — `Metalman`, `DBZ cell`) that cover the same part of a 4:3
screen, two are oversized `p1` explods (`TronBonne`, `wario`) and one is a
helper (`Nameless One`). Growing a helper or a world-space explod to the
window would move art that moves, to close one or two gaps in the roster; the
evidence does not justify it.
