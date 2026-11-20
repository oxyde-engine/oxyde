# Does FUSE cover everything MUGEN and Ikemen can say?

*The audit, what it found, and why the question needs asking on three axes
rather than one.*

## Why this page exists

FUSE had no syntax for a character's constants for months, and nobody noticed.
Every controller was covered. Every trigger was covered. Those are the two
things anyone counts when asked whether a language is complete, and both
answers were "yes" while a character still could not be fully written in FUSE.

What was missing was a whole **file section** — `[Data]`, `[Size]`,
`[Velocity]`, `[Movement]` — and no check compared the sections real content
contains against the sections the language can express.

So the audit checks three axes, and `oxtool coverage` runs it:

```sh
oxtool coverage                 # the tables alone
oxtool coverage <installation>  # …and what the archive actually contains
```

It exits non-zero if any section used five or more times cannot be expressed.

## 1. Controllers — 160, all writable

FUSE emits controllers from the same `SctrlKind` table the engine executes, so
parity here is structural rather than maintained: a controller that exists can
be written. Ikemen GO's own additions are in that table too — `MapSet`,
`MapAdd`, `RemapSprite`, `ModifyHitDef`, `TargetAdd`, `PlayBGM`,
`DizzyPointsAdd`, `GuardPointsAdd`, `RedLifeAdd`, `TagIn`, `TagOut` — all
present and all writable.

## 2. Triggers — 281, all readable

Same table, same argument. Oxyde carries the MUGEN set plus Ikemen's, plus
thirteen of its own.

## 3. File sections — the axis that was missing

| section | how FUSE says it |
|---|---|
| `[Statedef N]` | `state N { … }` |
| `[State …]` | a controller call inside a state |
| `[Command]` | `commands { name = motion }` |
| `[Defaults]` | `commands (time: …, buffer: …)` |
| `[Data]` `[Size]` `[Velocity]` `[Movement]` | `constants { data { … } … }` |
| `[Constants]` (Ikemen) | `constants { … }`, written bare |
| `[Remap]` | `remap { x = a }` |

Measured against the 2,152-character roster: **222,968 of 222,989 section
instances covered**, and *no section used five or more times is missing*. The
remainder are bracketed comments and typos in authors' own files.

## What the audit found the first time it ran

Two real gaps, both now closed.

### `[Remap]` was not read at all

407 characters declare one. 397 are the identity and cost nothing — but **10
swap their punches and kicks**, and Oxyde ignored the section entirely, so
those ten played with the wrong buttons and nothing reported it.

Now parsed into `ButtonRemap` and applied in `Simulation::set_input`, the one
point where raw input becomes a player's history, so command matching,
`AssertInput` and the buffer all see the logical buttons. Helpers copy their
root's already-remapped history and inherit it for free. FUSE gained
`remap { x = a }` and the transpiler emits it.

### `[State-1]` was silently skipped

The controller-section test was `lname.starts_with("state ")` — with a space.
MUGEN tolerates `[State-1]` and `[State1000,10]`, and the archive contains 20
of them. Every one was dropped, taking its controllers with it: a move that
never fires and nothing to show for it. Now any `state` followed by a space,
digit, `-`, `,` or `+` is a controller section, while `[Stateless]` still is
not.

## The rule this leaves behind

A language feature is not covered because its controller exists. It is covered
when **a real file containing it can be read, written, and read back
identically**. The round-trip test in `oxyde-core` does exactly that for
constants: parse CNS, transpile to FUSE, parse that, and assert every constant
key, every tuple component and every `.x` alias matches. Anything added to the
language should get the same treatment, and `COVERED` in
`crates/oxyde-tool/src/coverage.rs` should gain a row on the same commit.
