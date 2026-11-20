# Modding Oxyde

How to change what the engine does without changing the engine. Oxyde runs
Lua 5.4 mods: a mod is a `.lua` file that defines a few global functions, the
engine calls the ones it recognises, and everything else is left alone. This
document is the end-to-end story — the line a mod lives on and why, the hooks
it has to work with, how a misbehaving one is contained, how to iterate on one
while the game runs, how to package one, and what maps across if you are coming
from Ikemen GO's Lua.

For the per-hook reference, this leans on two documents rather than restating
them: [SCRIPTING.md](SCRIPTING.md) is the hooks, field by field, and
[SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md) is the `layout` hook and the
`Screen` payload. [MOD-MANIFEST.md](MOD-MANIFEST.md) is the `mod.toml` format.
The templates under [`../modules/templates/`](../modules/templates/) are a
skeleton for the main hooks (`modes`, `ai`, `hud`, `layout`);
[`../modules/examples/last-dancer/`](../modules/examples/last-dancer/)
is a mod that uses most of them together.

Nothing runs unless you ask. In `oxyde.cfg`, in the `[Game]` section:

```ini
[Game]
mods = 1
```

Then drop a `.lua` in `mods/`. `oxtool mods .` checks one without starting the
game, whatever the switch says. Options → **MODS** in-game lists what loaded.

---

## 1. The line, and why everything is arranged around it

**No script runs inside `Match::step`.** That is not a limitation waiting to be
lifted; it is the thing the rest of the engine is built on. `Match::step` is a
pure function of `(state, inputs)`, and four features fall straight out of
that:

- **Deterministic replays.** A replay is the inputs and the seed; replaying
  re-runs `step` and gets the same fight. A script reaching into `step` would
  be an input the replay never recorded.
- **Spectating and rollback netplay.** The net code is two `u16`s a frame and a
  re-run of `step` from a known state. Nothing irreversible may happen inside
  it, and a script is about as irreversible as code gets.
- **A headless test suite that asserts on fights.** The engine runs `step`
  with no window and no graphics device at all — which is also why the HUD and
  layout hooks *describe* what to draw rather than issue draw calls: a readout
  built from plain data renders the same in a real window, in a software
  rasteriser and in a headless test, and needs no GPU present to be checked.

So a mod lives on the same side of the line as a joystick:

```
   your controller ─┐
   a mod's ai() ────┼──► inputs ──► Match::step ──► the frame ──► the screen
   the network ─────┘                    ▲                           │
                                         │                           │
                              nothing scripted here      mods draw over it here
```

A scripted opponent's buttons go through the same `set_input` a pad's do. They
are recorded in replays, sent over the wire, and rolled back like any other
input. **A mod cannot desynchronise a netplay session any more than a joystick
can**, because from the simulation's point of view that is all it is.

Everything a mod does is on one of two sides of that line: it produces
**inputs and setup** before and around the match (`modes`, `rules`, `matchup`,
`ai`, `flow`), or it **draws over** a frame the engine already produced (`hud`,
`layout`). Neither side reaches `step`. When a feature seems to need to, the
feature is wrong — there is a hook for the legitimate version of almost
everything, and the one case there genuinely is not (changing what a move
*does*) belongs in the character or in the common states, not in a mod.

### What crosses the boundary

One type: a tree of numbers, strings, booleans and tables — the same shape as
the packets the net code already sends. No live Rust object is ever handed to a
script. That is deliberate and it is what makes the boundary cheap to reason
about:

- a script cannot hold a reference the engine then has to keep valid;
- there is no Rust object for a script to misuse into a panic;
- the same value marshals to a script on a server and an answer back to a
  client that has none of the engine's types.

The cost is one marshalling pass per call. For a menu, a rules decision or an
AI tick that is nothing. For `step` it would be ruinous — which is the same
reason, from the other direction, that scripts do not run there.

---

## 2. The hooks

A mod defines global functions; the engine calls the ones it recognises and
ignores the rest. A mod that implements one hook pays nothing for the others —
nothing is registered, nothing is declared to the engine (the `hooks-used`
line in `mod.toml` is for humans and packagers, not the engine). Each is
**optional**, each is **allowed to fail**, and a failure switches *that mod*
off for the session rather than the engine.

| Function | Called | Returns |
|---|---|---|
| `modes()` | once, at load | extra rows for the title menu |
| `rules(ctx)` | once a bout | the rules to play under |
| `matchup(ctx)` | when the next fight is chosen | who it is against, and where |
| `ai(view)` | once per CPU fighter per frame | which buttons to hold |
| `flow(event)` | at each hand-off between screens | what happens next, or nothing |
| `hud(state)` | once a frame, during a fight | things to draw over it |
| `layout(screen)` | once a frame, per screen | things to draw over the screenpack, or a description of it |

A declared mode may also carry `screens` — the sequence of screens its run is
made of, from a fixed vocabulary. That is **data a mode carries, not a hook**:
it is a field on what `modes()` returns, not a global function, which is why it
is absent from the table above and from `hooks-used`.

What follows is a signature and the shortest honest example of each. The
field-by-field meaning — every `ctx` key, every rules knob, every clamp — is
[SCRIPTING.md](SCRIPTING.md); this is the map, not the territory.

### `modes()` — new game modes

```lua
function modes()
  return {
    { slug = "ironman", label = "IRON MAN",
      description = "SURVIVAL, NO RECOVERY",
      base  = "survival",                 -- the built-in flow to borrow
      rules = { recover = 0.0, rounds_to_win = 1, carry_power = true } },
  }
end
```

The highest-value hook: a new mode used to be a Rust edit and a rebuild. A
scripted mode names a built-in whose **screen flow** it borrows and replaces
the numbers; a rule you do not mention keeps the base mode's answer. Nonsense
is clamped (`rounds_to_win = 10000` → 99), and a base that does not exist is
reported by name and skipped while the rest of the file loads.

### `screens` — the shape of a run (data on a mode)

```lua
screens = {
  before = { { screen = "interlude", text = { "THE TOWER" }, seconds = 4 } },
  each    = { { screen = "interlude", text = { "FLOOR {bout}" }, seconds = 2 }, "vs", "fight" },
  after   = { "result" },
}
```

`before` plays once, `each` once per rung, `after` when the run is over — three
lists because the one thing a flat sequence cannot say is which part repeats,
and repetition is the whole of what a ladder is. Vocabulary: `select`, `vs`,
`interlude`, `fight`, `result`, `ending`. **Leaving `select` out means the
engine deals you a fighter** — a mode in itself, and one that was not
expressible before. An `each` that does not `fight` exactly once is refused
outright with the reason, rather than quietly behaving like the base mode.

### `rules(ctx)` — the rules for this bout

```lua
function rules(ctx)
  if ctx.mode == "escalation" and ctx.streak % 5 == 0 then
    return { difficulty = 8, life_scale = 1.4 }   -- the boss round
  end
end
```

The same sixteen knobs a `rules/*.rules` file sets, decided in code — **one
vocabulary, two ways to reach it**. A table from Lua becomes the same sparse
delta a file becomes, then composed, clamped and conflict-checked identically,
so a script cannot skip the clamp. Returning nothing leaves the rules alone,
which is what a hook that cares about one case should do for every other.
`ctx` carries `mode`, `ruleset`, `streak`, `bout`, `defeated`, `difficulty` and
`state` — enough to answer "what should the rules be here" with no way into the
simulation.

### `matchup(ctx)` — who you fight, and where

```lua
function matchup(ctx)
  if ctx.defeated == 4 then
    return { opponent = "Kung Fu Man", stage = "Training Room" }
  end
  -- ...or describe the ladder and let the engine resolve it:
  -- return { query = "life>1400 has:super sort:-life limit:4" }
end
```

Turns "a mod can adjust the rules" into "a mod decides the run". **Characters
are named, never numbered** — an index means nothing on another installation,
and a name nobody has is reported with the nearest match while the bout is
picked as it would have been, so a mod naming a character the player does not
own never ends the run. A `query` is resolved against the character index
*before* the match, so the replay records the concrete fighters by path and
plays back for someone who has neither the mod nor the index. `ctx.roster` and
`ctx.stages` are what is actually installed.

### Remembering things

Every `ctx` carries `ctx.state` — this mod's own table, as it left it — and any
hook may return `state` to replace it. It survives the game closing, written to
`mods/state.json` as JSON (so you can read and fix it by hand), saved at the
end of every bout rather than on a clean exit, because a fighting game closes
by the window button. Each mod gets its own; two cannot read or overwrite each
other's. Short-lived coordination between hooks within a session uses module
locals instead — see the worked example.

### `ai(view)` — a computer opponent

```lua
function ai(view)
  local me, foe = view.me, view.foe
  if not foe or not me.ctrl then return nil end          -- no opinion; fall back
  if foe.attacking and view.distance < 90 then
    return { [view.away] = true, down = true }           -- block
  end
  if view.distance > 70 then return { [view.toward] = true } end
  return { a = true }
end
```

Called at exactly the point the built-in opponent would have answered. Return
button names, a flag map, or a raw bitmask; `nil` means "no opinion this frame"
and the engine falls back, which is how a mod drives only the situations it
understands. `view` is a **snapshot** — positions, health, what the other
fighter is doing, `distance`, and `toward`/`away` already resolved so every mod
does not recompute the sign and half get it wrong. There is deliberately no way
to read the opponent's variables or next state. `ai` is called for **every** CPU
seat regardless of mode, because `view` carries no mode — a mode-specific AI
gates itself on a module local its own `rules` set (the worked example does
exactly this).

### `flow(event)` — what happens after a match

```lua
function flow(event)
  if event.event == "match_over"
     and event.scripted_mode == "ironman" and not event.won then
    return { next = "gameover" }
  end
  if event.event == "round_over" and event.scripted_mode == "sudden_death" then
    return { next = "title" }          -- a run that ends on the first dropped round
  end
end
```

`event.event` is one of:

| `event` | when | a `next` redirects…
|---|---|---|
| `round_over` | a round ended and the same two fight another | the whole match, early |
| `match_over` | the match is decided | what follows the match |

`next` may be `"title"`, `"gameover"`, `"result"`, or `"continue"` — the last
meaning "carry on with the built-in flow", the same as returning nothing.
`match_over` is asked **before** anything else decides, including a mode's
declared `after`, so a hook that answers one situation beats a sequence written
once for every situation; `round_over` is asked as the next round is about to
begin, and is *not* sent when the match itself is decided — that is `match_over`.
A `next` the engine does not know is **reported** to the Problems screen and the
built-in flow is taken, never guessed at — the same loud-on-a-typo treatment a
misnamed binding gets. Returning nothing leaves the engine's own flow alone.

### `hud(state)` — an overlay on a fight

```lua
function hud(state)
  return {
    { kind = "rect",  x = 118, y = 222, w = 84, h = 12, colour = 0, alpha = 120 },
    { kind = "frame", x = 118, y = 222, w = 84, h = 12, colour = 0x445566 },
    { kind = "text",  x = 160, y = 225, align = "centre",
      text = "BEST COMBO " .. best, colour = 0xFFB347 },
  }
end
```

Three shapes — `text`, `rect`, `frame` — in 320x240 coordinates, drawn over the
life bars and under any dialogue. The vocabulary is small on purpose: a script
issuing arbitrary draw calls sixty times a second would be drawing *into the
renderer*, across the boundary this design keeps narrow, and every call would
need validating anyway. A readout is what an overlay is for. `state` carries
only what a spectator can see — life, power, combo, round, clock, tick — and
**nothing from inside the match**, for the same reason the layout payload does
not: a HUD that read `pos` or `var` could change with the simulation, and then
it is a participant in it. A typo draws the wrong thing; it does not disable the
mod.

### `layout(screen)` — a screenpack screen

```lua
function layout(screen)
  if screen.kind ~= "title" then return nil end
  return {
    menu  = reorder(screen.menu),      -- a table DESCRIBES the screen
    hide  = { "logo" },                -- engine furniture to leave out
    place = { menu = { x = 74, y = 100 } },
    items = { { kind = "text", text = "...", x = 8, y = 8 } },  -- additive
  }
end
```

Runs *after* the engine has built a screen from `system.def`, which stays the
definition. A **list** adds things over what the engine laid out; a **table**
describes the screen — which menu rows, what they are called, which engine
furniture to hide or move — and the engine still *draws* all of it, so the
cursor, scrolling, fonts and every window size keep working. Describing beats
drawing for the same reason `screens` beats a flow hook: a pack says *what* its
menu is and keeps everything the engine already gets right. The full `Screen`
payload, what it may and may not see, and why that list is short, are in
[SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md).

---

## 3. What a misbehaving mod can do

"A script must not provoke a panic" is met by construction, not by a handler:
nothing crosses the boundary but plain data, so there is no Rust object for a
script to misuse. The sandbox removes the dangerous standard libraries outright
rather than trusting a mod not to call them.

| Failure | What happens |
|---|---|
| Syntax error | Rejected at load; the mod never installs |
| Runtime error — `nil` index, bad arithmetic, `error()` | The mod is switched off for the session; the engine falls back |
| `while true do end` | Instruction budget expires → same |
| Runaway allocation | Memory cap → same |
| Reading a file, spawning a process, loading a C library | Impossible: `io`, `os`, `package` and `debug` are not in the interpreter |
| `require`, or loading Lua bytecode | Impossible / refused: `package` is gone and `load` is removed — chunks are text-only |
| A coroutine yielding out of a host call | Impossible: `coroutine` is not loaded |
| Reaching another mod's globals | Impossible: each script has its own environment |
| Reaching the simulation | There is no hook that can |

A latched failure is permanent for the session and reported **once** — a mod
that errors every frame must not cost a frame's work every frame or bury the
log. Everything reported shows on the Problems screen and prints from `oxtool
mods <root>` without starting the game.

### The budget

```ini
[Mods]
instructions = 20000000   ; per CALL, not per session
memorymb     = 64         ; the whole interpreter, across every mod
```

Per *call*: a mod doing a lot of work once a round is not penalised, while one
that never returns is stopped inside a frame. Twenty million instructions is
roughly 20 ms of dense Lua — far more than any menu or AI tick needs, far less
than a frame.

---

## 4. Iterating: hot reload

```ini
[Game]
watch = 1
```

Edit a `.lua` and it reloads in place, from scratch, without restarting — and a
mod that had latched off after an error gets another chance, which is the whole
point of editing it. The title menu gains or loses its rows; a scripted mode
that no longer exists stops supplying rules; module locals reset (so this is
how you clear a session's accumulated state). See
[CUSTOMISATION.md](CUSTOMISATION.md#hot-reloading) for what else reloads.

The tighter loop is the one that never opens a window. `oxtool mods .` calls
every hook with the exact payload the engine sends — field for field — walks a
declared `screens` sequence over several bouts, runs `rules` and `matchup`
across a spread of streaks and prints what each answered, exercises `ai` over a
window of frames, and lists every problem:

```
$ oxtool mods ~/my-install
mods
  last-dancer

modes declared  1
  lastdancer     base survival     ONE LIFE BAR, WHOEVER YOU ARE GIVEN

rules  answered for mode "lastdancer"
  streak 0  difficulty = 4
  streak 4  difficulty = 8, life_scale = 1.3, super_defence = 1.4

matchup  over six bouts: (dealt) Alpha, Beta, Gamma, Delta, Epsilon, Zeta  (remembered: best, seen)
ai  exercising 120 frames — answered 118/120
hud  312 overlay item(s) over 180 frames  (frame, rect, text)

no problems
```

A probe that invented its own payload shape would test the probe; this one does
not, so a mod that passes it cannot fail in the game for a reason the probe hid.

---

## 5. Packaging a mod

A `.lua` dropped in `mods/` needs nothing more to run. A folder mod is a folder
whose entry file the engine loads as `init.lua`. To **hand it to someone**, add
a `mod.toml` beside it:

```text
mods/
  last-dancer/
    init.lua
    mod.toml
    README.md
```

```toml
[mod]
name               = "Last Dancer"
version            = "1.0.0"
author             = "you"
description         = "Endless survival; the opponent sharpens as your run lasts."
engine-min-version = "0.36.0"
hooks-used         = ["modes", "rules", "matchup", "ai", "hud", "flow"]
entry              = "init.lua"
```

The manifest is identity, not behaviour — it does not change what a mod may do
or switch any hook on. It is **packaging metadata**: the running engine
discovers mods by filename — a bare `.lua`, or a folder whose entry file is
`init.lua` — and does not itself read `mod.toml`. The format is fixed (see
[MOD-MANIFEST.md](MOD-MANIFEST.md)) so a packaged mod is ready for the loader
that consumes it; at that point `engine-min-version` is the field it acts on —
reporting a mod that needs a newer engine at load rather than latching it off
mid-bout — and `entry` is what lets a folder's entry file be named something
other than `init.lua`.

Mods load from `mods/` first, then `data/mods/`, alphabetically — so two
machines with the same set load them in the same order and a mod that overrides
another does so predictably. Where several hooks of the same kind answer, load
order decides: later mods win for `rules`, `matchup` and `flow`; the first to
answer wins for `layout`; `hud` overlays stack; `ai` takes the first mod that
has an opinion.

---

## 6. Coming from Ikemen GO

Ikemen GO is also Lua, and the instinct is to port a script line for line. Most
of that instinct does not transfer, and the parts that do not are the parts
worth understanding before you start. The short version: **Ikemen's Lua *is*
the engine's UI; Oxyde's Lua sits beside the engine and hands it data.**

### What an Ikemen "mod" actually is

Open one of Ikemen's bundled modes and you find it reaching into `main`,
`start`, `options` and `motif`, adding itself to tables like
`main.t_itemname`, registering `hook.add(...)` callbacks, calling
`setGameMode`, `remapInput`, `sndPlay`, `animNew`, `gameOption`,
`modifyGameOption`. Those are not an extension API — they are the engine's own
UI internals, written in Lua, which a mode slots into because the whole screen
flow *is* Lua. A `bossrush.lua` for Ikemen is 60 lines of flipping `main.*`
booleans; a `ratio.lua` is 400 lines driving the team menu, the options screen,
the roster builder and the per-frame icon drawing.

Oxyde has no such surface, on purpose. There is no `main` table to mutate, no
`gameOption` to call, no `animNew` to draw with. A mod does not slot into the
engine's UI; it answers questions the engine asks.

### What maps

| You want to… | In Ikemen | In Oxyde |
|---|---|---|
| add a game mode | a function in `main.t_itemname` + a `start.t_makeRoster` entry + booleans | one entry from `modes()`, naming a `base` and its `rules` |
| decide the roster / ladder | `start.t_makeRoster.<mode>` building ratiomatches tables | `matchup(ctx)` returning names or a `query` |
| change the rules per mode | booleans on `main.*`, `main.matchWins`, `main.lifebar` | `rules(ctx)` returning the knobs that differ |
| drive a computer opponent | `AILevel`, ramps, char-side scripting | `ai(view)` returning buttons |
| draw over a fight | `main.f_drawText` / anim draws in a fight loop | `hud(state)` returning a readout |
| re-lay-out a screen | `motif.*` reads and draws in `main.lua` | `layout(screen)` describing the screen |
| remember progress | your own files via `saveIni` / Lua `io` | return `state`; the engine persists it |

The *reads* map almost for free, because Oxyde already reads the motif format:
an Ikemen motif is a `system.def`, and its `main.lua` reads
`motif.select_info`, `motif.title_info`, `motif.files` and `motif.info` — which
are that file's `[Select Info]`, `[Title Info]`, `[Files]` and `[Info]`
sections. Oxyde loads the same `system.def`. You do not port the motif; you
point Oxyde at it.

### What becomes describe-not-draw

Everything Ikemen does by **drawing** you do in Oxyde by **describing**, and
this is the one shift to internalise:

- An Ikemen mode owns the cursor, the scrolling, the fonts, the sounds, and
  draws each menu row itself with `animNew`/`f_drawText`. An Oxyde `layout`
  returns a list of menu rows by id and the engine draws them — so the cursor
  still steps, the motif's fonts and sounds still apply, and it works at 320x240
  and at 4K because none of that ever left the engine. You *cannot* draw a menu
  yourself here, and that is the feature: you get everything the engine already
  gets right for free, and you cannot get it wrong.
- An Ikemen HUD draws anims and text anywhere, every frame. An Oxyde `hud`
  returns `text`/`rect`/`frame` items in 320x240 and the engine draws them —
  no image handles, no arbitrary blits, because the draw list has to validate
  and has to render the same headless, where there is no GPU to blit with.

### What does not port at all, and what to do instead

- **`gameOption` / `modifyGameOption`.** Ikemen's UI scripts change how the
  game *plays*. Oxyde has no equivalent and will not: the simulation is on the
  other side of the line. Anything that changed a match in Ikemen by setting an
  option is, in Oxyde, either a `rules` knob (if it is one of the sixteen the
  engine already reads) or it is a change to a character / the common states,
  not a mod.
- **`io` / `saveIni` for your own save files.** Not available — `io` is out of
  the sandbox. Return `state` from a hook and the engine persists it to
  `mods/state.json` for you.
- **`hook.add` into engine internals.** There are no internals to hook. The
  seven named hooks are the whole surface; if your Ikemen script hooked
  something not in the table above, that behaviour is either expressible as one
  of these hooks or it was reaching somewhere Oxyde deliberately does not go.
- **`require` / splitting across modules with `package`.** `package` is gone.
  Split a mod with the manifest's `entry = ["lib.lua", "mod.lua"]` list
  instead, loaded in order into one environment.

Ikemen proves the two formats coexist — it reads `system.def` and drives the
screens from Lua. Oxyde reads the same format and keeps the driving in the
engine. You are not translating a program; you are deciding which of a few
questions your mod wants to answer, and letting the engine keep doing the rest.

---

## See also

- [SCRIPTING.md](SCRIPTING.md) — the hooks, field by field, with every `ctx`
  key and rules knob.
- [SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md) — the `layout` hook and the
  `Screen` payload.
- [MOD-MANIFEST.md](MOD-MANIFEST.md) — the `mod.toml` format.
- [RULESETS.md](RULESETS.md) — the sixteen knobs `rules` shares with the files.
- [`../modules/templates/`](../modules/templates/) — a skeleton for the main hooks.
- [`../modules/examples/last-dancer/`](../modules/examples/last-dancer/) — a mod
  using most of them together.
