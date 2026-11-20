# Oxyde — Changelog

Engine-facing changes, newest first. This is the public engine release's
changelog; the full internal development history is kept separately.

## v0.37.0

### 2026-11-19 — Story opens Single Player, and every menu shares one backdrop

The Single Player submenu now leads with **Story**, then **Arcade** (the classic
ladder). And the menus that sit off the title — **Online**, **Options**,
**Records** — now draw the same warm backdrop the title does, instead of the
engine's cold circuit field, so every screen looks of a piece. Presentation
only; the simulation, its checksum, replays and netplay are untouched.

### 2026-11-16 — Tag Versus, a menu grouped by who you play, and the Temper strength test

- **Tag Versus.** A new **TAG** team form beside SINGLE, SIMUL and TURNS: both
  sides field a team of up to four, one fighter on the stage and the rest in
  reserve, and you **swap the active fighter on the tag button** mid-fight —
  KOF/Marvel style. Built on the engine's universal tag, so every character can
  be tagged and a tag is as replayable and netcode-safe as a jump.
- **The title menu is grouped by who you play.** The two dozen modes now sit
  under a handful of headings — **Single Player**, **Versus**, **Online**,
  **Training**, **Extras** — and choosing one opens a submenu; **B** goes back.
  The grouping is a view over the mode list, so a mod's modes and a screenpack's
  menu still work exactly as before.
- **Temper, a strength-test bonus.** The arcade "test your might" / bottle-break
  game as one mechanic: *mash* a button to drive a draining bar up, or time a
  *sweeping* cursor near the top, then strike past the marker. Each obstacle
  takes three good strikes and breaks with sparks, a camera shove and debris. The
  run of obstacles is content (`data/bonus/temper.def`), so an install can set
  its own without an engine change.
- **Configurable stage-break transitions.** A stage's `[Break]` section can name
  a `style` (`wall`, `fall`, `rise` or `portal`), a `trigger`/`threshold` and an
  effect pack — the hard-coded wall-break generalised into content-driven
  transitions.

### 2026-11-14 — Versus Bonus plays as a duel, stages break and never go silent

- **Versus Bonus** is a proper two-player duel: both players pick at the same
  time, stand on opposite sides of the shared prop, and the game is won on
  **score** (most damage dealt, ties broken by least taken).
- **Every stage has music.** A stage that names no track draws a stage-stable one
  from the installed pool instead of playing in silence, and a new
  `[Options] randomstagemusic` rolls a track for every venue (seeded from the
  match, so replays are unchanged).
- **Stage breaking across the archive.** Most stages now name a break target, so
  a cornered wall-smash carries the fight into another stage; `[Options] wallbreak`
  is the master switch.

### 2026-11-16 — Hardening: untrusted content can't exhaust memory or escape the game folder

Loading hostile content is now bounded. An SFF sprite that claims an enormous
canvas is capped rather than allocated blindly, and the virtual file system
refuses to follow a symlink or a `..` path out of the game root — so a malicious
character pack can neither exhaust memory nor read a file outside the folder it
was dropped in. No behaviour change for well-formed content.

## v0.36.0

### 2026-11-11 — An MCP server, so an AI assistant can query the engine directly

The release now ships **`oxyde-mcp`**, a Model Context Protocol server that
exposes the engine's own read-only tools to any MCP client — an editor
assistant, a chat client, an agent. It is the fifth face of Rusty Gear: it lets
an outside assistant author against the engine's ground truth instead of
guessing. Every answer is `oxtool`'s, exactly — `ask`, `transpile_fuse`, `moves`,
`info`, `audit`, `verify`, `fusediff` — and every tool is read-only; nothing is
written, repaired or deleted behind a tool call, and there is no network. It
ships beside `oxtool`, which it drives. See `docs/MCP.md` for the client
configuration.

### 2026-11-11 — Content validation: the engine confirms content is what it says it is

Every character is now checked at load against what its files claim to be, and
the findings are reported — never acted on. It is **detection only**: nothing is
converted, rewritten or repaired, and nothing runs inside the simulation, so a
match plays, replays and nets exactly as before.

Three checks, all read-only: every file a `.def` names in `[Files]` exists (the
guard against the oversized-render bug, where a missing constants file silently
fell back to default scale); each script file really is the language its
extension claims — a `.cns` renamed `.fuse`, or two of CNS/ZSS/FUSE in one file,
is named rather than mis-run; and no transpiled `.fuse` is older than its source.

Findings are written to a bounded `oxyde-validate.log` under the game root,
always and silently; the terminal stays quiet unless `OXYDE_VALIDATE` asks
(`fatal` or `all`). `oxtool validate <game-root>` is the on-demand report for a
whole roster. Detection is deliberately conservative — it speaks only when sure —
so a healthy game, including one mixing CNS, ZSS and FUSE characters, says
nothing. See `docs/VALIDATION.md`.

### 2026-11-10 — libvpx is loaded at run time, so video survives a distro upgrade

VP8/VP9 video backgrounds now load the system **libvpx** at run time, trying each
soname in turn — `libvpx.so.10`, `.9`, `.8`, `.7`, `.6`, then `libvpx.so`. One
binary starts on any Linux distribution and decodes video wherever a libvpx is
installed, instead of refusing to launch when the exact library it was built
against is missing (the `libvpx.so.9: cannot open shared object file` error after
a distro upgrade). Where no libvpx is present, the engine still starts and names
the codec in its fallback. Nothing about the simulation changed — video is drawn,
never simulated.

### Recent engine highlights

- **Knuckle Up** — a belt-scroll brawler mode built on the engine's 2.5D depth
  axis, with timed floor power-ups, boss-capped stages and campaigns.
- **Last Stand** — timed horde-survival; the healthiest survivor wins.
- **Rulesets** — a base mode plus a stack of sparse overrides, declared in a
  `.rules` file or a Lua table.
- **Styled wall-break transitions** — a stage author controls the flash that
  covers one arena breaking into the next.
- **HD / UHD sprite tier** — optional AI-upscaled sprites shipped as an SFF
  sidecar over the same geometry; the base art and hit boxes are unchanged.
- **Deterministic core** — replays, rollback netplay and spectating all ride the
  same two-bytes-a-frame input stream, matching bit-for-bit across x86-64 and ARM.
- **Training** — frame step, save states, input history and a recording dummy.

See `docs/` for the reference on each feature — start with `docs/CAPABILITIES.md`.
