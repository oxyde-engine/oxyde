# Laying out a screen from Lua

**Status: wired to the renderer on every screen the engine builds. A script may add to
what the engine laid out — a loose display list, or a closed vocabulary of
described, data-bound `elements` (text, sprites, rects, value-bound bars) — may
replace the title menu, and may hide or move the engine's own furniture on the
title, select, versus and result screens.**

`system.def` stays. This adds a hook that runs *after* the engine has built a
screen from it, and may change what is about to be drawn. A pack with no script
behaves bit-identically to today, which is the property everything else here is
arranged to protect.

---

## 1. What crosses, and why that list is short

This document exists because the first thing to get right is not drawing — it
is deciding what a layout script may see. Everything else follows from it, and
widening it later is far harder than starting narrow.

A layout script receives a **`Screen`**: plain data, built fresh, handed over by
value. It answers with a **list of items to draw**, a **table describing the
screen**, or nothing — in which case the engine draws what it had.

### It may see

| | | sent today |
|---|---|---|
| which screen this is | `"title"`, `"select"`, `"versus"`, `"fight"`, and the rest | yes, as `kind` |
| the screen's own size | `width`, `height`, and the `scale` the window is drawn at | yes |
| how many fighters are installed | `roster` | yes |
| the round and the clock | `round`, `rounds_to_win`; absent outside a fight, so `if screen.round then` is honest | yes |
| the menu, on the title screen | `menu`, a list of `{ id, label, hint }` in the order the engine built it | yes |
| the roster, on the select screen | display name, author, and whether each slot is taken | not yet |
| the two fighters, on a fight screen | name, life fraction, power fraction, wins, palette | not yet |
| what the player just did | the menu item moved to, the slot hovered, the button pressed | not yet |

The last three are on the allowed side of the boundary and simply are not built
yet; a test holds the whole list, so the payload cannot quietly grow a field
nobody wrote down here.

### It may not see

Anything that would make the layout a participant in the match. Named exactly,
so the list can be checked rather than interpreted — a test asserts that every
one of these appears here and is refused in the code:

    state_no   var       fvar     pos      vel
    rng        seed      tick     frame
    hitdef     buffer    juggle

**None of these are withheld to be awkward.** They are withheld because a
script that reads them is one edit away from a layout that changes depending on
the simulation, and the moment that happens replays, rollback and netplay are
all in play.

The HUD hook already exists for the things a HUD legitimately needs, and its
payload is deliberately the same things a person watching the screen can see.

### It may not write anything back

The return value is data: a display list, or a description of a screen. There
is no handle to the match, no callback into the engine, no `UserData` — only
[`Data`]. A script cannot hold a reference into the simulation, so there is
nothing for rollback to invalidate, and nothing it returns can reach `step()`.

---

## 2. Why this cannot break a MUGEN screenpack

Three reasons, in decreasing order of how much they would survive a careless
change:

1. **A character never names a screenpack.** Not one of the 2,527 here
   references `system.def`. Screenpacks are separate content, so nothing done
   here can touch a character, a stage, a `.cmd`, an `.air` or an `.sff`.
2. **`system.def` remains the definition.** The engine builds the screen from
   it exactly as now. The script is handed the result.
3. **No script, no change.** A pack that ships no Lua takes the same code path
   it takes today, and the hook is never called.

Ikemen GO is the existence proof that the two coexist: its `main.lua`
references the motif **302 times**. It reads `system.def` and drives the
screens from Lua. It did not replace the format, and neither does this.

**What is deliberately not done:** copying Ikemen's API shape so that its
scripts run here.

And on the question of converting their work instead of adopting it — there is
almost nothing to convert. An Ikemen *motif* is a `system.def`: its `main.lua`
reads `motif.select_info`, `motif.title_info`, `motif.files` and `motif.info`,
which are that file's `[Select Info]`, `[Title Info]`, `[Files]` and `[Info]`
sections. **Oxyde already reads that format.** The 12,000 lines of Lua in
`external/script` are Ikemen's own engine UI, not content an author ships, and
re-implementing them would be adopting their design with extra steps.

## What this does that other engines do not

Composing with the format is the compatibility story. These are the reasons to
prefer it on its own merits:

* **A layout cannot touch the match.** Ikemen's UI scripts call `gameOption`
  and `modifyGameOption` — they can change how the game plays. Here the payload
  carries nothing from the simulation and the return value is data, so a layout
  can never make a match play differently. That is a guarantee, not a
  convention: `oxyde-script` is absent from `oxyde-core`'s manifest, so the
  build enforces it.
* **A layout describes rather than draws.** Ikemen's motifs are Lua all the way
  down: the script owns the cursor, the scrolling, the fonts and the sounds, so
  every pack reimplements them and every pack gets a different subset right.
  Here a pack says *what* its title menu is and the engine still draws it — the
  cursor still steps, the motif's fonts and cursor sounds still apply, the
  window still scrolls, and it still works at 320x240 and at 4K, because none
  of that ever left the engine.
* **Therefore replays and rollback are untouched.** A screen drawn differently
  on two machines cannot desynchronise a match, because the screen is drawn
  from data the match never sees.
* **It composes with the format instead of replacing it.** A pack can be pure
  `system.def`, pure script, or `system.def` with a script adding the one thing
  the format cannot express. Nobody has to rewrite anything to gain anything.
* **Every hook is exercised by `oxtool mods`** with the payloads the engine
  really sends, across every screen the engine builds — so a script that passes
  the probe cannot fail in the game for a reason the probe hid.

---

## 3. The rule that keeps it honest

`oxyde-script` is not in `oxyde-core`'s manifest, and must never be. That one
fact is what makes "no script runs inside `step()`" a property of the build
rather than a rule somebody has to remember. A layout hook lives in
`oxyde-app`, is called from the screen flow, and is as far from the simulation
as the mode list is.

If adding a layout feature ever seems to need `oxyde-script` in `oxyde-core`,
the feature is wrong, not the rule.

---

## 4. The hook

```lua
-- Called after the engine has built a screen. Return a list of items to draw,
-- a table describing the screen, or nil to accept what it built.
function layout(screen)
  if screen.kind ~= "select" then return nil end
  return {
    { kind = "text",
      text = string.format("%d fighters", screen.roster),
      x = 160, y = screen.height - 24, align = "centre" },
  }
end
```

An item the engine does not understand is dropped with a diagnostic rather than
drawn wrongly, and a script that errors is disabled for the rest of the run with
its message reported once — the same policy the other hooks use. The
diagnostics are on the Problems screen, and `oxtool mods <root>` prints them
without starting the game.

`mods/layout_demo.lua` in the archive does everything below.

### 4.1 A list adds. A table describes.

A **list** is the display list: things drawn on top of what the engine laid
out, in 320x240 coordinates whatever the window size is. `kind` is `text`,
`rect` or `frame`. Nothing about the engine's own work changes, and this is the
arm every script written before this existed goes down.

A **table** describes the screen. Every field is optional, and a field left out
means "whatever the engine decided":

| | |
|---|---|
| `items` | the loose display list, exactly as above |
| `elements` | the described element list — text, sprites, rects, value-bound bars, anchors; see 4.5 |
| `menu` | the title menu, re-described — see 4.2 |
| `hide` | engine furniture to leave out — see 4.3 |
| `place` | engine furniture to move — see 4.3 |

The first pack that answers wins. Two packs both rewriting one screen is a
conflict nothing can resolve sensibly, and silently merging two layouts would
produce a screen neither author intended.

### 4.2 `menu` — the title menu, described

```lua
function layout(screen)
  if screen.kind ~= "title" then return nil end
  local rows = {}
  for _, row in ipairs(screen.menu) do
    if row.id == "training" then
      rows[#rows + 1] = { id = row.id, label = "PRACTICE" }
    elseif row.id == "netplayversus" then
      rows[#rows + 1] = { id = row.id, disabled = true }
    elseif row.id:sub(1, 4) ~= "team" then
      rows[#rows + 1] = { id = row.id }
    end
  end
  return { menu = rows }
end
```

A row is `{ id, label, disabled }`, or a bare string when the id is all you
have to say. `id` is the mode's `GameMode` slug — `arcade`, `versus`,
`training`, `netplayversus`, `options`, `exit`, and a mod's own mode under the
slug it declared. It is matched case-blind, and it is the same word a character
compares `GameMode` against and the same word `oxtool shot --mode` takes:
inventing a second set of names for the same eighteen things would guarantee
the two drifted.

* **`label`** renames the row. Left out, the row keeps whatever this install
  calls it — the motif's word from `[Title Info]` where it has one, the
  engine's otherwise. The name is the pack's; the *mode* is still the engine's,
  so a renamed row runs the thing it renamed.
* **`disabled`** puts the row on the menu and refuses it: drawn grey, stepped
  over by the cursor, and Start does nothing on it. That is a different message
  from leaving it out — "this exists and you cannot have it here" — and a pack
  that means the other one omits the row.
* **The list is the menu.** A row the plan does not name is not on it.

**So walk `screen.menu` rather than typing out the rows.** A pack that wrote
eighteen ids would silently drop every mode a mod declared, and this engine has
already learnt twice what a list nobody reconciled costs. Deriving is also what
makes a plan survive the engine gaining a mode.

Two things the engine refuses:

* A menu with nothing on it that can be chosen — empty, or every row disabled.
  That is a title screen you can neither start a game from nor leave. The
  engine's own menu is drawn instead and the refusal is reported.
* An id that names no row on this install, and an id listed twice. Both are
  reported and skipped; the rest of the menu stands.

**The menu is asked for once**, when the menu is built, and again when mods are
reloaded — not once a frame. A menu whose rows can move between two frames is a
menu where the row you pressed Start on is not the row that runs. Everything
else in a plan *is* read every frame, because it only affects how the screen is
drawn.

### 4.3 `hide` and `place` — the engine's own furniture

The engine draws a few things around a pack's artwork. A plan can turn them off
and move them. The vocabulary is closed, and a name outside it is reported
rather than ignored:

| | |
|---|---|
| `logo` | the OXYDE wordmark on the engine's own menu screens |
| `tagline` | the tagline, its rule and the infinity mark, on the same |
| `subtitle` | the roster count — under the rule, or beside the version in the engine title's footer |
| `status` | the red status line (top left on the engine's title, along the bottom elsewhere) |
| `menu` | the list itself, on both the engine's title screen and a pack's |
| `hint` | the line explaining the selected row, and the controls in the engine title's footer |
| `version` | the `OXYDE Vx.y.z` stamp in the corner of a title screen |

The vocabulary is **per screen** — a name is understood on the screen it belongs
to and reported as a typo on any other, and the diagnostic says which screen it
was looking at. The furniture above is the **title** screen's. The other three
screens a plan can now describe have their own:

**Select** (the character grid):

| | |
|---|---|
| `grid` | the portrait cells themselves; the paging and the cursors stay live underneath, so input still lands where the player aims it |
| `stage` | the stage line (also anchorable) |
| `hint` | the prompt in player two's empty corner |

**Versus** — both `hide` and `place` are honoured for every one of these:

| | |
|---|---|
| `p1portrait` / `p2portrait` | the two fighters' portraits either side of the split |
| `p1name` / `p2name` | their names |

> The *size* of those portraits is set in `system.def`'s `[VS Screen]`. Beyond
> MUGEN's fixed `p1.scale`/`p2.scale`, Oxyde reads `p1.window`/`p2.window = w, h`
> to **fit** each portrait into a shared box — so an HD portrait and a classic
> low-res one render at matched size instead of the HD one dwarfing the other.
> Omit it to keep the fixed scale. See AUTHORING-SCREENPACKS.md.

**Result** (the win / continue screen):

| | |
|---|---|
| `banner` | the win-message banner the engine announces the winner with |

```lua
return {
  hide = { "logo", "tagline", "version" },
  place = { menu = { x = 74, y = 100 } },
}
-- on the versus screen, a pack with its own framed art:
-- return { hide = { "p1name", "p2name" }, place = { p1portrait = { x = 30, y = 90 } } }
```

`hide` takes one name, a list of them, or a table of name-to-yes. `place` takes
`x`, `y`, or both, in **320x240** — the same coordinates a plan's drawn items
use, and the same ones every screenpack is written against. A pack's own
`localcoord` is converted for it, so `x = 160` is the middle of the screen
whatever the pack thinks it is authored at and whatever size the window is. For
the menu, `x` is where each row is centred.

**Hiding does not give the space back.** Every measurement on a menu screen is
settled before anything is drawn, and a screen that reflows as pieces come and
go is a screen a pack cannot place anything on. `place` is how a plan moves
things.

### 4.4 What is not re-describable, and why

The settings panels — options, key bindings, the training dummy menu, the move
list — are not. They are the engine configuring itself, not content: their rows
are the settings, a row renamed is a setting a player cannot look up, and a row
hidden is a setting that cannot be changed and no longer appears to exist. The
title menu is the one list on any screen whose entries are a fixed vocabulary
the engine and the pack can both name. The same goes for the saved-replay list
and the Problems screen: renaming a diagnostic is not a layout decision.

The settings panels stay **additive only** for exactly that reason: a plan may
draw `elements` over them, but it may not `hide`, `place` or rename their rows.

### 4.5 `elements` — the described element vocabulary

Where `items` is a loose list of draw ops, `elements` is a closed, typed
vocabulary the engine renders deterministically. Every entry is a table with a
`kind` and the fields that kind reads; a `kind` the engine does not know, like a
colour or a binding it does not know, is reported to the Problems screen rather
than drawn wrong in silence. Positions are in **320x240**, like everything else
a script draws.

| `kind` | what it is | its fields |
|---|---|---|
| `text` | a line of text | `x`, `y`, `text` (or `bind`), `format`, `color`, `align`, `font`, `show_when` |
| `sprite` | a sprite from the motif's sheet, or a character's portrait when bound | `x`, `y`, `group`, `image`, `bind`, `scale`, `show_when` |
| `rect` | a filled box | `x`, `y`, `w`, `h`, `color`, `alpha`, `show_when` |
| `bar` | a bar whose fill tracks a bound value | `x`, `y`, `w`, `h`, `bind`, `max`, `color`, `back`, `show_when` |
| `anchor` | moves a named piece of engine furniture — the same as `place`, written inline | `name`, `x`, `y` |

```lua
return {
  elements = {
    { kind = "text", x = 160, y = 20, bind = "p1.name", color = "p1", align = "centre" },
    { kind = "bar",  x = 20, y = 30, w = 120, h = 6, bind = "p1.life", max = "p1.life_max", color = "p1" },
    { kind = "sprite", x = 40, y = 60, bind = "p1.portrait" },
    { kind = "rect", x = 0, y = 0, w = 320, h = 16, color = "panel", alpha = 180 },
  },
}
```

#### Colours are theme tokens

A `color` (or `back`) is a **token** the engine resolves to pixels in whatever
theme is in force, so a pack reskins by naming the role rather than freezing one
build's orange into itself. A raw `0xRRGGBB` number is still accepted where a
pack genuinely means one exact colour — a pixel is not a setting. The tokens:

`ink`, `dim`, `value`, `panel`, `edge`, `accent`, `selected`, `warn`, `hint`,
`shadow`, `p1`, `p2`.

#### Values are bindings

A `bind` is a **name** the engine resolves against a snapshot it builds from
what a person watching the screen can already see — the mod never reads the
state itself, so a bound element can no more change a replay than a drawn
rectangle can. A `text` draws its bound value; a `bar` fills `value / max`
(where `max` is a number or a second binding); a `sprite` draws the portrait a
`p1.portrait`/`p2.portrait` names. A name outside this closed list is reported:

`p1.life`, `p1.life_max`, `p1.life_ratio`, `p1.power`, `p1.power_max`,
`p1.power_ratio`, `p1.name`, `p1.portrait`, `p1.wins`, `p1.combo`, `p2.life`,
`p2.life_max`, `p2.life_ratio`, `p2.power`, `p2.power_max`, `p2.power_ratio`,
`p2.name`, `p2.portrait`, `p2.wins`, `p2.combo`, `combo.hits`, `combo.damage`,
`score.p1`, `score.p2`, `timer`, `cursor`, `roster`, `round`.

The two `*_ratio` bindings are the life and power bars' fill as a fraction
`0..1` — the number a `show_when` below compares against, and the number a
`percent`-formatted text reads. `p1.combo`/`p2.combo` are each side's own live
hit count, where `combo.hits` is the leading side's; both are what the HUD's
counter already draws.

A binding the current screen cannot answer — a fighter on a screen with no fight
behind it — resolves to nothing, and the element draws blank or empty rather
than a guess. Every one of these names something already on the screen, which is
exactly what keeps a binding on the safe side of the boundary in section 1.

#### `format` — how a bound number reads

A bound `text` shows its value as it arrives: `format` picks instead one of a
handful of renderings a person already understands. The engine does the
formatting in Rust at draw; it computes nothing the value did not already carry,
so a `format` crosses no more of the boundary than the raw number did. An
unbound `text` ignores it, and a value that is not a number reads as itself.

| `format` | `420` | `0.25` | `95` |
|---|---|---|---|
| `plain` *(default)* | `420` | `0.2` | `95` |
| `int` | `420` | `0` | `95` |
| `percent` | — | `25%` | — |
| `time` | `7:00` | — | `1:35` |
| `signed` | `+420` | `+0` | `+95` |

```lua
{ kind = "text", x = 160, y = 8, bind = "timer", format = "time", align = "centre" },
{ kind = "text", x = 20, y = 40, bind = "p1.life_ratio", format = "percent" },
```

#### `show_when` — draw only while a condition holds

An element may carry a `show_when`, and is drawn only while it holds. The
condition is a **closed** three-part form — `<binding> <op> <number>` — read
once when the plan is parsed and evaluated by the engine against the same
snapshot every binding resolves against. The left side is a binding from the
list above, the operator is one of `<`, `<=`, `>`, `>=`, `==`, `!=`, and the
right side is a literal number. No line of the mod's code runs at draw time, so
a `show_when` reads nothing the simulation did not already put on the screen —
it is the one conditional in the vocabulary, and it cannot compute from live
state any more than a bound bar can.

```lua
-- a low-life warning that blinks on under a quarter bar
{ kind = "text", x = 20, y = 46, text = "DANGER", color = "warn",
  show_when = "p1.life_ratio < 0.25" },
```

A binding the screen cannot answer makes the condition **false** — the element
stays hidden — rather than guessing a fighter into being. A `show_when` that
does not parse (a misspelled binding, an operator that is not one of ours, a
right side that is not a number) is reported to the Problems screen and dropped,
and the element then draws unconditionally: a mistyped guard shows its element,
it does not silently swallow it.

The HUD has had its own hook all along (`hud(state)`), and it has the live
payload a HUD needs; `elements` is for the screens around the fight.
