# Rulesets: a base mode plus a stack of toggles

A ruleset is a named set of changes that applies to **any** mode. "Expert" is
one file, not four; switching it on top of Arcade, Survival or Team Rumble does
the same thing to each.

```ini
; rules/expert.rules
[Modifier]
name        = EXPERT
description = MAXIMUM CPU, ONE ROUND, NO RECOVERY

[Set]
rounds_to_win = 1
difficulty    = 8
recover       = 0
```

`oxtool rules <root> --list` prints every rule a modifier may set, with its
range. `oxtool rules <root>` checks every ruleset in an installation and
reports all of it at once.

## Why a stack instead of more modes

`N` modes and `M` modifiers give `N × M` experiences from `N + M` things to
write. "Expert" as a *mode* means writing Expert Arcade, Expert Survival,
Expert Team Arcade and Expert Rumble — and writing them again when a fifth
mode appears.

The machinery was already here. `mods::apply_rules` is a sparse overlay onto a
mutable `Rules`: a scripted mode states the two fields it wants changed and
everything unmentioned keeps the base mode's answer. **A modifier stack is that
function called more than once.**

## The default path is unchanged code

An empty stack applies nothing. `Game::rules()` skips composition entirely when
nothing is switched on, so there is no branch a normal game takes that it did
not already take.

`an_installation_with_no_rulesets_is_unchanged` asserts it over **every mode**,
not just the one somebody happened to test — so "adding this changed nothing"
is a test that fails the build rather than a claim anyone has to believe.

## What a modifier may touch

Only the 23 knobs in `ruleset::KNOBS`, **every one of which the engine already
reads**. `life_scale`, `power_bars`, `command_buffer`, the meter rates,
`liedown_scale`, `super_freeze_max`, the universal mechanics (`chip_damage`,
`universal_recovery`, `burst`, `push_block`) and their costs, and
`corner_break` (a hard hit on a cornered opponent smashes the wall into the
stage's `[Break]` destination — see [EXTENSIONS.md](EXTENSIONS.md#the-camera))
are fields of `oxyde_core::sim::MatchRules`; `rounds_to_win`, `recover`, `turns`
and the rest are fields of `mode::Rules`. Nothing here is new plumbing into the
simulation.

The shipped **`ARCADE EDITION`** ruleset (`rules/arcade-edition.rules`) turns the
whole universal-mechanics layer on at once — burst, push-block, tech, chip and a
looser input buffer — so a scraped roster plays like a game designed around those
systems. It is the universal-mechanics layer expressed as data, not code.

**Nothing runs inside `step()`.** The values are read once when a match is set
up, exactly as `rounds_to_win` already was. That is what keeps rollback,
replays, spectating and netplay working, and it is not negotiable for a rules
screen. A modifier that wanted to run code during a fight would be a different
feature with a different cost.

A knob that parses and then does nothing would be worse than a missing one — it
reads as supported and silently is not — so `every_knob_in_the_table_does_something`
sets each one and asserts something changed. It caught two bugs in its own first
two versions: `carry_power` is already on for Arcade, and `difficulty`'s
midpoint is its default, so both looked dead when they were not.

## Conflicts are reported, not resolved quietly

Two rulesets setting the same rule: the **later** one wins, because that is the
order the player switched them on and it is the only rule a person can predict
without reading the files. The collision is named:

```
NOTE  rules/expert.rules: `rounds_to_win` was already set by MARATHON;
      EXPERT wins because it is later in the stack
```

A rules system whose conflicts are invisible is how somebody ends up unable to
explain the match they just played.

## Clamp and report, never trust and never fail

| what you wrote | what happens |
|---|---|
| `rounds_to_win = 10000` | clamped to 99, reported with the file and both numbers |
| `rounds_to_wins = 3` | *"no rule called `rounds_to_wins`; did you mean `rounds_to_win`?"* — the rest of the file still loads |
| `training = maybe` | read as no, and said so |
| `life_scale = lots` | left alone, and said so |
| two files with the same `name` | the second is refused by name rather than shadowing quietly |
| a malformed file | that file is skipped; every other one loads |
| `training` with a ladder | refused by name — nobody can be knocked out, so no bout can end |

Every message carries the file it came from. *"invalid value"* is a dead end;
*"expert.rules: life_scale = 99, clamped to 4"* is a fix.

## Checking before you play

```
oxtool rules <game-root>
3 ruleset(s) in <game-root>/rules
  EXPERT             3   rule(s)   MAXIMUM CPU, ONE ROUND, NO RECOVERY
  GLASS CANNON       1   rule(s)   HALF LIFE BOTH SIDES
  MARATHON           1   rule(s)   BEST OF SEVEN

3 note(s):
  ADJUSTED  rules/broken.rules: life_scale = 99, clamped to 4 (allowed 0.1..4)
  ADJUSTED  rules/broken.rules: no rule called `rounds_to_wins`; did you mean `rounds_to_win`?
  ADJUSTED  rules/broken.rules: training = `maybe` is not yes or no; read as no
```

**Exit code 0.** A clamp is not an error — the game runs, the value is stated,
and failing a build over "99 instead of 10000" would teach people to stop
running the check. Only a ruleset that could not be loaded at all makes it
non-zero.

Parsing alone finds unknown keys; a value out of range is only discovered when
it is *applied*, so both the checker and the engine compose each ruleset on its
own at load. An author wants every problem in their file at once, not the first
one, and not only the ones a particular stack happens to reach.

## Shipped examples

`rules/arcade-edition.rules` — the "designed game" preset: it turns the whole
universal-mechanics layer on at once (burst, push-block, universal recovery,
chip, a looser input buffer), so a scraped roster plays like a game built around
those systems. `oxtool mechanics` measures that each of those knobs actually
fires across the roster.

Also `expert.rules`, `glass-cannon.rules` (half life both sides — fights last
about twenty seconds) and `marathon.rules` (best of seven).

## Still to come

The **rules screen**: toggling from inside the game, and a Save As that writes
the file for you. Nobody's first customization should require a text editor,
and a finite vocabulary of a couple of dozen named parameters is exactly what a screen of
checkboxes and sliders can be built for — which is the point of keeping the
vocabulary finite.
