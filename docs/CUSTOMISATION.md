# Customisation and backwards compatibility

MUGEN's real appeal is that everything is a text file you can edit. This
document is the honest account of how much of that Oxyde preserves:
what it reads from an existing installation, what you can change, and what it
does not yet let you touch.

## The short version

| Area | Status |
|---|---|
| Characters, animations, sprites, sounds, palettes | **Fully compatible** — unchanged files, nothing to convert |
| Stages, including parallax and shadows | **Fully compatible** |
| `data/common1.cns` shared states | **Fully compatible** |
| `data/select.def` — roster, order, per-character stages, arcade ladder | **Read and honoured** |
| `data/mugen.cfg` — options, rules, engine limits, key bindings | **Read and honoured** |
| `data/fightfx.*`, `data/common.snd` | **Read** |
| Screenpack rendering — `system.def` art, fonts, backgrounds, cursors, sounds | **Rendered** |
| `fight.def` lifebar art, portraits, timer, combo, round calls and pacing | **Rendered** |
| Storyboards (`logo.storyboard`, `intro.storyboard`) | **Played** |
| Character endings (`[Arcade] ending.storyboard`) | **Played** |
| `[Default Ending]`, `[End Credits]` | **Played** |
| `[Win Screen]`, `[Continue Screen]`, `[Game Over Screen]`, `[Survival Results Screen]` | **Rendered** |
| `[Demo Mode]` attract loop | **Played** |
| Stage `[BGCtrl]` background controllers | **Run** |
| Replay recording and playback (`[Replay]`) | **Complete** |
| MUGEN's team-mode screen (`p1.teammenu.*`) | **Rendered**, dot row and all |
| Content in `.zip` and `.rar` | **Mounted as folders** |
| `[Info] localcoord` on characters | **Applied** |
| Lua mods — modes, rules, matchup, computer opponent, screen flow, HUD and screenpack layout | **Sandboxed**, off by default |
| Hot reloading of screenpack, HUD, mods and config | **Live**, off by default |
| glTF 3D stage backdrops, WebM video backgrounds | **Drawn**, hardware path |

Nothing in your installation is modified. Oxyde reads the same files the
original does and writes only its own `oxyde.cfg`.

## Content you can author

Everything Oxyde plays is data you can create or edit — no engine rebuild. This
is the full map of authorable content and where each one is documented:

| You can author | As | Documented in |
|---|---|---|
| **Characters** | MUGEN `.def`/CNS/SFF, or FUSE | [FUSE.md](FUSE.md), [BYOC.md](BYOC.md), the roster dropped under `chars/` |
| **Stages** | standard MUGEN `.def`/`.sff` | this doc (fully compatible); stage logic (hazards, breakable floors) in FUSE → [STAGE-LOGIC.md](STAGE-LOGIC.md); camera zoom and the versus `[Break]` corner-break → [EXTENSIONS.md](EXTENSIONS.md#the-camera) |
| **Screen packs** | MUGEN `system.def`/`fight.def`/`.sff`/fonts | [AUTHORING-SCREENPACKS.md](AUTHORING-SCREENPACKS.md); optional Lua menus → [SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md) |
| **Knuckle Up campaigns** | a `.knuckle` INI | [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md) |
| **Belt stages** (a street with waves, props, a boss) | `[Stage …]` sections in a campaign | [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md) |
| **Street props** | a prop folder + `prop.ini`, or a `[KnuckleUp]` block on any prop `.def` | [KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md#a-custom-prop--oxtool-props-build) |
| **Bosses** | an ordinary character, named by `boss =` in a campaign | [KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md#d-a-boss) |
| **Bonus-game characters** | a character with `bonus = 1` in `select.def` | [BONUS.md](BONUS.md) |
| **Pickup skins** | a folder of PNGs named by kind | [KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md#b-a-custom-pickup-skin) |
| **Rulesets** | a base mode plus sparse `.rules` deltas | [RULESETS.md](RULESETS.md) |
| **Lua mods** | sandboxed Lua 5.4 (modes, rules, matchup, CPU, flow, HUD, layout) | [SCRIPTING.md](SCRIPTING.md) |

Two things are **not** authorable as data and are engine code instead: the seven
procedural bonus **minigame types** and their physics (you can add bonus-game
*characters*, not new procedural types — see [BONUS.md](BONUS.md#adding-one)),
and the street auto-dresser's theme/catalog mix is being made data-driven
separately (see the street-dresser doc; until then it is the built-in fallback
in `crates/oxyde-app/src/street.rs`).

## Where to put things

Oxyde does not impose a layout of its own. `--root` points at a **MUGEN
installation** and everything is found relative to it, exactly the way the
original engine finds it — so the right answer is almost always "leave your
MUGEN folder alone and point at it".

```
/your/mugen/                 <- --root points here
  data/
    mugen.cfg                read for options, rules, limits and key bindings
    select.def               read for the roster and stage assignments
    common1.cns              merged into characters that need it
    fightfx.sff / .air       hit sparks
    common.snd               shared sounds
    system.def, fight.def    rendered: menus, select grid, versus screen, HUD
  chars/
    kfm/kfm.def              one folder per character, any depth
    ...
  stages/
    *.def, *.sff
  sound/                     music named by stages and select.def
  oxyde.cfg                  written by Oxyde; the only file it creates
  splash.jpg                 optional, your own splash art
```

Paths inside `.def` files are resolved case-insensitively and accept `\` or `/`
interchangeably, so content authored on Windows works unchanged on Linux. A
`..` that would escape the root is refused rather than followed.

### Keeping the binary somewhere else

The executable does not have to live in the game folder, and the two are better
kept apart — an engine you rebuild and a content archive you have curated for
twenty years have nothing to do with each other.

```
~/games/oxyde/oxyde          the binary, from `cargo build --release`
~/games/oxyde/oxtool         the diagnostics
~/mugen/                     the content, untouched

$ ~/games/oxyde/oxyde --root ~/mugen --config ~/mugen/oxyde.cfg
```

`--root` defaults to the current directory and `--config` to `oxyde.cfg`
*relative to where you ran the command*, so keeping the config next to the
content (as above) is worth being explicit about if you run from elsewhere. A
one-line shell alias or `.desktop` entry is the usual way to make that
permanent.

### Adding content

There is nothing to register. Drop a character folder under `chars/` and either

* add its name to `data/select.def` — the roster is then exactly what you
  listed, in your order; or
* set `[Game] useselectdef = 0` in `oxyde.cfg`, and every folder under `chars/`
  is scanned instead.

Stages work the same way: named in `select.def` under `[ExtraStages]`, or found
by scanning. Check the result before playing:

```bash
oxtool doctor ~/mugen        # every character, classified
```

### Several installations at once

Nothing is global. Each `--root` is independent, and `--config` chooses which
settings go with it, so a curated 40-character roster and the full 1,051 can
live side by side:

```bash
oxyde --root ~/mugen-full  --config ~/mugen-full/oxyde.cfg
oxyde --root ~/mugen-tourney --config ~/mugen-tourney/oxyde.cfg
```

## Precedence

Settings are layered, so an existing install behaves the way it always did and
anything you set in the new file wins:

```
built-in defaults  ->  data/mugen.cfg  ->  oxyde.cfg  ->  command line
```

If you have no `mugen.cfg`, nothing is lost — the defaults are MUGEN's own.

## `data/select.def`

This is where people spend their time, so it is read in full.

```ini
[Characters]
kfm
akuma, stages/95_iori.def
ryu, stages/flames.def, music=sound/theme.mp3, order=2
guile, random, includestage=0
boss, stages/final.def, order=3, ai=7
randomselect
-

[ExtraStages]
stages/agony.def

[Options]
arcade.maxmatches = 6,1,1,0,0,0,0,0,0,0
team.maxmatches   = 4,1,1,0,0,0,0,0,0,0
```

| Feature | Behaviour |
|---|---|
| Roster contents and order | The select screen shows exactly what you listed, in your order |
| `name, stage.def` | That character fights on that stage |
| `music = ...` | Played when that character fights, in preference to the stage's own |
| `order = n` | Recorded for arcade ordering |
| `includestage = 0` | Keeps that stage out of the random pool |
| `ai = n` | Per-character AI level, recorded |
| `[ExtraStages]` | Adds to the stage pool; the pool is *only* what you listed |
| `arcade.maxmatches` | Sets the arcade ladder length (`6,1,1,0` is eight opponents) |
| `-` blank slots | Counted and skipped — the engine lays the grid out itself |
| `randomselect` | Skipped; random selection is a menu action here |

An entry naming a character that is not installed is reported at startup and
skipped, rather than failing the load. On this archive that is 11 of 1,029
entries.

Set `[Game] useselectdef = 0` in `oxyde.cfg` to ignore it and list every folder
under `chars/` instead.

## `data/mugen.cfg`

```
$ oxyde --root .
  roster     2527 characters, 215 stages (308 ms) from select.def
  mugen.cfg  difficulty 8, life 100%, 60 fps, helpers 48, explods 64
```

The banner counts `select.def` **entries**, which is why it says 1,052 where
the rest of these documents say 1,051 characters: one row of this archive's
`[Characters]` list — `stages/oxyde_reactor_core.def`, on line 68 — lost its
character name and now names a stage, so it loads, finds no `[Files] sprite`
and shows a dead cell. Both numbers are true readings of the same file, and
`oxtool docs` accepts either until the row is repaired.

### `[Options]`

| Key | Effect |
|---|---|
| `Difficulty` | CPU strength, 1-8 |
| `Life` | Scales every character's life bar (100 = unchanged) |
| `Time` | Seconds per round; `-1` removes the timer |
| `GameSpeed` | Ticks per second; `-1` defers to `[Config]` |
| `WavVolume` | Master sound volume |
| `Team.1VS2Life`, `Team.LoseOnKO` | Read into the match rules |
| `motif` | Selects which `system.def` is drawn |

### `[Rules]`

These are the numbers characters were balanced against, and they are no longer
hard-coded:

| Key | Effect |
|---|---|
| `Default.Attack.LifeToPowerMul` | Power the attacker gains per point of damage |
| `Default.GetHit.LifeToPowerMul` | Power the defender gains |
| `Super.TargetDefenceMul` | Extra defence for a player being run by someone else's state -- inside a throw or a cinematic super |

### `[Config]` engine limits

Raising these for a helper-heavy roster is a legitimate thing to want, so they
are settings rather than constants:

`AfterImageMax`, `ExplodMax`, `SysExplodMax`, `HelperMax`,
`PlayerProjectileMax`, `DrawShadows`, `GameSpeed`.

`HelperMax` also sizes the player table, so a roster of characters that spawn
forty helpers works by editing one number.

### `[P1 Keys]` / `[P2 Keys]`

MUGEN stores bindings as **DOS set-1 scan codes**. They are translated to
physical key positions, so an existing key config carries over exactly —
including the classic default of punches on `L ; '` and kicks on `, . /`.

A scan code that cannot be translated leaves that binding at its default rather
than silently mapping to the wrong key.

### Read but not honoured

`[P1 Joystick]` scan codes (pads are mapped by the engine — see
[CONFIGURATION.md](CONFIGURATION.md)), and `[Rules] GameType` other than `VS`.
Both are reported at startup rather than ignored in silence.

## `oxyde.cfg`

Everything the engine adds on top. Written with `oxyde --write-config`, in the
same INI dialect. See [CONFIGURATION.md](CONFIGURATION.md) for the full list;
the parts that exist specifically for customisation:

```ini
[Game]
difficulty = 4        ; overrides mugen.cfg
roundtime = 99
rounds = 2
useselectdef = 1      ; 0 scans chars/ instead
selectcolumns = 0     ; 0 follows the screenpack, then 12. Whatever the number,
                      ; it is reduced to what leaves a cell wide enough for a
                      ; portrait and a readable name at your window size.
splash = splash.jpg   ; your own splash art
splashframes = 90

[Video]
renderer = auto       ; software | gpu | auto
scale = 0             ; 0 fits the window, or a fixed integer zoom
spritecachemb = 192

[Balance]
enabled = 0           ; opt-in; see BALANCE.md
table = balance.cfg   ; generated by `oxtool balance`
```

## Dropping content in

`.zip` and `.rar` files are folders as far as this engine is concerned. Drop
`chars/Ryu.zip` holding `Ryu/ryu.def` in and `select.def` can say `Ryu`; drop a
*pack* holding twenty characters in and each one is also published under its own
name, so a `select.def` that names them directly works without unpacking
anything. The same goes for `stages/`.

Each archive is unpacked once into a cache beside it, keyed on its size and
modification time, so the cost is paid once per install rather than once per
launch. Listing an archive is cheap and unpacking is not, so a `chars/` full of
them costs a listing each at start-up and an unpack only when something actually
resolves into one.

A real folder always beats an archive of the same name — which makes unpacking
one by hand the documented way to override it.

## Scripting

Lua 5.4 mods can add game modes, set the rules and the matchup, drive the
computer opponent, steer the flow between screens, draw over the HUD and
re-describe a screenpack screen. Off by default:

```ini
[Game]
mods = 1
```

See [SCRIPTING.md](SCRIPTING.md) for the seven hooks, the sandbox and what a
misbehaving mod can and cannot do.

## Hot reloading

```ini
[Game]
watch = 1
watchinterval = 250   ; milliseconds
```

Edit a file and it takes effect without restarting:

| Watched | Reloaded | Safe during a match |
|---|---|---|
| the motif's `system.def` and its art | screenpack, menus, fonts | yes |
| `fight.def` and its art | life bars, HUD, round calls | yes |
| `mods/*.lua`, `data/mods/*.lua` | every script, from scratch | yes |
| `oxyde.cfg` | shader, shader strength, debug switches | yes |
| `data/select.def`, a character folder | detected and reported | **applied at the title screen** |

A character cannot be swapped mid-match and will not be. `Match::step` reads a
character's state table, and a rollback snapshot taken before a swap would
restore state referencing the old one; in netplay both peers would have to swap
on the identical frame. Everything in the table above is on the *presentation*
side of that line, which is why it is free.

The watch set is small and explicit — the handful of files being edited, never a
tree. This archive is 2,137 character folders and 202 stages, Linux's default
`inotify` limit is 8,192 watches per user, and a recursive watch over `chars/`
would spend most of it on changes that could not be applied anyway. Polling a
dozen files four times a second costs one `stat` each and cannot be exhausted.

Off by default: it is an authoring convenience, and it is the one switch that
makes the engine read from disk during a match.

## What is not customisable yet

Being direct about this, because it is the real gap:

**Screenpacks are rendered.** `system.def` and the `fight.def` it names drive
the title menu, the character select grid, the versus screen, the options
backdrop and the whole in-match HUD, including the motif's own fonts, cursor
sounds and round announcements. `screenpack = 0` under `[Game]` in `oxyde.cfg`
falls back to the engine's own look, which sizes itself to the window and pages
over any roster size; every screen also falls back on its own if the motif
cannot supply what it needs.

**Storyboards** are played: `logo.storyboard` and `intro.storyboard` before the
title screen, a character's `[Arcade] ending.storyboard` when they finish an
arcade ladder, and the motif's `[Default Ending]` and `[End Credits]` after it.
Scenes, layers, per-layer start times, fades and per-scene music are all
honoured. Losing a ladder offers `[Continue Screen]` and then
`[Game Over Screen]`; surviving one ends on `[Survival Results Screen]`.
The attract loop a motif's `[Demo Mode]` asks for is played when the title
screen is left alone.

See `kb/screenpacks.html` for the full format reference.

**Music** is played from a stage's `[Music] bgmusic` and from a character's
`music =` column in `select.def`, the character's choice winning. MP3, Ogg
Vorbis, FLAC, WAV and M4A are all read, streamed rather than loaded. Turn it
off, or turn it down separately from the sound effects, in the options screen
or under `[Sound]` in `oxyde.cfg`.

## Verifying your installation

```bash
oxtool doctor .     # every character, classified, with repairs listed
oxtool verify .     # everything that parsed, and everything that did not
oxtool compat .     # which MUGEN release each file belongs to, and whether it loads
oxtool mods .       # every Lua mod, every hook it defines, and what went wrong
```

All of them read your files without modifying them.
