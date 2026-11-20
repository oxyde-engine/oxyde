# M.U.G.E.N vs Ikemen GO vs Oxyde

Three engines that play the same content, compared feature by feature.

* **M.U.G.E.N** — WinMugen (2006-08-31), the 296 KB `Winmugen.exe` sitting next
  to this folder, and MUGEN 1.1 beta where it differs. Closed source,
  abandoned, 32-bit Windows, DirectX 7, 16-bit colour, single-threaded. The
  engine every character in this archive was written for.
* **Ikemen GO** — the open-source Go rewrite (MIT), currently at 1.0. About
  126,000 lines of Go plus 15,000 of Lua and ZSS. OpenGL 3.3 core, GLES 3.2 and
  Vulkan back ends. Aims at "backwards-compatibility on par with MUGEN 1.1
  beta, while simultaneously expanding on its features".
* **Oxyde** — this engine. About 301,000 lines of Rust across thirteen
  crates, ~2,900 tests, a CPU rasteriser by default with an optional hardware
  path, sandboxed Lua mods, three state languages with a language server and a
  linter, MIT OR Apache-2.0.

This is the honest version. Every "no" is a real no, and
[§12](#12-where-oxyde-is-behind) lists what Oxyde does *not* have as plainly as
the rest lists what it does. The two other engines' columns are filled in from
their own documentation and source, both of which are in this repository
(`Ikemen-GO/`, `Ikemen-GO.wiki/`, `mugen_docs/`) — not from memory. And where a
row turns on *behaviour* rather than documentation, the other engine can be run
and watched rather than only read — WinMUGEN under wine, and Ikemen GO headless
under a software renderer — so a disagreement is settled by observation, not
assertion.

**Legend** — ● full · ◐ partial · ○ none

---

## Contents

| | |
|---|---|
| [1. What each one is](#1-what-each-one-is) | Identity, licence, platform |
| [2. Content compatibility](#2-content-compatibility) | Reading the same files |
| [3. The engine language](#3-the-engine-language) | Triggers, controllers, states, variables |
| [4. Gameplay systems](#4-gameplay-systems) | Meters, parry, tag, the third axis |
| [5. Presentation](#5-presentation) | Rendering, camera, effects |
| [6. Modes](#6-modes) | What you can actually play |
| [7. Online](#7-online) | Netcode, and the tournament |
| [8. Scripting and extension](#8-scripting-and-extension) | Lua, ZSS, FUSE, Rust |
| [9. Tooling and verification](#9-tooling-and-verification) | How each one is checked |
| [10. Performance and reach](#10-performance-and-reach) | What it runs on |
| [11. Robustness](#11-robustness) | What happens when content is wrong |
| [12. Where Oxyde is behind](#12-where-oxyde-is-behind) | The honest list |
| [13. Scoreboard](#13-scoreboard) | The summary |

---

## 1. What each one is

| | M.U.G.E.N | Ikemen GO | Oxyde |
|---|---|---|---|
| Latest release | WinMugen 2006 / 1.1b 2013 | 1.0, actively developed | 0.37.0 |
| Source | closed, lost | MIT, Go | MIT OR Apache-2.0, Rust |
| Size | 296 KB binary | ~126k lines Go + 15k Lua/ZSS | ~301k lines Rust |
| Platforms | 32-bit Windows | Windows, macOS, Linux, Android | Windows, Linux (one checkout builds both) |
| Graphics | DirectX 7, 16-bit | OpenGL 3.3 core / GLES 3.2 / Vulkan | **CPU rasteriser**, GPU used only to scale the result |
| Needs a GPU | yes (DX7) | yes | **no** |
| Memory safety | — | garbage-collected | `unsafe` confined to 35 sites in 7 files, almost all video-decoder FFI; none in the simulation |
| Tests | — | none in the repository | **~2,900**, none of which needs the archive |

The size difference is worth reading twice in each direction. MUGEN does an
enormous amount in 296 KB and nobody can ever change any of it again. Ikemen GO
carries two scripting languages and three graphics back ends. Oxyde is now the
largest of the three, and the honest reading is that a CPU rasteriser, a
language server, a linter and forty-odd diagnostic tools cost lines that a
thinner engine does not spend.

---

## 2. Content compatibility

The whole point of all three. Nothing below converts anything; the same
`chars/`, `stages/` and `data/` folder serves all three engines.

| | MUGEN | Ikemen GO | Oxyde | Notes |
|---|---|---|---|---|
| `.def` / `.cns` / `.cmd` / `.air` | ● | ● | ● | |
| `.sff` v1 sprites | ● | ● | ● | Oxyde's decoder is byte-verified against an independent implementation |
| `.sff` v2 (RAW/RLE8/RLE5/LZ5) | 1.1 only | ● | ● | Verified against Ikemen GO's own 1.1 characters |
| `.sff` v2.01 embedded PNG | 1.1 only | ● | ● | Three bugs found and fixed doing it — see below |
| `.snd`, `.act`, `.pcx`, `.fnt` | ● | ● | ● | |
| `data/select.def` | ● | ● | ● | Oxyde also reads `bonus`, `[ExtraStages]`, `arcade.maxmatches` |
| `data/mugen.cfg` | ● | ● | ● | Including both players' DOS-scancode key bindings |
| Screenpack (`system.def`) | ● | ● | ● | |
| Lifebars (`fight.def`) | ● | ● | ● | |
| Storyboards | ● | ● | ● | |
| Stage `[BGCtrl]` | ● | ● | ● | All nine controller types |
| Parallax backgrounds | ● | ● | ● | Drawn a scanline at a time |
| Reflections, shadows | ● | ● | ● | |
| Character endings, credits | ● | ● | ● | |
| Attract / demo loop | ● | ● | ● | |
| Text encodings | Shift-JIS era | ● | ● | Oxyde auto-detects UTF-8, Windows-1252 and Shift-JIS |
| Content from `.zip` | ○ | ● characters and stages | ● | Characters, stages and packs |
| Content from `.rar` | ○ | ○ | ● | |
| `[Info] localcoord` on characters | 1.0+ | ● | ● | A 1280-wide fighter is drawn and moves at a quarter scale |
| Case-insensitive paths on Linux | — | ● | ● | Oxyde through a VFS layer |
| Hot reload of screenpack / HUD / mods | ○ | ◐ | ● | |

### The four MUGEN releases

"Compatible with DOS MUGEN, WinMUGEN, 1.0 and 1.1" is easy to write and hard to
mean, so `oxtool compat` classifies every file by the release its *contents*
place it in — declared version first, then what the files actually use, later
wins — loads each one, and reports the two numbers together. An era with no
content in it is reported as **untested**, not as supported.

```
$ oxtool compat . --stages
  era         years       characters  loaded
  DOS MUGEN   1999-2001       844     844
  WinMUGEN    2002-2004       198     198
  MUGEN 1.0   2009              9       9
  MUGEN 1.1   2011              0       -   none in this archive

$ oxtool compat Ikemen-GO-Screenpack --stages
  MUGEN 1.1   2011              4       4   (SFF v2.01 PNG sprites)
  MUGEN 1.1   2011              8       8   stages
```

Testing against Ikemen GO's own 1.1 content is what closed the last row, and it
found three real bugs in the process:

* **SFF v2.01 PNG sprites never decoded.** The payload carries the same four-byte
  uncompressed-size prefix the RLE and LZ5 payloads do, ahead of the PNG
  signature. Every one of `kfm720`'s 281 sprites failed.
* **8-bit PNG sprites drew as black silhouettes.** Their `PLTE` is a placeholder
  — the indices are shared by all twelve of a character's palettes and the real
  colours live in the SFF's own table. Ikemen reads it the same way and never
  looks at the PNG palette.
* **`localcoord` was read and never applied.** A 1280x720 character was drawn at
  native sprite size, four times too big. Every character in *this* archive
  declares `320,240`, so applying it cannot change any of them.

**Measured, on this archive** — 2,489 characters, 202 stages, 16 GB:

```
$ oxtool doctor .
  perfect      2101   84.4%
  playable      384   15.4%
  repaired        4    0.2%
  unplayable      0    0.0%
  broken          0    0.0%

  2489 of 2527 characters are playable (100.0%)
```

---

## 3. The engine language

### Vocabulary

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Triggers recognised | **127** (Elecbyte 1.1b `trigger.html`) | **267** — those + 140 new (its own wiki) | **281** |
| State controllers recognised | **89** (Elecbyte 1.1b `sctrls.html`) | **158** — those + 69 new (its own wiki) | **160** |
| State controllers executed | 89 | all | all 160 |
| Global states | `-1`, `-2`, `-3` | those | those, plus **`-4`** and **`+1`** |
| Variables per fighter | 60 int, 40 float | any `int32` index, unbounded count | any `u32` index, **capped at 65,536 live slots per bank** |
| `RedirectID` on every controller | ○ | ● | ● |
| Named variables (`[Map]`, `Map(name)`) | ○ | ● | ● |
| Maths (`Max`, `Clamp`, `Lerp`, `Atan2`, …) | ○ | ● | ● — and folded at compile time when the arguments are constant |
| Introspection (`ExplodVar`, `ProjVar`, `ClsnVar`, `SoundVar`) | ○ | ● | ● |
| Collision queries (`ClsnOverlap`, `HitByAttr`) | ○ | ● | ● |
| `Text` on screen from a `.cns` | ○ | ● | ● |
| Command file `\|`, `L`/`R`, `N`, `/30`, `steptime` | ○ | ● | ● |

Every Ikemen GO trigger name and every Ikemen GO state controller name is
recognised by Oxyde. That is a mechanical claim and it is mechanically checked:
the names were extracted from `Ikemen-GO.wiki/` and diffed against the engine's
own tables, and the test
`every_extension_controller_runs_rather_than_counting_as_unimplemented` fires
every one of them in a single state and asserts that none reaches the
"documented and not done" counter.

Where the *behaviour* behind a name is not something a software rasteriser can
do, it is said so here and in [EXTENSIONS.md](EXTENSIONS.md) rather than left to
be discovered — see [§12](#12-where-oxyde-is-behind).

### Compilation

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Expression evaluation | interpreted | interpreted | **compiled to bytecode once**, then a jump-table dispatch |
| Constant folding | ○ | ○ | ● |
| Errors reported with a line number | ◐ | ● | ● |
| A malformed `.cns` | aborts the process | degrades | degrades, and the diagnostic names the controller |

### Compatibility gates

Ikemen GO changes the meaning of a few triggers for characters that declare
`[Info] ikemenversion`, so old content keeps the old reading. Oxyde honours the
same gate for the same cases — `P2BodyDist Y` being the one that matters, which
327 files in this archive compare.

---

## 4. Gameplay systems

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Red life | ○ | ● | ● (opt-in) |
| Dizzy / stun | ○ | ● | ● (opt-in) |
| Guard break | ○ | ● | ● (opt-in) |
| Score | ○ | ● | ● (opt-in) |
| **Parry** | ○ | ○ | ● (opt-in) |
| Tag team | ○ | ● | ● |
| The third axis (`Pos Z`, `Depth`, `attack.depth`) | ○ | ● | ● |
| Juggle system | ● | ● | ● |
| Corner push | ● | ● | ● |
| Per-attack friction, `xaccel`, `keepstate`, `forcecrouch` | ○ | ● | ● |
| Damage / life balancing across a mixed roster | ○ | ○ | ● |
| Character processing order by *action* rather than index | ○ | ● | ● |
| SOCD resolution | ○ (both register) | ● | ● — and `0` restores MUGEN exactly |
| Button assist | ○ | ● | ● |

### The parry

**Neither of the other two engines has it.** Both can be made to look as though
they do — a `ReversalDef` catches an attack, and several characters here use one
— but a reversal is authored per move, by one character, against attributes it
lists in advance. A parry is a rule of the house: it applies to every attack in
the game, from every character, whether or not either author has heard of it.

Which is also why it is **off unless switched on**. A thousand characters
balanced against an engine with no parry are not balanced against one with it,
and the computer has to be taught to use it before it stops being free damage in
one direction. Every number is a setting; the whole system is one line in
`oxyde.cfg`. See [PARRY.md](PARRY.md).

### The four meters

All three of Ikemen GO's meters and Oxyde's four are computed from numbers every
character already has — the `damage` on a `HitDef`, the `[Data] life` constant —
which is the only way a rule can apply to a roster of a thousand files written
by people who never agreed on anything. The difference is what happens when one
runs out: Ikemen GO sends a dizzied fighter to state 6565300, defined in its own
`dizzy.zss`; Oxyde takes control away instead, because nothing in this archive
has a 6565300 to be sent to.

---

## 5. Presentation

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Renderer | DX7, fixed function | OpenGL / GLES / Vulkan | **software by default**, Vulkan/DX12/GL optional |
| Resolution | 320x240, stretched | any | any; art is drawn at the window's scale |
| Runs with no GPU at all | ○ | ○ | ● (the default path) |
| Upscaling filter | stretch | linear | nearest / **sharp-bilinear** / linear |
| CRT, scanline, LCD post-processing | ○ | ◐ (as shaders) | ● six built in |
| Camera zoom (`Zoom`, stage `AutoZoom`) | ○ | ● | ● |
| Camera control (`Camera` views) | ○ | ● | ● |
| `xshear`, draw windows, per-sprite transforms | ○ | ● | ● |
| `xangle` / `yangle` | ○ | ● | ● **true perspective divide** |
| `projection`, `focallength` | ○ | ● backgrounds only | ● backgrounds **and characters** |
| Background `angle` / `xshear` | ○ | ● | ● |
| GLSL shaders | ○ | ● | ◐ — **16 named built-in effects**, run on the CPU |
| 3D glTF backgrounds | ○ | ● | ● **lit, animated, shadow-mapped**; frustum fitted, not authored |
| Video backgrounds, in the game | ○ | ● VP8/VP9 as shipped | ● stages, screenpacks **and storyboards** |
| Video *decoding* | ○ | ● VP8/VP9/Opus/Vorbis | ● **AV1, MJPEG in Rust; VP8/VP9 through the system libvpx** (loaded at run time by soname, any `libvpx.so.6`–`.so.10`), tick-clocked |
| `PalFX hue`, `sinmul`, `invertblend` | ○ | ● | ● |
| Sprite remapping (`RemapSprite`, `[RemapPreset]`) | ○ | ● | ● |
| Collision-box overrides (`OverrideClsn`, `TransformClsn`) | ○ | ● | ● |
| Engine-drawn hyper flash | ○ | ○ | ● |
| Engine-drawn parry mark | ○ | ○ | ● |
| Procedural HUD when the pack has none | ○ | ◐ | ● |
| Combo counter | hits | hits, damage | hits, damage, **and what the damage was worth** |

### On the combo counter

All three count hits, and Ikemen GO adds the damage. The question neither
answers is the one anybody actually has at the end of a combo: *was that a
lot?* Characters in this archive run from 500 to 2000 life, so 300 damage is a
third of one fighter and a sixth of another.

So under the count, in subtext, Oxyde draws the damage, the share of a full
life bar that damage came to, and what the defender has left — the last of
those on a mini bar that echoes the one at the top of the screen, with the
chunk this combo just took drawn in the same red the life bar's own ghost
uses. The two percentages go unlabelled on purpose: red is what was taken and
matches the bite out of the bar, and the other is whatever colour that bar has
drained to, so "green 60%" and "red 8%" read before the digits do.

### On perspective

Oxyde places the four corners of an `xangle`/`yangle` sprite in space, projects
them, and builds the homography that maps the sprite's rectangle onto the
resulting quadrilateral — rather than squashing the axis being turned about,
which is exactly right only at 0 and 180 degrees, happens in *sprite* space, and
disagrees with any in-plane `angle` applied after it.
One inverse per sprite, and the inner loop is the same inverse-mapped read every
other path here uses — so rotation, shear and perspective are one function
rather than three, and the answer is exact rather than approximate.

`projection` and `focallength` are Ikemen's, spelled the same way. Oxyde accepts
them on `AngleDraw` as well as on backgrounds, which Ikemen does not: a fighter
tipping towards the camera is the same picture as a backdrop doing it, and there
is no reason one should be allowed to look right and the other not.

### On video backgrounds

Both engines play WebM. The difference is the **clock**. Ikemen advances a video
by elapsed real time; Oxyde addresses it by frame number derived from the tick
count, so a replay of a fight on a video stage shows the same backdrop frame it
showed live, and both sides of a netplay session agree. Seeking backwards is
then free, which is what a replay rewind is.

### On the shaders

Ikemen GO compiles a character's `.frag` on the GPU. Oxyde cannot, and says so.
What it does instead is resolve the *name* against a table of sixteen effects the
rasteriser knows how to do — greyscale, sepia, invert, tint, posterize, pixelate,
silhouette, outline, dissolve, hue, saturate, contrast, brightness, chroma shift,
scanlines, bloom — with the same sixteen `shaderparam.pN` floats.

The trade cuts both ways and is worth stating plainly. A character that ships its
own GLSL gets the nearest built-in or nothing, and `Shader` then answers `""` so
a `.cns` can tell. In exchange every one of these runs identically on a machine
with no GPU at all, cannot fail to compile, and is part of the deterministic
simulation rather than a property of the display — so a replay and a netplay peer
see the same picture. Eleven of the sixteen are palette transforms, which on
256-colour indexed art cost 256 operations per sprite and nothing per pixel.

---

## 6. Modes

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Arcade, Versus, Team Arcade/Versus/Co-op | ● | ● | ● |
| Survival, Survival Co-op | ● | ● | ● |
| Training | ● | ● | ● |
| Watch | ● | ● | ● |
| Boss Rush | ○ | ● | ○ |
| Time Attack, Score Challenge, 100 Kumite | ○ | ● (Lua mods) | ○ |
| Story Mode | ○ | ● | ● (storyboards, endings and declarative branching arcs — `.story`, `oxtool story`) |
| Bonus games (`bonus = 1` props) | ○ | ● | ● |
| **Bonus *stages*** (break the car, skeet, …) | ○ | ○ | ● — eight, procedural |
| Sparring (two-player practice, random re-roll) | ○ | ○ | ● |
| Team Rumble (3 v 3 from a bench of 8) | ○ | ◐ | ● |
| Team Tag | ○ | ● | ● |
| Roster Rumble (the whole roster, dealt out) | ○ | ○ | ● |
| Replays | ○ | ● (online only) | ● (**every** match, verified) |
| Move list | ○ | ● (authored file) | ● (**derived** from `.cmd`, plus the authored file) |
| Move and combo trials | ○ | ○ | ● (generated per character) |
| **Tournament** | ○ | ○ | ● |
| **Beat-'em-up** (waves, campaigns, lives, props, pickups) | ○ | ○ (depth-axis primitives only; up still jumps) | ● Knuckle Up, solo, local and online co-op |

The move list is the clearest example of the same feature reached from two
directions. Ikemen GO reads a `movelist.dat` the author wrote; exactly one
character in this archive of 1,051 ships one. Oxyde derives the list from every
character's own `.cmd` and `[Statedef -1]`, so all 1,051 have one — and where an
author *has* written a file, their names and their ordering win and the derived
list follows underneath.

---

## 7. Online

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Netplay at all | ○ | ● | ● — rounds, matches and rematches on one connection |
| A connection that outlives the match | ○ | ● | ● rematch / roster / quit, **both players vote** |
| In-game chat | ○ | ○ (not in its source; players use outside tools) | ● on one socket, never in the simulation |
| A player name | ○ | ● | ● one key, edited in the engine, kept in `oxyde.cfg` |
| Delay-based netcode | — | ● | — |
| Rollback netcode | — | ● (GGPO, on by default) | ● (own implementation) |
| Desync detection | — | ● | ● (checksum, every 30 frames) |
| LAN discovery | — | ○ (not in its source) | ● (beacon and browser) |
| Online team modes | — | ● | ◐ — four fighters, all driveable, but see below |
| A computer-driven seat online | — | ● | ◐ — the engine does it; no mode offers one, see below |

> **Online play's determinism rests on the round and the computer living inside
> `Match::step`.** The countdown, the verdict, the knockout clock, the win pose
> and the round score are the last statement of `step`, so a peer that is ahead
> rolls them back and re-simulates them like everything else; written instead at
> the app's displayed-frame cadence, hashed and never rolled back, they would
> kill a networked match at the round boundary. With them inside the step a
> networked match plays a whole two-round bout with the clock on — the round
> called at session frame 389, round two at 632, the match over at 1400, both
> peers agreeing on every frame while the one ahead re-simulates 1,434 of them —
> and offline is frame-for-frame unchanged (`oxtool regress` reports 1,051
> unchanged, 0 moved). Each frame's desync checksum is filed as it is simulated
> and compared against the frame it names, not a frame nine ticks later.
>
> **The connection outlives the match.** A *room* holds the session, the two
> names and the chat outside the bout, so the end of a match is a menu — rematch,
> roster, or quit, both players voting and the wider choice winning — and a
> rematch resumes the frozen session (frame 1401 to 1402) where a rebuilt one
> would start at zero.
>
> **What is still the app's:** the intro-to-fight `begin_fight()` write, safe
> only because control is withheld so every prediction is of empty input.
>
> **A computer-driven seat works online.** Its state is `Match::cpu`, decided at
> the top of `Match::step`, so it rides in every snapshot, both peers derive the
> same seed from the match seed, and nothing about it is sent — a hold timer, a
> cooldown, a half-performed motion and an RNG word advanced outside the step
> would ask a different question on a re-simulated frame than on the first pass.
> `ONLINE > TAG WITH A PARTNER` fields a team mate nobody is holding, and a
> tournament host can seat the house in a bye so that every bout of an odd field
> is fought. A spectator installs the seat the bout declared and re-derives the
> presses, which costs no bandwidth and leaves the relay two `u16`s a frame.
> Which seats are the computer's, and at what level, is folded into the setup
> hash — the one disagreement no input stream could ever reveal.
| Spectating | ○ | ○ | ● |
| **Tournament** | ○ | ○ | ● |
| **Playing without the content** | ○ | ○ | ● corrosion mode, **picture and sound** |

### The tournament

Eight people playing online, in MUGEN or in Ikemen GO, is eight people taking
turns to arrange private matches in a chat window and telling each other the
score. Neither engine has a bracket, and the reason is not that a bracket is
hard: **a tournament needs everybody who is not fighting to be watching the fight
that is**, and watching a match you are not in means either a video stream or a
deterministic simulation.

Oxyde has the second one. A whole match is a seed plus one number per player per
frame — that is what makes a replay two kilobytes — so a spectator is a peer that
receives both fighters' inputs and runs the same simulation. Two `u16`s a frame
is 240 bytes a second of *payload* — but the relay sends one datagram a frame,
and 28 of every 39 bytes on the wire are IPv4 and UDP header, so a spectator
really costs **18.7 kbit/s**. Six frames to a datagram brings it to 4.7, at a
tenth of a second of lag a spectator cannot perceive because they are watching
a recording rather than reacting to it. The *listing* is the expensive message in a
full room, not the relay: a thirty-two-entrant lobby republished every second is
322 kbit/s, seventeen times one spectator's stream.

```
  fighter A ──inputs──►  HOST  ──inputs A+B──► spectator
  fighter B ──inputs──►   │    ──inputs A+B──► spectator
                          └──── the other fighter's inputs back
```

Everything goes through the host — not because a mesh would be slower (it would
be faster) but because a mesh needs every entrant reachable from every other, and
in a group of eight exactly one person will forward a port. The host is also the
**authority**: it runs the same simulation and its copy decides who won, so a
fighter cannot claim a win and a fighter who disappears mid-bout forfeits.

Up to 32 entrants, single elimination with byes to the top seeds, a bracket every
machine derives from one shared seed rather than being sent, and a withdrawal
that forfeits rather than stalling. See [NETPLAY.md](NETPLAY.md).

---

### Corrosion mode

The other half of the same idea, from the other end. A tournament over rollback
requires every entrant to hold the same 6.6 GB of characters, byte for byte.
Corrosion mode removes that requirement by moving the engine instead of the
content: the host runs the game and streams the screen, the client sends a
controller and has **no archive at all**.

Neither other engine has anything like it, and the reason Oxyde can is
incidental rather than clever — the renderer already fills a plain `Framebuffer`
that nothing owns, so streaming it is a delta and a `deflate` rather than an
architecture.

Not a video codec, deliberately: an encoder buffers frames to compress them
better, and a fighting game is decided in three. A frame is cut into 16x16
tiles, only the changed tiles are sent, and on a measured fight that is under
20% of the screen and under 5% of the raw bytes — with *exact* pixels, which
matters on art made of hard edges.

The trade is one round trip of input latency, which rollback hides and this
cannot. Rollback remains the right answer when both ends have the content;
corrosion is for when they do not.

See [CORROSION.md](CORROSION.md).

---

## 8. Scripting and extension

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Modes written in a script | ○ | ● Lua | ● Lua |
| Computer opponent written in a script | ○ | ● Lua | ● Lua |
| Screen flow steerable from a script | ○ | ● Lua | ◐ hand-offs, not layout |
| HUD overlay from a script | ○ | ● Lua | ◐ text, rect, frame |
| ZSS state format | ○ | ● | ● |
| Own state language (FUSE) | ○ | ○ | ● |
| Language server for the state language | ○ | ○ | ● |
| CNS/ZSS → FUSE conversion, verified | ○ | ○ | ● |
| Linter for the state language | ○ | ○ | ● 10 rules |
| Graded benchmark for generated state code | ○ | ○ | ● |
| Common states redistributable with the engine | ○ Elecbyte's | ● MIT | ● its own |
| Screenpack *layout* scriptable | ○ | ● Lua | ● title menu re-described, chrome hidden or moved; other screens additive |
| Sandboxed: no filesystem, no process | n/a | ○ (full Lua stdlib) | ● |
| Runaway script stopped | n/a | ○ | ● instruction budget |
| A broken mod disables itself | n/a | ○ | ● latched off, engine continues |
| Hot reload while running | ○ | ◐ | ● |
| Engine source available | ○ | ● | ● |
| Save data from a `.cns` | ○ | ● (Go `gob`, written inline) | ● (engine store, host persists) |
| `[Shaders]` name mapping | ○ | ● | ● |

### State languages

All three engines read `.cns`. Ikemen GO adds ZSS, which brings real control
flow — `if`, `while`, `for`, functions and local variables — to a format that
had none. Oxyde reads ZSS too, in full: Ikemen's own fourteen `.zss` files
parse and lower with no errors, 140 states and 1,081 controllers, and its
`kfm_zss` fights.

### The common states, measured against each other

The one component of all three engines that is *content* rather than a binary,
and therefore the one that can be compared directly: swap `data/common1.*`
under one engine over one roster and change nothing else.

The archive's original 1,051 characters, `oxtool audit`, each file in turn — Elecbyte's
`common1.cns`, Ikemen GO's `common1.cns.zss`, Oxyde's `common1.fuse`:

| | Elecbyte | Ikemen GO | Oxyde |
|---|---:|---:|---:|
| deals damage | 96.8% | 93.5% | **97.7%** |
| blocks | 97.1% | 96.9% | 97.1% |
| gets up after a knockdown | 96.5% | 90.9% | 96.5% |
| completes the match | 99.0% | 95.7% | 99.0% |
| falls | **98.4%** | 96.7% | 98.1% |
| left frozen | 9 | 44 | 9 |
| went NaN | 2 | 2 | **1** |
| **mean function** | 91.8% | 91.3% | **91.8%** |

Oxyde's ties Elecbyte's and beats Ikemen GO's. It is also the only one of the
three that is the engine's own work: MUGEN's cannot be redistributed at all,
and Oxyde shipped Ikemen GO's under MIT until 0.28.0.

The full table, and why "takes damage in a free fight" is excluded from it,
are in [`metrics/engine-comparison.md`](../../metrics/engine-comparison.md).

Oxyde then adds **FUSE**, its own state language, documented in
[FUSE.md](FUSE.md). It keeps every trigger, controller and parameter name a
MUGEN author knows, and changes only the places the older syntax is ambiguous:
redirection is `p2.time` rather than `p2, time`, `==` compares while `=`
assigns, `x in [1, 5]` names the range test, and a local is a name with no
sigil. It also has things neither of the others does — named constants and
named states, local arrays, `stop`, `switch` arms over ranges — and refuses at
compile time what the others silently ignore.

The claim that the three languages are interchangeable is checked rather than
asserted. `oxtool fuse --verify` converts a file and compiles both sides:
Ikemen's ZSS produces **byte-identical bytecode** through FUSE, and the whole
archive — 1,051 of 1,051 characters, 2,094,037 controllers — converts with no
error the original did not already have.

`oxyde-lsp` is a language server for both, built on the compiler's own tables,
so an editor and the engine cannot disagree about what a name means. Alongside
it, a linter of ten rules catches what compiles and is still wrong — and across
all fourteen of Ikemen GO's own `.zss` files exactly two fire, both genuine.

### Modes and mods

Ikemen GO reached here first and still goes further: its screenpacks are Lua all
the way down, where Oxyde's are still `system.def`. The five mods in
`modules/external/mods/` — boss rush, ratio, score challenge, time challenge,
100 kumite — are exactly what that buys.

Oxyde now has the same four hooks Ikemen's mods mostly use — `modes`, `ai`,
`flow`, `hud` — and differs in **where the line is drawn and how hard it is
enforced**. No script runs inside `Match::step`, ever. A mod's `ai()` returns
the same sixteen bits a joystick does and is read at the same point in the
frame, so a scripted opponent is recorded in replays, sent over the wire and
rolled back like any other input, and **cannot desynchronise a netplay session
any more than a joystick can**.

That boundary is what makes the sandbox affordable, and the sandbox is the other
difference. Ikemen GO hands a mod the whole Lua standard library, including
`io` and `os`. Oxyde's interpreter does not contain them: `io`, `os`, `package`
and `debug` are not loaded, `load` is removed so bytecode cannot be injected, an
instruction budget stops `while true do end` inside a frame, a memory cap stops
a runaway allocation, and each mod gets its own environment so one cannot reach
another's globals. A mod that errors is switched off for the session and
reported **once** — a broken mod must not cost a frame's work every frame, and
must not bury the log.

"A script must not be able to provoke a panic" is met by construction:
nothing crosses the boundary but plain data — no Rust object is ever handed to
Lua, which is also what would let a mod run on a corrosion host and answer a
client that has none of the engine's types.

`Cargo.toml`'s `[profile.release]` sets no `panic` option, so release builds
unwind by default — **deliberately**: `Match::run_state_controllers` catches a panic in a
character's own state code so one broken character cannot take a round down
with it, and `catch_unwind` cannot catch an abort. §11's robustness promises
rest on that.

See [SCRIPTING.md](SCRIPTING.md).

On save files, Oxyde deliberately differs: `SaveFile` and `LoadFile` write into
an engine store that the *host* moves to and from disk between matches, rather
than doing file I/O inside a frame. A write inside `step()` is re-run by every
rollback and a read is a syscall whose result the checksum then depends on.
Same feature; a `.gob` written by Ikemen GO is not readable here.

---

## 9. Tooling and verification

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Content checker | ○ | ○ | ● `oxtool doctor` / `verify` |
| Whole-roster simulation | ○ | ○ | ● `oxtool soak` — 1,051 characters, 10 s each, 7 s wall |
| Per-character function score | ○ | ○ | ● `oxtool audit` |
| Netcode test against a lossy link | ○ | ○ | ● `oxtool netcheck` |
| Input-mashing stress test | ○ | ○ | ● `oxtool stress` |
| Balance report | ○ | ○ | ● `oxtool balance` |
| Scripted single-move trace | ○ | ○ | ● `oxtool simulate --inputs --trace` |
| Cornered-opponent reproduction | ○ | ○ | ● `oxtool simulate --corner` |
| Headless play | ○ | ◐ | ● `--headless --shot` |
| Windowed self-test driving real input | ○ | ○ | ● `--selftest` |
| Unit tests | ○ | ○ | ● ~2,900 |
| Randomtest / autolevel | ○ | ● | ◐ (`soak` and `audit` cover the same ground differently) |

```
$ oxtool soak . --ticks 600
simulated       2527 mirror matches
distinct states 28027
took 27.13s (917 character-seconds of gameplay per wall second)

$ oxtool netcheck . chars/ryu/ryu.def chars/kfm/kfm.def --latency 8 --loss 4
  CONVERGED: both peers agree (checksum 0x6297d51ac4881752)
```

Every character in the archive fights itself for ten seconds — simulated *and*
rendered — in seven seconds on twelve cores, with no panic, hang or unwind.

---

## 10. Performance and reach

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Minimum graphics | DirectX 7 | OpenGL 3.3 / Vulkan | **none** — a framebuffer |
| Runs headless | ○ | ◐ | ● |
| Runs over SSH / in CI | ○ | ○ | ● |
| Deterministic simulation | ◐ | ● | ● |
| Replay size | — | inputs | ~2 KB per match |
| Character load | one at a time | all at once | all at once, in parallel |
| Roster indexing (1,051 characters) | — | — | 178 ms |

The renderer being a CPU rasteriser is a deliberate choice, not a fallback. The
content is 320x240 palette-indexed art from 2002; a software blitter draws it at
hundreds of frames a second on twenty-year-old hardware, needs no driver, no
shader compilation and no GPU memory, and looks identical everywhere. The price
is paid in [§5](#5-presentation) and it is the price of the GLSL row.

---

## 11. Robustness

The archive this engine exists for is 1,051 characters by a thousand authors
across two decades, and a great many of them are broken in small ways.

| | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| A malformed `.cns` | aborts the process | reports, continues | reports, continues, names the controller |
| A missing sprite file | fails to load the character | fails | **repairs**: looks for a file that is there |
| A missing `stcommon` | character does nothing | — | supplies `common1.cns` |
| A `p2stateno` that does not exist | victim frozen for the round | — | the hit lands as an ordinary one |
| A state that never ends | fighter stuck for the round | — | deadlock rescue after a measured window |
| A fighter who leaves the world | gone | — | brought back after 45 ticks |
| A helper that spawns helpers for ever | hangs | bounded | bounded, and counted |
| An expression that overflows the stack | — | — | yields `0` rather than unwinding |

Every one of those rows is a bug that was reported from play against this
archive, traced to a root cause, and fixed. `CHANGELOG.md` names them.

---

## 12. Where Oxyde is behind

The list that makes the rest of this document worth reading.

**Behind Ikemen GO:**

* **A screenpack that is a Lua *program* on every screen.** `layout(screen)`
  now **re-describes** more than the title menu: on the title, select, versus
  and result screens a plan can hide or move the engine's named furniture and
  add described, data-bound `elements` — `text`, `sprite`, `rect`, `bar` and
  `anchor`, coloured from theme tokens and bound by name to engine state
  (`p1.life`, `p1.portrait`, `combo.hits`, `score`, `timer`, `cursor`…), all by
  returning *data describing the screen* rather than drawing one. The settings
  panels stay additive on purpose — a renamed setting is a setting nobody can
  look up — and the furniture-hide surface on select and result is narrower than
  on versus. What remains is the free-form part: Ikemen's motifs are a Lua
  *program* on every screen, where Oxyde's is a closed, described vocabulary the
  engine renders. See [MODDING.md](MODDING.md) and
  [SCREENPACK-SCRIPTING.md](SCREENPACK-SCRIPTING.md).
* **Shaders.** Present-time post-processing takes a *supplied* WGSL shader (and
  GLSL with the `glsl` feature), and a character may now also ship its **own
  per-sprite shader** as an opt-in cosmetic lane: a `.wgsl` (or a `.frag` under
  the feature) named in `[Shaders]`. It is **display only** — excluded from the
  simulation checksum, so it changes the picture and nothing a netplay peer or a
  replay can see — and it **degrades gracefully**, falling back to the nearest of
  the sixteen built-ins when a shader will not compile, the feature is off, or
  the machine has no GPU. The one honest limit left: it paints on the hardware
  fighter-draw path, which today is the 3D-model stage path; flat stages and the
  software renderer draw the built-in the simulation already chose. The sixteen
  built-ins remain the deterministic default. See [RENDERING.md](RENDERING.md).
* **The Lua-shipped extra modes** Ikemen ships in the box (boss rush, time
  attack, 100 kumite and the like). Oxyde now has a declarative **Story mode**
  with branching arcs (`.story`, validated by `oxtool story`) and the sandboxed
  hooks and `mod.toml` packaging to write the rest — see [MODDING.md](MODDING.md)
  — but ships fewer of them than Ikemen does today.

**Behind MUGEN:**

* **`SendToStage` has no specification anywhere.** Absent from Elecbyte's 1.1
  manual, absent from Ikemen GO, and used by none of the 2,527 characters here.
  It is implemented as the one operation its name can only mean and that the tag
  system needs — the inverse of `TagOut`, putting a fighter back on the stage —
  and that choice is a guess, stated as one.

**Partly there:**

* `buffer.shared` and `autogreater` are read and **warn that they do nothing**,
  naming what the engine does instead. Neither is implemented because neither
  is needed by this matcher, and zero characters in the archive — or in Ikemen
  GO's own content — use either.
* A script can **declare** the sequence of screens a mode is made of — see
  `screens` in [SCRIPTING.md](SCRIPTING.md) — re-describe the title menu, and
  add items to any screen's layout. What it cannot do is lay a screen out from
  nothing.
* **ZSS is read but not authored in.** All fourteen of Ikemen GO's own `.zss`
  files transpile to FUSE and lower to bytecode, so ZSS *content* runs here;
  what does not exist is ZSS as a language somebody writes a new character in,
  because FUSE is that language in this engine.
* Corrosion's audio is **lossy and bounded, not perfect**: IMA ADPCM at 4:1,
  and drift is corrected by dropping samples rather than resampling, so
  lip-sync is bounded by the jitter ceiling rather than zero. Stretching would
  trade one click for a permanent pitch error.

**On Ikemen and ffmpeg.** Ikemen's own `build/build.sh` configures its
auto-built ffmpeg with `--enable-decoder=libvpx_vp8,libvpx_vp9,opus,vorbis`
and its `BUILDING.md` calls the feature "background video: VP8/VP9/Opus/Vorbis
in WebM/Matroska"; anything beyond that is what a *user* gets by opting into a
system ffmpeg. So the shipped codec gap is VP8/VP9 — which Oxyde already has —
and matching "ffmpeg" would trade the single binary for a C toolchain, six
shared libraries and an LGPL relinking obligation to gain nothing. What is
worth adding is a royalty-free codec needing no C: AV1 through `rav1d`, pure
Rust and BSD-2-Clause, plus MJPEG through the JPEG decoder already here for
SFF v2 sprites.

**Already present**, and listed because the gaps above are only worth trusting
if the capabilities that are *not* gaps are named too:
**flag-set membership** — `HasFlag(set, flags)`, which answers Ikemen's
`HitDefVar(guardflag) = H` comparison and every future flag trigger with one
mechanism rather than nine one-off opcodes, and unlike Ikemen's leaves the mask
readable as a number; **`$N`**, a real "any press or release of any key"
rather than "nothing on the stick"; Lua
scripting, `.zip` and `.rar` content, SFF v2 and v2.01 PNG (verified against
Ikemen GO's own 1.1 characters), `localcoord`, true `xangle`/`yangle`
perspective, glTF backdrops, WebM video, a hardware renderer with six
post-processing shaders, MUGEN's team-mode screen, the tag system, hot
reloading, and **fighter depth-occlusion in glTF stages** (a fighter walking
deeper is drawn behind the scenery at the depth they stand, on the GPU
path — display-only and outside the checksum).

---

## 13. Scoreboard

Counting rows is a crude summary of a document whose point is the detail, so
read it as an index rather than a verdict.

| Area | MUGEN | Ikemen GO | Oxyde |
|---|---|---|---|
| Content compatibility | baseline | ● | ● **+ zip/rar, four-era census** |
| Engine language size | 89 + 127 | 158 + 267 | **160 + 281** |
| Gameplay systems | baseline | ● | ● **+ parry, + tag** |
| Presentation | ○ | ● **+ ZSS-era 3D depth** | ● **+ lit and animated 3D, video, perspective, post-processing** |
| Modes | 11 | ~22 | **16 playable (18 title rows, two of which are Options and Exit) + any number scripted, with their own screens + bonus stages + tournament** |
| Online | ○ | ● | ● **+ spectating + tournament + corrosion** |
| Scripting | ○ | ● **Lua + ZSS, unsandboxed** | ● **Lua, sandboxed** + re-describable menus + declared screens; ZSS read, not authored |
| Tooling | ○ | ◐ | ● 79 `oxtool` commands, **+ frame data and a training debugger in the game** |
| Runs without a GPU | ○ | ○ | ● (still the default) |
| Tests | ○ | ○ | ● ~2,900 |
| Robustness against broken content | ○ | ◐ | ● |

**Where each one wins.** MUGEN is the reference: it is what every file in this
archive was written against, and where the manual is ambiguous the answer is
whatever `Winmugen.exe` does. Ikemen GO still wins on *reach into the engine* —
ZSS, screenpacks that are Lua all the way down, and a fuller 3D character layer —
and its head start on mods is real. Oxyde wins on *the
archive and on what can be proved about it*: the largest language surface of the
three, the only parry, spectating, tournament and corrosion modes, the only one
that runs with no GPU, the only sandboxed script runtime, and the only one whose
behaviour against 1,051 characters across four MUGEN releases is measured rather
than asserted.

---

## Appendix: how this document is kept honest

* Every Ikemen GO claim comes from `Ikemen-GO.wiki/` or `Ikemen-GO/src/` in this
  repository, both read directly.
* Every MUGEN claim comes from `mugen_docs/elecbyte.com/` or from asking
  `Winmugen.exe` under Wine — see `metrics/winmugen-sweep.py`.
* Every Oxyde claim is either a number printed by `oxtool` or a test that fails
  when it stops being true.
* The name-level comparison in [§3](#3-the-engine-language) is regenerated
  mechanically: the wiki's headings are extracted and diffed against the
  engine's own tables. The diff is currently empty in one direction.

---

## Appendix B: FUSE completeness

A third state language is only an advantage if a character can actually be
*written* in it. `oxtool coverage` audits FUSE against real content on three
axes — controllers, triggers and the file sections real characters contain —
and fails on any gap used five or more times:

| axis | result |
|---|---|
| controllers | 160, all writable in FUSE |
| triggers | 281, all readable in FUSE |
| file sections | covered, down to a character's constants and remaps |

The third axis is the one that matters and the one most easily missed: a
language can read every trigger and write every controller and still have no
syntax for a character's constants, so the other two counts read "complete"
while real files do not round-trip. `constants { … }` and `remap { … }` close
that gap.

Ikemen GO's ZSS has no equivalent audit and no constants syntax of its own —
its `.zss` characters still keep constants in INI. MUGEN has one language and
no alternative. This is the one place where Oxyde's third language is a
measurable advantage rather than a preference.
