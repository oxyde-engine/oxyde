# Scripting

Oxyde runs Lua 5.4 mods. This is what they can do, what they cannot, and
why the line is drawn where it is.

Nothing runs unless you ask for it:

```ini
[Options]
mods = 1
```

Then drop a `.lua` in `mods/`. `oxtool mods .` checks one without starting the
game.

---

## The line

**No script runs inside `Match::step`.**

That is not a limitation to be lifted later; it is the thing everything else in
this engine is built on. `Match::step` is a pure function of `(state, inputs)`,
which is what buys deterministic replays, spectating, rollback netcode in about
four hundred lines, and a headless test suite that can assert on a fight. A
script that could reach into the simulation would cost all four.

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

---

## The six hooks

A mod is a Lua file that defines global functions. The engine calls the ones it
recognises and ignores the rest; a mod that implements one pays nothing for the
others.

| Function | Called | Returns |
|---|---|---|
| `modes()` | once, at load | extra rows for the title menu |
| `rules(ctx)` | once a bout | the rules to play under |
| `matchup(ctx)` | when the next fight is chosen | who it is against, and where |
| `ai(view)` | once per computer-driven fighter per frame | which buttons to hold |
| `flow(event)` | when a match ends | what happens next, or nothing |
| `hud(state)` | once a frame while a fight is on screen | things to draw over it |

### `modes()` — new game modes

The highest-value hook. `mode.rs` is 1,286 lines that are essentially a table,
and every new mode used to be a Rust edit and a rebuild.

A scripted mode names a built-in whose *screen flow* it borrows — which screens
follow which, what the epilogue does — and replaces the numbers.

```lua
function modes()
  return {
    {
      slug        = "ironman",
      label       = "IRON MAN",
      description = "SURVIVAL WITH NO RECOVERY BETWEEN BOUTS",
      base        = "survival",
      rules = {
        ladder        = "endless",   -- or a count, or "none"
        recover       = 0.0,         -- survival normally hands life back
        rounds_to_win = 1,
        carry_power   = true,
      },
    },
  }
end
```

Every rule you do not mention keeps the base mode's answer. Rules understood:
`ladder`, `rounds_to_win`, `turns`, `continuous`, `training`, `carry_power`,
`recover`, `picks`, `sizes`, `on_screen`, `drives`.

`drives = { {"human"}, {"cpu"} }` says who plays each seat.

Nonsense is clamped rather than trusted — `rounds_to_win = 10000` becomes 99 —
and a mode naming a base that does not exist is reported by name and skipped
while the rest of the file loads.

### `screens` — the shape of a run

`base` borrows a built-in mode's screens. A mode that wants its own declares
them, from a fixed vocabulary, as data:

```lua
{
  slug    = "tower",
  label   = "THE TOWER",
  base    = "survival",            -- still the numbers a run is played with
  rules   = { ladder = "endless", rounds_to_win = 1 },
  screens = {
    before = {
      { screen = "interlude", text = { "THE TOWER", "TEN FLOORS." }, seconds = 4 },
    },
    each = {
      { screen = "interlude", text = { "FLOOR {bout}", "{opponent}" }, seconds = 2 },
      "vs",
      "fight",
    },
    after = { "result" },
  },
}
```

A run plays **`before` once**, then **`each` once per rung**, then **`after`**
when the run is over. Three lists rather than one sequence, because the single
thing a flat list cannot say is which of its steps happen again for the second
opponent — and that is the whole of what a ladder is.

| Word | Means | Allowed in |
|---|---|---|
| `select` | the roster | `before` |
| `vs` | the screenpack's versus screen | `before`, `each` |
| `interlude` | a screen of your own words | anywhere |
| `fight` | the fight itself | `each`, exactly once |
| `result` | the result summary | `after` |
| `ending` | the winner's ending storyboard, or the motif's | `after` |

**Leaving `select` out means the engine deals you a fighter** rather than
asking for one. That is a mode in itself, and it was not expressible before.

An `interlude` takes `text` — a line or a list of them — and `seconds`, where
`0` means it waits for a button. Its words may carry `{bout}`, `{defeated}`,
`{streak}`, `{opponent}` and `{mode}`, filled in when the screen appears; a
brace that is not one of those is left exactly as it was written, because it is
far likelier to be a brace you wanted on screen. Eight lines, sixty-four
characters and thirty seconds are the caps, and anything past them is cut with
a note rather than obeyed.

A step written **after** `fight` belongs to the bout that just ended, so it is
shown before the next opponent is chosen. A step before `fight` is shown once
there is somebody to announce.

Two things a declared sequence does not get to do. **A lost run is still
offered another go first** — the continue screen belongs to the player, not to
the mod. And a sequence whose `each` does not fight exactly once is refused
outright, with the reason, rather than quietly falling back to the base mode's
flow: a mode that looks declared and behaves like Survival is worse than one
that says it would not load.

A declared sequence is not played **online or in a tournament bout**: both are
waiting on somebody else, and a screen one side holds up and the other does not
is a desynchronised match rather than a presentation.

See the whole run without playing it:

```
$ oxtool mods .
screens  declared by mode "tower", over three bouts
   1. (the engine deals a fighter)
   2. interlude "THE TOWER" (4s)
   3. interlude "FLOOR {bout}" (2s)
   4. vs
   5. fight
   6. (the next opponent is chosen)
   ...
```

That walk is built from the same two functions the engine queues from, so a
sequence that reads one way there cannot play another way in the game. The
worked example is `mods/tower.lua`.

### `rules(ctx)` — the rules for this bout

The same sixteen knobs a `rules/*.rules` file sets, decided in code:

```lua
function rules(ctx)
  if ctx.streak >= 5 then
    return { difficulty = 8, rounds_to_win = 1 }   -- the boss round
  end
end
```

`ctx` carries `mode`, `ruleset`, `streak`, `bout`, `defeated` and
`difficulty` — enough to answer *"what should the rules be here"* without
handing a script any way into the simulation. A script that wanted the
fighters' positions would be writing an AI, and there is a hook for that.

Returning nothing leaves the rules alone.

A scripted mode's own `rules = { ... }` block sets the rules *once*, when the
mode is defined. This hook is the same vocabulary asked again each bout, when
there is something to ask about. Use the block for what the mode always is, and
the hook for what depends on how the night is going.

**This is one vocabulary with two ways to reach it.** Files are the data path
and this is the logic path; a table from Lua becomes the same sparse delta a
file becomes, and is then composed, clamped, checked for conflicts and reported
on identically. `a_script_and_a_file_reach_the_same_rules` pins that they
produce the same match, and `a_mods_rules_are_clamped_like_anyone_elses` pins
that a script cannot skip the clamp — `rounds_to_win = 10000` becomes 99
whoever wrote it.

An unknown key is reported against the hook, with the nearest real name, and
the rest of the table still applies. The hook runs **after** the ruleset files,
so a script can answer a situation the files could not know about and that
answer wins.

`oxtool rules <root> --list` prints every knob and its range, and
`oxtool mods <root>` calls the hook for a spread of streaks and prints what it
answered for each — so a ramp reads as a ramp, and a mistyped knob is named
before the game ever runs:

```
rules  answered for mode "escalation"
  streak 0  difficulty = 4
  streak 5  difficulty = 8, life_scale = 1.4, rounds_to_win = 1, super_defence = 1.5
```

`oxtool mods <root>` runs `matchup` for six bouts in a row and prints what it
chose each time, which is the only way to see a ladder that does not repeat
itself — and it says whether the mod remembered anything between them.

A working example ships in `mods/escalation.lua`. It is inert until
`mods = 1`, so it costs nothing to leave in place.

### `matchup(ctx)` — who you fight, and where

The hook that turns *a mod can adjust the rules* into **a mod decides the run**:
a scripted ladder, a boss order, a themed stage rotation.

```lua
function matchup(ctx)
  if ctx.defeated == 4 then
    return { opponent = "Kung Fu Man", stage = "Training Room" }
  end
end
```

`ctx` carries `mode`, `bout`, `defeated`, `streak`, `difficulty`, and the names
actually installed as `ctx.roster` and `ctx.stages` — so a mod can choose from
what is there rather than guessing. `opponent` may be a list, for a team.

**Characters are named, not numbered.** An index means nothing on somebody
else's installation, and a shared mod is the whole point. A name nobody has is
reported with the nearest match and the bout is picked the way it would have
been anyway: *a mod naming a character the player does not own must not end the
run.* Returning nothing declines silently, so a script can pin one boss fight
without authoring every other rung.

### Remembering things

Every hook is handed `ctx.state` — this mod's own table, as it left it — and
any hook may return `state` to replace it:

```lua
function matchup(ctx)
  local seen = ctx.state or { beaten = {} }
  ...
  return { opponent = pick, state = seen }
end
```

It survives the game closing, which is what makes a scripted ladder a ladder
rather than a sequence of unrelated fights. Each mod gets its own; two of them
cannot read or overwrite each other's. It is written to `mods/state.json` — as
JSON, because you will want to read it, and occasionally to fix it by hand —
and saved at the end of every bout rather than only on a clean exit, because
the way a fighting game actually closes is the window button.

A file that will not parse is discarded with a note rather than half-read: a
mod handed a truncated table behaves unpredictably, and starting from nothing
is a state it already has to handle.

### `ai(view)` — a computer opponent

Called at exactly the point the built-in opponent would have answered.

```lua
function ai(view)
  local me, foe = view.me, view.foe
  if not foe or not me.ctrl then return nil end   -- no opinion; fall back
  if foe.attacking and view.distance < 90 then
    return { [view.away] = true, down = true }    -- block
  end
  if view.distance > 70 then
    return { [view.toward] = true }
  end
  return { a = true }
end
```

Return a list of button names (`{"right", "a"}`), a map of flags
(`{ right = true, a = true }`), or a raw bitmask. Returning `nil` means "no
opinion this frame" and the built-in opponent answers instead — which is how a
mod can drive only the situations it understands.

`view` is a **snapshot**, not a handle: positions, health, what the other
fighter is doing, `distance`, and `toward`/`away` already resolved so every mod
does not compute the same sign and half of them get it wrong. There is
deliberately no way to read the opponent's variables or their next state.

### `flow(event)` — what happens after a match

```lua
function flow(event)
  if event.event == "match_over"
     and event.scripted_mode == "ironman"
     and not event.won then
    return { next = "gameover" }
  end
end
```

`event.event` is `"round_over"` — a round ended and the same two fight another,
the one hand-off inside a match — or `"match_over"`, once the match is decided.
`next` may be `"title"`, `"gameover"`, `"result"`, or `"continue"` (the same as
returning nothing). A `round_over` redirect ends the whole match early; it is
*not* sent when the match itself is decided, which is `match_over`. A `next` the
engine does not know is **reported** to the Problems screen and the built-in
flow is taken rather than guessed at. Returning nothing leaves the engine's own
flow alone, which is what a mod that only cares about one case should do.

`match_over` is asked **before** anything else decides, including a mode's
declared `after`: a hook that answers a particular situation beats a sequence
written once for every situation. A mod that wants its declared ending to play
should say nothing here for that case.

### `hud(state)` — an overlay

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
life bars and under any dialogue.

The vocabulary is small on purpose. A script issuing arbitrary draw calls sixty
times a second would be drawing *into the renderer*, across the boundary this
design exists to keep narrow, and every call would have to be validated anyway.
A readout is what an overlay is for.

A typo in an overlay draws the wrong thing; it does not disable the mod. A HUD
hook that latched off mid-round would take the score with it.

---

## What a misbehaving mod can do

"A script must not be able to provoke a panic" is a requirement, and it is met
by construction rather than by a handler: nothing crosses the boundary but plain
data, so there is no Rust object for a script to misuse. Release builds unwind
rather than abort — see `Cargo.toml` — so a panic that did escape would be
caught, but a caught panic is a bug report, not a design.

| Failure | What happens |
|---|---|
| Syntax error | Rejected at load; the mod never installs |
| Runtime error — `nil` index, bad arithmetic, `error()` | The mod is switched off for the session and the engine falls back |
| `while true do end` | Instruction budget expires → same as above |
| Runaway allocation | Memory cap → same as above |
| Reading a file, spawning a process, loading a C library | Impossible: `io`, `os`, `package` and `debug` are not in the interpreter |
| Loading Lua bytecode | Refused: `load` is removed and chunks are text-only |
| Reaching another mod's globals | Impossible: each script has its own environment |
| Reaching the simulation | There is no hook that can |

A latched failure is permanent for the session and reported **once**. A mod that
errors every frame must not cost a frame's work every frame, and must not bury
the log.

### The budget

```ini
[Mods]
instructions = 20000000   ; per call, not per session
memorymb     = 64         ; the whole interpreter
```

Per *call*: a mod that does a lot of work once a round is not penalised for it,
while one that never returns is stopped inside a frame. Twenty million
instructions is roughly 20 ms of dense Lua — far more than any menu or AI tick
needs, and far less than a frame.

---

## Hot reloading

```ini
[Options]
watch = 1
```

Edit a `.lua` and it reloads in place, from scratch, without restarting — and a
mod that had latched off after an error gets another chance, which is the whole
point of editing it. The title menu gains or loses its rows, and a scripted mode
that no longer exists stops supplying rules.

See [CUSTOMISATION.md](CUSTOMISATION.md#hot-reloading) for what else reloads.

---

## Checking a mod

```
$ oxtool mods .
mods
  ironman
  scoreboard
  turtle

modes declared  2
  ironman        base survival     SURVIVAL WITH NO RECOVERY BETWEEN BOUTS
  gauntlet       base arcade       TEN OPPONENTS - BEST OF ONE - NO RECOVERY

ai  exercising 120 frames
  answered 120/120 frames

flow  answered Map({"next": Str("gameover")})
hud   484 overlay item(s) over 180 frames  (frame, rect, text)

no problems
```

Every hook is called with the same payload the engine sends, field for field.
A probe that invents its own shape tests the probe.

---

## Where mods live

```
mods/
  ironman.lua          one file
  ratio/
    init.lua           or a folder, for a mod with data beside it
```

`mods/` first, then `data/mods/`, alphabetically — so two machines with the same
mods load them in the same order and a mod that overrides another does so
predictably.

Five ship with the engine as worked examples: `ironman.lua` (two modes),
`turtle.lua` (a defensive opponent), `scoreboard.lua` (an overlay and a flow
rule), `escalation.lua` (rules that climb, and a memory) and `tower.lua` (a
mode with screens of its own). `layout_demo.lua` is a sixth, for the screenpack
hook — see SCREENPACK-SCRIPTING.md.
