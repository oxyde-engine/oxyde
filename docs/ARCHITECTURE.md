# Architecture

## The shape of the problem

MUGEN content is a programming language, a sprite format, an animation format,
a sound archive and a screenpack, all authored by strangers over twenty years
with no compiler, no linter and no validation. A meaningful fraction of it is
damaged. The engine's job is to run all of it anyway.

That single constraint explains most of the decisions below.

## Crate layout

```
oxyde-vfs      Case-insensitive, separator-agnostic path resolution, and
                `.zip`/`.rar` content mounted as folders.
oxyde-format   Bytes on disk: DEF/INI, PCX, SFF, AIR, SND, ACT, FNT, JSON,
                encodings.
oxyde-cns      Character logic: lexer, expression compiler, bytecode VM,
                state controller and Statedef compilation, the three state
                languages — CNS, ZSS and FUSE — that share all of it, the
                transpiler between them, and the linter.
oxyde-core     The game: character loading, input, combat, the simulation.
oxyde-render   Software rasteriser, sprite cache, scene assembly, stages,
                shadows, HUD, select screen, splash, text, PNG and image I/O.
oxyde-script   A sandboxed Lua 5.4 runtime and the plain-data boundary that
                is the only thing allowed to cross it.
oxyde-gpu      Optional hardware presentation: six post-processing shaders and
                glTF stage backdrops. Never required.
oxyde-video    WebM/VP8/VP9 backgrounds, addressed by tick rather than by clock.
oxyde-encode   Video files out: AV1 + Opus in WebM (pure Rust), H.264 through
                the user's ffmpeg, GIF. Knows frames and PCM, not the game.
oxyde-net      Rollback netcode, its UDP transport, and corrosion mode.
oxyde-app      Config, modes, AI, mods, audio and music, training and bonus
               stages, the options screen, platform shell, the `oxyde` binary.
oxyde-lsp      A language server for FUSE and ZSS, built on oxyde-cns's own
                tables. A separate binary; the game never loads it.
oxyde-tool     `oxtool`: offline diagnostics over a whole archive.
```

Dependencies point strictly downward. Nothing below `oxyde-core` knows what a
match, a frame or a player is; nothing below `oxyde-app` knows what a window
is. That is what lets the lower layers be unit-tested in isolation and reused
by tooling, and what keeps the platform shell small enough to be obviously
correct.

Three of these are *optional by construction* rather than by convention, and the
boundary is the dependency graph itself:

* **`oxyde-script` never appears in `oxyde-core`'s manifest.** That is what
  enforces "no script runs inside `Match::step`" — not a rule somebody has to
  remember, but an edge that does not exist. If `mlua` is never a dependency of
  the simulation, the invariant cannot rot.
* **`oxyde-gpu` is behind a cargo feature and a config value.** Compiled in by
  default and *used* only when `renderer` says so, which is not the default. A
  machine whose driver is broken still starts.
* **`oxyde-video` loads the system libvpx at run time, not at link time.** VP8/VP9
  resolve `libvpx.so.6` through `.so.10` by soname via `dlopen`, so the default
  build needs no feature: it plays them wherever libvpx is installed and still
  starts on a machine that has none.

## Five decisions that drive everything

### 1. Compile once, never parse again

Every trigger expression and controller parameter is compiled at load time into
a flat `Vec<Op>` bytecode with an interned string pool. Evaluation is a tight
loop over a slice with a fixed 64-slot value stack: no allocation, no string
comparison, no tree walking.

Constant subexpressions are folded at compile time, and a parameter that is a
plain number (`damage = 43`) bypasses the VM entirely through
`Program::as_constant`.

The archive contains **1,424,195 state controllers**. This is the difference
between a playable frame budget and not.

```rust
// crates/oxyde-cns/src/vm.rs
pub enum Op {
    Const(Value),
    Trigger(TriggerId, u8),
    CompareFlag { id: TriggerId, state_mask: u32, attr_mask: u32, negate: bool },
    Redirect { kind: Redirect, has_arg: bool, on_missing: u32 },
    AndJump(u32),
    Range { lo_inclusive: bool, hi_inclusive: bool, negate: bool },
    // ...
}
```

### 2. Nothing panics on content

Every offset and length in these files was written by third-party tools across
twenty years, and much of it is wrong. All of it is treated as hostile input:
parsers return `Result`, recoverable damage lands in a `warnings` list, and
loading continues.

Release builds **unwind**, deliberately, and `Cargo.toml` says why: a panic
inside a character's own state code is caught by `Match::run_state_controllers`,
which disables that character rather than taking the round down with it, and
`catch_unwind` cannot catch an abort. So "nothing panics on content" is a
property the code is written for *and* a backstop the profile keeps available —
not an argument for switching the backstop off. The evidence is `oxtool soak`
over the archive's original 1,051 characters, and several parsers carry deterministic fuzz smoke
tests.

### 3. The simulation is a pure function

`(previous state, inputs) -> next state`. No wall-clock time, no float derived
from frame duration, an explicit RNG advanced only by the simulation, and no
I/O anywhere inside `Match::step`.

This is a structural constraint, not an optimisation. It is the precondition
for deterministic tests, replays, and the rollback netcode — which is roughly
400 lines as a result instead of a rewrite.

Sound and rumble are *queues* the simulation appends to (`Match::sounds`,
`Match::rumble`) and the platform drains, precisely so that playing a sound or
shaking a controller is not a side effect that rollback would have to undo.

### 4. Laziness and sharing

Opening an SFF parses only the index; sprite pixels are decoded on demand and
cached in their palette-indexed form, so a twelve-palette character holds one
copy of each sprite and a palette swap is free. Files are memory-mapped, so the
OS page cache is shared between characters that reference the same file.

This is why a 6.6 GB archive indexes in 3.4 seconds.

### 5. The engine owns what MUGEN's engine owns

A recurring failure mode in third-party MUGEN engines is assuming the CNS does
everything. It does not. `common1.cns` contains no code to turn "hold forward"
into a walk, and none to restore control after the intro. Those are engine
behaviours, and characters are authored assuming they exist:

* **Movement transitions** — stand ↔ walk / crouch / jump, and the automatic
  turn when an opponent crosses over (`Match::standard_transitions`).
* **Guard entry** — the engine puts a blocking player into state 120
  (`Match::update_guarding`). Guard *exit* is the other way round: the common
  states watch `command != "holdback" || !inGuardDist` and change to 140
  themselves. The line between those two is the one it is easiest to put in
  the wrong place, and `data/common1.fuse` is where it is written down.
* **Control at round start** — the intro chain `5900 → 190 → 191 → 0` sets
  `ctrl = 0` and nothing ever sets it back; `Match::begin_fight` does.
* **The gethit states** — the engine writes `GetHitVar`s and routes the
  defender into the 5000-series by stance (5000/5010/5020/5080), or the
  guard-hit *shake* states (150/152/154) when the hit was blocked; the
  character's own CNS decides what that looks like.

Because of the last point, the same combat code works for a 2001 character and
a 2021 one.

## Tick order

```
1. Advance timers (pause, hit pause, palette effects, hit-by filters).
2. Per player: sample input, update command buffers.
3. Per player: engine movement transitions.
4. Per player: run states -3, -2, -1, then the current state.
5. Resolve collisions and apply hits (players, then projectiles).
6. Physics, binding, player pushing, stage bounds.
7. Advance animations, after-image trails, explods.
8. Environment (shake, colour), reaping, camera.
```

Characters depend on this order. A `[Statedef -2]` controller must observe the
state a `[Statedef -1]` transition just produced, and a `HitDef` set this tick
must be able to connect on the same tick.

## Combat

`Clsn1` (attack) boxes are tested against `Clsn2` (hurt) boxes in world space,
after mirroring by facing and scaling — mirroring is about the axis, and getting
that wrong puts every left-facing character's hitboxes behind them.

A landed hit then runs a fixed sequence, each step of which changes the feel of
the game:

1. **Eligibility** — team, hit flags, `HitBy`/`NotHitBy` filters, juggle,
   chain IDs, and whether this HitDef has already spent its `numhits`.
2. **Guard** — whether the defender is in the 120–155 guard states and whether
   `guardflag` covers their state type.
3. **Application** — damage through attack/defence multipliers and the balance
   rules, power exchange, pause and shake, velocities in the defender's frame,
   sparks and sounds, and the transition into the 5000-series.

`HitDef` has around eighty parameters, most of which default *in terms of other
parameters*: `air.type` from `ground.type`, `guard.hittime` from
`ground.hittime`, `airguard.velocity` from `air.velocity` scaled. Those chained
defaults are where third-party engines usually diverge, so each one is written
out explicitly in `Match::build_hitdef` with the spec as its source.

## Rendering

A CPU rasteriser fills a 32-bit XRGB `Framebuffer` which the platform layer
presents unchanged — the layout is chosen so presentation is a memcpy.

Three properties make it fast enough:

* Palette lookup happens at blit time through a 256-entry table built once per
  sprite, so palette effects cost one table build rather than per-pixel work.
* Transparent runs are skipped before touching the destination; MUGEN sprites
  are mostly index 0.
* The unrotated path steps the source in 16.16 fixed point and clips before the
  inner loop, so the common case never touches floating point per pixel.

Scene assembly sorts by sprite priority and insertion order. Priority is
per-entity and changes during a hit (`p1sprpriority` / `p2sprpriority`), and
`ontop` explods force themselves above everything — getting this wrong is
immediately visible as an attacker drawing behind the person they just hit.

## Testing strategy

| Kind | Where | What it proves |
|---|---|---|
| Unit | ~2,900 tests across 14 crates | Semantics: int division truncates, `Clsn` mirrors, guard reduces damage, rollback converges |
| Fuzz smoke | PCX, SFF, WAV, packets | No input panics |
| Archive | `oxtool verify`, `doctor`, `soak`, `compat` | 1,051 real characters load, simulate and render, across four MUGEN releases |
| Netcode | `oxtool netcheck` | Two peers converge bit-for-bit on real characters over a lossy link |
| Cross-platform | `cargo build --target x86_64-pc-windows-gnu` | Both binaries build for Windows |
| Hardware | `oxyde-gpu`, against `llvmpipe` | Every shader compiles and draws; the GPU frame matches the CPU one |
| Sandbox | `oxyde-script` | A runaway mod is stopped, a broken one is switched off, and neither reaches the engine |
| Streaming | `oxyde-net::corrosion` | A fight reconstructs pixel-exact from deltas, and a gap is repaired rather than smeared |
| Differential languages | `oxtool fuse --verify` | ZSS and FUSE compile to byte-identical bytecode over Ikemen's own files, and the archive's original 1,051 characters all convert |
| Common states | `oxtool audit` over three roots | The engine's own `common1.fuse` ties MUGEN's `common1.cns` and beats Ikemen GO's, over the archive's original 1,051 characters |
| Benchmark | `oxtool eval` | 2,000 held-out completion tasks; answering the original scores exactly 100%, so the scorer is checked against itself |

No unit test reads the game archive. The archive is a separate, explicit target,
which keeps `cargo test` fast and hermetic while still holding the engine to
real content.

### How three state languages are kept honest

The strongest test here is not a test that was written; it is one that fell out
of having a converter. ZSS and FUSE both lower to the same `Block`, so a ZSS
file can be printed as FUSE, parsed back, and the two results compared *at the
bytecode level* — not "the output looks right" but "both sides compile to the
same thing".

Run over Ikemen GO's own fourteen `.zss` files — 140 states written by people
solving real problems, not by someone writing test cases — that is 1,081
controllers with zero mismatches. Run over the archive's CNS with
`--roster`, it is 2,094,037 controllers, and the only remaining errors are ones
the original file already had.

Nothing hand-written would cover as much of either language, and the property
is exactly the one that matters: *a character written in any of the three is
the same character.*
