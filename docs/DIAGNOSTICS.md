# When something does not load

Oxyde starts anyway. That is deliberate — a broken mod or an unreadable
character should cost you that mod or that character, never the game. The cost
of the choice is that a game can quietly do less than it should, so everything
that went wrong has to be somewhere a person can read it.

## The screen

A **PROBLEMS** row appears on the title menu, above OPTIONS, **only when there
is something to read**. A permanent "PROBLEMS (0)" on a healthy game trains
everybody to ignore it, and then it is useless on the day it matters.

```
FAILED    mods/ratio.lua:12: attempt to index a nil value
ADJUSTED  mods/expert.rules:4: damage_scale = 50, clamped to 10
NOTE      data/mugen.cfg: [Arcade] AI.Cheat = 1
```

Three severities. **FAILED** means something you expected is absent.
**ADJUSTED** means it loaded, but not as written. **NOTE** means nothing was
lost. Failures sort first, so the first line on the screen is the one that cost
you something.

## Provenance is the whole point

*"invalid value"* is a dead end. *"expert.rules line 4: damage_scale = 50,
clamped to 10"* is a fix. Every entry carries where it came from, and
`Diagnostic` cannot be constructed without one — `origin` is not an `Option`,
so a call site that has nothing to say has to write "unknown" and be seen doing
it.

## What this replaced

Four separate lists, each printed to a terminal a player double-clicking an
icon never sees, and each **truncated**:

| source | shown | now |
|---|---|---|
| `Assets::warnings` | first 5 | all of them |
| `MugenConfig::unsupported` | first 3 | all of them |
| the screenpack's warnings | first 4 | all of them |
| `Mods::problems` | **none — read by nothing outside `mods.rs`** | all of them |

The first run after consolidating them reported **4 problems where the old
output showed 3**: a `[p2 joystick]` note had been falling off the end of a
`take(3)` since the day it was written. Four caps mean a player is told their
game has "a few notes" when it has two hundred.

## Bounded, not a log

Entries are deduplicated by (origin, message) and counted, so one fault across
a 2,400-character roster is one line saying `(x2400)` rather than 2,400 lines
burying everything else. The list is capped at 200 and admits what it dropped —
*"and 1,847 more"* is information; an unbounded list is not.

A log grows forever and is read by somebody who already knows what they are
looking for. This is a short list of things a person can act on.

## Safe mode

```
oxyde --safe
```

Starts with mods and file watching off. It is a **flag, not a setting**,
because a setting lives in the config file that might be the problem, and it is
applied *after* the config file is read so it always wins.

It turns off only what a game can run without. The renderer, the roster and the
screenpack are not optional; a fault in one of those is a bug to fix, not
something to switch off.

## You should not have to know safe mode exists

The person who most needs it is the one least likely to have read this page. So
the engine writes `.oxyde-starting` before it loads anything optional and
removes it once the game is up. If that file is still there at the next start,
the previous run died somewhere in between — which is exactly the window in
which a mod, a screenpack or a config file gets to break things — and safe mode
is entered automatically, with a line on the Diagnostics screen saying why.

No crash handler is involved, and nothing has to run *during* the failure. The
mechanism is a file that did not get cleaned up, which works however the
process died — including a power cut. Writing the mark is best-effort: a
read-only installation loses the automatic rescue, not the ability to start.

## The rule underneath all of it

**Customization may change what the engine does. It may never change whether
the engine runs.**
