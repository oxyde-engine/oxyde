# Designing Knuckle Up stages

How to build a Knuckle Up level the beat-'em-up way: the player walks right
down a long street, gangs of enemies wait at points along it, a car is parked
halfway down to be smashed for a prize, and the boss waits at the far end.

**There is no Knuckle Up section in a stage file.** A Knuckle Up stage is an
ordinary MUGEN stage `.def`, the same kind every versus fight uses. Everything
that makes it a *level* (where each wave stands, where the car is parked, the
boss, the story card, the music, the stage's hazards) lives in the campaign
file, a `.knuckle` in `knuckleup/campaigns/`. The stage is the street; the campaign
says what happens on it. So one stage can serve two campaigns that use it
differently, and a stage built for Knuckle Up still works as a normal versus
stage.

**Where the files go.** A street made for Knuckle Up goes in the mode's own
folder, `knuckleup/stages/<name>/` (the `.def`, its `.sff`, a README); its
campaign in `knuckleup/campaigns/`, its music in `knuckleup/music/`, its intro
in `knuckleup/storyboards/` and its logic in `knuckleup/logic/`. Nothing in
`knuckleup/` is offered by another mode, so a three-screen street never comes
up in a versus rotation. A stage that *should* also be a versus stage stays in
the shared `stages/` and is listed in `select.def`; the campaign names it the
same way. The folder, and how a campaign's paths are looked up in it, is in
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#the-knuckleup-folder).

| You want to change… | Where it lives |
| --- | --- |
| how long the street is, what it looks like, the depth you can walk | the stage `.def` (this page, step 1) |
| where waves wait, which enemies, how tough, the boss, the order of stages | the campaign `.knuckle` (step 3; full key list in [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md)) |
| bonus challenges inside the level (the parked car) | the campaign's `prop` keys (step 4) |
| hazards, breakable floors, backgrounds that react | FUSE stage logic (step 5, [STAGE-LOGIC.md](STAGE-LOGIC.md)) |
| story cards, storyboards, music | the campaign (step 6) |

---

## What a level plays like

1. The stage card comes up (`STAGE 1`, the title, the story lines). A button
   skips it.
2. The first wave is waiting where the player starts.
3. When it is down, the **GO** prompt slides in at the right edge — under the
   corner plate, above head height, dimming if anyone jumps through it — an
   ember glow runs down that side of the screen, and the round clock holds. The player walks right; the camera follows.
   With `[KnuckleUp] cameralead` on (the default) it leads: with nothing left
   to fight it eases ahead of the hero — 7% of the gap a tick, never
   more than seven units — until they stand about a third of the way in from
   the left, so the street scrolls as soon as they walk on rather than when
   they reach the edge. It never runs back, and never so far that a co-op
   partner further back leaves the picture.
4. Reaching a wave's position (`at`) brings that wave in: from ahead, or from
   behind with `from = left`. The screen **locks** where it was met until the
   last of the wave falls.
5. Anything parked along the street (a prop) is just there to be found. It
   never locks the screen, and breaking it is optional.
6. The boss waits at its own position. It gets the big bar along the bottom,
   and the screen locks until it falls.
7. Beating the boss moves the run to the next stage, with the player's life
   carried over.

A campaign stage with no `at` anywhere plays the older way: each wave walks in
as soon as the last is cleared, on a stage of any width.

---

## Step 1: build the stage

Start from any MUGEN stage `.def`. These are the keys that matter for a
side-scroller:

| section | key | what it does here |
| --- | --- | --- |
| `[Camera]` | `boundleft`, `boundright` | **The length of the street.** The camera can travel between these; a fighter can walk about 160 units past each (MUGEN's half screen). A versus stage is usually ±150 to ±250; a street wants `boundright` in the thousands. |
| `[Camera]` | `startx`, `tension`, `verticalfollow` | As in any stage. |
| `[Camera]` | `beltaxis` | `horizontal` (the default) or `vertical` (also `v`, `northsouth`): a **vertical-belt** street scrolls up and down with the party's depth, and waves walk in from *up the street* (ahead in depth) rather than from the side of the picture. Local Knuckle Up only — online co-op's wave path stays horizontal. |
| `[PlayerInfo]` | `p1startx`, `p2startx` | Where the player and the first wave start. |
| `[PlayerInfo]` | `leftbound`, `rightbound` | The hard wall no fighter can pass. Make it **wider than the camera's reach** (below), or it cuts the street short. |
| `[PlayerInfo]` | `topbound`, `botbound` | **The depth strip** the player walks up and down in (up walks into the screen). For example `topbound = -40`, `botbound = 40`. Left equal (the MUGEN default), Knuckle Up opens a strip of its own. |
| `[Scaling]` | `depthtoscreen` | How far up the screen a unit of depth moves a fighter: deeper is higher and smaller. Knuckle Up uses `0.4` when a stage gives none. |
| `[StageInfo]` | `zoffset` | Where the floor line is, as in any stage. |
| `[Bound]` | `screenleft`, `screenright` | How close to the screen edge a fighter can stand. |
| `[Music]` | `bgmusic` | The stage's own track. A campaign can override it (step 6). |
| `[StageInfo]` | `states` | A FUSE file of hazards and breakables (step 5). |

**How far a fighter can walk:** from `max(leftbound, boundleft - 160) + 40` to
`min(rightbound, boundright + 160) - 40`. The shipped street has `boundright =
1400` and `rightbound = 2200`, so the far end is x = 1520. `oxtool campaign
--root` does this arithmetic for you and warns about anything placed beyond it.

**The art has to be as long as the street.** Either draw one wide backdrop, or
tile the layers you have with `tile = 1,0`. Tiling has one trap: for an
`anim` layer, `tilespacing` is the distance from one tile's **left edge to the
next** (so set it to the art's width), while for a `normal` layer it is the
**gap between** tiles. A layer whose `delta` is below 1 scrolls slower and
reads as further away, which is how a long street gets depth.

The shipped example `knuckleup/stages/knuckle_rust_street.def` is the "Rundown back
alley" stage made into a long street: the same art, `boundright = 1400`, a
depth strip, and every layer tiled (`tilespacing = 768,0` for the 768-pixel
wall, `736,0` for the 736-pixel floor strips). Art drawn to repeat tiles
without seams; borrowed art shows where it repeats.

### Using the stage

A campaign names its stage either by a name from `select.def` (the same
match `oxtool shot --stage` uses) or **by path**: `stage =
stages/knuckle_rust_street.def`. A path is looked for in `knuckleup/stages/`
first — a leading `stages/` is read as "the stage folder", so that line finds
`knuckleup/stages/knuckle_rust_street.def` — then beside the campaign, then in
the shared `stages/`. `stage = 07_old_town` finds
`knuckleup/stages/07_old_town/07_old_town.def`. A stage named by path does not
have to be in `select.def`, and one in `knuckleup/stages/` never appears in any
other mode's stage list or rotation.

The stage's own paths (`spr`, `bgmusic`) can stay as they were written: a
sprite file is found beside the `.def` when the path it names is not there,
and a stage in `knuckleup/` hears `knuckleup/music/` before `sound/`.

---

## Step 2: decide where things happen

Positions are **stage x coordinates**, the same units as `boundleft` and
`p1startx`: 0 is the middle of the original stage, and positive is to the
right. A good first plan for a street of `boundright = 1400`:

| x | what |
| --- | --- |
| -70 | the player starts; wave 1 is waiting |
| 450 | wave 2 |
| 700 | a parked car |
| 900 | wave 3, coming from behind |
| 1350 | the boss arena |

Leave each fight room to happen: about a screen (300 to 450 units) between
positions keeps one locked screen from overlapping the next.

---

## Step 3: write the campaign

The placement keys, added to an ordinary `[Stage <name>]` section:

| key | example | meaning |
| --- | --- | --- |
| `waveN.at` | `wave2.at = 450` | Wave N waits until the leading player reaches x = 450, then walks in and the screen locks. Wave 1 always opens the stage, so `wave1.at` is ignored (and `oxtool campaign` says so). |
| `waveN.from` | `wave3.from = left` | Where it walks in from: `right` (ahead, the default) or `left` (behind the player). |
| `propN` | `prop1 = car2, at 700, random` | A prop parked at x = 700 from the start of the stage. The older form, `prop1 = car2, 2, random`, parks it in front of the player when wave 2 walks in. |
| `boss.at` | `boss.at = 1350` | The boss arena. |
| `boss.from` | `boss.from = left` | As for a wave. |
| `boss.music` | `boss.music = boss.mp3` | A track that takes over when the boss walks in. |

The rest of the stage section (`waveN` with its enemies and their life,
`boss`, `pickupN`, `title`, `storyN`, `life`) is unchanged; see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md).

Rules worth knowing:

- A position past where a fighter can walk fires at the far edge instead of
  never, so a level cannot strand the player.
- A position *behind* the last one fires as soon as the last wave is down.
- Placed and unplaced waves can be mixed. An unplaced wave follows the one
  before it straight away.
- While the player walks to the next position, the round clock holds.

---

## Step 4: bonus challenges in the level

A **prop** is a bonus-game character parked in the street: the Mercedes from
the car-breaking bonus stage, standing there while enemies are fought around
it. Breaking it is optional. It never locks the screen and nobody waits for
it, and a full break pays 3,000 points plus its `reward`:

| reward | effect |
| --- | --- |
| `random` | one of the four below, drawn from the run's seed |
| `oneup` | one extra life |
| `health:N` | N percent of each player's life back |
| `power:N` | N percent of each player's super gauge |
| `score:N` | N points |

**Not every bonus game can be a prop.** On its own bonus stage a bonus game is
free to be anything: one draws its whole backdrop, one builds the car out of
helpers around an invisible root parked off to the side, one zeroes its own
life the moment it starts. In a street those read wrong. Check them with:

```
$ oxtool props .
1 of 7 bonus props can be parked in a Knuckle Up stage

  no        bonus2           chars/bonus2/bonus2.def
              - wanders: its root moved 200 units from where it was put
              - draws nothing itself: what shows is helpers around an invisible root
  no        FF2BreakCar      chars/FF2BreakCar/FF2BreakCar.def
              - wanders: its root moved 520 units from where it was put
  usable    car2             chars/car2/car2.def
  …
```

On the development archive the Mercedes (`car2`) is the one that works. To
make your own, build a character that:

- is listed in `select.def` with `bonus = 1`, or lives in
  `knuckleup/props/<name>/<name>.def` (either keeps it out of the roster);
- stands where it is put and does not move itself;
- draws itself with its own root, not only with helpers, and no sprite as wide
  as a screen;
- goes down and **stays** down when its life reaches zero.

`oxtool campaign <file> --root .` measures every prop a campaign names the same
way and warns about any that cannot stand in a street; `oxtool props .` measures
the `bonus = 1` characters and everything in `knuckleup/props/`.

### Writing a prop: lessons from the OXYDE prop pack

The *Knuckle Up Master Pack* ships ten props written as MUGEN characters
(crate, locker, vending machine, cash terminal, generator, barrel, medical
station, dumpster, forklift, capsule). They are built into
`knuckleup/props/` by the prop pipeline, and parked by
`oxyde_props_showcase.knuckle` (all ten in a row) and
`oxyde_long_run_animated.knuckle` (two a street). What a prop needs:

- **A `[Statedef -2]` header.** A controller belongs to the `[Statedef]`
  above it; its `[State -2, ...]` label is only a name. Written after
  `[Statedef 0]` with no header, the anchoring and the return from a hit ran
  only while the prop stood, so the first hit dropped it into the common
  get-hit states and it lay there with life left. `oxtool props` does not see
  this (it breaks a prop by setting its life, not by hitting it); a versus
  match against it does: `oxyde --headless --p1 kfm --p2 <prop.def> --ai 8`.
- **Its own 5150, reached from -2 when `!Alive`.** Otherwise a knockout plays
  the common fall states, which ask for animations (5000-5170) a prop does
  not have.
- **No throws** (`NotHitBy` `SCA, AT`): a throw plays the thrower's own
  animations on the victim.
- **Facing.** The mode parks a prop facing left, which mirrors any lettering
  on it; a prop that must read the right way round `Turn`s in -2.
- **Size.** Art drawn at twice a fighter's scale is halved with
  `localcoord = 640,480` in `[Info]`, which scales sprites and boxes together
  and draws the art sharper.
- **Once, by a flag.** A broken prop's state clock does not run, so `Time = 0`
  stays true in 5150; an `Explod` triggered on it is lit again every tick.
  Use a variable that the state sets after firing.

### A prop that hurts the people around it

A prop's own attacks never land (`Player::prop`), so an exploding barrel cannot
be a `HitDef`. It can be stage logic: `knuckleup/logic/oxyde_props.fuse`
(name it with `logic =` on the campaign stage) remembers every prop it sees
standing that carries a tag (`var(59)` = 7001 for the barrel, 7002 for the
generator, with `fvar(39)` = -731.5 as a check), and the tick one can no
longer be seen — a stage's redirects reach only the living — it puts a
`StageHazard` where the prop stood. The blast is neutral (the hero who broke it
takes it too), takes life only (nobody is knocked down or reels), and is
`kill: 0`, so it never knocks anyone out by itself.

---

## Step 5: hazards and breakables (FUSE stage logic)

A stage can run a state machine written in FUSE: spikes that hurt, a floor
that gives way, a background that flashes when a super lands. It runs inside
the simulation, so it is deterministic and works in co-op and replays. There
are two ways to attach it:

- **On the stage**, for every fight on it: `[StageInfo] states = hazard.fuse`.
- **In the campaign**, for this campaign's use of the stage only: `logic =
  alley.fuse` in the `[Stage <name>]` section, found in `knuckleup/logic/`,
  beside the campaign, or in `data/campaigns/`. A campaign's `logic` replaces
  the stage's own.

The controllers and triggers a stage can use are in
[STAGE-LOGIC.md](STAGE-LOGIC.md).

---

## Step 6: story, storyboards and music

| key (in `[Stage <name>]`) | what it does |
| --- | --- |
| `title`, `story1`, `story2`… | The card shown before the stage. |
| `intro = alley.def` | A MUGEN storyboard played before the stage, after the versus screen for the first stage. Found in `knuckleup/storyboards/`, then beside the campaign, then in `data/campaigns/` (`../kfm/intro.def` from there reaches the KFM motif's). Its sprites are read beside it. Any button skips it, as with every storyboard. |
| `music = alley.mp3` | The stage's track, replacing the stage file's own `bgmusic`. Found in `knuckleup/music/` (`sound/alley.mp3` there too), beside the campaign, then `data/campaigns/`, the archive and `sound/`. |
| `boss.music = boss.mp3` | Takes over when the boss walks in. |

---

## Step 7: check it and play it

```
oxtool campaign knuckleup/campaigns/my_city.knuckle --root .
oxtool campaign --root .            # every campaign installed
```

prints every stage, wave, prop and placement, where each path it names was
found (`knuckleup`, `beside campaign`, `legacy`), then:

- **notes**: things that will play but are probably not what you meant (a
  `wave1.at`, a position behind the last one or past the end of the street,
  a stage that is not installed, a prop that cannot stand in a street, an
  enemy or boss the roster does not have or that a display name sends to
  another character, a `music` or `boss.music` file that is not there);
- **faults**: things that make the campaign unplayable, such as a stage with
  nothing to fight, an unknown pickup or reward, or an unknown `from`.

To play it, choose **Knuckle Up** on the title menu. With more than one
campaign installed (`knuckleup/campaigns/`, then the legacy `data/campaigns/`),
a list comes up, showing each campaign's name and its stages; with only one,
it just plays. `OXYDE_KNUCKLE_CAMPAIGN=<path, file name or name>` picks one
without the menu.

---

## A complete example

The stage, abbreviated from `stages/knuckle_rust_street.def`:

```ini
[Info]
name = "Rust Street"

[Camera]
startx = 0
boundleft = -224
boundright = 1400        ; the street: a fighter can walk to about x = 1520
tension = 50

[PlayerInfo]
p1startx = -70
p2startx = 70
leftbound  = -1000
rightbound =  2200       ; wider than the camera's reach
topbound = -40           ; the depth strip
botbound =  40

[Scaling]
depthtoscreen = 0.4

[StageInfo]
zoffset = 215

[BGdef]
spr = stages/bckalley.sff

[BG 0]
type = anim
actionno = 0
start = 0,240
delta = 1,1
tile = 1,0
tilespacing = 768,0      ; anim layer: left edge to left edge = the art's width
```

The campaign's first stage, from `knuckleup/campaigns/rust_city.knuckle`:

```ini
[Stage rust_alley]
title  = Rust Street
story1 = The Rust gang runs the old quarter now.
stage  = stages/knuckle_rust_street.def
wave1    = 2, aba*0.35, abubo*0.35        ; waiting at the start
wave2    = 2, Acid*0.4, aba*0.35
wave2.at = 450
wave3    = 2, abubo*0.35, Acid*0.4
wave3.at = 900
wave3.from = left                          ; from behind
prop1    = car2, at 700, random            ; smash it for a prize
pickup1  = health, 2, 250
boss     = adon, 2.0
boss.at  = 1350
```

---

## Art specification: making a street look right

Everything in this section was measured on the ten stages of *OXYDE: Long
Run* (`knuckleup/campaigns/oxyde_long_run.knuckle`, generated by
the Knuckle Up prop pipeline), rendered headlessly at
960x720 and 1280x720. The generator is the worked example: every rule below
is a line of it.

### The screen, in world units

The engine's world is MUGEN's: 240 units tall. How wide the view is depends
on the **playfield** (`PLAYFIELD` in the options, `auto` follows the
configured window), not on the window:

| playfield | view (world units) | in a 960x720 window | in a 1280x720 window |
| --- | --- | --- | --- |
| 4:3 | 320 x 240 | 1:1, nothing extra | letterboxed |
| 16:9 | 426.7 x 240 | 426.7 x 320: **80 extra units above y = 0** | 1:1 |

So draw for the wide view and the tall one at once:

- **Cover 427 units across** (1280 px at 1280x720). Whatever the aspect, the
  engine narrows the camera's travel by the overscan, so what can be seen is
  always `boundleft - 160` to `boundright + 160`.
- **Extend the sky (or ceiling) 80 units above y = 0** (240 px). A 16:9
  playfield in a 4:3 window shows it, and without art there the top of the
  screen is gutter fill.

### Draw at 1280x720 and say so

    [Info]
    localcoord = 1280,720

Every number in the `.def` is then in those units (three to a world unit) and
the engine converts them all, so one art pixel is one screen pixel in a
720-line window: sharp at 960x720 and at 1280x720. **A campaign's positions
(`waveN.at`, `prop … at`, `boss.at`) are in the stage's own coordinates too**:
on such a stage `boss.at = 7050` is world x = 2350. `oxtool campaign --root`
checks them in the same units.

### The vertical layout

A fighter's feet are at `y = zoffset - z * depthtoscreen`, with z running
from `topbound` (nearest, lowest on the screen) to `botbound` (deepest,
highest). Work from the bottom up (world units; multiply by 3 for the file):

| what | rule | example: depth 48 |
| --- | --- | --- |
| nearest feet | y = 228: a shadow's worth clear of the bottom edge | 228 (684 px) |
| `zoffset` | 228 - depth x 0.4 | 208.8 (626 px) |
| deepest feet | zoffset - depth x 0.4 | 189.6 (569 px) |
| floor's back edge | 10 units behind the deepest row | 179.6 (539 px) |
| far layer | its bottom tucked 8-13 units under that edge | |
| sky / ceiling | from y = -80 down past the far layer's top | |

Keep `depthtoscreen` at 0.4 (Knuckle Up's default) and change `zoffset` with
the depth instead. A `zoffset` left at 215 with a depth of 62 puts the
nearest row's feet at y = 240: on the bottom edge, shadow off the screen.

### The layers

| layer | delta | what goes in it | size in the pack |
| --- | --- | --- | --- |
| sky or ceiling | 0.03-0.06 outdoors, 0.25-0.35 indoors | gradient, clouds, far skyline; a vault or upper wall indoors | 2048-2560 x (edge + 240), tiled |
| far | computed (0.29-0.39 here) | one wide painted panorama | the concept strip at 3x: ~4300 x 240-350 |
| mid | 0.55-0.85 | structure that frames the street: cranes, a railway deck, arches, trees, trusses | 2048-2560 wide, transparent, tiled |
| floor | 1 | the ground **and** whatever stands on its back edge: rail, fence, lamp posts, kerb | 2560-3072 x (720 - top), tiled |
| set pieces | 1 | four OXYDE landmarks, each `tile = 0` | 240-900 px wide |
| foreground | 1.3-1.35, `layerno = 1` | cables or chains at the top, one thin pillar every 4,000-5,000 px | 4200-5200 x 720, tiled |
| weather | 1, `layerno = 1` | rain, embers, dust, leaves | 1280 x 720, tiled both ways |

**Only delta 1 can touch the floor.** Anything that meets the ground at
another delta slides against it as the camera moves. So the floor layer
carries the rail, kerb and lamp posts that stand on it, and a slower layer's
base is hidden behind them.

**A panorama that never repeats.** A single image `W` px wide covers the
whole street at 16:9 when

    delta   = (W/3 - 426.7 - 20) / ((boundright - 53.3) - (boundleft + 53.3))
    start.x = ((boundleft + 53.3) * delta - 213.3) * 3 - 30        (axis at its top-left)

(world units for the bounds; `start.x` in the file's units). That is how the
pack's 1,432-pixel concept strips, enlarged 3x, span streets of 2,400-3,240
units with no seam. Give it `tile = 1,0` anyway, so a wider screen shows a
repeat rather than black.

### Tiling, and the tilespacing trap

- `tile = 1,0` repeats a layer sideways. For a **normal** layer `tilespacing`
  is the *gap* between copies (0 for art that joins itself); for an **anim**
  layer it is left edge to left edge (the frame width).
- Art has to join itself: anything that crosses the right edge must come back
  at the left. The generator draws every tile three times, shifted by one
  tile width each way, and keeps the middle. Two ways that still seam, both
  found in this pack: a regular pattern whose step does not divide the tile
  (hazard stripes every 28 px on a 3072 tile; use 32), and a full-width
  overlay painted *after* the shapes it should darken.
- Weather tiles **both** ways (`tile = 1,1`, `tilespacing = 1280,720`) and
  moves with `velocity`; its three frames only make it shimmer in place.
  Drawing the fall into the frames makes every drop jump a third of a
  screen at once.

### What the engine can draw: 256 colours, on or off

Every sprite is drawn through a palette whose colours are either there or not.
A 32-bit PNG is quantised on load and its alpha becomes on/off: a soft glow
painted into a transparent area comes out as a solid disc, rain at 15% as
opaque white streaks. So:

- Base sprites: pixels at least half opaque are drawn, the rest are not.
  Dither a dark shadow you need to keep.
- Light (neon halos, lamp cones, rain, mist, an alarm beacon): its own layer
  drawn with `trans = add`, at the same position, delta and tiling. Black adds
  nothing, so it needs no transparency at all.
- Quantise each sprite to 255 colours yourself, with dithering, before it
  goes in: the engine's own median cut bands a wide gradient.
- Fade nothing into transparency. The far strip's top is blended into the
  colour of the sky behind it instead.

### Animation loops over a street: what each row costs

*OXYDE: Long Run (Animated)* (`oxyde_long_run_animated.knuckle`, built by
the animation pipeline) lays the loops of the animated upgrade
over the ten streets as a second stage set, so the originals and the tapes
recorded on them stay as they were. What it measured:

- The software blitter passes over **every row of a sprite**, lit or not, and
  tests each pixel. A 3072-wide loop as tall as the screen costs about a
  millisecond at 1280x720 even when it is nearly all transparent; the first
  cut of four loops added 5.7 ms to Rust City Streets.
- So a sparse loop is cut to the rows it lights and **split into one `[BG]`
  element per lit band** (gaps of more than 24 rows), and light under 4/255 is
  cut first. Lines of distant lights then cost their lines, not the sky
  between them.
- Additive light over a wide area costs on every pixel: a flash that washes
  the whole sky added 3 ms a frame. Keep the bright part (the bolt) and let
  the stage's own art carry the rest.
- A loop goes in at its own depth: after the last layer that scrolls no faster
  than it, so far lights sit behind the middle structure and set pieces.
- Loops that draw an *object* (a monitor frame, a banner, a ring of lights) at
  a fixed spot of their tile float in mid-air over generated art that has no
  such object there; look at each on the street before keeping it.

The result: every animated street draws in under 11.5 ms at 1280x720, between
0.3 and 2.1 ms over its original.

### Set pieces: landmarks against repetition

A tile of 2048-3072 px repeats every 680-1020 units: two or three screens.
Four unique pieces per street break that up: one on the first screen (at
3.5% of the length, so it is there when the stage opens), then at 38% and 66%,
and the last in the boss arena, 120 units short of `boss.at` (where the locked
camera centred on the tension camera: the hero met `boss.at` near the right of
the view; with CAMERA LEAD the view runs ahead of the hero and locks about 75
units past `boss.at` at 16:9, which still has the piece on screen), so the fight with the
boss has its own backdrop. Each stands on the floor's back edge (its axis is
the bottom of its solid part, not of its glow) and is drawn behind the
fighters. Something beyond the edge, such as a ship moored past the quay rail,
goes before the floor layer so the rail stays in front of it.

### The street's length and pacing

A street of 4,700-6,800 units is 15-21 screens: a walk between fights. This
pack uses 2,400-3,240 (7.5-10 screens at 4:3, 5.6-7.6 at 16:9) for eight
waves, a parked car and a boss, with positions:

- about 290-370 units apart: a 4:3 screen each, so one locked fight does
  not overlap the next;
- the first placed wave a screen from the start;
- the car near halfway, between waves;
- the boss 200 units or more short of the far walk, so its arena is not
  pressed against the wall.

### Colour and contrast

- Keep the band the fighters stand in **calm**: mid-dark, low-contrast,
  low-frequency floor. Detail and saturation belong up the screen and in
  the far layer.
- Nothing on the floor should look like a pickup. Health and weapon pickups
  are a green and a yellow cross; a glowing green puddle under the feet reads
  as one.
- Put the brightest thing in the scene behind the fighters' heads, not
  their feet: a furnace mouth or a lit shutter at waist height silhouettes
  everyone in front of it.
- Light pools on the floor belong to a lamp in the same layer, so they stay
  under it as the camera moves.
- The OXYDE accent is `#FF7A1A` on near-black; the hex emblem is drawn by
  `kutools.hex_logo`.

### Building the sprite file

`oxtool sprmake <stage>-sff.def -o <stage>.sff` takes indexed PNGs and writes
an SFF v2 with a palette per sprite; it reads every sprite back and says so.
The pack's stages are 3-12.5 MB each. Sprite groups follow the pack's contract: `0,n`
the tiled layers, `1,0..3` the set pieces, `2,n` the weather, `3,n` the
additive light.

### Checklist

1. The prop pipeline's per-tile check reports any tile whose
   wrap seam is worse than its ordinary columns.
2. `oxtool sprmake`: every sprite decodes at its size and axis.
3. `oxtool campaign knuckleup/campaigns/<file>.knuckle --root <game-root>`: no
   faults, and no notes. With `--root` it checks that every stage is
   installed, every position is somewhere a fighter can walk, every prop can
   stand in a street, **every enemy and boss name resolves** (and to the folder
   you meant: a display name can capture a lookup, so `slash` is `eslash`),
   and every `music` and `boss.music` file exists.
4. Render it at both playfields, from a scratch root, with a one-stage
   campaign:
   `OXYDE_KNUCKLE_CAMPAIGN=<file> oxyde --root <root> --config <cfg> --headless --mode knuckleup --p1 <hero> --frames 420 --shot out.png`,
   once with a config of `[Video] width = 960, height = 720` and once with
   1280x720. Look for feet on the floor across the depth strip, no gaps at
   either end, no seams, the foreground clear of the fighters.
5. Play it through headlessly with `OXYDE_KNUCKLE_TRACE=1` and the grunts'
   `life` turned right down: every wave arrives at its position, the camera
   follows, the boss walks in at `boss.at` and the run moves on.

---

## A second stage set: the Animated Stages Set 02 belt streets

*OXYDE: Set 02 Tour* (`knuckleup/campaigns/oxyde_set02_tour.knuckle`) adds five
more belt streets, built by the Set 02 prop pipeline from a different
kind of source than the Long Run ten. Where those draw everything and borrow only
the concept-board strip for the far layer, these are **composed from a
production pack's own art**: each pack (`Oxyde_Animated_Stages_Set_02/<Stage>/`)
ships a painted MAIN STAGE board and transparent prop and VFX cut-outs
(cars, bus stops, cranes, forklifts, steam vents, sparks, molten pours, buoys).

- **Rush Hour Strip** — a rain-slick industrial traffic strip.
- **Rust Market Alley** — a black-market bazaar of stalls and lanterns.
- **Foundry Mile** — a molten steel foundry, embers drifting.
- **Floodline Metro** — a flooded transit platform, live cables.
- **Seawall Freight Docks** — a storm-lashed container yard, a lit buoy.

How the pack art becomes a stage (`packstage.py`, `set02.py`):

- The pack's **MAIN STAGE painting** is cropped above its own near road and used
  as the one non-repeating far panorama (`pieces.far_layer`), feathered into a
  themed sky. Because that panorama is opaque and tiled, it and the floor cover
  the screen, so **no separate sky layer is drawn** — the sky is built only as the
  colour the panorama's top feathers into. That alone saves a full-screen pass.
- The **floor** is drawn by the generator (so it tiles cleanly and stays calm
  under the fighters), themed per pack, with the back wall, kerb, reflections and
  lamp light a belt needs.
- Four of the pack's **prop cut-outs** stand on the floor's back edge as set
  pieces, resampled with the premultiplied-Lanczos filter of
  the bonus-pack pipeline and never enlarged past the source.
- The pack's **light-emitting cut-outs** (steam, a blinking beacon, a molten
  pour, cable sparks, wave spray) are drawn as additive loops (`trans = add`,
  black the transparency key), built after the engine split exactly as
  `animated.py` does, and kept small and local to stay in budget.
- The **foreground** is a thin band of cables across the top only (no full-height
  element, which would cost a full-screen pass for a mostly-empty sprite), and
  rain or embers tile over everything on `layerno 1`.

They install the ordinary way — `knuckleup/stages/<slug>/` and the campaign in
`knuckleup/campaigns/` — and are checked and rendered with the same tools
(`oxtool campaign --root .`, the headless render with `OXYDE_RENDER_EVERY=1`).
Each draws comfortably under ~12 ms a frame at 1280x720 in a full Knuckle Up
fight. The shipped Long Run campaigns are untouched, so their replays still match.

---

## What is not there yet

- **Online co-op** plays its waves inside the simulation and does not have
  lives, props or placement yet; all of this is local play, and its wave path
  stays horizontal even on a vertical-belt stage.
- A campaign places waves by x only — it cannot author a wave's depth.
