# Authoring screen packs for Oxyde

Oxyde reads **standard MUGEN screen packs** (the "motif"). If a pack loads in
MUGEN 1.1, it loads in Oxyde — the engine builds the screen from `system.def`
and `fight.def` exactly as MUGEN does, resolving the sprite file, sounds and
fonts against the pack's folder and honouring `[Info] localcoord`. Both
**WinMUGEN (4:3)** and **MUGEN 1.1 (hi-res / localcoord)** packs work, as do
Ikemen GO motifs (an Ikemen motif *is* a `system.def`).

So the short version: **author a normal MUGEN 1.1 screen pack.** The rest of
this document is the exact file contract, the two Oxyde-specific rules, how to
test, and the optional Lua layer for Oxyde's extra modes.

---

## 1. What a pack ships

A screen pack is a folder named in `data/system.def` (or selected in Options).
It contains, all resolved relative to the `system.def` folder via its `[Files]`
section:

| File | Purpose |
|---|---|
| `system.def` | Title screen, main menu, the character-**select** grid layout, VS screen, continue/win screens, fonts and the UI sprite file. The definition the engine draws from. |
| `fight.def` | In-fight HUD: life bars, power bars, timer, round/KO graphics, combo counter, win icons. |
| one `.sff` | Every UI sprite the two `.def` files reference by `group, image`. |
| one `.snd` | Menu/cursor/select sounds. |
| up to **8 fonts each** | `font1`..`font8` in `system.def`, and again in `fight.def` — `.fnt` bitmap fonts, `.def`-based fonts, or TrueType where supported. |

The loader reads `[Info] localcoord` to know the pack's design resolution and
letterboxes/anchors it to the player's actual window (a 16:9 `fight.def` in a
4:3 window has its spare height handled automatically, and vice-versa), so you
author at one resolution and it fits every screen.

### Sections the engine reads from `system.def`
- `[Info]` — `name`, `author`, `localcoord`
- `[Files]` — `spr`, `snd`, `font1..font8`, `logo.storyboard`, `intro.storyboard`, `select` (the roster list file — see rule #1 below), `fight`
- `[Title Info]` — the main-menu position, font, spacing, cursor, and the menu item list
- `[Select Info]` — the character-select screen: grid rows/columns, cell size/spacing, the P1/P2 cursor and portrait positions, the random cell, the stage/"press start" text
- `[VS Screen]`, `[Victory Screen]`, `[Continue Screen]`, `[Game Over Screen]` — the between-match screens

### From `fight.def`
- `[Lifebar]`, `[Powerbar]`, `[Face]`, `[Name]`, `[Time]`, `[Combo]`, `[Round]`, `[WinIcon]` — every HUD element, by sprite number and position.

Everything above is **stock MUGEN** — write it the way you would for MUGEN 1.1.

### `[VS Screen]` portraits: fixed scale or fit-to-box

Stock MUGEN sizes each versus portrait with `p1.scale`/`p2.scale`, a fixed
factor applied to the character's own `9000,1` portrait. That looks right only
while every character's portrait is the same resolution — pair an HD portrait
with a classic low-res one and the HD one renders far larger. Oxyde adds an
optional **fit-to-box** sizing:

```ini
[VS Screen]
p1.pos    = 41, 83       ; the near corner of the box
p1.window = 240, 250     ; fit the portrait into a 240x250 box (motif coords)
p2.pos    = 599, 83
p2.window = 240, 250
```

With `p?.window` set, the portrait is scaled — up or down — to fit the box and
centred in it, so any two characters render at matched size regardless of their
portrait resolution. Drop the key to fall back to the fixed `p?.scale`, so a
stock motif is unchanged. The shipped Oxyde screenpack sets a window on both
sides. (`oxtool shot <root> versus --vs NAME --as NAME` renders a chosen pairing
so you can check your box.)

---

## 2. The two Oxyde-specific rules

### Rule 1 — a pack supplies the UI, **not the roster**
In MUGEN the `select` file (the character list) often ships *inside* the pack.
**In Oxyde, do not bundle your own roster.** The playable roster comes from the
game's own `data/select.def`; a pack that ships its own character list fights
the installed roster and the install breaks. Ship the *layout* of the select
screen (in `[Select Info]`), but point `select` at the game's `select.def`, or
leave the roster to the engine. This is the single most common third-party-pack
mistake.

### Rule 2 — Oxyde has extra modes a MUGEN menu won't list
Beyond Arcade/Versus/Training/Team, Oxyde adds modes a stock MUGEN `system.def`
menu doesn't know: **Knuckle Up**, **Knuckle Up Co-op**, **Online**,
**Escalation**, **The Tower**, **Roster Rumble**, **Bonus Rush**, **Records**,
**Replays**, and more. A plain MUGEN pack still works — it just shows the modes
its own menu defines. To expose the Oxyde modes you have two choices:

- **Add the menu items in `system.def`** `[Title Info]` like any other item
  (Oxyde recognises them by name), **or**
- Use Oxyde's **optional Lua layer** (`docs/SCREENPACK-SCRIPTING.md`) to
  describe the menu and extras *without changing the MUGEN format*. The
  guarantee there is **"no script, no change"**: a pack that ships no Lua takes
  the exact same code path a MUGEN screen pack takes today. The Lua only *adds*;
  it never rewrites `system.def`, and it can never touch a character, stage or
  `.sff`.

---

## 3. Minimal working skeleton

A smallest-useful `system.def`:

```ini
[Info]
name       = "My Pack"
author     = "you"
versiondate = 01,01,2026
mugenversion = 1.1
localcoord = 1280, 720

[Files]
spr   = system.sff
snd   = system.snd
font1 = f-6x9.def
font2 = jg.fnt
select = select.def        ; the GAME's roster — do not ship your own
fight  = fight.def

[Title Info]
menu.pos        = 640, 360
menu.item.font  = 2, 0, 0
menu.item.active.font = 1, 0, 0
menu.item.spacing = 0, 28
menu.itemname.arcade   = ARCADE
menu.itemname.versus   = VERSUS
menu.itemname.training = TRAINING
menu.itemname.knuckleup = KNUCKLE UP      ; an Oxyde mode, recognised by name
menu.itemname.online   = ONLINE
menu.itemname.options  = OPTIONS
menu.itemname.exit     = EXIT

[Select Info]
rows = 5
columns = 10
cell.size = 27, 27
cell.spacing = 2, 2
pos = 90, 280
p1.cursor.startcell = 0, 0
p2.cursor.startcell = 0, 9
portrait.offset = 0, 0
portrait.scale  = 1, 1
; ... random cell, title, stage text, etc. as in MUGEN 1.1
```

Plus a standard `fight.def`, a `system.sff` holding every sprite number the two
files reference, a `system.snd`, and the fonts. That is a complete pack.

---

## 4. Testing a pack

Render any screen headlessly without launching the game:

```
oxtool shot <game-root> <title|select|versus|fight|options|records|…> --out out.png
```

Point `<game-root>` at the install whose `data/system.def` names your pack (or
the pack folder set in Options). Render `title`, `select`, `versus` and `fight`
and check: fonts resolve (no missing-glyph boxes), sprite numbers resolve (no
holes), the select grid lines up at your `localcoord`, and the HUD elements sit
where you placed them. The render reports the painted-pixel percentage so a
mostly-black screen flags a missing sprite source immediately.

---

## 5. Common mistakes (checklist)

- ❌ **Shipping a roster/`select.def`** inside the pack → the install breaks. Point `select` at the game's `select.def` (Rule 1).
- ❌ Referencing a sprite `group,image` that isn't in the `.sff` → a hole on screen. Render with `oxtool shot` to catch it.
- ❌ Wrong or missing `[Info] localcoord` → everything is positioned at the wrong scale. Set it to the resolution you authored at.
- ❌ A font named in `[Files]` that isn't beside the `.def` → missing text. Keep fonts in the pack folder.
- ❌ Expecting Ikemen Lua (`main.lua`) to run as-is → Oxyde does **not** copy Ikemen's Lua API. Use `system.def` for layout, and Oxyde's own Lua layer (`SCREENPACK-SCRIPTING.md`) for extras.
- ⚠️ Leaving out the Oxyde modes → they simply won't appear in the menu; the pack still works. Add them per Rule 2 when you want them.

---

## 6. Going further — the Lua layer

Oxyde can hand a pack's optional Lua a *description* of each built screen (the
menu, the select grid, the engine's own on-screen furniture) to re-place, hide
or extend — see **`docs/SCREENPACK-SCRIPTING.md`**. What crosses to Lua is a
short read-only list of what the engine already laid out; the script adds to it
and never writes the format back, which is why it cannot break a MUGEN pack.
Use it for Oxyde-mode menus, dynamic layout, or data-driven furniture — not as
a replacement for `system.def`.

---

## 7. Editing a pack is editing data — the generator is optional

A screen pack is **plain MUGEN data**. You author it by editing the data files
directly — `system.def`, `fight.def`, the `.sff` sprite file, the fonts — in any
text or sprite editor, exactly as you would for MUGEN 1.1. There is no build
step and nothing to compile; the engine reads those files as they are.

Oxyde's own default pack (`data/oxyde/`) happens to be **generated** by a Python
script, `build_screenpack.py`, which lays out the HUD and select screen onto a
palette ramp and writes the `.sff`. That script is a convenience for maintaining
*our* pack — **you do not need it to author one.** Hand-editing the data files is
a first-class workflow; the generator is just how the shipped pack is kept
consistent.

Two cautions if you *do* use or regenerate the default pack:

- **There are several copies of `build_screenpack.py`** — in `theme-src/` and
  `install/` in the source tree, and one under `data/oxyde/` in each live game
  root. Editing one does not touch the others; make sure you are editing the one
  that feeds the pack you mean to change.
- **A regenerated or hand-edited HUD must be deployed to the pack the running
  game actually loads.** The default pack is at `data/oxyde/` of the game root,
  and any additional game root has its own copy at `<that-root>/data/oxyde/`. If you
  regenerate into one root but play the other, the running build shows the
  **old** HUD — a common source of "my change didn't take". Deploy your edited
  `system.def`/`fight.def`/`.sff` into every root you play.

Whether you hand-edit or regenerate, verify with `oxtool shot` (section 4): it
renders the screen the engine will actually draw from the deployed files.

---

**In one line:** ship a standard MUGEN 1.1 `system.def` + `fight.def` + `.sff`
+ `.snd` + fonts, keep the roster out of the pack, add Oxyde's modes by name (or
in Lua) when you want them, and test each screen with `oxtool shot`.
