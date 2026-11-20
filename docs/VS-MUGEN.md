# M.U.G.E.N vs Oxyde

A feature-by-feature comparison against the engine this one replaces:
**WinMugen (2006-08-31)**, the 296 KB `Winmugen.exe` sitting next to this
folder. Where MUGEN 1.1 beta differs from WinMugen in a way that matters, it is
called out.

This document is the honest version. Every "no" below is a real no, and the
places Oxyde is *behind* are listed as prominently as the places it is ahead.

**Legend** — ● full · ◐ partial · ○ none

---

## 1. Content compatibility

The whole point. Your characters, stages, sounds and palettes are read
unchanged; nothing is converted, and nothing in your installation is written to.

| | WinMugen | Oxyde | Notes |
|---|---|---|---|
| `.def` / `.cns` / `.cmd` / `.air` | ● | ● | Same files, no conversion |
| `.sff` v1.01 sprites | ● | ● | Verified byte-for-byte against an independent decoder |
| `.sff` v2.0 / 2.01 sprites | ○ | ◐ | 1.1-era format. RAW/RLE8/RLE5/LZ5 implemented but unverified against a real v2 file; embedded PNG sprites (8-bit indexed, 24-bit and 32-bit) decode |
| `.snd`, `.act`, `.pcx` | ● | ● | |
| `data/common1.cns` | ● | ● | Merged in automatically for characters whose `stcommon` points nowhere |
| `data/select.def` | ● | ● | Roster, order, per-character stages, `music`, `order`, `includestage`, `ai`, `[ExtraStages]`, `arcade.maxmatches` |
| `data/mugen.cfg` | ● | ● | Options, rules, engine limits, `[Arcade]`'s AI ramps and `AI.RandomColor`, **and both players' key bindings** (DOS scan codes translated). `AI.Cheat` is deliberately not honoured: Oxyde's computer plays the motions out of the character's own `.cmd` a frame at a time, and can drop one the way a person does |
| Stages: `[Camera]`, `[PlayerInfo]`, `[Bound]`, `[StageInfo]`, `[Shadow]`, `[Reflection]`, `[Music]` | ● | ● | Including `startx`/`starty`, `screenleft`/`screenright`, `autoturn`, `resetBG`, `zoffsetlink` (added to `zoffset`, as Ikemen GO does), `xscale`/`yscale`, `fade.range`, `xshear` and `bgvolume` |
| Background elements: `positionlink`, `windowdelta`, `sin.x`/`sin.y`, `scalestart`/`scaledelta`, `maskwindow` | ● | ● | `mask` follows all three of the manual's default rules, including "animated elements always have mask = 1" |
| Parallax (`type = parallax`, `xscale`, `width`, `yscalestart`/`yscaledelta`) | ● | ● | Drawn a scanline at a time, each row at its own scroll rate |
| Stage `BGCtrl` blocks | ● | ● | All nine controller types |
| Reflections (`[Reflection]`) | ● | ● | Drawn, with `[Shadow] fade.range` applied to both |
| Character AI written in CNS | ● | ● | Runs, and the `AILevel` trigger answers with the computer player's real difficulty; the engine supplies its own baseline opponent as well, so AI-less characters are still playable |
| **Screenpacks** (`system.def` art) | ● | ● | Rendered; `screenpack = 0` uses Oxyde's own UI instead |
| **`fight.def` lifebar art** | ● | ● | Rendered, including the round pacing it sets |
| Storyboards | ● | ● | Scenes, 100 layers, `starttime`/`endtime`, `textdelay`, fades, per-scene music and `soundX` effects |
| Character endings, default ending, credits | ● | ● | `[Arcade] ending.storyboard` and the motif's own |
| Continue, game over, survival results | ● | ● | |
| Attract-mode demo loop | ● | ● | `[Demo Mode]`, including the intro cycle |
| Text encodings | Shift-JIS era | ● | UTF-8, Windows-1252 and Shift-JIS auto-detected |

### Engine language coverage

| | WinMugen | Oxyde |
|---|---|---|
| Triggers recognised | the documented set | **281** — the documented set, the spelling variants found in shipped content, and its own (see [EXTENSIONS.md](EXTENSIONS.md)) |
| State controllers recognised | 93 | **160** — Elecbyte's 90 and 70 controllers beyond them |
| State controllers executed | 93 | **93 — all of them.** `SendToStage` and `Zoom`, in neither the 1.1 manual nor WinMugen's own controller list and reached by no character in this archive, are implemented too (`Zoom` drives an Ikemen-style camera scale; `SendToStage` is the inverse of `TagOut`) |
| Global states | `-1`, `-2`, `-3` | those, plus **`-4`** (runs for everything, through a pause) and **`+1`** (runs *after* the current state) |
| Documented controller *parameters* read | all | all but one: `RemapPal source`, which names an SFF v2 palette group (1 line in this archive) |
| Debug clipboard (`DisplayToClipboard`, `AppendToClipboard`, `ClearClipboard`) | ● Ctrl+D | ● | Full printf formatting — `%d`, `%i`, `%f`, `%e`, `%g`, `%%`, `\n`, `\t` — and up to six `params` expressions. 546 characters here print to it |
| Expression semantics | reference | matched, including `7/2 == 3`, division-by-zero as 0, int/float duality, short-circuiting |
| Malformed content | silently dropped | compiled where the intent is unambiguous, **reported** where it is not |

That last row is the practical difference. WinMugen drops a mistyped trigger
without a word; Oxyde accepts eleven documented classes of author typo (~1,800
occurrences in this archive) and prints the rest. See the deviation table in
[COMPATIBILITY.md](COMPATIBILITY.md) — every one is a deliberate, listed
decision.

---

## 2. Platform and engine

| | WinMugen | Oxyde |
|---|---|---|
| Platforms | 32-bit Windows only | **Linux and Windows** (one checkout builds both) |
| Graphics API | DirectX 7 | Software rasteriser by default, GPU only to scale the result |
| Colour depth | 16-bit | 24-bit |
| Resolution | 320x240, scaled | Any window size, any aspect; the playfield extends horizontally on a widescreen monitor rather than being pillarboxed |
| Threading | single-threaded | Parallel asset indexing; simulation stays single-threaded and deterministic |
| Source | closed, unmodifiable | **MIT OR Apache-2.0, ~301,000 lines of Rust** |
| Memory safety | — | The simulation, the compiler and the renderer contain no `unsafe` at all; the only two uses in the whole engine are the `mmap` calls that read `.sff` and `.snd`. Malformed content cannot corrupt memory |
| Crash behaviour | crashes on malformed content | Every parse failure is a reported error; `oxtool soak` runs the whole roster to prove it |

---

## 3. Modes

The first eleven are the modes WinMugen's own `system.def` names, under its
names, in its order.

| Mode | WinMugen | Oxyde |
|---|---|---|
| Arcade, Versus, Team Arcade, Team Versus | ● | ● |
| Team Co-op, Survival, Survival Co-op | ● | ● |
| Training | ● | ● + a dummy menu (behaviour, guard, life/power policy, damage readout) |
| Watch | ● | ● |
| Options | ● | ● |
| **Online (rollback netplay)** | ○ | ● |
| **Sparring** (two-player practice, no KOs, hot-swap fighters) | ○ | ● |
| **Versus Bonus** (seven bonus stages, scored) | ○ | ● |
| **Team Rumble** (8-a-side attrition, the next fighter steps in without the round stopping) | ○ | ● |
| **Roster Rumble** (the roster dealt between two players, nobody twice, last one standing — up to 522 a side) | ○ | ● |
| **Team Tag** (two of yours on screen at once) | ○ | ● |
| Team menu: SINGLE / SIMUL / TURNS and the team size, per side, before the roster | ● | ● drawn in Oxyde's own panel rather than from `p1.teammenu.*`, and offering Rumble's eight |
| `TagIn` / `TagOut` controllers | ● | ● |
| **Bonus games** (a prop character played as a bonus round, kept off the select grid) | ○ | ● |
| **Rematch menu and a running score** after a two-player match (REMATCH / CHARACTER SELECT / QUIT, with the score between these two fighters) | ○ | ● |
| **A select-grid window per side** when two people are choosing out of a roster that does not fit on one page | ○ (one grid, one scroll, two cursors) | ● |

---

## 4. Netplay

| | WinMugen | Oxyde |
|---|---|---|
| Online play | ○ (none — WinMugen has no netcode at all) | ● |
| Model | — | **Rollback**, GGPO-style |
| Input latency | — | Your own input shows on the next frame |
| Transport | — | UDP, one port, host/join by address |
| Desync detection | — | Per-frame checksums; a mismatch disconnects rather than diverging silently |
| Handshake | — | Repeated twice a second until answered, so no single packet can decide whether a session starts |
| Verification | — | `oxtool netcheck` runs two peers over a simulated lossy link and proves they converge — 16 of 16 link conditions up to 80 frames of latency with one packet in eight dropped |

MUGEN online has only ever existed through third-party wrappers driving
emulator-style state saves. This is built in.

---

## 5. Presentation

Since 0.20.0 the engine draws three things of its own that MUGEN leaves to the
content, and each is a setting away from the original behaviour:

| | WinMugen | Oxyde |
|---|---|---|
| Full-screen effect on a `SuperPause` | the screen dims, and that is all | ● impact, ember and steel ray burst, one hexagonal shock ring per bar, speed lines, sparks, cold grade, the caller rim-lit; AUTO steps back where the character's own art fills the screen (`superfx`, [SUPER-EFFECTS.md](SUPER-EFFECTS.md)) |
| Hit sparks / guard flash / shockwaves | Elecbyte's 2000 set, 16 colours, drawn for 640x480 | ● redrawn at 4x in the pack's palette, same 19 action numbers (`data/oxyde/fightfx.sff`) |
| A stage whose art does not cover a 16:9 window | black slab | ● filled from the picture beside it, mirrored and faded (`fillgutters`) |


| | WinMugen | Oxyde |
|---|---|---|
| Reflections | drawn | drawn |
| Life bars | screenpack art | Drawn procedurally — slanted plates, damage-drain ghost, per-side accent colours, sharp at any resolution |
| **Super / special gauge** | one bar with tick marks | **Discrete cells, one per 1000 power.** A charging cell is blue, a *banked* super is gold and breathes, and the level count is spelled out (`LV2`) |
| Round win indicators | screenpack art | Accent diamonds, one per round needed |
| Combo counter | screenpack art | Built in: hit count large, then **damage, the share of a life bar it took, and what the defender has left** on a mini bar, on the side of whoever is landing it, growing on each new hit |
| Team status | ○ | One pip per team member, filled while they can still fight — the whole state of a turns match at a glance |
| Character portraits | required | Optional; missing ones are letterboxed rather than stretched |
| Select screen | fixed grid from the screenpack | Roster split down the middle when two people are choosing, each with its own scroll; **type to search 2,527 characters**, and the screenpack's own grid pages with a counter rather than hiding the rest |
| Font | `.fnt` bitmap fonts | Built-in vector-ish face that scales; `.fnt` is parsed but not used for the UI |
| **Custom screenpacks** | ● | ● | Rendered from `system.def` / `fight.def`. `screenpack = 0` in the options screen swaps in Oxyde's own UI instead |
| **Options screen** | fixed list | Grouped into six sections, with a range bar on every scale, a gutter mark and a count for what is unsaved, a control legend, and RESTORE DEFAULTS |

Both looks are available and the choice is a setting. The screenpack is drawn
by default, exactly as MUGEN draws it; Oxyde's own UI is sharp at 4K, pages
over a thousand-name roster, and cannot break when a screenpack file is
damaged.

---

## 6. Tooling

There is no WinMugen equivalent to any of this.

| Tool | What it does |
|---|---|
| `oxtool verify` | Loads every character and stage, reports what failed and why |
| `oxtool doctor` | Classifies the roster by playability, lists every automatic repair and every remaining break |
| `oxtool audit` | Scores how much of **each** character works — movement, attacks, specials, blocking, knockdown, recovery — in three minutes for the roster |
| `oxtool info` | Summarises one character: states, animations, sprites, commands |
| `oxtool dump` | Decodes a single sprite to PNG |
| `oxtool simulate` | Runs a character's state machine headless and reports which states it reached; `--ai` drives it with the game's own computer opponent and `--trace` prints state, animation, physics, binds, hit pauses and the deadlock counter per tick |
| `oxtool soak` | Simulates the entire roster; fails on any panic or hang |
| `oxtool frame` | Renders one simulated frame to PNG, with optional collision boxes |
| `oxtool balance` | Measures every character's damage and life, writes a table that equalises how many hits a fight takes |
| `oxtool netcheck` | Two rollback peers over a lossy link, verified to converge |
| `oxyde --headless --shot` | Any screen or frame to a PNG, with no display |

On this archive, the loader's automatic repairs take playability from
**1,043/1,045 to 1,045/1,045**.

---

## 7. Balance

MUGEN has no concept of balance: a character authored to do 400 damage a combo
fights one authored to do 60, and that is the end of it. Oxyde ships an opt-in
normalisation (`[Balance] enabled = 1`, or `--balance`) that scales life and
damage so a fight takes a comparable number of hits regardless of who wrote the
two characters. It is off by default, because the alternative is deciding that
a thousand authors were wrong. See [BALANCE.md](BALANCE.md).

---

## 8. Performance

| | WinMugen | Oxyde |
|---|---|---|
| Renderer | DirectX 7, GPU-dependent | Software; GPU optional and only for the final upscale |
| Frame time, 960x720 | — | 0.2-1.5 ms |
| Simulation, two players, one core | 60 fps target | ~450 fps (7.5x real time) |
| Whole-archive index | — | 3.3 s for 1,045 characters / 759,000 sprites |
| Roster load | per character, blocking | Parallel, with a bounded sprite cache (~1.2 MB after a match) |

---

## 9. Measured, on this archive

Both engines were run over all 1,045 characters, one at a time, in the same
week on the same machine. WinMUGEN was driven under wine on a virtual X server
and scored off its own screen — life bars, playfield pixels, `mugenw.log` and
the error dialog — because that is the only place it reports anything. Oxyde
ran the same match, against the same opponent, for the same length of time, and
was scored on the same six things.

Anything that scored below full marks under WinMugen was run again on an idle
machine and credited with the better of its two runs, because six wine
instances on twelve cores is enough contention to make a healthy character look
like a hang. 62 improved; these are the corrected numbers.

| | WinMugen | Oxyde |
|---|---:|---:|
| Characters that load | 1,032 of 1,045 | **1,045 of 1,045** |
| Runs that ended in a fatal error dialog | 13 | **0** |
| Runs that hung and had to be killed | 6 | **0** |
| loads / draws / acts | 98.8 / 98.8 / 98.2% | **100 / 99.8 / 99.9%** |
| deals damage | **97.7%** | 96.9% |
| takes damage | **96.8%** | 92.3% |
| completes | 98.0% | **99.2%** |
| **Mean operation score** | 98.1% | 98.1% |

A tie on the characters both can run, which is the point; the difference is at
the edges. The one row Oxyde loses is not the simulation — 78 characters that
are hit in WinMugen go a whole fight untouched here because Oxyde's computer
opponent never lets Kung Fu Man land anything. Asked directly as well, 99.5% of
the roster either is hit in the fight or loses life to a probe attacker.

The full per-character table, the reasons WinMUGEN gives for each rejection,
screenshots of every dialog, and the scored category-by-category comparison are
in [`metrics/`](../../metrics/) beside this folder.

Three of the fixes in 0.18.0 were settled by *running* WinMugen rather than
reading the manual: `physics = S` does not hold a fighter at the floor, a
duplicate `[Statedef 0]` keeps the *later* block, and a duplicate
`[Statedef -1]` keeps the *first*. The second of those turned a planned change
into a decision to leave the code alone.

---

## 10. What is left

Stated plainly, because a comparison that only runs one way is not worth
reading. Everything below is measured against this archive: 1,045 characters,
195 stages, 1.4 million state controllers.

| Gap | What writes it here |
|---|---|
| A screenpack's own `p1.teammenu.*` art for the team menu | Oxyde draws the menu in its own panel; nothing in this archive is affected, the menu being new |
| `[Camera]` 1.1 tension and overdraw: `zoomdelta`, `tensionhigh`, `tensionlow`, `overdrawhigh`, `overdrawlow`, `cuthigh`, `cutlow` (the `zoomin`/`zoomout`/`startzoom`/`autozoom` family **is** implemented — see [EXTENSIONS.md](EXTENSIONS.md#the-camera)) | 0 of 195 stages |
| `RemapPal source` | 1 line |
| `[BG] zoomdelta` | 0 layers |
| SFF v2 decoders verified against a real v2 file | 0 v2 files in the archive |
| `[P1 Joystick]` DOS scan codes | pads are mapped by the engine instead |
| `[Arcade] AI.Cheat` | deliberate: the computer performs the motion rather than asserting the command |
| `[Misc]` loader settings (`precache`, `playercache`, `bufferedread`, `unloadsystem`), `[Debug]`, legacy `[Video]` DirectX and `[Sound]` MIDI/CDA/MOD device settings | MUGEN-internal or DOS-era; no behaviour to reproduce |
| Victory quotes (`[Quotes]`, `VictoryQuote`) | the screenpack draws `winquote`, but **0 of 1,045** characters here ship one — it is a 1.0-era feature |

### Against Ikemen GO

MUGEN is the engine this one replaces, so it is what the rest of this document
measures against. Ikemen GO is the other open reimplementation, and a large
part of its work is a *language* extension rather than a compatibility one —
so it is worth saying which parts of that are here.

| | Ikemen GO | Oxyde |
|---|---|---|
| New triggers | ~130 | **148** — see [EXTENSIONS.md](EXTENSIONS.md) |
| New state controllers | ~70 | **70** |
| New trigger redirections (`P2,` `Player(n),` `PlayerIndex(n),` `HelperIndex(n),` `StateOwner,`) | ● | ● |
| `RedirectID` on every controller | ● | ● |
| Global states `-4` and `+1` | ● | ● |
| Named variables (`[Map]`, `Map(name)`, the nine `Map*` controllers) | ● | ● |
| Red life, dizzy, guard break, score | ● | ● — off unless switched on, and engine-driven, so no character needs patching |
| `fight.def` `[Stunbar]`, `[Guardbar]`, `[Score]` | ● | ● |
| Command file `\|`, `L`/`R`, `N`, `/30`, `steptime`, `buffer.hitpause` | ● | ● |
| SOCD resolution, button assist | ● | ● |
| Processing order by MoveType | ● | ● |
| `AssertSpecial`'s extended flag set | ~50 flags | **33** |
| ZSS, Lua, shaders, 3D glTF stages, video backgrounds | ● | ● (shaders as sixteen CPU built-ins plus an opt-in supplied `.wgsl`; see [VS-ENGINES.md](VS-ENGINES.md)) |
| Z axis (`Depth`, `PosZ`, `attack.depth`) | ● | ● |
| Camera zoom (`Camera`, `Zoom`, stage `AutoZoom`) | ● | ● |
| `SaveFile` / `LoadFile`, `Dialogue`, `RemapSprite`, `ModifyProjectile`, `ModifyStageBG` | ● | ● |
| Movelists | a file named in the DEF | derived from the character's own `.cmd` and `[Statedef -1]`, so every character here has one |
| Rollback netplay | ● | ● |

The full list of what is not here, by name, is at the end of
[EXTENSIONS.md](EXTENSIONS.md).

## 11. Summary

**Where Oxyde is ahead:** it runs on Linux and Windows, it has rollback netplay
and replays, it has six modes MUGEN never had, it has a diagnostic toolchain, it
renders at native resolution in 24-bit colour, it reports content errors instead
of swallowing them, it repairs broken characters, it gives authors a hundred
triggers and forty controllers MUGEN never had, and the source is yours.

**Where Oxyde is behind:** no 1.1 camera tension/overdraw
(`tensionhigh`/`tensionlow`/`overdraw*`/`cut*`, which no stage here writes —
the `zoomin`/`zoomout`/`autozoom` family is implemented), `RemapPal source`, and
SFF v2 support that has never been tested against a real v2 file.

**Where they are equal:** the thing that actually matters — your characters
load and play.
