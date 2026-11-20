# Oxyde

A modern, deterministic fighting-game engine, compatible with MUGEN and Ikemen
GO content. Oxyde reads the characters, stages and screenpacks authors already
have, and runs them sharper, cleaner and frame-for-frame reproducibly.

This repository is the **public engine release**: the engine, its tools, the
documentation, and a default screenpack with one reference fighter and one
reference stage. It boots and plays with no extra content — then you bring your
own roster.

## Quick start

1. Download the build for your platform from the latest
   [Release](../../releases) (`oxyde` for Linux, `oxyde.exe` for Windows).
2. Put the binary at the root of this folder (next to `chars/` and `data/`).
3. Run it. You start on **Arroyo** in the **Oxyde Battle Ring** — the reference
   fighter and stage that ship with the engine.
4. Add characters to `chars/` and stages to `stages/`, list them in
   `data/select.def` (or delete that file to let the engine scan the folders),
   and they appear on the select screens.

## What's in here

| Path | What it is |
|------|------------|
| `chars/Arroyo/` | The reference fighter — complete, documented, a model to author against. |
| `stages/` | The reference stage, Oxyde Battle Ring. |
| `data/oxyde/` | The default screenpack (menus, HUD, fonts). Override per-screen or wholesale. |
| `data/select.def` | The roster and stage list. Edit it, or delete it for a folder scan. |
| `data/common1.fuse` | The engine's common states, in source form. Also embedded in the binary. |
| `docs/` | Author and engine documentation — start with `docs/CAPABILITIES.md`. |
| `tools/` | The `oxtool` command-line toolkit: convert, audit, troubleshoot, screenshot, package. |

## Tools

`oxtool` (in the Release, documented in `tools/`) converts MUGEN/Ikemen content
to Oxyde's FUSE format, audits how much of a character works, repairs common
faults, renders any screen headlessly, and packages a build. See
`docs/IMPORT-PIPELINE.md`, `docs/FUSE-CONVERSION.md` and `docs/DIAGNOSTICS.md`.

## Authoring

Oxyde runs standard MUGEN/Ikemen characters, stages and screenpacks. To go
further — the FUSE language, Knuckle Up belt-scroll mode, custom screenpacks,
mods — see `docs/`. Everything the default screenpack does is overridable; see
`docs/AUTHORING-SCREENPACKS.md` and `docs/MODDING.md`.

## Credits & licensing

Oxyde is developed by Oxyde. The engine is distributed here as binaries; see
`LICENSE.md`.

The engine's bundled common states derive from Ikemen GO's MIT-licensed common
states — the piece that makes an engine-only distribution possible. The
reference fighter Arroyo and the reference stage are original Oxyde content.
