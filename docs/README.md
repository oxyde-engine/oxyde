# Oxyde documentation

Every document in this folder, grouped by what you came here to do. Oxyde is a
MUGEN-compatible fighting-game engine written in Rust: it plays the characters,
stages and screenpacks you already have, and adds its own modes, tooling and
state-language extensions on top. (This index lists the docs; the `README.md`
and `LICENSE.md` one level up cover installing and the license.)

> **A note on the character counts.** The engine ships with just one reference
> fighter (Arroyo) and one stage — you bring your own roster. The large numbers
> these docs quote (e.g. *2,527 characters*) are a **test library** the engine is
> validated against, not content included in the download. Each measurement names
> the roster it was taken over; a figure that cites the **original 1,051
> characters** is a historical measurement against the base test set, not a claim
> about today's 2,500+ archive.

## Start here

- [ARCHITECTURE.md](ARCHITECTURE.md) — how the engine is put together.
- [COMPATIBILITY.md](COMPATIBILITY.md) — how faithful Oxyde is to MUGEN, what the engine owns, and the deliberate deviations.
- [CUSTOMISATION.md](CUSTOMISATION.md) — the ways an installation can be changed, and which doc owns each one.
- [CAPABILITIES.md](CAPABILITIES.md) — what the engine can do, as a feature matrix.

## Playing: modes and sessions

- [MODES.md](MODES.md) — every playable mode (Arcade, Versus, the Team modes, Survival, Training, Watch, Sparring, the Rumbles, Tag, Records, Replays) and how each plays.
- [RULESETS.md](RULESETS.md) — a base mode plus a stack of sparse deltas; the knobs a ruleset may set, all of which the engine already reads.
- [BONUS.md](BONUS.md) — the bonus games, and the `bonus = 1` prop characters behind Versus Bonus.
- [TAG.md](TAG.md) — the universal tag mechanic (TagIn/TagOut on a button, for every character).
- [PARRY.md](PARRY.md) — the parry and other defensive mechanics.
- [SUPER-EFFECTS.md](SUPER-EFFECTS.md) — the super-move screen effects (the darkening, EnvColor) and how they are controlled.

### Knuckle Up (the belt-scroll brawler)

- [KNUCKLE-UP.md](KNUCKLE-UP.md) — the mode overview: walking the depth axis, pickups, props and bosses.
- [KNUCKLE-UP-FLOW.md](KNUCKLE-UP-FLOW.md) — the run/seating flow: the Story / Arcade / Survival / Boss Rush / Last Stand runs and solo/couch/online/hybrid seating.
- [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md) — the `.knuckle` campaign format and the built-in campaigns.
- [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md) — belt stages, street dressing and the procedural streets (`streetthemes.def`).
- [KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md) — authoring Knuckle Up content: props, waves, hazards and boss conventions.

### Online

- [NETPLAY.md](NETPLAY.md) — rollback netplay, the lobby formats, and the online settings model.
- [COOP-ONLINE.md](COOP-ONLINE.md) — online co-op (Knuckle Up over the net), host/join and run selection over the wire.
- [COOP-MULTIPEER.md](COOP-MULTIPEER.md) — the design for three-or-more separate machines on one side.
- [CORROSION.md](CORROSION.md) — the thin-client "corrosion" protocol for a content-less spectator.

## Authoring characters and stages

- [FUSE.md](FUSE.md) — the FUSE state language: the engine's own way to write a character.
- [CONTROLLERS.md](CONTROLLERS.md) — generated reference: every state controller the compiler accepts, with its parameters.
- [TRIGGERS.md](TRIGGERS.md) — generated reference: every trigger.
- [STATES.md](STATES.md) — generated reference: the reserved common-state numbers and what each one is for.
- [EXTENSIONS.md](EXTENSIONS.md) — Oxyde's additions beyond MUGEN: the camera, the depth axis, stage logic, and the versus corner-break.
- [STAGE-LOGIC.md](STAGE-LOGIC.md) — stage FUSE state machines: hazards (`StageHazard`), breakable floors (`StageBreakFloor`).
- [SCRIPTING.md](SCRIPTING.md) — the Lua mod scripting boundary: what lives outside `step()` and what data crosses it.
- [MODDING.md](MODDING.md) — the declarative mod surface: what a mod can add and how it is packaged.
- [MOD-MANIFEST.md](MOD-MANIFEST.md) — the mod manifest format, field by field.

## Screenpacks and presentation

- [AUTHORING-SCREENPACKS.md](AUTHORING-SCREENPACKS.md) — building and customising a screenpack's layout.
- [SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md) — how the shipped screenpack is generated, and scripting it.
- [RENDERING.md](RENDERING.md) — the renderer and its post-processing shaders.
- [CONFIGURATION.md](CONFIGURATION.md) — every configuration/options key the engine reads.

## Working with an existing roster

- [BYOC.md](BYOC.md) — bring-your-own-characters: packing a character as one portable, content-verified file.
- [IMPORT-PIPELINE.md](IMPORT-PIPELINE.md) — staging and fighting a large character download before trusting it.
- [FUSE-CONVERSION.md](FUSE-CONVERSION.md) — converting CNS/ZSS characters to FUSE, and proving the conversion kept the behaviour.
- [FUSE-COVERAGE.md](FUSE-COVERAGE.md) — how much of the content FUSE can express, on three axes.
- [BALANCE.md](BALANCE.md) — measuring a character against a roster's own distribution.
- [HD-SPRITES.md](HD-SPRITES.md) — the HD/UHD sprite tier: AI-upscaled sprites as an SFF sidecar over the same geometry.
- [DIAGNOSTICS.md](DIAGNOSTICS.md) — the in-game diagnostics screen and safe mode.
- [VALIDATION.md](VALIDATION.md) — content validation: the engine confirms your content is what it says it is, and where it is not.
- [MCP.md](MCP.md) — the Model Context Protocol server: let an AI assistant query the engine's own read-only tools.

## Diagnosing a fault

- [CASEBOOK.md](CASEBOOK.md) — worked differential diagnoses: a symptom traced to the engine or the character.
- [TOOLS.md](TOOLS.md) — `oxtool`: every subcommand and what it proves.

## Compared with other engines

- [VS-MUGEN.md](VS-MUGEN.md) — against WinMUGEN, feature by feature.
- [VS-ENGINES.md](VS-ENGINES.md) — against Ikemen GO and the others.

## Performance and internals

- [PERFORMANCE.md](PERFORMANCE.md) — performance characteristics, and the GPU.

---

Generated references (`CONTROLLERS.md`, `TRIGGERS.md`, `STATES.md`) are produced
by `oxtool reference` and should be regenerated rather than hand-edited. See
[TOOLS.md](TOOLS.md) for that and every other `oxtool` command.
