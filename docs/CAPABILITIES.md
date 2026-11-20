# Capabilities — Oxyde and FUSE

What the engine and the language can actually do, in one place.
Every number here is **derived from the code** by `oxtool docs` (which fails the
build if a figure drifts), as of the latest build; the features are the ones
that exist and are tested, not a roadmap.

**At a glance:** 298,000 lines of Rust across 14 crates, 2,981 tests, a 2,527-
character playable roster (2,504 in the test roster), 160 state controllers,
281 triggers, 215 stages, and a 78-command tool.

---

## Part 1 — Oxyde, the engine

### Compatibility (the whole premise)
- Runs **MUGEN content unmodified** — WinMUGEN through 1.1. None of it ships with
  the engine; you bring your own `chars/`. Correctness is **measured against a
  test library of over 2,500 real MUGEN/Ikemen characters** (2,527 today), every
  one of which loads, simulates and renders — and a 900-tick determinism
  fingerprint over a fixed 1,051-character baseline is the gate, byte-identical
  after every change.
- **160 state controllers** (90 from Elecbyte's manuals, 66 shared with Ikemen
  GO, 2 Oxyde's own and 2 unattributed) and **281 triggers** (148 beyond the
  manuals).
- Sprite formats **SFF v1 and v2.01**, animations (AIR), state code (CNS),
  commands (CMD), palettes (ACT), sound (SND), and glTF/WebM where Ikemen added
  them.

### Determinism — the capability everything else is built on
`Match::step` is a pure function: a whole match is two `u16`s a frame. Nothing
irreversible happens inside it. That single property *buys*, rather than
re-implements:
- **Replays** (record / play / verify / export), ~2 KB a match.
- **Rollback netplay**, and a setup-hash that **refuses** a mismatched match
  rather than desyncing.
- **Spectating** — one match relayed to any number of watchers for free.
- **Reproducible bug reports** — a replay *is* the repro, now with content-hash
  identity so a mismatch is named ("you have a different version of this
  character").
- **Tournaments** across many machines.

### Rendering
- A **software rasteriser** that is authoritative (the GPU path must draw the
  same thing), plus a **wgpu / Vulkan** hardware path.
- A real **depth axis** (Ikemen-style 2.5D): `pos_z`, depth-gated hits,
  perspective projection, depth-sorted draw.
- EnvColor, the super-flash darkening, afterimages, shadows, glTF backdrops,
  shaders.

### Online — nine modes, not one
Versus · Team Rumble · Team Tag · **Tag with a (CPU) Partner** · Tournament ·
**King of the Hill** · Relay · Round Robin · **Spectate a lobby**. Plus
**Corrosion mode**: the engine runs on a host and streams the picture to a
content-less client, so a laptop can play a 40 GB roster it does not have.

### Modes
Arcade, Team Arcade, Versus, Survival, **Training-as-a-debugger** (frame-step,
save/load state, input history, a recording dummy, hitbox overlay, a live frame
meter), **auto-generated combo Trials**, Bonus games, Team Rumble, Roster
Rumble, Team Tag, and **Knuckle Up** — a belt-scroll beat-'em-up with depth
movement, waves, pickups (health/weapon), bosses and declarative `.knuckle`
campaigns. New modes can be added in **Lua** (matchup / persistent state /
screen-graph hooks) without touching the simulation.

### The universal-mechanics layer (opt-in, off by default)
Engine-wide systems applied to *any* character without editing it, because the
common states are Oxyde's own — each a `MatchRules` knob, gated so the default
roster is untouched:
- **Parry** (with an **absorb** layer — trade the parry's frame advantage for
  power or recoverable life), **burst** (combo escape), **push-block** (advancing
  guard), **ground/air tech**, **chip damage**, **red-life / dizzy / guard-break**
  meters, **auto-balance** (clamp outliers to the roster's own distribution),
  a looser input buffer, faster get-up, and a cap on super-freeze.
- The shipped **`ARCADE EDITION`** ruleset turns the layer on at once — a scraped
  roster that plays like a designed game.
- **Rulesets:** 23 knobs the engine already reads, stacked as sparse deltas.

### Derived facts (measured, not hand-written)
Frame data (startup / active / recovery / on-block, checked live against the
game), a per-character capability inventory, balance percentiles, and a health
audit that scores how much of a character works — all computed by *simulating*.

---

## Part 2 — FUSE, the language

### What it is
Oxyde's own successor to MUGEN's CNS, and a **superset**: it runs existing CNS
byte-for-byte *and* adds modern language features. Oxyde owns the language and
the common states (`common1.fuse`), which is what makes engine-wide mechanics
and code reuse possible at all.

### Language features
- States, controllers and triggers, as CNS — plus structure CNS never had.
- **`import`** with inheritance and cycle-guarding — a "shoto base" several
  characters can share (no other engine in this family has code reuse *between*
  characters).
- Full **non-ASCII** handling (byte-safe), and the common states as Oxyde's own,
  MIT-publishable, so the engine can ship alone.

### The boundary that keeps determinism
FUSE describes what happens **inside** a fight and runs in `step()`
deterministically. Lua mods live **outside** `step()` (modes, flow, HUD,
layout); only plain data crosses the line, enforced structurally — the script
crate is absent from the simulation crate's manifest, so "no script runs inside
the fight" is a build fact, not a promise.

### Language tooling
- **`oxyde-lsp`** — a language server for FUSE and ZSS: real controller/parameter
  completion and lint, straight from the compiler.
- **`fuseify`** (convert CNS → FUSE), **`fuse-verify`** (prove the conversion is
  faithful by re-fighting), **`fusediff`** (catch a lossy conversion statically),
  **`defrefs`** (find and repair dangling `.def` references).
