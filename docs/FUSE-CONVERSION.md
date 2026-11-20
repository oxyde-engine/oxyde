# Converting a character to FUSE without changing it

*Two bugs that made transcription lossy, the tool that now makes losing
impossible, and what still stands between here and 100% FUSE.*

## The contract

FUSE is a second spelling of the same character. A conversion that changes
behaviour is a bug in the transpiler, never a cost to accept. That is the
standard this page holds to, and the reason for the verifier described below.

## What went wrong

`oxtool fuseify` converted 3,894 files across the roster. Re-fighting every
character afterwards found **62 newly refused and 939 down more than five
points**. Two distinct causes, and both were invisible to fuseify's existing
guard, which compares a character's *shape* — its state count and move count —
and reverts if either changes. The shapes matched exactly.

### 1. The constants file was renamed

`Character::load` reads a character's constants only from non-script files:

```rust
for (rel, bytes) in &sources {
    if script_dialect(rel).is_none() {
        constants.absorb(&Def::parse_bytes(bytes));
    }
}
```

`[Data]`, `[Size]`, `[Velocity]` and `[Movement]` live in the file named by
`cns =`. The moment fuseify renamed that file to `.fuse`, the constants stopped
being read at all — and `velocity.walk.fwd` of zero is a character that cannot
walk. Measured on `Shin Kazuma`:

```
CNS   walks yes  jumps yes    ACCEPT 92%
FUSE  walks NO   jumps NO     ACCEPT 81%
```

Nothing else differed. Every state was present, every move was in the list.

**The fix.** `cns =` is MUGEN's *constants* slot and `st =` its *states* slot.
When the file carries constants, `cns =` now keeps pointing at the original
`.cns` while `st =` moves to the `.fuse`; state files load after the constants
file, so the FUSE states still win. Where `cns =` was the only key naming the
file, a fresh `st` slot is appended so the converted states are not orphaned.

### 2. Move lists were classified from the wrong list

A `StateDef` stores its controllers in the flat `controllers` vector that CNS
produces **or** in the structured `body` that FUSE and ZSS produce — never
both. `MoveList::classify` read only the flat one, so against a converted
character it saw no `SuperPause` and no `HitDef`:

```
CNS   SUPER    FURY   -> 8000    SPECIAL  FIN  -> 292
FUSE  SPECIAL  FURY   -> 8000    MOVEMENT FIN  -> 292
```

Every super was demoted to a special and every special to a movement. The moves
still came out and still connected; only their classification changed — which
is why nothing crashed and the count of states stayed identical. The move list,
the training trials and the CPU all read this join, so all three inherited it.

**The fix.** `each_controller` walks the flat list *and* descends the
structured body through `if`, `while` and `for`.

> The flat-list-only assumption is a recurring source of bugs. If code reads
> `state.controllers`, ask what it does for a FUSE character before believing
> the answer.

## The measurement trap that nearly hid the fix

Every character is scored against `chars/kfm/kfm.def`. Kung Fu Man is also a
roster character, so the first fix repaired *him* too — and comparing a sweep
taken before against one taken after made 100 unrelated characters look newly
broken. The ruler had moved with the thing being measured.

**Hold the opponent constant across both arms of any comparison**, or convert
it first and re-baseline. Two sweeps taken with different dummies cannot be
compared at all.

## `oxtool fuse-verify`

The fix for "a conversion must never make a character worse" is not vigilance,
it is a gate:

```sh
oxtool gate <root> <char.def> --tsv     # sweep before converting
oxtool fuseify <root>
oxtool gate <root> <char.def> --tsv     # sweep after
oxtool fuse-verify <root> before.tsv after.tsv --revert
```

It reports every character the conversion degraded and restores those to CNS
from the `.def.cns-backup` fuseify leaves behind. Degradation is judged on what
matters, not on the score alone: losing hittability, losing damage, starting to
freeze or leave the playfield, falling to `REFUSE`, or losing two or more
specials. A drop of a point or two is timing noise and is ignored.

Two details worth knowing if you script around it:

* the backup's extension is lowercased, so `AOSHI.DEF` has `AOSHI.def.cns-backup`;
* removing the `.fuse` files alone makes things **worse**, because fuseify
  repoints the `.def` at them. Restoring the `.def` is the revert.

## The three bugs the *third* pass found

Re-transcribing the whole roster after the constants work exposed three more,
each of which had been quietly capping conversion.

### Non-ASCII command names were mangled — ~483 characters

The FUSE expression reader built its text **byte by byte** with
`push(c as char)`, which turns every byte above `0x7f` into a Latin-1
character. So `command == "ファイアブレス"` compiled to
`command == "ã\u{83}\u{95}ã\u{82}¡…"` — a string that could never match the
command declared two lines above it.

The move simply vanished. No diagnostic, no error: the shape check then saw a
character with fewer moves than before and reverted the whole conversion.
**14.8% of command names across a large roster are not ASCII**, so this alone
was reverting about 483 characters. Shape reverts fell from 498 to 15.

### A `.def` that disagrees about case — 244 characters

`00julirn.cns` declared, `00JULIRN.CNS` on disk. The engine resolves that
through its VFS; `fuseify` called `std::fs::read` on the literal string, got
`Err`, and `continue`d — skipping the entire character without printing a
word. Now resolved one path component at a time, case-insensitively, and a
file that genuinely cannot be read is *logged* rather than skipped silently.

### Constants sections contain prose

A `[Data]` section routinely holds an unprefixed Japanese note or a `-----`
separator, and because it contains an `=` the INI reader returns it as a key
and a value. Emitting those verbatim produced FUSE that would not parse. They
are now dropped, which loses nothing: the loader ignores them too, because
neither side is a number.

## Where the roster ended up

| | first pass | after everything |
|---|---|---|
| characters degraded by conversion | 939 | **1** (reverted) |
| characters improved by >5 points | — | 9 |
| mean score change | −4.7 | **≈0** |
| state files converted | 3,894 | **8,339** |
| shape-check reverts | — | 498 → **32** |
| **characters 100% FUSE** | 0 | **1,824 (90%)** |

`fuse-verify` is run after every conversion and reverts anything it made
worse, so "the conversion changed nothing for the worse" is enforced rather
than hoped for.

## Can a character be a single FUSE file?

Its logic can, today. FUSE lets one file hold both `commands { … }` and
`state N { … }`, and a character written that way loads identically — verified
on Kung Fu Man, whose score, specials, attacks and state count are unchanged
when `cmd` and `st` both point at one combined file. See
`docs/examples/kfm-single-file.fuse`.

Its constants can too. The **constants block** — `constants { … }` — now carries
`[Data]`, `[Size]`, `[Velocity]`, `[Movement]` and Ikemen's `[Constants]`, and
the loader reads them straight out of the script file alongside its states and
commands (`Character::load` in `oxyde-core`). So a fully converted character can
be a single `.fuse` file for everything — logic *and* constants — with no `.cns`
left behind to carry numbers.

## The four further bugs the second pass found

Each was invisible to the shape check, and each changed a character.

### Meter costs were dropped

`Power >= n` sits on the enclosing `if` in FUSE, not on the controller, and the
move list read only the controller's own triggers. Every costed move converted
as free — all six of Kung Fu Man's. Fixed by threading the requirement down the
block walk beside the command names, which were already threaded for exactly
the same reason.

### `[Remap]` was never read

MUGEN's button remapping. 407 characters declare one; **10 swap their punches
and kicks**, and Oxyde ignored the section entirely, so those ten played with
the wrong buttons. Now parsed, applied in `Simulation::set_input`, and
expressible as FUSE's `remap { x = a }`.

### `[State-1]` was silently skipped

The controller-section test required a space. 20 sections written
`[State-1]` or `[State1000,10]` — which MUGEN tolerates — lost their
controllers with no diagnostic at all.

### A trigger the original rejected failed the whole file

The transpiler emits tokens rather than a parse tree, so `movecontact!` — a
trailing `!`, which does not compile in CNS either — came out unchanged and
then failed the FUSE parser, refusing conversion for **126 files**.

A trigger that does not compile never fires, in either language. So the
faithful conversion is a condition that is never true, with the author's text
kept beside it:

```fuse
if false /* was: movecontact! */ {
```

`false` is FUSE; `/* … */` is a FUSE block comment; `movecontact!` is the
author's original CNS text quoted inside it. FUSE itself has no trailing `!` —
nothing about the broken spelling leaks into the language.

`false` rather than `0` on purpose: generated code is still read by people, and
`if false /* was: … */` says what happened at a glance where `if 0 /* … */`
makes the reader work it out. The character behaves exactly as it did, the file
converts, and the fault is recorded rather than hidden.

### Four faults only playing both forms could find

Every state, constant and command compared identical for most of these, and the
fighters still played differently. `oxtool ab` (FUSE against the original files,
tick by tick) found each one, and a fresh conversion with the fixes plays all
eight characters it named exactly as their originals do:

* **A recovered trigger was written as `false`.** The loader reads
  `AnimElem > = 1 = 1` as `AnimElemNo(0) > 0` and fires; the converter wrote
  `false`, so a HitDef it guarded never landed. Such a trigger is now kept as
  `cns("…")`, compiled by the CNS front-end, which is the same program by
  construction. Test `a_recovered_trigger_converts_to_the_program_the_loader_runs`.
* **Equal guards shared one `if`.** Two CNS controllers with the same triggers
  each evaluate them; one shared `if` drew a `Random` once where the original drew
  it twice. Each controller now has its own. Test
  `controllers_with_equal_guards_each_get_their_own_if`.
* **A guard was read while its controller sat the tick out.** CNS never reads a
  controller's triggers while it is paused, already fired with `persistent = 0`,
  or off its `persistent = n` beat; the FUSE executor evaluated the surrounding
  `if` anyway, and a `Random` in it moved the random stream. An `if` over only such
  controllers is now skipped. This one is in the engine, so it reaches every
  converted character without regenerating anything. Test
  `an_if_guarding_a_controller_that_sits_the_tick_out_is_not_read`.
* **`time = 0` on a command.** The `.cmd` loader reads it as 1; the FUSE loader
  kept the 0 the converter faithfully carried across, and four attack buttons of
  one character never fired. Also in the engine. Test
  `a_zero_command_time_reads_as_one_in_fuse_as_in_a_cmd`.

The two converter fixes reach a character only when its `.fuse` files are
written again. `oxtool fuseify <root> --only-list FILE` does that in place for
the characters listed: a `.fuse` the converter wrote, with its CNS still beside
it, is refreshed when the CNS now converts to something else. The file it
replaces is kept once as `x.cns.fuse.refresh-backup`, and `oxtool revert <root>
--kind refresh --apply` puts every refreshed file back.

### One `if`, one reading

The converter fix above — one `if` per controller — was written for `Random`,
and it is more general than that. Two CNS controllers with equal triggers each
read them, and the second reads them **after the first has run**. One shared
`if` reads them once, before either. Homer's `[Statedef 3005]` is two `Explod`s
on `Time = 0 && NumExplod(1006) = 0`: in CNS the first explod makes
`NumExplod(1006)` one and the second never fires; under the shared `if` on disk
both did, and `oxtool ab` shows it — the computer fight parts at tick 689 with
two explods against one.

`oxtool fuse --verify` called those states identical, because it composed each
controller's guard from the `if`s around it: the *condition* was the same, only
the number of readings was not. `oxyde_cns::compare` now numbers each `if` and
asks, whenever one is shared by controllers that were separate in the CNS,
whether anything run between the readings can change what the condition reads.
`oxyde_cns::effects` answers that conservatively: what each trigger reads and
each controller writes, by name, with anything it does not name reading or
writing everything, `Random` and `:=` never shareable, and two constant
variable slots told apart (`VarSet var(2)` cannot change `var(1) = 0`).
Controllers split from one CNS controller share its single reading, correctly.
Tests `one_if_over_two_controllers_is_not_two_readings` and
`a_shared_reading_nothing_can_change_is_the_same_program`; with the check
switched off both fail.

`oxtool fusediff <root> --programs` asks the same question of the files **on
disk** rather than of a fresh conversion. Run across a large roster, it reports
the scope directly — for example **1,311 characters, 4,896 states** read a guard once
where their original read it per controller and something in between can
change it. 868 of those states draw `Random`; 406 follow an `Explod` and read
`NumExplod` or `ExplodVar`; 759 follow a `PosSet`, mostly the landing idiom `Pos Y >= 0` →
`PosSet y = 0` → `ChangeState`, which re-reads true and which the analysis
cannot prove harmless and does not try to.
A refresh removes every one of them without adding a difference: 2,055 files,
2,051 of them the same program in every state afterwards (the other four keep a
value their CNS could not compile either). `--regen DIR` writes those files for
inspection; `--apply` refreshes them in place through `fuseify`'s refresh, each
backed up once as `.fuse.refresh-backup`, and touches nothing else in the
character.

## What stands between here and 100% FUSE

Three things, in order of size:

1. ~~Constants have no FUSE syntax.~~ **Done** — `constants { … }` carries
   `[Data]`, `[Size]`, `[Velocity]`, `[Movement]` and Ikemen's `[Constants]`,
   round-trip tested key by key. This is what made full transcription possible:
   **1,300 characters now have every state slot in FUSE.**
2. ~~`ProjHitID(n)` was rejected.~~ **Done** — accepted alongside the three
   spellings of `ProjHit` Oxyde already took.
3. ~~126 files failed on a trigger the original also rejected.~~ **Done** — see
   above.
4. **A residual set still fails to transpile**, mostly `missing )` and
   comparison-form errors in `animelem` and `hitdefattr`. These are real
   grammar gaps rather than authoring faults, and each needs its own fix.
5. **A residual set still behaves differently** after conversion and is held on
   CNS by `fuse-verify`. Each is a transpiler bug waiting to be found, and each
   is reproducible: convert it, fight it, compare.

"Convert everything to FUSE" means "convert everything the transpiler can
express, and prove each one unchanged". The second half is the part that is
now enforced rather than hoped for.

## Why a character may be left as CNS

Before trusting any count of converted characters, check how it was taken. A
regex like `^ *(st[0-9]*|cns) *=` matches spaces only, and many `.def` files
separate the key from the `=` with a **tab** — so a fully converted character
(`586_misaki` is one) is counted as unconverted and the CNS total comes out too
high. Match whitespace of either kind.

A character genuinely still on CNS falls into one of a few buckets: it declares
no state file at all; it declares one that is unconverted; or it declares one,
is unconverted, yet is **carrying orphaned `.fuse` files** — and some of those
also carry a **conversion backup**.

### The orphaned-`.fuse`-plus-backup fingerprint

That last fingerprint — orphaned converted files beside a conversion backup —
is diagnostic. It means the character *was* converted, measured as worse, and
rolled back. That is the correct outcome when a conversion really is worse — but
not always the reason here. If the measurement that rejected them read a **stale
directory index** (see TOOLS.md), the freshly written `.fuse` files were
invisible, the character loaded with no states, and the conversion was blamed;
the reverts then needed re-attempting once that bug was fixed.

Agito is the clean example: every `.fuse` file it needs sits in its folder,
unreferenced, with `Agito.def.cns-backup` beside them — and converted in
isolation it produces six files and reverts none.

`oxtool inventory` reports this fingerprint as a signal to re-run the migration,
rather than leaving it to be rediscovered.

### Two converter faults found on the way

**A colon comment.** Rambo's `.def` declares five state files, two ending in a
`;` comment and three in a bare `:` one. The two loaded; the three did not,
because the filename read from those lines carried the whole comment. A colon
cannot appear in a filename except as a drive letter, which is only ever the
second character, so `ini::file_value` now ends a value there.

**Two parse failures in converted output**, still open: `expected '=' after a
constant name` (k9999) and `expected '{'` (robin). These are the converter
producing FUSE it cannot itself read, which is the clearest kind of bug to fix
and has a reproduction in each case.

### What remains on CNS

The characters that stay on CNS after a clean run are those that declare no
state file at all, and those that genuinely degrade when converted and are
correctly held back. One edge case is its own gap: a character that **cannot be
rolled back** because no `.def.cns-backup` exists. A revert that cannot revert
should refuse to apply in the first place.

## Is it the conversion? `oxtool ab`

Asked from play: are the character bugs being reported happening only in
FUSE, or would they happen in the original files too? Every converted
character still has what it was written in — `fuseify` keeps the old `.def` as
`x.def.cns-backup`, and the `.cns`/`.cmd` it names stay beside the `.fuse`
files — so the question is an experiment, not an argument:

* **Play it as it was written.** `oxyde --original`, `[Game] originalfiles =
  1`, or Options → System → `CHARACTER FILES`. The fight screen says
  `ORIGINAL FILES`. If the bug goes away, the conversion caused it. If it
  stays, it is the engine or the character, and converting it back would not
  help. `oxtool <anything> --original` asks any tool's question of the
  original form.
* **Measure both.** `oxtool ab <root> <character>` loads the two forms and
  runs them through one deterministic battery; `--roster` does an
  installation.

### What is measured

| Axis | How | Denominator |
|---|---|---|
| Functionality | `oxtool audit`'s battery on each form — walk, crouch, jump, turn, guard, fall and get up, be hurt, deal damage, finish a fight, never freeze, stay on screen, the six attack buttons and whether they land, every special and whether it lands, and the function score built from them | characters where both forms load |
| Behaviour | two scripted runs per form (the computer against the standard opponent, and a fixed input pattern against an idle one), compared every tick on each fighter's state, animation, element, position, life, power and control, and the live helper, projectile and explod counts | ticks; the first differing tick is printed with both sides |
| Static fidelity | the two forms *as the engine compiled them*: every state as bytecode (`compare::same_state`), every constant, every `[Command]` field, every derived move-list entry | states, constants, commands |
| WinMUGEN | [`winmugen::predict`](../crates/oxyde-tool/src/winmugen.rs) on the original files; WinMUGEN cannot read FUSE at all | characters with an original |
| Load report | Oxyde's warnings, compile errors, and compile warnings (FUSE reports a parameter given twice; CNS keeps the first silently, so the raw counts are not comparable) | per form |

### Worse, defined

The FUSE form is **worse** when it is behind the original on any axis of the
functionality table — a capability the original has and it lacks, or fewer
buttons, specials or hits landing, or fewer moves in the derived list — or,
with every such axis equal, a lower function score. The comparison is exact.
There is no tolerance, because there is no noise: the simulation is
deterministic, two runs of one form produce the same numbers, and any
difference is the forms'. **Fixed** is the same test the other way round, and
a character ahead on one axis and behind on another is **mixed**, never netted
to "no change".

### The guarantee

"No character does worse after conversion" is enforced, not hoped for:

* `oxtool ab <root> --roster --out base` writes a baseline.
* `oxtool ab <root> --roster --check base.tsv` exits nonzero if any character
  is worse with nothing protecting players from it, or if one that behaved
  identically in the baseline now diverges — the same contract as
  `oxtool regress --check`.
* `--apply-fallback` writes `x.def.play-original` beside every character that
  is worse, with the measured loss inside, and removes it from every one that
  no longer is. The loader then plays that character's original files
  (`Character::load` honours the marker; the explicit forms the tool measures
  with do not), and the fight screen says `ORIGINAL FILES`. Until the
  conversion is fixed, the worst a conversion can do to a character is leave
  it exactly as written.
* A difference somebody has looked at and judged benign is recorded in
  `x.def.ab-justified`, whose text the report prints. Nothing is waved through
  without one.

Every loss is also **classified by experiment**: the original is converted
again, now, by the current converter, into a scratch root (links for
everything, copies of what a conversion writes beside), and that fresh
conversion is scored. If it loses the same way, the converter is at fault and
fixing it there fixes every character with the pattern. If it does not and a
repair changed the FUSE form since (`fusediff`, `defrefs`, ... — the
`*-backup` files say which ran and on which file), the repair hurt and
`oxtool revert` takes it back. If neither, an older converter wrote the files
and re-running `fuseify` on the character fixes it.

### Three faults it found on its first run

All three were in the FUSE path only, which is why the 1,051-character CNS
regression never saw them.

**Negative states ran twice a tick.** 2,002 of the 2,406 converted characters
name one file as both `cns` and `st` — the ordinary MUGEN idiom, kept by the
converter as `cns = x.cns.fuse` and `st = x.cns.fuse`. CNS replaces a state
read twice, so that was harmless; FUSE *appends* `[StateDef -1]`, `-2` and
`-3` across files (Ikemen GO's common states depend on it), so the second
read appended the same blocks again and every `VarAdd` in them counted
double. Each file is now merged once.

**FUSE commands dropped their buffer through hit pauses.** `CommandSet::from_fuse`
defaulted `buffer.hitpause` and `buffer.pauseend` to off, where the `.cmd`
reader and MUGEN default them on. Every state and constant of `God Ken` was
identical in both forms and a special still would not come out in FUSE. The
test that was meant to prove the two readers agree compared five of a
command's seven fields; it now compares all of them.

**Fireballs were melee to the computer.** The move list's `ranged` flag read
only CNS's flat controller list, the same fault `classify` had once, so the
computer never threw a converted character's projectile from range. That
was the last difference between the two forms of `God Ken`: after it, both
scripted runs agree on every one of 2,400 ticks.

### Would WinMUGEN refuse it?

The predictor is seven load-time rules, each one a refusal WinMUGEN's own
error dialog named in the fitting sweep, generalised no further than the
dialog's wording, and then corrected by what WinMUGEN actually loads: `Clsn[0]
= ...` is a box and `Clns2[2] = ...` is not; a box count no frame follows is
dropped; triggers stop at the first missing number; a `[State]` before any
`[StateDef]` is never read; a repeated `[Files]` key is read once; `AnimElem`
keeps its low 32 bits and refuses a negative result. A missing command label
is reported but not counted, because it matched five refusals in the sweep
and then six held-out characters loaded with one.

Its agreement is measured, not asserted (`--winmugen-check <sweep.jsonl>`):

| Ground truth | Characters | Agreement | Refusals caught | Refusal calls right |
|---|---|---|---|---|
| The sweep of the base archive the rules were fitted to | 1,044 | 1,041 (99.7%) | 10 of 13 | 10 of 10 |
| Held-out sample 1, `Winmugen.exe` under wine, rules **as frozen before it ran** | 49 | 40 | 10 of 10 | 10 of 19 |
| Held-out sample 1, after the corrections it prompted (so no longer held out) | 49 | 49 | 10 of 10 | 10 of 10 |

The three sweep refusals it now misses are the three missing-command-label
cases it no longer counts. The first held-out sample was drawn to contain
every character the predictor then called refused (19) plus 30 it called
loading, so its agreement is not a roster rate; precision and recall are the
figures to read. A second held-out sample, drawn after the corrections, is in
`oxtool ab`'s report when it has been run.
