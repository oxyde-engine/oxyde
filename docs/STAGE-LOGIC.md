# Stage logic in FUSE

Stages in MUGEN and Ikemen GO are scenery. A `.def` describes camera bounds,
player start positions and a stack of `[BG]` layers that a renderer scrolls and
animates with `[BGCtrl]`, and none of it can read the fight or change it. A
spike pit that hurts you, a floor that gives way, a background that flares when
a super lands — none of that has ever been expressible, because a stage has no
state machine.

This document describes giving one to it, written in **FUSE** — the same state
language the characters and the common states are written in.

This began as a **foundation** — the design, the wiring into the simulation,
and one hazard end to end. Three named follow-ons now build on it, each proven
end to end:

1. **The stage-context trigger set** — a stage reads a fighter's position,
   velocity and state type through a `player(n)` redirect, so a hazard's *when*
   can live in a trigger.
2. **Breakable floors** — a second stage controller that drops the fighters
   standing on a zone, its condition written with (1).
3. **Reactive backgrounds** — controllers that flash and move the `[BG]` layers
   in response to a super, running *during* the pause the super holds.

The foundation's guarantees are unchanged: everything runs inside
`Match::step`, is deterministic and checksummed, and a stage with no FUSE logic
is byte-identical to before. What each addition does and does not cover is
stated with it below, and the remaining follow-on work is named at the end.

## Why FUSE and not Lua

Oxyde already lets a mod add game modes in Lua. Stage logic could not be one of
them, and the reason is the reason the whole engine is built the way it is.

A match in Oxyde is a pure function of its state and its inputs:
`Match::step` is deterministic, and nothing irreversible happens inside it.
That is what makes rollback netplay, spectating, replays and reproducible bug
reports the same capability wearing different clothes — see
[[oxyde-determinism-buys-features]]. The script boundary is enforced
structurally: `oxyde-script` is absent from `oxyde-core`'s manifest, so **no
Lua runs inside `step`** — see [[oxyde-the-scripting-boundary]].

A stage hazard has to run inside `step`: it reads where the fighters are and it
takes their life. So it cannot be Lua. A hazard scripted in Lua could not be
rolled back (the interpreter's heap is not in the snapshot), would not
re-simulate identically on a spectator's machine, and would make every replay
of that stage hostage to the exact mod file at the exact version. The same
hazard in FUSE is rollback-safe and replay-safe *by construction*, because FUSE
compiles to the same bytecode the fighters run and executes inside the same
checksummed tick.

That is the shape of the answer throughout this family of features: **what
happens inside the fight is FUSE; everything outside it is Lua.**

## The non-negotiable: it is purely additive

Both formats stay fully supported. A MUGEN stage `.def` with `[BG]`/`[BGCtrl]`
and no FUSE logic loads and plays **exactly as it does today** — zero behaviour
change.

A stage *opts in* by naming a FUSE state file:

```ini
[StageInfo]
states = stage-hazard.fuse
```

The key lives in `[StageInfo]` because that is where a stage's behavioural
configuration already lives (`zoffset`, `autoturn`, `resetBG`), and a stage has
no `[Files]` section of its own — this follows how a character `.def` names its
state files in `[Files]`, moved to the section a stage actually has. Neither
MUGEN 1.1 nor Ikemen GO has stage state logic at all, so there is no prior key
to honour; this is Oxyde's own, and it is documented here rather than guessed
at.

With no `states` key:

* `Stage::states_file` is `None` (`crates/oxyde-render/src/stage.rs`);
* the app never builds a machine, so `Match::stage_machine` is `None`
  (`crates/oxyde-app/src/game.rs`, `attach_stage_logic`);
* `Match::step` runs **not one instruction** of the stage machinery — the call
  is behind `if self.stage_machine.is_some()`;
* `Match::checksum` mixes **not one extra byte** — the fold is behind
  `if let Some(sm) = &self.stage_machine`.

So a stage with no FUSE logic is byte-identical in simulation to before the
feature existed. That is proven two ways:

* `oxyde_core::stage_logic::tests::an_inert_stage_machine_does_not_touch_the_fighters`
  steps two matches in lockstep — one with no machine, one with a machine that
  only changes its own state — and asserts both fighters are byte-identical
  every tick.
* `oxtool regress .. --check ../metrics/regression-baseline.tsv --listed`
  fingerprints the archive's original 1,051 characters, each fought by the computer against a dummy and against itself, and must report **1051 unchanged, 0
  moved**. None of those matches names a stage state file, so none carries a
  machine, so none can move.

## What a stage machine is

A stage is not a fighter. It has no `life`, no `anim`, no position, no command
list, and it is not a target. So the machine is deliberately smaller than a
character's.

`oxyde_core::stage_logic` defines it in two halves, so a rollback snapshot pays
for only what changes:

* **`StageProgram`** — the compiled, immutable states, behind an `Arc`. Keyed
  by state number in a `BTreeMap`, never a `HashMap`, because the checksum and
  the entry-state choice both iterate it and a `HashMap`'s order is not
  reproducible across machines. Cloning the machine clones this `Arc`, not the
  table.
* **`StageLive`** — the per-frame state a rollback copies: the current and
  previous state number, the state clock (`time`), the `persistent = 0`
  fire-once record, and the machine's own `var`/`fvar` banks (MUGEN's sizes,
  60 and 40, because a stage author already knows them).

It is compiled through **exactly the character front-end** —
`oxyde_cns::fuse::parse` then `oxyde_cns::script::lower` — so a stage state and
a character state are the same `StateDef` reached through the same door.
Nothing here is a second compiler.

### The machine begins in state 0

When a stage machine is attached, its live state starts in state `0` if the
file defines one, otherwise the lowest-numbered state — deterministic either
way because the source is a `BTreeMap`. The clock advances at the end of each
tick, so `time = 0` is true on the tick a state is entered, exactly as it is
for a fighter.

## Where it runs in the tick

`Match::step` calls `step_stage` after the fighters have moved and been clamped
to the stage, and before `step_round` judges the round:

* **after** movement and the stage clamp, so a hazard's zone check reads the
  fighters' *final* positions for the tick;
* **before** the round is judged, so a hazard that lands a killing blow is
  settled this tick like any other death.

**Under a pause** the foundation froze the whole machine. Follow-on 3 reopens
exactly one door, so a background can flash for a super *on the pause tick
itself*. While the screen is held for a `SuperPause` or a `Pause`:

* the clock does **not** advance (`state_time` is held), so nothing `time`-based
  drifts across a freeze;
* a `ChangeState` is suppressed, so the machine holds its state across the
  freeze exactly as before;
* every fight-touching and machine-progressing controller — `StageHazard`,
  `StageBreakFloor`, `VarSet` — is suppressed **before its guard runs**, so a
  fighter held motionless cannot be chipped or dropped and the shared RNG is not
  advanced on their behalf;
* only the background reactions run — `ModifyStageBG` and `BgPalFx`, guarded on
  `pausetime > 0`.

A stage with no background controller therefore behaves under a pause exactly as
it did under the foundation: its `if`-conditions evaluate but no controller
acts. The preserved invariant — a hazard cannot bite a frozen fighter — is
`a_hazard_cannot_bite_a_fighter_frozen_by_a_super`.

## The triggers a stage can read

`StageEnv` (in `oxyde_core::stage_logic`) is the `Env` a stage expression reads
through. It answers a curated subset and reads `0` for everything else — a
stage's `life` is not a small number, it is *no* number, and `0` is the
documented answer rather than a forgotten one.

| trigger | meaning for a stage |
|---|---|
| `time` | ticks the current stage state has run |
| `stateno`, `prevstateno` | the machine's own state numbers |
| `random` | the match RNG — deterministic and checksummed |
| `gametime`, `stagetime` | `Match::tick` |
| `roundstate` | the round's phase (intro / fight / over) |
| `roundtime` | ticks this round has run |
| `pausetime` | super-pause / pause ticks left — how a stage sees *"a super is active"* |
| `numplayer` | live root fighters on the stage |
| `var(n)`, `fvar(n)` | the machine's own variable banks |
| `stagevar(...)` | the stage's own `.def` settings, as the character-side trigger reads them |

### Reaching a fighter: the stage-context redirects (follow-on 1)

A stage has no "self", so the **self-relative** redirects — `parent`, `root`,
`partner`, `enemy`, `enemyNear`, `p2`, `target`, `helper`, `helperIndex`,
`stateOwner` — still yield `0`: each names a player *relative to the one
evaluating*, and there is no such player. What a stage **can** reach are the
redirects whose answer needs no self:

| redirect | who it reaches from a stage |
|---|---|
| `player(n)` | the fighter in seat `n` — `1` and `2` are the two front fighters, `3`/`4` their partners |
| `playerIndex(n)` | the raw `n`th entry of the player list, helpers included |
| `playerID(id)` | the player whose `id` is `id` |

Through one of those, a stage reads that fighter's `pos`, `pos y`, `vel`,
`life`, `alive`, `ctrl`, `stateNo`, `prevStateNo`, `time`, `facing`, `id`,
`statetype`, `movetype` and `var`/`fvar` — the **same triggers, with the same
meanings** the fighter side answers, because a stage trigger that mirrors a
character trigger must match its semantics (`docs/exp.html`). The
`a_redirected_statetype_reads_the_fighter` test compares the two paths for
every state type so the stage helper cannot drift from `sim`'s own.

This is what lets a hazard's *when* live in a trigger:

```fuse
state 1 {
    // Bite only a fighter who is standing in the band, not one who jumped it.
    if player(1).pos x in [-50, 50] && player(1).statetype != A {
        StageHazard(zone: -50, 50, damage: 25)
    }
}
```

**A redirect reaches only the living.** `player(n)`, `playerIndex(n)` and
`playerID(id)` apply the fighter side's own gate: a fighter whose life has
gone is not there, and every read through it is `0`. So a stage cannot watch
for `stateNo = 5150`. To act on a knockout, remember the fighter while it
stands — its place in the player list in a `var`, where it stood in an
`fvar` — and act on the tick it can no longer be seen; players are never
removed from the list, so the place is stable. `playerIndex(n)` past the end
of the list also reads `0`, so `life == 0` is true for an empty slot: test for
something a fighter sets. The worked example is the Knuckle Up prop blast,
`knuckleup/logic/oxyde_props.fuse` (written by
the prop pipeline; see [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md)).

**Why seats and not "nearest".** The follow-on brief floated a `nearest`
redirect. "Nearest" is a distance *from the asker*, and a stage has no position
to measure from — the same reason the self-relative redirects are empty. A
stage enumerates the fighters it cares about by seat (`player(1)`,
`player(2)`), which is deterministic, self-independent, and exactly MUGEN's own
handle for "the fighter on that side"; `numplayers` bounds the loop. The zone
check may still live in the controller (it has the whole player table in hand),
but it no longer *has* to.

## The controllers a stage can run

`Match::run_stage_ctrl_kind` dispatches the subset a stage understands:

* **`ChangeState`** — move the machine's own state. Resets the clock and the
  fire-once record and follows the change within the tick, exactly as a
  fighter's does, with the same bounded-hop guard against two states that
  bounce off each other.
* **`VarSet` / `VarAdd`** — write the machine's own `var`/`fvar` banks. This is
  what a FUSE `var(0) = expr` statement compiles to, so a stage that remembers a
  fighter's last position between ticks has a place to keep it. A stage has no
  `sysvar` banks, so those writes are dropped, exactly as `StageEnv::set_var`
  drops them.
* **`StageHazard`** — take life inside a zone (below).
* **`StageBreakFloor`** — drop the fighters standing on a zone (follow-on 2).
* **`ModifyStageBG` / `BgPalFx`** — react the `[BG]` layers (follow-on 3).
* **`Null`** — nothing.

Any other controller — one that belongs to a fighter — is ignored. That is the
safe, documented answer: a stage is not a fighter and has no field for a
fighter's controller to write. (A stage may also write its own `var`s inside a
trigger, `var(0) := ...`, which goes through `StageEnv::set_var`.)

Variable banks aside, the structured body itself is fully supported: `if`,
`while`, `for`, `let`, `stop`, `break` and `continue` all run, evaluated
against `StageEnv`, with the same loop cap (`MAX_LOOP_ITERATIONS`) and nesting
bound the fighter path uses — a runaway stage loop cannot hang the frame.

## The one hazard: `StageHazard`

`StageHazard` is a new state controller, `oxyde_cns::sctrl::SctrlKind::StageHazard`,
Oxyde's own provenance (it is the first controller Oxyde adds that neither
Elecbyte's manuals nor Ikemen GO name). It does nothing in a fighter's
`execute` and everything in `Match::stage_hazard`.

It damages every root fighter whose feet are inside a horizontal zone:

| parameter | meaning |
|---|---|
| `zone = x1, x2` | the world-x span (order-insensitive). Omit it and the whole floor is the zone. |
| `damage = n` | life removed from each fighter in the zone this fire. |
| `kill = 0\|1` | whether the damage may drop a fighter to `0` (a KO). Defaults to `1`; `0` floors life at `1`. |
| `launch = 0\|1\|2` | the hit reaction. `0` (the default, and every stage written before it) takes life and nothing else. `1` lands a knockdown, thrown away from the zone's middle; `2` a long stagger (a shock). Either is a hit from nobody through the fighter's own get-hit states (`oxyde_core::blast`), so their invulnerability holds; its damage is capped at a fifth of their life, and a prop in the zone is dented but never broken. |

Parameters are expressions, evaluated against `StageEnv`, so `damage` may scale
with `time` or a stage `var`. It applies to roots, not helpers — a helper is
the character's own creation and its life is the character's business — and it
mirrors the combat path's own clamp-and-`alive` handling so a hazard KO looks
like any other death to the round logic.

The worked example is [`examples/stage-hazard.fuse`](examples/stage-hazard.fuse):
a centre-band spike that extends, bites every six ticks, and retracts.

### It is proven

`oxyde_core::stage_logic::tests`:

* `a_floor_spike_damages_the_fighter_in_its_zone_and_spares_the_one_outside` —
  two fighters, one in the band and one clear of it; after the spike extends
  and bites, the one in the band has lost life and the one outside is
  untouched. This is the test that fails first: with the damage line in
  `stage_hazard` disabled, both keep full life and it fails, and it is the
  *only* test that fails — the mutation check.
* `the_hazard_is_deterministic_tick_for_tick` — two identical matches produce
  the same checksum every tick.
* `the_stage_machine_state_reaches_the_checksum` — forcing one machine into a
  different state parts the checksums, so a stage divergence is a reported
  desync, not a silent one.
* `a_hazard_with_launch_knocks_down_and_one_without_only_takes_life` — the
  same zone with `launch: 1` puts the fighter in it through a knockdown, and
  without it takes only life, as it always did.
* `an_unknown_stage_controller_is_a_diagnostic` — a typo'd controller in a
  stage file is refused with the nearest real name, not silently dropped.

## The breakable floor: `StageBreakFloor` (follow-on 2)

`StageBreakFloor` is Oxyde's second stage controller (`SctrlKind::StageBreakFloor`).
It drops every root fighter *standing on* a horizontal zone into a fall:

| parameter | meaning |
|---|---|
| `zone = x1, x2` | the world-x span (order-insensitive). Omit it and the whole floor gives way. |
| `depth = n` | how far the floor drops, in world units. Default `240`, about a screen height. |
| `vel = v` | the downward velocity the drop starts with. Default `0`; gravity does the rest. |

**The mechanism, and why this one.** A fighter falls when its feet are above
its floor under gravity, and MUGEN already gives every fighter a *personal*
floor — `GroundLevelOffset` (`Player::ground_level`) — for platforms. The
controller lowers that floor by `depth` and switches the fighter to air physics;
`Match::apply_physics` does the falling and the landing at the pit bottom next
tick, and the stage clamp never touches `y`, so nothing fights it. The rejected
alternative was to `ChangeState` the fighter into a common fall state (5050),
which needs the character to *have* that state and not override it — a breakable
floor must work on **every** character, so it uses physics, which every
character has.

"Standing on it" is `pos.y` at or below the fighter's current floor: an
already-airborne fighter is not supported by this floor and is spared, which
also means the controller cannot re-drop a fighter it has already dropped.
Roots only, for the same reason `StageHazard` is.

The **condition** — *when* the floor breaks — is written with the follow-on-1
trigger set, not baked into the controller: the worked example watches
`player(1).pos x in [-50, 50] && player(1).statetype != A` and only then
`ChangeState`s to the broken-floor state.

Proven by `oxyde_core::stage_logic::tests`:

* `a_broken_floor_drops_the_fighter_on_it_and_spares_the_one_clear` — the
  fighter over the pit falls (`pos.y` climbs, its floor drops); the one clear of
  it keeps standing. Fails first with `p.ground_level += depth` disabled, and it
  is the only test that fails — the mutation check.
* `the_broken_floor_is_deterministic_tick_for_tick` — two identical matches
  agree on the checksum every tick, so the fall (`pos.y`, `vel.y` and
  `ground_level` are all in the hash) cannot drift.

## Reactive backgrounds: `ModifyStageBG` and `BgPalFx` (follow-on 3)

A stage can now reach its own `[BG]` layers from the machine, so a background
can react to the fight:

* **`ModifyStageBG`** — change a `[BG]` element, narrowed by `id`/`index`, with
  Ikemen GO's parameters: `pos.x`/`pos.y` (from the start position, the scroll
  included), `velocity.x`/`.y`, `delta.x`/`.y`, `start.x`/`.y`, `actionno` (anim
  elements), `spriteno` (normal elements), `layerno`, `trans` and `alpha`,
  `scalestart`, `angle`/`xangle`/`yangle`, `xshear`, `focallength` and
  `projection`. It writes the `Match::stage_bg` mirror, the same one a
  fighter's `ModifyStageBG` writes, and stamps each field it wrote; the
  renderer reads the mirror every frame and applies each stamp it has not
  applied yet (`Stage::apply_bg_mirror`), so the stage's own `[BGCtrl]`s carry
  on afterwards and the latest write wins. The mirror is filled from the
  stage's `[BG]` elements, in file order, when a round is set up
  (`Stage::seed_bg_mirror`), which is also what `NumStageBG` and `StageBGVar`
  count and read. `alpha` without `trans`, which Ikemen refuses, fades the
  element here.
* **`BgPalFx`** — set the stage's own `Match::bg_palfx`, the palette effect the
  renderer folds over every layer, so the sky can flare white for a super. The
  core flash parameters — `time`, `add`, `mul`, `color`, `invertall` — are
  supported; the sine/hue extensions are not (a reaction flash does not need
  them, and a stage author reaching for them is the next follow-on).

Both run **during a pause**, guarded on `pausetime > 0` — see *Under a pause*
above — because a super flash that could not fire while the super holds the
screen would be pointless.

A fighter's `ModifyBGCtrl` reaches the stage's `[BGCtrl]` blocks the same way:
its `time`, `value`, `x` and `y` are kept per `sctrlid` in `Match::bg_ctrl_edits`,
which the renderer reads every frame and writes into each `[BGCtrl]` that carries
that `sctrlid` (`Stage::apply_bg_ctrl_edits`). Like Ikemen GO, a controller that
names no `sctrlid` answers to `0`. `ModifyBGCtrl3D` is recorded and has nothing to
move.

**Simulation or presentation?** Neither `stage_bg` nor `bg_palfx` is folded into
`Match::checksum`: both are **presentation mirrors**, and each is a deterministic
function of the checksummed machine state that drove it — exactly as the
*fighter-side* `ModifyStageBG`/`BgPalFx` already are. The machine's *decision* to
fire (its `state_no`, `once_fired`, `var`s) **is** checksummed, so two peers can
never disagree about whether the reaction happened. A fighter can read a layer
back through `StageBGVar`; that is the pre-existing reason the mirror values must
be — and are — a pure function of checksummed state, and these controllers keep
that contract rather than changing it. So the effect is presentation; the
*decision* is simulation, and it is the decision that is checksummed.

Proven by `oxyde_core::stage_logic::tests`:

* `a_background_reacts_to_a_super_during_the_pause` — with a super holding the
  screen, a `[BG]` layer slides and fades and the palette flashes white, all on
  the pause tick. Fails first with `ModifyStageBG` removed from
  `ctrl_runs_during_pause`, and it is the only test that fails — the mutation
  check.
* `a_background_is_untouched_without_a_super` — the negative half: no super, the
  `pausetime > 0` guard never holds, the layer is never touched.
And from the mirror to the screen, by `oxyde_render::stage::tests` and
`oxyde_core::exec_ext::tests`:

* `the_mirror_is_every_bg_element_in_file_order` — what the simulation is handed
  is the stage's `[BG]` list, ids and all.
* `a_modify_stage_bg_edit_reaches_the_layer_once_and_then_bgctrl_may_win` —
  `pos.x`, `actionno`, `spriteno`, `layerno` and `trans` land on the layer,
  each on its own kind of element, once; a `[BGCtrl]` afterwards wins.
* `a_new_round_seeds_a_fresh_mirror_and_its_first_edit_still_lands`.
* `modify_stage_bg_selects_by_id_and_index_and_stamps_what_it_wrote` — `id` and
  `index` select as Ikemen's `getMultipleStageBg` does.
* `a_modify_bgctrl_edit_rewrites_the_controller_its_sctrlid_names`.

* `a_hazard_cannot_bite_a_fighter_frozen_by_a_super` — the preserved invariant:
  a hazard is *frozen* during the same pause the background reacts in, so a
  motionless fighter is never chipped, and it bites again the instant the freeze
  lifts.

## Determinism, restated

Every guarantee above rests on the same property, and each is a test rather
than a promise:

* the machine reads no `HashMap` iteration order and no wall clock — its RNG is
  the match's, folded into the checksum;
* its live state is part of `Match::checksum`, so two peers whose stages have
  drifted are *caught*, at the same 30-frame cadence a drifted fighter is;
* it runs at a fixed point in the tick, so a replay reproduces it exactly.

## What is landed, and what is still follow-on

The three follow-ons the foundation named are now landed:

* **The stage-context trigger set** — `player(n)`/`playerIndex(n)`/`playerID(id)`
  redirects, reading a fighter's `pos`, `vel`, `statetype` and the rest.
* **Breakable floors** — `StageBreakFloor`, its condition written with the
  trigger set.
* **Reactive backgrounds** — `ModifyStageBG` and `BgPalFx`, running during a
  pause.

What is honestly **still** follow-on:

* **`EnvShake` from the stage side.** A background that *shakes* for a super,
  not just flashes and slides, wants the stage to drive `EnvShake` the way a
  fighter can. `BgPalFx`'s sine/hue palette extensions are not wired either.
* **`StageBGVar` reads the mirror, not the screen.** The mirror is what the
  round started with plus every `ModifyStageBG` since; motion the stage's own
  `[BGCtrl]`s and `velocity` add on the renderer's side is not fed back, so
  `StageBGVar(id, 0, pos.x)` does not follow a scrolling layer.
* **Distance and edge triggers.** A stage reads a fighter's position by seat,
  but there is no stage-native `p2bodydist`-style distance between two fighters,
  nor a "how close to the stage edge" that a wall hazard might want. A stage can
  compute these from `player(1).pos x` and `player(2).pos x` today; a dedicated
  trigger would be sugar.
* **`StageBreakFloor` variety.** The floor drops straight down a fixed depth.
  A floor that tilts, crumbles in stages, or that a fighter can be knocked back
  onto is more machine, not more engine.
* **A `nearest`/self-anchored redirect.** Deliberately *not* built — a stage has
  no position to be "near" — but a hazard anchored at its own `zone` centre
  could justify one later; it would be sugar over a seat scan.

Each remaining item is a controller and/or a trigger added to the same machine,
which is the point of having landed the machine first.
