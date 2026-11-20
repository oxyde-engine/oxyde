# Oxyde — the screenpack

The engine's own look, moved out of the binary and into a pack you can edit: a
black circuit board with etched traces, the **OXYDE** wordmark — its O cut as
the HUD's hexagon, in ember, and the rest in cold steel — a hairline rule
broken by an infinity mark, and Oxyde orange for whatever the player is about
to choose.

The title screen is drawn by the engine: `[Title Info] title.style = oxyde`
hands it over, and Oxyde draws its own animated title (the wordmark, every
mode, the highlighted one in orange and the line explaining it) at the
window's own resolution. An engine that ignores the key lays the menu out from
the rest of `[Title Info]` over `[TitleBG]`, as any pack's.

It is also built for **this** archive rather than adapted to it: 1,040
characters and 179 stages, laid out so all of them are reachable.

Installed by `data/mugen.cfg`:

```ini
[Options]
motif = data/oxyde/system.def
```

The pack the install shipped with is untouched in `data/system.def`; putting
that line back restores it. `screenpack = 0` in `oxyde.cfg` turns the whole
mechanism off and the engine draws its own screens instead — which are the
same design, which is the point.

## What is here

| File | What it is |
|---|---|
| `system.def` | The menus: title, character select, versus, options, and the screens that close a run. |
| `system.sff` | 36 sprites — the four backdrops, the wordmark, the select banner, the grid cell, the random cell, both cursors and the team-menu icons. |
| `fight.def` | The in-match HUD: life and power bars, portraits, names, the timer, the combo counter, the round announcements and the win icons. **Generated** — edit the `LAYOUT` table in `build_screenpack.py`, not this file. |
| `fight.sff` | 25 sprites — bar housings, bar fills, the clock badge and the announcements. |
| `font/oxyde-s.fnt` | 11px. Footers, counters, the search box. |
| `font/oxyde-m.fnt` | 15px. Names, the stage line, the title menu. |
| `font/oxyde-l.fnt` | 19px. Headings and the win message. |
| `font/oxyde-xl.fnt` | 46px. The round clock, which is a motif font at 1:1 on a 720p screen and needs its own size to fill the badge. |
| `hud/` | The Oxyde HUD art pack the bars were first cut from. |
| `build_screenpack.py` | Generates every sprite and every font above. |

Sounds come from `data/system.snd` and `data/fight.snd`, which the pack names
without copying.

## The theme

Everything visual is one palette, at the top of `build_screenpack.py` and
copied from `mugen-oxyde/crates/oxyde-render/src/splash.rs`:

| | |
|---|---|
| `VOID` `6,7,9` | the board |
| `TRACE` `24,29,36` / `TRACE_LIT` `46,56,68` | an etched run, and one catching the light |
| `PAD` `38,47,58` | where a run terminates at a via |
| steel `226,232,242` → `96,106,124` | cold steel: the wordmark's XYDE, rims |
| rust `198,92,26` → `88,32,8` | molten rust: the wordmark's hexagonal O, accents |
| `EMBER` `255,140,44` | the one warm accent |
| `CYAN` `96,214,246` | reserved for the current selection, and nothing else |

The board, the rule and the infinity mark are ported from the engine's own
drawing code (`splash.rs`, the same generator with the same seed), and the
wordmark from `brand.rs`, so the pack and the engine's own screens are one
design rather than two that resemble each other. Keep them in step if you change either.

## Why 640x480 for the menus, and 1280x720 for the HUD

The two files are authored on different canvases, because they are answering
different questions. `system.def` is sized to fit a thousand characters in a
grid; `fight.def` is sized to the picture its own artwork was drawn on —
`MugenOxyde_HUD/preview/01_hud_1280x720.jpg` — so the layout table in
`build_screenpack.py` is that mockup's geometry rather than a conversion of
it. The engine fits each motif file to the window by its own `localcoord`, so
the two coexist without either being scaled by hand.

`[Info] localcoord = 640, 480`. Every WinMugen pack is authored in 320x240
units, and a thousand characters do not fit in 320 units at any legible size —
the pack that shipped here asked for 53 columns of 4x5-pixel cells, which is a
wall of coloured dots. At twice the density the grid is **20 x 10 cells of 28
pixels: 200 characters a page, six pages for the roster**, and the fonts have
enough pixels to stay sharp on a 1080p panel.

The trade is that this is a MUGEN 1.0-and-later idea. WinMugen only knows
320x240 and would draw this pack wrong; it is built for the engine in
`mugen-oxyde/`, which scales the whole motif to whatever window it is given.

## The layout

```
 y   0  mode name (centre) - search box (left) - page counter (right)
 y  32  player one's portrait          the pack banner          player two's
 y 133  chosen fighter's name                                   their name
 y 136                        what the mode still wants
 y 156  ...................  the grid: 20 x 10 cells  ...................
 y 459                    the stage the match will use
```

Paths inside `system.def` and `fight.def` are written relative to `data/`
(`spr = oxyde/system.sff`), which is how a pack installed in a subfolder of
`data/` has to write them: that spelling resolves whether the engine looks
beside the file, from the game root, or under `data/`.

## Changing it

Edit `build_screenpack.py` and re-run it:

```bash
python3 data/oxyde/build_screenpack.py
```

The palette is at the top, the grid geometry is one `GRID` dict, the HUD
geometry is one `HUD` dict, and each screen is a function that draws it. The
`.def` files hold the positions; the script holds the art. Change the grid in
both — the backdrop draws the plate the cells sit on, so they have to agree.

Requires Python 3 with Pillow, and DejaVu Sans (any system with
`fonts-dejavu-core` installed).
