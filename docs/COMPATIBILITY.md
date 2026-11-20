# Compatibility

What of M.U.G.E.N is implemented, what is not, and every place this engine
deliberately behaves differently.

## Formats

| Format | Support |
|---|---|
| `.def` (character, stage, system, fight) | Full. Repeated sections and keys preserved in order; `;` comments respect quotes. |
| `.cns` / `.cmd` (states, constants, commands) | Full. |
| `.air` (animations) | Full: `Clsn1`/`Clsn2`, `Default` scoping, `Loopstart`, flip, blending. |
| `.sff` v1.01 (sprites) | Full, verified byte-for-byte against an independent decoder. Linked sprites and shared palettes handled. |
| `.sff` v2.00 / 2.01 | Full: RAW, RLE8, RLE5, LZ5 and embedded PNG (formats 10-12). LZ5's **long** back-reference form takes its distance and its count one greater than they are written — `d = (d<<2 \| next) + 1`, `n = next + 2` — which Oxyde had wrong in both halves until 0.29.0; the short form was right, so only a frame whose stream reached for a long run came out one pixel short and drifting. **Verified against Ikemen GO's own 1.1 characters**, which is what turned up the two bugs that had made every PNG sprite in the format fail — see [the era census](#the-four-mugen-releases). An **8-bit** PNG sprite takes the file's palette, not its own `PLTE`: that table is a placeholder, because the indices are shared by all twelve of the character's palettes. A 24- or 32-bit one is indexed on the way in against a palette built from its own colours. |
| `.snd` (sounds) | Full index; WAV payloads decoded as 8/16/24/32-bit PCM and 32-bit float, mono or stereo. |
| Stage and character music (`[Music] bgmusic`, `select.def` `music =`) | Played, streamed from disk. MP3, Ogg Vorbis, FLAC, WAV and M4A. |
| `.act` (palettes) | Full, including MUGEN's reversed byte order. |
| `.fnt` (bitmap fonts) | Read and drawn: the motif's own fonts are what the menus, the HUD and storyboard text use. |
| `.pcx` | 8bpp/1-plane RLE, which is what SFF v1 is made of — and 8bpp/**3**-plane, which a handful of this archive's characters have inside their SFF v1 anyway: 158 sprites over fifteen characters, 66 of them in `chars/Seiya3`. MUGEN reads those as though they were indexed, which turns each row into three rows of garbage; Oxyde reads the three planes as the RGB they are and indexes them against a palette built from the sprite's own colours, the way a truecolour PNG sprite is handled. The transparent colour is whichever holds the image's border. `oxtool sprites` is what found them. |
| `data/select.def` | Full: roster and order, per-character stages, `music`, `order`, `includestage`, `ai`, `[ExtraStages]`, `arcade.maxmatches`, `team.maxmatches`, blank slots. The arcade ladder walks the `order` groups that `arcade.maxmatches` names, falling back to the whole roster for a group nobody is in. Plus one extension: `bonus = 1` and a `[BonusGames]` section — see [BONUS.md](BONUS.md). |
| `data/mugen.cfg` | `[Options]`, `[Rules]`, `[Config]` engine limits and `[P1/P2 Keys]` scan codes are read and applied. |
| `system.def` / `fight.def` | Rendered: menus, select grid, versus screen, HUD, fonts, cursor sounds, round announcements and pacing. |
| Text encodings | UTF-8, Windows-1252 and Shift-JIS detection. Shift-JIS double-byte glyphs render as a replacement character; the bytes are preserved. |
| `.zip` / `.rar` content | Mounted as folders, anywhere in the tree. `chars/Ryu.zip` holding `Ryu/ryu.def` resolves as `chars/Ryu/`; a *pack* holding several characters also publishes each one into the parent, so a `select.def` naming them directly works. Unpacked once into a cache beside the archive and keyed on size and mtime, so it is paid once per install. Unpacking one by hand next to it silently overrides it. |
| `[Info] localcoord` | Applied. Ikemen GO's rule: every distance a character declares, and its drawn scale, is multiplied by `320 / localcoord.x`. Every character in this archive declares `320,240`, so the conversion is the identity for all of them. |
| `[BGdef] model` (glTF/GLB) | Ikemen GO's 3D backdrops, on the hardware path only — see [RENDERING.md](RENDERING.md). |
| `[BG] type = video` | WebM, VP8 and VP9, behind a build feature. |

## The four MUGEN releases

DOS MUGEN, WinMUGEN, 1.0 and 1.1 share most of their formats — SFF v1, AIR, SND
and CNS are the same files in 1999 and 2011 — so "compatible with all four" is a
claim a feature table cannot settle. `oxtool compat` settles it by classifying
every file by what it actually *uses* and then loading it:

```
$ oxtool compat . --stages
  era         years       characters  loaded
  DOS MUGEN   1999-2001       844     844
  WinMUGEN    2002-2004       198     198
  MUGEN 1.0   2009              9       9
  MUGEN 1.1   2011              0       -   none in this archive
```

An era with no content in it is reported as **untested**, not as supported.

Stages are classified the same way, and all 202 in this archive load — 186 DOS,
16 that declare a `localcoord` and so are 1.0.

The 1.1 row was filled in by pointing the tool at Ikemen GO's own content —
four characters and eight stages, all of which load — and doing that found three
real defects in this engine. They are written up in
[`metrics/bugs-fixed.md`](../../metrics/bugs-fixed.md).

## The common states

The 0-series and 5000-series — standing, walking, crouching, jumping, running,
guarding, being hit, falling, getting up — are not in a character's own file.
They live in a shared one, and a character's `stcommon` names it. Oxyde resolves
that name across all three conventions, because a name written in 2001 has to
find a file written in any of them:

| declared | found on disk | whose convention |
|---|---|---|
| `common1.cns` | `common1.cns` | MUGEN's |
| `common1.cns` | `common1.cns.zss` | Ikemen GO's — the extension is *added* |
| `common1.cns` | `common1.fuse` | Oxyde's — the extension is *replaced* |

A character that names no `stcommon` at all, or names a file that is not there,
gets the shared one from `data/` — which is what the original engine's default
does, and is the difference between a character that loads and does nothing and
a character that fights.

**Which shared file wins.** `data/common1.cns` is preferred when it exists,
then `common1.cns.zss`, then `common1.fuse`. That order is deliberate: pointing
Oxyde at an existing MUGEN installation must not change how it plays, and that
installation has a `common1.cns` in it. Oxyde's own file ships in the engine
archive, where it is the only one present. To use it over an existing install
instead, move `data/common1.cns` aside and drop `common1.fuse` in beside it;
the measured difference is in
[`metrics/engine-comparison.md`](../../metrics/engine-comparison.md).

## Reading an existing installation

Oxyde reads your MUGEN folder as it stands and modifies nothing in it.
Settings layer so that an existing install keeps behaving the way it did:

```
built-in defaults  ->  data/mugen.cfg  ->  oxyde.cfg  ->  command line
```

That covers the roster and its stage assignments, the arcade ladder length, the
rules characters were balanced against (`Default.Attack.LifeToPowerMul`,
`Default.GetHit.LifeToPowerMul`, `Super.TargetDefenceMul`), the engine limits
(`HelperMax`, `ExplodMax`, `SysExplodMax`, `PlayerProjectileMax`,
`AfterImageMax`, `DrawShadows`), difficulty, round time, game speed, volume and
both players' key bindings -- MUGEN stores those as DOS set-1 scan codes, which
are translated to physical key positions, so `L ; '` / `, . /` carries over
exactly. A scan code with no translation leaves that binding at its default
rather than mapping to the wrong key.

Anything read but not honoured is printed at startup rather than dropped in
silence. The full surface is in [CUSTOMISATION.md](CUSTOMISATION.md).

## Expressions and triggers

The full CNS expression language is implemented: the documented operator
precedence, int/float duality with MUGEN's exact arithmetic (`7/2 == 3`,
division by zero is 0, `%` on floats is an error yielding 0), short-circuiting
`&&`/`||`, intervals, assignment, and trigger redirection.

**281 triggers** are recognised: the whole documented set, the spelling
variants that appear in shipped content, and the extensions outside Elecbyte's
vocabulary — see [EXTENSIONS.md](EXTENSIONS.md). Those that need systems not present
(some projectile timing) return 0 rather than failing to compile, so a
character using them still loads and plays.

`StageVar` and `StageConst` used to be among them and are not any more: both
now read the stage's own `.def`, which is worse than absent when it answers a
constant zero and a character scales a move to it.

`P3Name` and `P4Name` were the same kind of fault and were worse hidden. Both
answered `false` unconditionally, and the manual is why nobody noticed: with no
teammate, `p3name = "x"` returns 0 and `p3name != "x"` returns 1, which is
exactly what a false equality gives once it is negated. So the hardwired answer
was *correct* for a one-on-one — the only shape anybody tested — and in every
team match the check silently never fired. Counted byte-wise over 36,919 state
files, **1,141 characters compare against one of them**: 359 of the 1,051 in the
game root and 782 of the 2,413 under the larger test roster, a third of the roster either
way. They now resolve to the asking fighter's team mate and second opponent,
relative to whoever asks rather than to an absolute seat — side two's team mate
is on side two.

## State controllers

All **93** of Elecbyte's controller types are recognised and their parameters
compiled, and every parameter the manual documents is read — with one
exception, noted below. **All 93 are executed.** Two of them appear in
neither the 1.1 manual nor WinMUGEN's controller list, and no character in this
archive reaches either, but both are implemented regardless:

| Controller | What it does here | Reached by this archive |
|---|---|---|
| `SendToStage` | The inverse of `TagOut`: places a fighter back on the stage | never |
| `Zoom` | Drives an Ikemen-style camera scale (MUGEN's own camera cannot scale, so there it does nothing) | never |

Thirty-nine more controllers are this engine's own, and no character here
reaches one of those either — see [EXTENSIONS.md](EXTENSIONS.md).

`TagIn` and `TagOut` **are** executed. Neither is in the manual either —
`TagIn` appears only in WinMUGEN's list of controller names, with no reference
section behind it — so the specification used is the one two independent
authors reproduced verbatim in this archive, evidently from Elecbyte's own
text: "Changes the state number of the player, and that of the player's
partner", with `stateno`, `partnerstateno` and `ctrl`. Where it says "Crashes
if triggered without a partner being present", Oxyde changes its own state and
leaves it there.

The one documented parameter still unread is `RemapPal source`, which names an
SFF v2 palette *group*; Oxyde's palette model is a single index per sprite.
One line in this archive writes it. `oxtool soak --render` counts every
controller the roster reaches but the engine does not execute, which is how
this list is kept honest.

## Engine-owned behaviour

These are implemented in the engine because that is where MUGEN implements
them. `common1.cns` contains no code for any of them, and characters are
authored assuming they happen:

* Stand to walk (20), crouch (10/11/12) and jump (40) transitions.
* Automatic turning when an opponent crosses over (states 5 / 6), suppressed by
  `AssertSpecial noautoturn`.
* Guard entry into state 120 when a player holds away inside guard distance,
  suppressed by `nostandguard` / `nocrouchguard` / `noairguard`.
* Restoring `ctrl` at the start of the round. The intro chain
  `5900 -> 190 -> 191 -> 0` sets `ctrl = 0` and nothing in the CNS sets it back.
* Writing `GetHitVar`s and routing a hit player into 5000 / 5010 / 5020 / 5080
  by stance, or 150 / 152 / 154 when guarding. Those three are the guard-hit
  *shake* states; 151, 153 and 155 are each one's knocked-back continuation and
  are reached from the shake state, never entered from outside.
* Player pushing, screen bounds and camera following.
* **Deciding a time over.** When the round clock expires the engine gives the
  round to the side with the greater *share* of its bar left — life ÷ lifemax,
  summed over standing members and kept in integer per-mille — not the one
  holding the most absolute life points. This matches MUGEN and Ikemen GO, and
  is what keeps a fighter plainly ahead on his own bar from losing to a
  scaled-up boss who holds more raw points behind a bigger `life`/`lifemax`. An
  exact tie is a draw.

  A screen bound holds a fighter's **position** inside the stage's
  `[Bound] screenleft` / `screenright` margin — their axis, not the edge of
  their push box, which is what the manual says and what the archive expects.
  A wide fighter in the corner therefore has part of themselves off the side
  of the screen. Holding the whole box inside the screen looks tidier and
  breaks every move that waits for the corner: those wait on
  `BackEdgeBodyDist`, which is measured from the back of the width bar, so a
  box held inside the screen leaves it a whole body width above zero for ever.
  Of the ways this archive's characters compare that trigger, `<= 0` appears
  203 times and `<= -50` 32 — they expect to reach zero and pass it. The
  `Width` controller's `edge` pair is the one width that does apply, and it
  applies facing-relative.

And, just as importantly, what the engine does **not** own, because the line is
easy to put in the wrong place:

* **Ending a guard.** The engine decides that a guard *begins* — it puts the
  player into 120 — and the common states decide when it ends: let go of back,
  or the attacker leaves guard distance, and 130/131/132 change to 140. A
  common-state file that leaves this out gives fighters who block once and then
  block for the rest of the round.
* **Jump velocity.** State 40 sets it, from the character's own constants and
  the direction held at that moment. The engine only routes the player there.
* **Restoring `ctrl` between movement states.** The 0/10/11/12/20/50/100
  headers deliberately do not mention `ctrl`, so it carries through unchanged
  and the engine's transitions can move a fighter between them. Writing
  `ctrl = 0` into one of those headers — state 10 is the easy mistake — strips
  control from anyone who ducks and never gives it back.

**State numbers 0-199 and 5000-5999 are effectively reserved.** A character
that parks itself in state 20 without holding a direction will be returned to
state 0, because state 20 *is* the walk state.

## Deliberate deviations from the 2002 specification

Documented so they are decisions rather than accidents. All are permissive:
they make authored intent work where the original engine silently dropped it.

| Form | Specification | Here | Occurrences in this archive |
|---|---|---|---|
| `AnimElem >= 3` | Invalid; the trigger never fires | Compiled as `AnimElemNo(0) >= 3` | ~1,300 |
| `statetime` | Not a trigger | Accepted as `Time` | ~200 |
| `TimeMod >= 10, 0` | Invalid | Leading operator accepted and ignored | ~13 |
| `animelem = 1[0,45]`, `animelem = 1, [1,5]` | Invalid | Accepted as the interval form | ~40 |
| `animelem = 1, => 0` | Invalid | Accepted as `>=` | ~2 |
| `ProjHit(1005)`, `ProjHit[1005]` | Only the `ProjHit1005` suffix form is documented | All three accepted | ~60 |
| `Clsn1Defualt:` | Invalid; every box in the animation is dropped | Any word before the colon means "default" | ~120 |
| `command =` (empty) | Error | Treated as a deliberately disabled command | ~250 |
| `stcommon = common1.cns` | Searched next to the `.def` | Also searched in `data/` | ~500 characters |
| Scalar `walk.fwd = 2.4` | -- | Also answers to `const(velocity.walk.fwd.x)` | Universal |

One deviation is **not** permissive and is worth knowing: `root, var(1) := 5`
evaluates the right-hand side inside the redirected context rather than the
local one. The archive contains zero instances of redirected assignment, so
this is currently unobservable; it is noted rather than fixed to keep the
compiler simple.

Content errors that the original engine also rejects -- `NumExplod(6051)!`,
`ProjHitcount(3200)`, `projhitid` -- are still reported and still compile to
`0`. Being lenient about typos that change gameplay would be a different kind
of bug.

## Automatic repairs

The loader repairs two classes of damage, and reports every repair through
`LoadReport::repairs` and `oxtool doctor`:

1. **A `sprite =` or `anim =` line pointing at a file that is not there.** If
   the character's folder contains exactly one `.sff` (or `.air`), that file is
   used. Ambiguity is deliberately not resolved: a folder with three `.sff`
   files might be a character plus two spares, and guessing wrong is worse than
   reporting the problem.
2. **Missing common states.** A character with no state 0 and no state 5000 has
   no `stcommon`, or one that points nowhere; the shared `data/common1.cns` is
   merged in, with the character's own states always winning.

On this archive that is enough to take playability from 1,043/1,045 to
**1,045/1,045**.

Two more repairs happen at run time rather than at load:

3. **A fighter stuck in a state where nothing is happening.** Same state, same
   animation, same life and within twenty units of the same place for seven
   straight seconds, and control is handed back. `RAOH`'s 1061 is a throw that
   never lets go.
4. **A fighter abandoned in somebody else's custom state.** A `p2stateno` hit
   or a `TargetState` puts the victim into one of the *attacker's* states, and
   only a controller the attacker's author wrote can take them out of it
   again. When that controller is missing — or is gated on something the
   victim can never reach — the victim stays there for the rest of the round,
   animating out of the attacker's file: a copy of the attacker standing where
   the opponent was. Five seconds after the owner stops attacking, the victim
   is handed back. Unlike (3) this does not wait for them to be still: some of
   these states leave the victim sliding across the stage for ever.

## Beyond MUGEN

101 triggers, 39 state controllers, two global states, five command symbols and
five optional gameplay systems are outside Elecbyte's vocabulary altogether.
They are documented on their own page — [EXTENSIONS.md](EXTENSIONS.md) — and the
three engines are put side by side in [VS-ENGINES.md](VS-ENGINES.md), which is
also where the list of what Ikemen GO has and this does not now lives.

None of them can change how an existing character plays: every name was a
compile error before it existed, so no shipped `.cns` can be reading one by
accident, and the five gameplay systems are off until a line in `oxyde.cfg`
switches them on.

The one measured exception in 0.25.0 is worth naming: **twenty-seven
`down.recover` and four `xaccel` parameters that authors in this archive wrote
and this engine was dropping are now honoured**, which moves the soak by 25
distinct states out of 12,256. That is a documented parameter being read for the
first time rather than a rule being changed.

## Not implemented

* MUGEN's own team-mode selection UI. Every team mode the original names is
  here -- Team Arcade, Team Versus, Team Co-op, Survival Co-op, plus this
  engine's Team Rumble and Team Tag; see [MODES.md](MODES.md) -- but the team
  size is fixed per mode rather than chosen on a MUGEN-style team screen.
* `[P1 Joystick]` scan codes. Pads are mapped by the engine instead; see
  [CONFIGURATION.md](CONFIGURATION.md).
* `[Camera] tensionhigh` / `tensionlow`, `overdrawhigh` / `overdrawlow` and
  `cuthigh` / `cutlow`. Nothing in this archive's 195 stages writes any of them;
  the playfield is fitted to the window instead, which is the problem those
  parameters exist to solve. **`zoomin`, `zoomout`, `startzoom`, `autozoom`,
  `zoominspeed`, `zoomoutspeed`, `zoomindelay`, `zoomanchor`, `yscrollspeed`,
  `tensionvel` and `autocenter` are implemented** as of 0.25.0 — see
  [EXTENSIONS.md](EXTENSIONS.md#the-camera).
* **Screenpack layout in Lua.** Ikemen GO's screens are Lua all the way down;
  this engine's are `system.def`, with Lua covering modes, the computer
  opponent, screen hand-offs and a HUD overlay. An architectural difference
  rather than an oversight — see [SCRIPTING.md](SCRIPTING.md).

**ZSS is read in full**, as of 0.27.0. All fourteen `.zss` files Ikemen ships
parse and lower with no errors — 140 states, 1,081 controllers — and `kfm_zss`
fights. Three details of ZSS are not MUGEN's and are implemented as Ikemen has
them rather than as the manual would suggest:

* A **negative state appends across files** rather than replacing. Six of
  Ikemen's own `data/*.zss` files declare `[StateDef -4]` and three declare
  `[StateDef -2]`; `kfm_zss` puts its moves in `command.zss` and its AI in
  `AI.zss`, both under `[StateDef -1]`. CNS keeps MUGEN's replace rule.
* `[Constants]` in a `.const` file names values that `const(...)` reads with
  no section prefix, which is how `[StateDef const(StateDizzy)]` gets a number.
* `stcommon = common1.cns` finds `common1.cns.zss` when that is the file on
  disk.

`GO` is accepted as a third effect-file selector beside `S` and `F`. This
engine loads one shared effect set, so `GO` draws from it rather than from a
separate `gofx.def`.

Oxyde also has a state language of its own, **FUSE** — see
[FUSE.md](FUSE.md) — and converts CNS and ZSS to it with `oxtool fuse`.

* **GLSL shaders.** `ShaderSet` works against sixteen named built-in effects;
  arbitrary GLSL is not read. 3D glTF backgrounds and video backgrounds *are*
  implemented — see [RENDERING.md](RENDERING.md).
* AI authored inside a character's CNS is given no difficulty boost of its own
  beyond the `AILevel` trigger, which now answers with the computer player's
  real level; the engine supplies its own baseline opponent as well, so
  characters with no AI are still playable against.

### The screenpack, and the alternative to it

`system.def` and the `fight.def` it names are rendered: the title menu, the
character select grid, the versus screen, the options backdrop, the whole
in-match HUD, the motif's fonts and cursor sounds, its round announcements, and
the pacing its `[Round]` block asks for. Every screen falls back to the
engine's own look for anything the motif cannot supply, so a half-broken pack
still plays, and the startup line says exactly what was found.

The pack this installation now uses -- `data/oxyde`, described in
[the README](../README.md#the-oxyde-pack) -- is the engine's own theme
authored as a screenpack, at 640x480 for this roster: 20x10 cells of 28 pixels,
200 characters a page. The one it replaced is still in `data/system.def`:
320x240 art from 2008 laid out for a 53x35 grid of 4x5-pixel cells.

The engine's own menus remain available with `screenpack = 0`, and they are not
a consolation prize. The built-in HUD and select screen stay sharp at any
resolution, page over any roster size, letterbox mismatched portraits instead
of overlapping them, and cannot break when a screenpack file is damaged.

### Deviations worth knowing about

* **`PlaySnd volume` is an offset, not a percentage.** MUGEN's parameter runs
  -255..255 with `0` meaning "as authored". This engine now reads it that way.
  It previously treated it as a percentage with a default of 100, which
  silenced every character that ducked a sound slightly with `volume = -40`.
* **Versus is human against human**, as it is in MUGEN, and both sides are
  chosen. `VERSUS PLAYER 2 = COMPUTER` in the options screen restores the
  single-player behaviour this engine used to have.
* **Bonus stages are not characters.** MUGEN has no bonus-stage concept at all;
  the ones here are engine-side props, not fighters with a life bar. See
  [BONUS.md](BONUS.md).
* **The screenpack's grid is honoured exactly; the engine's own is not.** With
  `screenpack = 1` the motif's `rows`, `columns`, `cell.size` and
  `cell.spacing` are used as written. With `screenpack = 0` a column count that
  would make cells narrower than a portrait plus a readable name is reduced to
  what fits.
* **A roster larger than the screenpack's grid pages rather than truncating.**
  MUGEN would simply have hidden the rest. The page counter, the search box and
  the mode note that go with that are drawn on the motif's own select screen
  too, placed by `search.offset`, `note.offset` and `page.offset` if the pack
  names them and in the strip above the grid if it does not.
* **A portrait too big for its cell is shrunk into it and centred** rather than
  drawn at the pack's scale whatever size it is. Sixty characters here have no
  small portrait at all and fall back to the 120x140 one, which at a scale
  chosen for 25x25 covers a fifth of the grid. A portrait that fits is drawn
  exactly where the pack asked. The HUD portrait is held the same way, to the
  size a nominal 25x25 would have been drawn at.
* **`select.def`'s `randomselect` slot is a cell on the grid**, resolved to a
  character at random the moment it is locked in. MUGEN draws the same cell;
  this engine had been dropping the slot on the way in.
* **The camera will rise past a stage's `boundhigh`** rather than let a jumping
  fighter leave the top of the screen, and no further than it must.
  `camerakeepvisible = 0` restores MUGEN's behaviour exactly.
* **A line of text that would fall off the bottom of the motif's own box is
  moved up to sit on it.** Packs put the stage name at y = 237 of 240.
* **Players are processed by what they are doing, not by their place in the
  table.** MUGEN reads player 1 before player 2 on every tick, which is a real
  edge in any exchange where both swing at once. Attackers are read first here,
  then idlers, then whoever is being hit, roots before their helpers.
  `[Rules] indexprocessingorder = 1` restores MUGEN's order.
* **Left and right pressed together register as neither**, and so do up and
  down. A stick cannot do it; a keyboard can, and MUGEN passing both through
  is what lets a player hold both and be un-crossable.
  `[Input] socdresolution = 0` restores MUGEN's behaviour, and three other
  resolutions are available. This is the one default on either list that is
  not MUGEN's.
* **A `DisplayToClipboard` may take sixteen `params` rather than six.** A
  shorter list simply ends sooner, so nothing depends on the limit being
  exactly six — and `PrintToConsole` and `Text`, which share the formatter,
  are documented with no limit at all.
* **`select.def` finds a character named as a path.** Entries are documented
  as relative to `chars/`, so `kfm/kfm.def` means `chars/kfm/kfm.def`; a path
  from the game root is tried after it.

## Known rough edges

* Around 1,200 trigger expressions still fail to compile. These
  are overwhelmingly genuine author typos that the original engine also
  rejected; `oxtool verify --show 50` lists them classified.
* 50 sprite files in the archive have truncated payloads and 49 have a wrong
  header count. They load with the sprites they do have.
* Characters that spawn more than `HelperMax` simultaneous helpers hit the
  player-table cap, which defaults to MUGEN's own limit and is read from
  `mugen.cfg`. Destroyed helper slots are recycled; raising the number is a
  one-line edit rather than a rebuild.
