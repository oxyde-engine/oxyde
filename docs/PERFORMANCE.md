# Performance and old hardware

The engine is designed to run well on a machine from the era the content came
from. Nothing here is a fallback path: the CPU renderer is the *default*, and
the GPU exists only to scale the result onto a modern panel.

## Why software rendering is the right default

The content is 320x240 palette-indexed 8-bit art. A CPU blitter draws it at
several hundred frames per second on twenty-year-old hardware, needs no driver,
no shader compilation and no GPU memory, and produces an identical image on
every machine. A GPU path adds a driver dependency, a class of initialisation
failures, and — on integrated graphics of that era — is often *slower* for this
workload because the bottleneck is per-sprite state changes, not fill rate.

Three properties make the rasteriser fast enough:

* **Palette lookup at blit time**, through a 256-entry table built once per
  sprite. Palette effects therefore cost one table build instead of per-pixel
  work, and a twelve-palette character caches one copy of each sprite.
* **Transparent runs skipped before touching the destination.** MUGEN sprites
  are mostly index 0.
* **Fixed-point stepping and pre-clipping** on the unrotated path, so the
  common case never touches floating point per pixel and the inner loop has no
  bounds branch.

## Measured

All figures measured on a large (1,045-character) archive,
on a 12-core machine, release build. The release profile sets
`opt-level = 3`, with thin LTO and a single codegen unit, so these are
fully-optimised numbers rather than a debug build's.

| Operation | Result |
|---|---|
| Index the whole archive | 3.4 s (310 characters/s, 226,000 sprites/s) |
| Load one character | 1-15 ms |
| Simulate + render 1,045 mirror matches, 10 s each | 5.8 s (1,809 character-seconds of gameplay per wall second) |
| Two-player simulation, one core | ~450 fps (7.5x real time) |
| Render one 960x720 frame | 0.2-1.5 ms |
| Rollback with all re-simulation, one core | 330 fps |
| Sprite cache after a match | ~1.2 MB |

The simulation running at 7.5x real time on one core is the headroom rollback
needs: a 7-frame rollback costs 7 extra simulation steps in the same frame
budget.

## Tuning for a weak machine

```ini
[Video]
width  = 640
height = 480
scale  = 2          ; exact pixel doubling, no filtering
renderer = software ; skip GPU initialisation entirely
frameskip = 1       ; keep the simulation at 60 Hz, drop rendered frames
spritecachemb = 32  ; under 2 GB of RAM
vsync = 0           ; if the compositor adds latency
```

`frameskip = 1` is the important one. The frame loop catches up on missed ticks
so the *simulation* keeps real time, capped at four catch-up steps so a stall
cannot spiral. The game slows down visually rather than desynchronising from
real time.

`scale` set to an integer avoids resampling entirely: at `scale = 2` in a
640x480 window, every source pixel becomes exactly four destination pixels.

## Memory

* The archive is memory-mapped, so indexing touches only header pages and the
  OS shares the page cache between characters using the same file.
* Decoded sprites are cached palette-indexed at one byte per pixel, bounded by
  `spritecachemb`, evicted least-recently-used.
* A loaded character is shared behind `Arc`, so a mirror match holds one copy.
* Rollback retains `max_rollback + 2` match snapshots, a few hundred kilobytes.

Peak resident memory for a two-character match is a few tens of megabytes, not
the multi-gigabyte figure the archive size suggests.

## Where the time goes

Profiling a two-character match, roughly:

* ~55% expression evaluation and state controller execution. The archive
  contains 1.4 million controllers; a busy character runs several hundred
  trigger expressions per frame. This is why expressions are compiled to
  bytecode rather than interpreted from text.
* ~30% sprite blitting, dominated by the stage's tiled parallax layers.
* ~10% collision and hit resolution.
* ~5% everything else.

The first number is why `Program::as_constant` exists: a controller parameter
that is a plain number bypasses the VM entirely, and most of them are.

## Threading

The simulation is single-threaded and deterministic by design — that is what
makes rollback and replays possible, and a fighting game at 60 Hz with two
players has no need for more.

Parallelism is used where it is free of ordering concerns: `oxtool` fans the
whole archive across cores with `rayon` for verification, doctoring, balancing
and soak testing, which is what turns a 20-minute archive scan into a
3.4-second one.
