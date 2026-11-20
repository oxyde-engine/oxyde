# Configuration

Most settings can be changed from **OPTIONS** on the title menu, which writes
them back to `oxyde.cfg`. Everything is also editable by hand: the file is the
same INI dialect as `mugen.cfg`, and the screen and the file always agree
because both read and write the same fields.

```bash
oxyde --write-config      # a commented default, for editing by hand
```

Everything has a working default: a missing or corrupt config never stops the
game from starting.

Settings are layered, so an existing MUGEN installation keeps its own
behaviour and anything you set here wins:

```
built-in defaults  ->  data/mugen.cfg  ->  oxyde.cfg  ->  command line
```

`data/mugen.cfg` supplies difficulty, life scale, round time, game speed,
volume, the balance rules, the engine limits and both players' key bindings.
See [CUSTOMISATION.md](CUSTOMISATION.md) for exactly which keys are read.

## Video

```ini
[Video]
width  = 960
height = 720
fullscreen = 0
vsync = 1
; 0 = fit the window; otherwise a fixed integer zoom of the 320x240 stage.
scale = 0
; software = CPU rasteriser (works on any machine, no GPU driver needed)
; gpu      = the same image, scaled by the GPU
; auto     = gpu if it initialises, else software
renderer = software
; Drop rendered frames rather than slowing the game down on weak hardware.
frameskip = 1
spritecachemb = 192
; AI-upscaled sprite sidecars (ky.sff -> ky.hd2.sff). off | hd | uhd.
; Presentational only: geometry and the match checksum are unchanged.
sprite_hd = off
```

`scale = 0` fits the 320x240 stage to the window on whichever axis is tighter.
Setting an explicit integer (2, 3, 4) gives exact pixel doubling, which is
sharper on a display whose resolution is not a clean multiple.

`spritecachemb` bounds decoded sprite memory. Sprites are cached palette-indexed
(one byte per pixel), so 192 MB holds a great many characters; lower it to 32
on a machine with under 2 GB of RAM.

### The renderer, and the shader that goes with it

`renderer = software` is the default: the CPU rasteriser is the authoritative
path, the one every test asserts against, and the one that runs on a machine
whose GPU driver is a rumour. `gpu` asks for hardware and *says so* if it cannot
be had; `auto` tries and falls back in silence. A software Vulkan implementation
is declined rather than used — llvmpipe presenting a scaled frame is slower than
the `memcpy` it would be replacing.

```ini
[Game]
; Post-processing, on the hardware path only.
; none | nearest | sharp | smooth | scanlines | crt | lcd
shader = none
shaderstrength = 1.0
```

The default is `none`: the CPU rasteriser already draws at the window's native
resolution, so there is nothing to upscale. `sharp` is sharp-bilinear: hard
edges without the shimmer nearest-neighbour gives at a non-integer scale, and
without the mush plain bilinear gives — a good choice for 320x240 art on a
screen that is not a whole multiple of it. `oxtool gpu . --out shots/` writes a
picture of each one.

See [RENDERING.md](RENDERING.md).

## Game

```ini
[Game]
speed = 60
; Seconds per round; 0 removes the timer entirely.
roundtime = 99
; The longest a fighter's own entrance may hold the round up, in frames.
introtime = 300
; Rounds a player must win to take the match.
rounds = 2
debugboxes = 0
; Play characters from the files they had before conversion to FUSE.
originalfiles = 0
; CPU strength, 1-8. Overrides [Options] Difficulty in mugen.cfg.
difficulty = 4
; 1 = build the roster from data/select.def, honouring its order, blank slots,
;     per-character stages and arcade.maxmatches.
; 0 = list every folder under chars/ instead.
useselectdef = 1
; Columns on the select grid. 0 follows the screenpack's
; [Select Info] columns, then falls back to 12. Rows follow the window height.
selectcolumns = 0
; Offer the stage-select screen after the character select. Off (0) plays each
; match on the stage select.def paired with the character. On by default.
stageselect = 1
; Every character's life bar, as a percentage. Read from mugen.cfg [Options]
; Life when there is one.
life = 100
; Full super bars every character gets, whatever their own [Data] power
; says. 0 leaves each character as their author wrote them, which is MUGEN.
powerbars = 0
; Frames a completed command stays live for, as a floor under every
; character's own command.buffer.time. 1 is exactly MUGEN.
inputbuffer = 4
; Hand side two to the computer in Versus and Team Versus, for playing alone.
; MUGEN's Versus is human against human, so this is off by default.
versuscpup2 = 0
; Opponents in an arcade ladder, unless select.def sets its own.
arcadeopponents = 8
; Team Rumble: fighters a side on the stage at once (2-4), and how many each
; side brings, bench included (2-16). The team menu opens on the second.
teamrumbleonscreen = 3
teamrumblesize = 8
; Splash background art (PNG or JPEG). Looked for in the working directory,
; then in the game data root. Falls back to a built-in backdrop.
splash = splash.jpg
; Minimum frames the splash stays up; 0 skips it.
splashframes = 90
; The screenpack. Empty follows mugen.cfg's own [Options] motif, then
; data/system.def.
motif =
; The engine's own super effect on any screen freeze long enough to be a
; super, including one held with a plain Pause: off, auto or always. 0 and 1,
; from before it had three settings, still read as off and auto.
superfx = auto
; Grow a screen-anchored explod drawn to fill MUGEN's 4:3 screen to the whole
; window, so a super's backdrop does not stop short of a 16:9 screen's side.
fitsuperart = 1
; Fill anything the stage's back layer does not reach from the art beside it,
; rather than leaving a black slab. Costs one pass over the frame, and only
; on the stages that actually have a hole.
fillgutters = 1
stagezoom = 0
; Let a cornered wall-smash break the stage and carry the fight into the stage
; the venue names ([Break] next). 1 (default) allows it; 0 turns every stage
; break off. A stage that names no next stage never breaks. Local/versus only —
; never over netplay, where serving a break would desynchronise the machines.
wallbreak = 1
; Draw each stage's background music at random from the installed music pool
; instead of the track the stage names. 0 (default) plays the authored track.
; Either way a stage that names no music of its own still draws one, so none is
; silent. The roll is seeded from the match, so a replay plays the same music.
randomstagemusic = 0
; The shape of the screen the fight measures: ScreenPos, the screen edges and
; the bound that keeps fighters in view. auto follows [Video] width x height.
playfield = auto
; How quickly a knocked-down fighter gets up, as a multiple of the time
; their own character asked for. Never cuts into the downed animation.
getupspeed = 1.67
```

`splash` accepts a PNG or JPEG of any size; it is scaled to cover the window,
cropped rather than stretched, then darkened and vignetted so the wordmark and
progress bar stay readable over any photograph. Preview one with
`oxtool splash --image <file>`.

`difficulty` also sets the CPU level for arcade and survival ladders; a
`--ai` on the command line overrides it. The computer performs the driven
character's *own* special moves and supers — read out of its `.cmd` and
`[Statedef -1]` the same way the training move list is — so how technical it
plays depends on what the character owns rather than on anything written here.

`powerbars` is the super gauge, forced to the same length for everybody.
`[Data] power` is authored per character and this archive runs from 1000 to
9000, so "one bar" means a different amount of meter on each side of the
screen and a three-bar super costs one fighter their whole gauge and another a
third of theirs. Only the maximum moves: what a character charges per hit is
still their own `PowerAdd` and the `LifeToPowerMul` rules, so a shorter bar
fills faster and a longer one slower, exactly as if the author had written the
number. `0` is MUGEN — every character keeps their own.

`inputbuffer` is the one setting that changes how the game *feels* under the
hand. A `.cmd`'s `command.buffer.time` is how long a command stays asserted
after the motion completes, and virtually every character in this archive
leaves it at MUGEN's default of 1: the command is true for the single tick the
last button landed on and no other. Cancel windows are frequently one frame
wide too, and hitting a one-frame window with a one-frame input is why chaining
a normal into a special feels like guesswork.

Raising the floor is the remedy Elecbyte's own `.cmd` documentation names, in
so many words: *"With a higher value, such as 3 or 4, you can get a looser feel
to the command. The result is that combos can become easier to do because you
can perform the command early."* Nobody's files are edited; the engine simply
holds every command live for at least this many frames. Measured on CvS Gouki's
crouching heavy punch into a fireball, the window a player has to hit goes from
three frames to five. Set it to `1` for exactly what MUGEN does. Hold-only
commands (`/F`) are never buffered, which the same documentation is explicit
about.

`getupspeed` is the one default here that is deliberately *not* MUGEN. A
knockdown in this archive is frequently authored at a length that made sense
against one opponent in 2003 and reads as dead air now, and the shipped `1.67`
takes a fighter off the floor in six tenths of the time their own file asked
for. Two rules keep it from being a cheat: it never cuts into the downed
animation itself — which is what would make a get-up look like a teleport —
and it never makes a get-up *slower* than the character wrote, so a fighter
authored to bounce straight back up still does. Set it to `1.0` for exactly
what MUGEN does. Like `inputbuffer` and `introtime`, it is part of the
simulation, so both peers of a network match need the same number.

`superfx`, `fitsuperart` and `fillgutters` are the places the engine draws
over content it was given. All three are cosmetic, all three are outside the
simulation, and any of them can be changed without affecting a replay or a
netplay peer.

`superfx` (OPTIONS, PRESENTATION, SUPER EFFECTS) is the engine's own super
effect, described in [SUPER-EFFECTS.md](SUPER-EFFECTS.md): a white-hot impact,
a two-layer ember and steel ray burst from the fighter who called it, one
hexagonal shock ring per bar the super cost, speed lines, sparks, a cold grade
and vignette on the rest of the picture, and the caller rimmed in light. It
rides on any screen freeze long enough to be a super rather than on
`SuperPause` alone, so the characters that hold the screen with a plain
`Pause` get the moment too.

- `off` — MUGEN: the character's own art and the plain dimming, nothing else.
- `auto`, the default — the effect at full strength when the character brings
  little super art of its own, and toned down to an accent (the impact, a
  light burst and the rings at about a quarter) when the character's own art
  already fills the screen. On every frame of the freeze the renderer measures
  what the caller is drawing — its explods, helpers, projectiles and trails,
  rasterised on a coarse grid of the screen, plus an `EnvColor` or a strong
  `BGPalFX` held through the pause — and plays the effect at full strength
  below 30% coverage, as the accent above 60%, and in between on a smooth
  ramp. Where the author's art covers the screen, the effect also steps back
  locally, so it shows round the art rather than over it.
- `always` — full strength on every super.

Whatever the setting, the engine never hides, recolours or reorders anything a
character draws. The effect is composited after MUGEN's darkening and before
the foreground — `ontop` explods, the `SuperPause` charge animation and hit
sparks — so the author's foreground art is always in front of it; it only adds
light and shade of its own. A character that flashes the screen itself on the
opening ticks (a short `EnvColor` or `BGPalFX`) gets no second flash from the
engine: there is only ever one bright flash per super, and nothing in the
effect strobes.

`fitsuperart` (OPTIONS, PRESENTATION, FIT SUPER ART TO SCREEN) grows an explod
the author drew to fill MUGEN's 320x240 screen to the whole window. It applies
only in a window wider than 4:3 — at MUGEN's own shape the art is the art —
and only to explods placed relative to the screen (`postype = left`, `right`,
`front` or `back`), unrotated, that fill at least 95% of the 4:3 screen in
both directions; anything smaller is drawn exactly as authored. The plate is
scaled evenly and centred, so the overspill goes off the top and bottom rather
than the art being stretched. On by default. `oxtool superfx-audit` found 166
characters whose super backdrop stops short of a 16:9 screen's side; the fit
closes 158 of them and changes nothing at 4:3. See
[SUPER-EFFECTS.md](SUPER-EFFECTS.md).

`fillgutters` covers the case where a stage's back layer does not reach the
edge of a modern window: the hole is filled from the art beside it instead of
showing black. The fill re-measures the art edge whenever the camera pans, so
the mirrored border tracks the scenery rather than snapping behind it.

`wallbreak` (OPTIONS, PRESENTATION, STAGE BREAK) is the master switch over stage
breaking: a cornered wall-smash that meets a stage's `[Break] next` carries the
fight on into that stage, behind a breaking-wall animation. `1`, the default,
allows it; `0` turns it off everywhere. It is a local and versus feature only —
never over netplay, where serving a break (loading the next stage mid-match)
cannot be kept in step across the two machines. The simulation is identical to a
stage that names no break when it is off, so the switch moves no checksum. See
[EXTENSIONS.md](EXTENSIONS.md).

`randomstagemusic` (OPTIONS, SOUND, RANDOM STAGE MUSIC) draws each stage's
background music at random from the installed pool (`sound/` and `music/`)
instead of the track the stage's own `.def` names; a character that assigns its
own stage music still keeps it. `0`, the default, plays the authored track.
Either way, a stage that names no music of its own now draws a (stage-stable)
track from the pool rather than playing in silence, so no stage is mute. The
roll is seeded from the match, so a replay plays the same music, and music is
never hashed, so neither the roll nor the setting can move a checksum.

`stagezoom` (OPTIONS, PRESENTATION, STAGE FIT) decides what happens when a
stage's art is narrower than the window. At `0`, NORMAL SIZE and the default, the
fight is drawn at the window's ordinary scale, so a fighter is the same size on
every stage, as in MUGEN, and the short edges are left to `fillgutters`. At `1`,
ZOOM, the view moves in until the art fills the window, as Ikemen GO's camera
does, and the fighters grow with it: by up to a third at 16:9, on ten of the
archive's stages. The playfield the simulation holds fighters inside is the
zoomed one either way, so this too changes only the picture. `oxtool stagescale`
lists the stages it affects at each window shape.

`playfield` (OPTIONS, PRESENTATION, PLAYFIELD) is the shape of the screen the
*simulation* measures: `ScreenPos`, `LeftEdge`/`RightEdge`, the screen-bound
clamp and the camera all use it. `auto`, the default, takes the shape of the
window the config files ask for (`[Video] width` x `height` here, or
`mugen.cfg`'s `[Video]`), read once when the file is loaded; `4:3` is MUGEN's
320 units, `16:9` is 427 and `21:9` is 560, the game screen MUGEN 1.1 and Ikemen
GO set with `localcoord` and `GameWidth`. The live window never changes it — a
resize, fullscreen or `--width` on the command line fits the same fight to a
different screen, showing more sky where the window is narrower than the
playfield — so a seed is the same fight at any window size. A stage whose art
is narrower than the playfield narrows it, as before. Online, the host's
playfield is the one played; see [NETPLAY.md](NETPLAY.md).

`useselectdef = 1` is the compatible default: your curated roster, in your
order, with the stages you assigned. Entries naming a character that is not
installed are reported at startup and skipped rather than failing the load.

`speed` is the simulation rate; 60 matches the original. When `roundtime`
expires the player with more life takes the round, and an exact tie ends the
round scoring for neither.

`introtime` caps a fighter's entrance. A character says its entrance is still
playing with `AssertSpecial flag = Intro` and the round waits for it before
anything is announced; a quarter of a large roster asks for more than three
seconds and the longest here runs to twenty-three, so this is a ceiling rather
than a wait. `0` skips entrances entirely. Any attack button or Start cuts one
short whatever it is set to — offline only, since both peers of a network match
have to start the round on the same frame. Changing it means you can only play
online against someone who has changed it the same way, as with `inputbuffer`. `debugboxes` draws attack and hurt boxes; `F2`
toggles it at run time.

`originalfiles = 1` plays every converted character from the files it was
written in — the `.def.cns-backup` the converter kept, and the `.cns`/`.cmd`
beside it — instead of its FUSE files. It is the experiment that settles whose
a fault is: if it goes away, the conversion caused it; if it stays, it is the
engine or the character. The fight screen says `ORIGINAL FILES` while it is
on, and the choice is part of each character's content identity, so a replay
or an online peer in the other form is told rather than desynced. `--original`
does the same for one run, and Options → System → `CHARACTER FILES` toggles it
from the next round. One character can be held on its originals on its own by
an `x.def.play-original` file beside its `.def`, which is what
`oxtool ab --apply-fallback` writes for every character whose FUSE form
measures worse (see [FUSE-CONVERSION.md](FUSE-CONVERSION.md#is-it-the-conversion-oxtool-ab)).

## Knuckle Up

`[KnuckleUp]` is the house rules for a Knuckle Up run, on top of what the
campaign declares; Options → KNUCKLE UP edits them.

They can live in two places. `oxyde.cfg`'s `[KnuckleUp]` is read first; then
**`knuckleup/knuckleup.cfg`**, the mode's own settings file in its own folder
at the game root (see [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#the-knuckleup-folder)),
is read over it, key by key: a key set there wins, a key left out or
commented out keeps `oxyde.cfg`'s value. While that file exists, Options →
KNUCKLE UP saves to it (the status line says `saved oxyde.cfg and
knuckleup/knuckleup.cfg`) and `oxyde.cfg` keeps its own `[KnuckleUp]`
untouched. The file ships with every key at its default and commented out,
so installing the folder changes nothing until somebody edits it; delete it
to go back to `oxyde.cfg`'s. The run, its replay header and the online
handshake all read the effective values — what is played is what is
recorded and compared.

```ini
[KnuckleUp]
continues = 3       ; after the last life; -1 is unlimited
lives = -1          ; lives a run starts with; -1 takes the campaign's own
extend = 2          ; extra life by score: 0 off, 1 = 10,000 then every 30,000,
                    ; 2 = 20,000/50,000, 3 = 30,000/70,000, 4 = 50,000/100,000
enemylife = 100     ; percent, bosses included
attackers = 2       ; enemies that close in on a hero at once; 0 is all
waveextra = 0       ; extra enemies in every grunt wave
bonus = 1           ; bonus stages between stages: 0 never, 1 sometimes, 2 every stage
friendlyfire = 0    ; co-op heroes can hit each other
enemyguard = 50     ; how readily enemies block, percent of what their difficulty
                    ; would have them do, decided once per attack; -1 is CLASSIC
guardbreak = 3      ; blocks in a row before the next hit breaks the guard; 0 off
bonusgames = auto   ; auto (the campaign's choice, else random), random (any
                    ; installed bonus game, on its own stage), street (a prop
                    ; parked in the street just cleared), or a list of names:
                    ; oxyde_crusher, oxyde_titan, car2
bonusreward = auto  ; auto (the campaign's, else mystery), mystery, random, or
                    ; one reward: health:50, fullheal, oneup, power:100,
                    ; score:5000, continue, invincible:10, multiplier:20,
                    ; surge:15, weapon:20, rapidfire:12, jackpot
wavevariety = full  ; recast wave enemies who keep coming back: full, light or off
guardbreakboss = 6  ; blocks in a row before a campaign boss's guard breaks; 0 is
                    ; one more than guardbreak, as for any brute
guardbreakrest = 3  ; seconds after a break before that enemy's blocks count again
cameralead = 1      ; with the screen clear the camera eases ahead of the hero
pickups = full      ; floor drops: full (every kind, drawn from the run) or classic
streetprops = auto  ; dress every street with breakable props and hazards: auto or off
droptable = rapidfire ; what the tables give where they gave the WEAPON:
                    ; rapidfire (RAPID FIRE, 12 s) or weapon
```

`droptable` puts **RAPID FIRE** where the drop tables had the WEAPON — a street
prop's prize, the mystery reward, the pickup waiting at the start of every
street — and in a cleared wave's table: for twelve
seconds a move that has let its projectile go recovers at double speed, and the
super gauge is held full. No weapon art has been added yet, so `rapidfire` is
the default; `weapon` puts the tables back. A campaign or `bonusreward` that
names `weapon` gets the weapon either way. It is on the replay (format 10); a
tape older than that plays on the weapon tables. It has no Options entry; set it
in the file.

`streetprops` (Options → KNUCKLE UP → `STREET PROPS`) dresses every street with
three or four breakable props — cargo crates, drums you can kick or blow up, a
power cell, the armoured OXYDE car — and one or two timed hazards (vents, live
plates) by the stage's theme, on top of what the campaign parks. Their prizes
drop as floor pickups. `off` leaves the streets as the campaign wrote them,
which is what every replay recorded before it plays on. See
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#street-props).

`bonusgames` and `bonusreward` are explained, with every reward, in
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#bonus-stages-between-stages).
They have no Options entry yet; set them in the file.

`wavevariety` (Options → KNUCKLE UP → `WAVE VARIETY`) recasts the waves so the
same fighters do not keep walking in. A campaign names each wave's enemies, and
a themed stage has six to nine of them for twenty-seven slots, so as written
the same faces came back wave after wave — on OXYDE: Long Run, 90 of 270 grunt
slots were someone from the wave before, and every fighter was back after two
waves. `full` (the default): nobody twice on screen, nobody from the last two
waves, nobody twice on one stage while the campaign has anyone left to send.
`light`: nobody twice on screen and nobody back within three waves, keeping
more of each stage's own cast. `off`: the waves exactly as written, which is
what every replay recorded before it plays on. A recast slot is filled from the
campaign's own grunts (its themed stage first, then its neighbours'; never a
boss, a prop or the hero), keeps the slot's life and tier, and is drawn from
the run's seed, so a replay and a co-op partner get the same line-up. A
campaign can turn it down with `[Campaign] variety` and widen the cast with
`pool` — see [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#wave-variety).

Each player has their own lives and score; the continues are the run's, shared
by both. A continue brings back the lives the run started with and drops that
player in where they fell: the stage, the wave, the boss and his life are
exactly as they were, and the score is kept. The CONTINUE? countdown is ten
seconds and any button on that player's controls takes it; alone, it holds the
screen, and in co-op the player out of lives is asked on their own plate while
the other fights on. Letting it run out drops them out of the run (START brings
them back while a continue is left); with nobody left the run is over. A street
is untimed unless its campaign sets a `time`; when one does, running out costs
a life rather than the round.

`cameralead` (Options → KNUCKLE UP → `CAMERA LEAD`): once a wave is down the
camera eases ahead of the hero, so walking on to the next one scrolls the
street at once instead of at the screen's edge
([KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md#what-a-level-plays-like)).
`pickups` (`PICKUPS`): `full` reads every pickup kind a campaign names, draws
a cleared wave's drop from the run's table — partial and full health and power,
POWER UP, SPEED, SHIELD, MAGNET, points — and lets one fallen grunt in five
drop something small; `classic` is the 150-life drop every run had before
([KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#pickup-kinds)). Both, like
`guardbreakboss` and `guardbreakrest` below, are recorded on a replay (format
8); a tape older than that plays on their old values: off, classic, 0 and 0.

`enemyguard` and `guardbreak` are the brawler's blocking. The computer's enemies
decide once per attack they see coming whether to block it — at `enemyguard`
percent of the chance their difficulty would give them, more for a tough enemy
or a boss and less for a pushover, each enemy with its own lean — and one that
decides not to is mostly caught standing. An enemy that blocks `guardbreak`
attacks in a row (within a second and a quarter of each other; one more for a
brute) has its guard broken: the next hit lands clean, under a
GUARD BREAK! over its head. A campaign boss holds out for `guardbreakboss`
blocks (default 6, Options → `BOSS GUARD BREAK`; `0` treats it as a brute,
the rule before), and for `guardbreakrest` seconds after any break (default 3,
`GUARD BREAK REST`) that enemy's blocks count for nothing, so one break cannot
be chained straight into the next. CLASSIC (`-1`) and `0` are the engine as it was
before, which is what a replay from before format 5 plays on. The extend defaults are sized from headless runs of the shipped
campaign, where a cleared stage scores 6,000-12,000: the first extra life comes
around the second stage, not every wave. Every key here changes how the run
plays, so all of them are part of the run's identity: an online partner or a
replay on different house rules is refused rather than desynced.

**A campaign can set these too.** `lives`, `continues`, `enemylife`,
`enemyguard`, `guardbreak`, `guardbreakboss`, `attackers` and `ailevel` can each
be written into a `.knuckle` (with a `difficulty = easy|normal|hard` preset),
for the whole run or one stage — see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#difficulty). Where a campaign
writes a knob, the option here can only make it **easier**, never harder: an
option set easier than its default eases the author's value by as much, one at
or above the default leaves it alone. An option for a knob the campaign does not
write stays entirely yours, as above. A campaign's own pickup art
(`[Campaign] pickups = <folder>`) is a separate thing from `pickups = full`
here: it changes how the pickups look, not which kinds drop, and is presentation
only — never on a tape or an online handshake.

## Player tags

`players.cfg`, beside the config file, holds the initials each controller last
used (`[Last] p1`/`p2`) and one `[Player XYZ]` section per set of initials:
`wins`, `losses`, `streak`, `best` and a `pick.<fighter>` count per fighter.
The game writes it; nothing in it affects a match, a replay or an online
handshake.

## Mods and hot reloading

```ini
[Game]
; Run the Lua mods under mods/. Off by default: an engine that executes
; third-party code out of a folder it found is not one you can hand somebody
; an archive for.
mods = 0

; Poll a small set of files and reload them in place. An authoring
; convenience, and the one switch that makes the engine read from disk
; during a match.
watch = 0
watchinterval = 250

[Mods]
; Per *call*, not per session: a mod that does a lot of work once a round is
; not penalised, and one that never returns is stopped inside a frame.
instructions = 20000000
; The whole interpreter, across every mod.
memorymb = 64
```

See [SCRIPTING.md](SCRIPTING.md) and
[CUSTOMISATION.md](CUSTOMISATION.md#hot-reloading).

## Sound

```ini
[Sound]
enabled = 1
; Sound effects: hits, voices, everything a character plays.
volume = 80
; Stage music, from each stage's own [Music] bgmusic.
music = 1
musicvolume = 60
; Width of the stereo field, in the units a character's position uses.
; Read from mugen.cfg [Sound Win] PanningWidth when there is one.
panningwidth = 240
```

**Music** is played from whatever each stage names in `[Music] bgmusic`, and
from a character's `music` column in `select.def` when it has one — the
character's choice wins, because that is the one somebody typed deliberately.
MP3, Ogg Vorbis, FLAC, WAV and M4A are all read. Tracks are streamed rather
than loaded, so a four-minute MP3 costs a few kilobytes rather than 90 MB.

A stage that names nothing, or names a file that is not there, plays nothing:
"leaving bgm_filename blank will result in no music being played". The menu
theme does not follow the players into the fight, so the cure for a silent
stage is a `bgmusic` line in its own `.def` rather than anything in the
engine. A stage that names no track, or names a file the pack never shipped,
can carry a `; Oxyde:` comment above the line noting what it originally asked
for and which stage a replacement was borrowed from.

The menu's own tracks come from the screenpack's `[Music]`, and
`title.bgm.loop`, `select.bgm.loop` and `vs.bgm.loop` decide whether each one
repeats.

`enabled = 0` silences both; `music = 0` silences only the soundtrack.

Effect volume comes from `mugen.cfg` `[Options] WavVolume` when there is one.
That is a 0-100 slider and installs commonly sit near 30, which is very quiet —
if the game sounds almost silent, that is where to look, and `EFFECT VOLUME` in
the options screen is how to change it.

If no output device can be opened the game says so, loudly, and continues
silently. Every sample format a device might ask for is supported; a device
that only offers 16-bit integer output — which is most of them — is not a
reason to run without sound.

## Practice

The training menu's settings, remembered between sessions. Written by the menu
itself; there is no need to edit them by hand.

```ini
[Training]
dummy = STAND
guard = NEVER
p1life = INFINITE
p2life = REFILL
p1power = INFINITE
p2power = NORMAL
timer = 0
boxes = 0
; Keep the combo counter up for twice as long once the combo ends.
damagereadout = 1
; Frames after the last hit before a REFILL bar comes back.
refilldelay = 90
```

## Input

```ini
[Input]
; What happens when two opposing directions arrive at once.
;   0  both register (MUGEN exactly)
;   1  the one pressed most recently wins
;   2  forward beats back, up beats down
;   3  the one pressed first keeps the axis
;   4  neither registers  (default)
socdresolution = 4
; Delay every button press by one frame, so two pressed a frame apart register
; together. Costs a frame of lag on every button.
buttonassist = 0
; Hold guard automatically for a side while it is not pressing anything, per
; player. Off by default; the training menu's GUARD row and Knuckle Up's own
; auto-guard drive the same two switches.
autoblock.p1 = 0
autoblock.p2 = 0
```

A stick cannot press left and right at once. A keyboard, a hitbox controller
and a loose d-pad all can, and MUGEN passes both through — which lets a player
hold both and be un-crossable and blocking in both directions at the same
time. `4` is what this engine already did on the horizontal axis and now does
on the vertical one as well; `0` restores MUGEN exactly.

Button assist exists because MUGEN's input path was loose enough that two
buttons pressed a frame apart usually registered together, and a great deal of
shipped content is written expecting it.

## Meters

Four mechanics commercial fighting games have and MUGEN does not: a red life
bar you can recover into, a stun meter that dizzies you, a guard meter that
breaks, and a score.

```ini
[Meters]
redlife    = 0
dizzy      = 0
guardbreak = 0
score      = 0
```

All four are **off**. They change how every character in the roster plays, and
a rule nobody asked for is a bug however good the rule is. Each is computed
from numbers every character already has — the `damage` on a `HitDef`, the
`[Data] life` constant — so nothing needs patching to take part, and a
character that wants to drive one itself has the vocabulary to.

Everything behind them is a setting, and here is all of it:

```ini
; What a hit costs each meter, per point of damage it did — once for an
; ordinary attack and once for a hyper.
lifetoredlifemul          = 0.5
superlifetoredlifemul     = 0.25
lifetodizzypointsmul      = 1.0
superlifetodizzypointsmul = 0.5
lifetoguardpointsmul      = 0.9
superlifetoguardpointsmul = 1.6
; How long a dizzy and a broken guard last, in ticks.
dizzytime      = 180
guardbreaktime = 60
; Ticks a fighter must be left alone before stun and guard start coming back,
; and how much of the bar returns per tick after that.
recoverdelay = 120
recoverrate  = 0.002
; Life regained per tick while resting, as a fraction of the life bar. Never
; past the red bar it is climbing towards.
redliferegen = 0.0004
; What the points are worth.
scoreperdamage   = 10
scorecombobonus  = 2
scoreperround    = 5000
scoreperfect     = 10000
scorefirstattack = 1000
```

The six `...mul` numbers are all *per point of damage*, which is what lets one
rule cover a roster whose characters run from 500 to 2000 life: a hit that
takes a tenth of a big character costs the same fraction of their stun bar as
a hit that takes a tenth of a small one. A hyper is counted separately because
a super that took a third of your life should not also be a third of the way
to dizzying you — hence the lower red-life and stun multipliers and the
*higher* guard one, since a blocked super is meant to be the thing that opens
a guard.

`recoverdelay` is the number that decides what these meters are about. The
clock is the **opponent's to reset** — any hit or blocked hit starts it again —
so stun and guard come back for a fighter who has been left alone and never
for one under pressure. Set it low and the meters measure time; set it high
and they measure the round.

`oxyde --write-config` writes all of them out with their comments, and
[EXTENSIONS.md](EXTENSIONS.md) has the mechanics each one feeds.

Oxyde's own HUD draws all four. A screenpack draws them if its `fight.def` has
`[Stunbar]`, `[Guardbar]` or `[Score]` sections — the same element vocabulary
as `[Lifebar]` — and simply does not if it has none, which is every `fight.def`
written before they existed.

## Parry

A tap toward an attack, in the moment before it lands, that consumes it
outright. Neither M.U.G.E.N nor Ikemen GO has the mechanic.

```ini
[Parry]
mode   = off      ; off | tap | hold
window = 8
cooldown = 12
freeze = 10
advantage = 6
redwindow = 4
projectiles = 1
throws = 0
unblockable = 0
power = 0
guardpoints = 0
ai = -1
effect = 1
sound = 5, 0
```

**Off**, for the same reason the meters are and for two more: a roster balanced
against an engine with no parry is not balanced against one with it, and the
computer parries only as well as `ai` allows — so switching this on and leaving
`ai = 0` makes the CPU measurably easier to beat. `-1` follows the session
difficulty, which is the answer that does not quietly change the game.

The training menu has a `PARRYING` row that switches it on for the live match,
because a window is a number nobody can pick without trying it against a real
attack — and training also draws the counter, the window as a bar under the
fighter, and how many frames early the tap was.

Every number is explained in [PARRY.md](PARRY.md).

## Absorb

Give up the punish a parry bought and take a share of what the parried move
cost instead — meter, and optionally a little recoverable life. Its own section
rather than more rows under `[Parry]` because it is a different decision:
somebody may well want parrying without it, and it is inert whenever parrying
is off.

```ini
[Absorb]
; Off unless switched on, and only works while [Parry] is on.
enabled = 0
; Ticks after a parry in which the follow-up nod is accepted.
window = 20
; Percent of the attacker's spend granted back as power.
share = 50
; Percent of max life returned per full bar absorbed, as recoverable (red)
; life only — never past the red-life ceiling, so it can give back damage
; already taken but never manufacture health. 0 switches it off (the default).
lifeshare = 0
; The smallest spend worth taking; below it nothing happens and the window
; never opens, so absorbing ordinary normals never flashes.
mincost = 250
; Absorbing hands the parry's frame advantage back to the attacker — the cost
; that makes the trade "punish or meter" rather than "punish and meter".
costsadvantage = 1
; Draw the mark and flash the palette.
effect = 1
; fightfx sound, as group, number.
sound = 5, 1
```

The mechanics each number feeds are in [EXTENSIONS.md](EXTENSIONS.md).

## Balance

```ini
[Balance]
; Off by default: these rules change how characters were authored to play.
enabled = 0
targetlife = 1000
lifenormalisation = 0.5
damagescale = 1.0
maxhitfraction = 0.35
table = balance.cfg
```

See [BALANCE.md](BALANCE.md). Generate the table with `oxtool balance`.

## Tag

Switching the on-screen fighter for a benched partner. Characters can always
drive it themselves with the `TagIn`/`TagOut` controllers; this section adds a
universal button combination so every character can tag whether its author
wrote for it or not.

```ini
[Tag]
; off | button. off leaves only the TagIn/TagOut controllers (the default,
; because a roster balanced without tagging is not balanced with it).
mode = off
; The buttons held together to tag, as a chord like b+z. Two by default: a
; single button collides with a move on almost every character, and three is
; a claw. A press that a character's own command claims stays theirs.
button = b+z
; Ticks before the same side may tag again, so holding the chord does not
; swap every frame.
cooldown = 60
; Ticks the arriving fighter spends without control — not invulnerable, just
; unable to attack the instant it appears.
lockout = 12
```

The mechanic is described in full in [TAG.md](TAG.md). (This is distinct from
`players.cfg` above, which only remembers each controller's initials and
records.)

## Netplay

```ini
[Netplay]
port = 7500
inputdelay = 2
; The last host joined, offered again next time.
peer =
; What this machine calls itself in the list a joiner sees when it looks for
; hosts on the local network. Empty uses the host name, then this machine's
; address.
name =
```

`peer` is written by the engine rather than by you: joining a host records its
address here, and the online screen offers it back as the default next time.
Clearing it clears the suggestion.

Hosts announce themselves on `port + 1`, so one number still describes the
whole of netplay — **including a tournament**, whose control channel and whose
relayed inputs share the same socket, told apart by a kind byte. One port to
forward however many people are playing. See [NETPLAY.md](NETPLAY.md).

## Content sharing (bring-your-own-characters)

When two people play online and one brings a character the other does not have,
this decides whether it is **sent over the connection** so the bout can happen,
instead of the match being refused because the rosters differ. Off on the giving
side and *ask* on the taking side by default, so nothing moves without opting in.

```ini
[Sharing]
; what THIS install will GIVE a peer
share           = off           ; off | on-request | roster
share-allow     = *             ; glob of character folders it may give
; what THIS install will TAKE from a peer
accept          = ask           ; off | ask | single | roster
accept-dir      = chars/.incoming ; where received characters are written
keep            = session       ; session (discard after the bout) | always
; size ceilings (a received character is also verified by content hash)
max-per-char-mb = 512           ; per character; clamped to what one transfer can carry (~854)
max-match-mb    = 2048          ; across every transfer in a match
```

- **`share`** — `off` gives nothing (a peer lacking a character is refused, as
  before). `on-request` gives a specific character when asked, after you approve
  the prompt. `roster` gives any character inside `share-allow` without a prompt.
- **`accept`** — `off` takes nothing. `ask` prompts you per character. `single`
  pulls the one character a match needs without a prompt, but never a bulk sync.
  `roster` pulls whatever a scope asks for, sync included, without a prompt.
- **`share-allow`** is a case-insensitive glob over the character's folder path;
  `*` is everything, `chars/mine/*` only your own.
- **`keep = session`** evaporates a received character when the room ends;
  `always` keeps it under `accept-dir`.
- The ceilings are a backstop to the per-file caps in the bundle format. The
  per-character value is clamped to what a single transfer can carry, so it never
  promises more than the wire can move. A received character is confined to its
  own directory and its content hash is checked against the one that was asked
  for before it is ever loaded — it is interpreted data, never code.

See [BYOC.md](BYOC.md) for the full design and the security model.

## Replay

Where recorded matches and the videos exported from them are kept, and when a
match is taped. The `RECORD REPLAYS` row on the options screen writes `record`;
the rest are edited here.

```ini
[Replay]
; ask | auto | off. ask offers to save on the result screen (the default);
; auto tapes every match; off records nothing.
record = ask
; How many recordings to keep. The oldest are pruned past this. 0 keeps none.
keep = 20
; Folder the tapes go in, relative to the game root.
dir = replays
; Folder for videos exported from a replay.
videodir = videos
; Export size, as WIDTHxHEIGHT.
videosize = 1280x720
; high | medium | small.
videoquality = medium
; auto | av1 | h264 | gif. auto picks the best encoder the build has.
videocodec = auto
```

A replay is a tiny input tape, not a video; see [TOOLS.md](TOOLS.md) for
`oxtool replay` and the export pipeline.

## Key bindings

```ini
[P1Keys]
up    = ArrowUp
down  = ArrowDown
left  = ArrowLeft
right = ArrowRight
a = KeyA
b = KeyS
c = KeyD
x = KeyZ
y = KeyX
z = KeyC
start = Enter
; Engine actions rather than moves: swapping both fighters in Sparring.
select = Tab
gamepad = 0

[P2Keys]
up    = KeyI
down  = KeyK
left  = KeyJ
right = KeyL
a = KeyT
b = KeyY
c = KeyU
x = KeyG
y = KeyH
z = KeyB
start = Backslash
select = Backquote
gamepad = 1
```

Key names are winit's `KeyCode` spellings — `KeyA`, `ArrowUp`, `Digit1`,
`Space`, `ShiftLeft`, `Backslash`, `Enter`. They are physical positions, so a
binding works the same on QWERTY and AZERTY.

`gamepad = -1` disables the pad for that player. Two players can share a
keyboard; a key bound by both drives both.

### The six buttons

MUGEN's buttons are `x`, `y`, `z` (light, medium, heavy punch) and `a`, `b`,
`c` (light, medium, heavy kick). `start` is the pause/taunt button, and opens
the training menu in Training and Sparring.

`select` is not a fighting-game input and is never sent to a character. It is
for things that happen *to* a match: in Sparring it swaps both fighters for
random ones without leaving the fight.

## Gamepads

Detected automatically through `gilrs` (evdev on Linux, XInput/DirectInput on
Windows). Pad 0 goes to player 1 and pad 1 to player 2 by default; change with
the `gamepad` key.

The layout follows the arcade convention — punches on the top row, kicks on the
bottom:

| Engine button | Pad control |
|---|---|
| `x` light punch | West face button (Square / X) |
| `y` medium punch | North face button (Triangle / Y) |
| `z` heavy punch | Right shoulder (R1 / RB) |
| `a` light kick | South face button (Cross / A) |
| `b` medium kick | East face button (Circle / B) |
| `c` heavy kick | Right trigger (R2 / RT) |
| `start` | Start / Options / Menu |
| `select` | Select / Back / View |

Rumble is driven by the `ForceFeedback` state controller, so a character that
asks for it gets it. Pads that report no force-feedback support are skipped
silently.

Directions come from the d-pad or the left stick, which registers past 50%
deflection. A d-pad reaches the engine either as four buttons or as a hat —
most pads on Linux report a hat — and both are read. Hot-plugged pads are
picked up without restarting, and a pad that drops out has its buttons
released rather than left held.

L1, L2 and the right stick are read but deliberately bound to nothing. MUGEN
has six attack buttons and the table above already spends six; putting a
seventh engine input under a second physical button would mean one press
sending two, which almost every character in this archive reads as a throw or
a super rather than as an attack.

### When a pad misbehaves

`oxyde --pads` lists what is attached, says whether each pad is driven by an
SDL mapping or by the driver's defaults, and then prints — for every press —
which of the engine's inputs it drove:

```
2 controller(s):
  pad 0  Microsoft X-Box 360 pad (SDL mapping)

press buttons — 30s, or ctrl-c:
  pad 0  x
  pad 0  --
  pad 0  Down + b
```

One press should print one name. Two names from one press is a pad whose
mapping overlaps; no name at all is a button the driver does not report. It
needs nothing else running, so it answers "is this the pad or the character?"
without loading a match.

## The options screen

`OPTIONS` on the title menu. Up and down choose a row, left and right change
it, Start activates one, `SAVE AND RETURN` writes `oxyde.cfg`, and `RETURN
WITHOUT SAVING` puts back exactly what was there when the screen was opened.
Home, End, Page Up and Page Down move about the list.

The list is grouped into six sections, and the cursor steps over the titles.
A setting that is a point on a scale carries a small bar showing where in that
scale it sits. A setting that no longer matches the file is marked in the
gutter, and the subtitle counts how many are unsaved.

| Section | Row | Field it writes |
|---|---|---|
| MATCH | `DIFFICULTY` | `[Game] difficulty` |
| | `ROUNDS TO WIN` | `[Game] rounds` |
| | `TIME LIMIT` | `[Game] roundtime` |
| | `LIFE` | `[Game] life` |
| | `SUPER BARS` | `[Game] powerbars` |
| | `ARCADE OPPONENTS` | `[Game] arcadeopponents` |
| | `TEAM LIFE (1 VS 2)` | `[Rules] team1vs2life` |
| | `TEAM LOSES ON ANY KO` | `[Rules] teamloseonko` |
| | `TEAM RUMBLE ON SCREEN` | `[Game] teamrumbleonscreen` |
| | `TEAM RUMBLE TEAM` | `[Game] teamrumblesize` |
| FEEL | `GAME SPEED` | `[Game] speed` |
| | `INPUT BUFFER` | `[Game] inputbuffer` |
| | `FREEZE LIMIT` | `[Game] superfreeze` |
| | `POWER GAIN` | `[Rules] attacklifetopowermul`, `gethitlifetopowermul` |
| | `DAMAGE BALANCING` | `[Balance] enabled` |
| | `BALANCING STRENGTH` | `[Balance] lifenormalisation`, `damagescale`, `maxhitfraction` |
| PRESENTATION | `ENTRANCES` | `[Game] introtime` |
| | `SCREENPACK` | `[Game] screenpack` |
| | `VERSUS SCREEN` | `[Game] vsscreen` |
| | `SELECT COLUMNS` | `[Game] selectcolumns` |
| | `KEEP JUMPS ON SCREEN` | `[Game] camerakeepvisible` |
| | `SHADOWS` | `[Rules] drawshadows` |
| | `SUPER EFFECTS` | `[Game] superfx` |
| | `FIT SUPER ART TO SCREEN` | `[Game] fitsuperart` |
| | `ATTRACT LOOP` | `[Game] attract` |
| | `COLLISION BOXES` | `[Game] debugboxes` |
| AUDIO | `SOUND` | `[Sound] enabled` |
| | `EFFECT VOLUME` | `[Sound] volume` |
| | `MUSIC` | `[Sound] music` |
| | `MUSIC VOLUME` | `[Sound] musicvolume` |
| | `STEREO WIDTH` | `[Sound] panningwidth` |
| INPUT | `VERSUS PLAYER 2` | `[Game] versuscpup2` |
| | `PLAYER 1 / 2 KEYS` | `[P1Keys]` / `[P2Keys]` |
| KNUCKLE UP | `CONTINUES` | `[KnuckleUp] continues` (in `knuckleup/knuckleup.cfg` when it exists) |
| | `LIVES` | `[KnuckleUp] lives` |
| | `EXTRA LIFE AT` | `[KnuckleUp] extend` |
| | `ENEMY LIFE` | `[KnuckleUp] enemylife` |
| | `ATTACKING AT ONCE` | `[KnuckleUp] attackers` |
| | `WAVE SIZE` | `[KnuckleUp] waveextra` |
| | `WAVE VARIETY` | `[KnuckleUp] wavevariety` |
| | `STREET PROPS` | `[KnuckleUp] streetprops` |
| | `BONUS GAMES` | `[KnuckleUp] bonus` |
| | `FRIENDLY FIRE` | `[KnuckleUp] friendlyfire` |
| | `ENEMY BLOCKING` | `[KnuckleUp] enemyguard` |
| | `GUARD BREAK` | `[KnuckleUp] guardbreak` |
| | `BOSS GUARD BREAK` | `[KnuckleUp] guardbreakboss` |
| | `GUARD BREAK REST` | `[KnuckleUp] guardbreakrest` |
| | `CAMERA LEAD` | `[KnuckleUp] cameralead` |
| | `PICKUPS` | `[KnuckleUp] pickups` |
| SYSTEM | `HELPER LIMIT` | `[Rules] helpermax` |
| | `CHARACTER FILES` | `[Game] originalfiles` |
| | `FRAME SKIP` | `[Video] frameskip` |
| | `RECORD REPLAYS` | `[Replay] record` |
| | `RESTORE DEFAULTS` | — |

`ENTRANCES` is the one worth knowing about if you have been mashing past them:
it caps how long a character's own entrance may hold the round up, as SKIPPED,
SHORT, NORMAL, LONG or UNCUT. Any attack button or Start still cuts one short
whatever it is set to.

`RESTORE DEFAULTS` puts every row above back to its shipped value and nothing
else — not the game root, not the window, not the renderer, not the key
bindings. It is not saved until `SAVE AND RETURN` is.

Rebinding shows a live list; choose a button, press the key you want, or
Escape to cancel. A key the other player already uses is refused with a reason
rather than accepted and discovered mid-match.

Video mode and the renderer are deliberately not here: changing them needs the
window rebuilt, and a half-applied resolution change is worse than editing a
line. The balance table is not here either, because `oxtool` generates it.

## Match rules and engine limits

`mugen.cfg` keeps these in `[Rules]` and `[Config]`, and Oxyde reads them from
there. What `oxyde.cfg` writes wins, so the options screen can change them
without touching your MUGEN installation.

```ini
[Rules]
; Power gained per point of damage, attacking and being hit.
attacklifetopowermul = 0.7
gethitlifetopowermul = 0.6
; Extra defence while running somebody else's state - throws and
; cinematic supers.
supertargetdefencemul = 1.5
; Life for one fighter facing two, as a percentage.
team1vs2life = 150
; A team loses the round the moment any member falls.
teamloseonko = 0
drawshadows = 1
; Live helpers one character may run at once.
helpermax = 32
; Process players in table order, the way MUGEN does. Off; see below.
indexprocessingorder = 0
```

`indexprocessingorder` is the only one of these that is not MUGEN's own.
MUGEN reads player 1 before player 2 on every tick, which is a real edge in
any exchange where both swing at once: P1's `HitDef` is on the table when P2
is asked whether it has been hit, and P2's is not. The default sorts by what
each fighter is *doing* — attackers, then idlers, then whoever is being hit,
roots before their helpers — so whoever is attacking is read first whichever
side of the screen they stand on. `1` restores MUGEN's order.

Characters are balanced against these numbers, so moving them changes how the
roster plays. `helpermax` is the one worth raising rather than lowering: a
helper-heavy character that hits the limit simply stops spawning, and `oxtool
soak` reports how often that happened across the whole archive.

## What Oxyde reads from `mugen.cfg`

`data/mugen.cfg` is read first, before `oxyde.cfg`, so an existing MUGEN
installation keeps working with its own file and anything `oxyde.cfg` writes
wins over it. These are the exact MUGEN key spellings the engine looks up —
the original dotted names, not the `oxyde.cfg` equivalents above. Everything
else in a `mugen.cfg` is ignored rather than rejected.

| `mugen.cfg` section | Key | What Oxyde does with it |
|---|---|---|
| `[Options]` | `Difficulty` | CPU strength 1–8 (unless `[Game] difficulty` overrides). |
| | `Life` | Life bar percentage. |
| | `Time` | Seconds per round; `-1` means untimed. |
| | `GameSpeed` | Game speed, when `> 0`. |
| | `Team.1VS2Life` | Life for one fighter facing two, as a percentage. |
| | `Team.LoseOnKO` | A team loses the moment any member falls. |
| | `Motif` | The screenpack to load. |
| | `WavVolume` | Effect volume. |
| `[Sound Win]` / `[Sound Linux]` / `[Sound]` | `PanningWidth` | Stereo spread. |
| | `Sound` | Master sound on/off. |
| | `StereoEffects` | `0` collapses panning to centre. |
| `[Rules]` | `Default.Attack.LifeToPowerMul` | Power gained per point of damage dealt. |
| | `Default.GetHit.LifeToPowerMul` | Power gained per point of damage taken. |
| | `Super.TargetDefenceMul` | Extra defence while in another fighter's state. |
| | `GameType` | Anything but `vs` is recorded as unsupported. |
| `[Arcade]` | `AI.RandomColor` | Pick a random palette for a CPU fighter. |
| | `AI.Cheat` | Recorded as unsupported — Oxyde's CPU plays the character's own `.cmd`. |
| | `Arcade.AIramp.Start` / `.End` | AI difficulty ramp across an arcade ladder. |
| | `Team.AIramp.Start` / `.End` | AI ramp for a team ladder. |
| | `Survival.AIramp.Start` / `.End` | AI ramp for a survival ladder. |
| `[Config]` | `GameSpeed` | Game speed. |
| | `DrawShadows` | Draw character shadows. |
| | `AfterImageMax` | Live afterimage limit. |
| | `ExplodMax` | Live explod limit. |
| | `SysExplodMax` | Live system-explod limit. |
| | `HelperMax` | Live helper limit per character. |
| | `PlayerProjectileMax` | Live projectile limit. |
| `[Video Win]` / `[Video Linux]` / `[Video]` | `Width` / `Height` | Starting window size, if `oxyde.cfg` sets none. |
| `[P1 Keys]` / `[P2 Keys]` | — | MUGEN key bindings, read as a fallback. |

## Command line

```
oxyde [--root <game dir>] [options]

  --help, -h          This message
  --version, -V       Print the version and exit
  --root <dir>        Game data directory (default: current directory)
  --config <file>     Config file (default: oxyde.cfg)
  --write-config      Write a commented default config and exit
  --width <n>         Window width
  --height <n>        Window height
  --software          Force the CPU renderer
  --boxes             Draw collision boxes
  --balance           Enable damage/life balancing
  --balance-table <f> Use a table from `oxtool balance`
  --pads              List attached controllers and what each button does,
                      then exit; nothing else needs to be running
  --stage <name>      Always fight on the stage whose file or name matches
  --seed <n>          Seed every random choice, to reproduce a run exactly
  --replay <file>     Play a recorded match back, and check it still
                      reproduces (headless: exits 1 if it diverged)
  --save-replay <f>   Headless: write the run's tape to <f> when it ends
  --host              Host a network match on the configured port
  --join <addr>       Join a network match at host:port

  --corrosion-host [addr]   Run the engine here and stream the screen. Two
                            seats, spectators welcome. Default port 7411.
  --corrosion-join <addr>   Join one as a client: a window and a controller,
                            and *no content loaded on this machine at all*
  --seat <0|1>              Which seat to take when joining

  --headless          Run without a window (for testing and CI)
  --frames <n>        Headless: how many frames to run (default 600)
  --ai <0-8>          Headless: CPU difficulty on every seat (default 5)
  --mode <name>       Headless: which mode to run (arcade, training,
                      versus-bonus, team-co-op, ... ; run with a bad name
                      to list them)
  --p1 <path>         Headless: character def for player 1
  --p2 <path>         Headless: character def for player 2
  --team-size <n>     Headless: how many fighters a side brings in a team
                      mode, standing in for the team menu; `1,4` sizes
                      the two sides separately
  --power-full        Headless: keep every fighter's meter full, so supers
                      actually come out — the computer only ever spends a
                      full bar and will sit on half of one all match
  --screen <name>     Headless: show a screen instead of a match (title,
                      select, teams, story, options, online; online-address
                      and online-lan open the two under it) or a practice
                      page over one (training, movelist, trials)
  --trial <n>         Headless: start a practice session running trial n
  --show-trial        Headless --trial: play its demonstration, the way
                      Select does
  --judge-demo        Headless --trial: play the demonstration and judge it
                      as if the player had done it, so the CLEAR banner can
                      be seen and the route proven through the game loop
  --dummy             Headless: player two stands still, as the training
                      dummy, instead of the computer fighting back
  --filter <text>     Headless --screen select: pre-fill the roster search
  --shot <file>       Headless: write a PNG of the final frame
  --shot-supers <d>   Headless: write a PNG into <d> for every frame a
                      SuperPause is running, numbered by tick
```

## In-game keys

| Key | Action |
|---|---|
| Type anything | Search the roster on the select screen |
| Backspace | Delete a search character |
| Delete | Clear the search |
| Enter / light punch | Confirm |
| Medium punch | Cancel a locked-in choice |
| Escape | Back out; quit from the title |
| F1 | Debug overlay (rollback stats, sprite cache, frame) |
| F2 | Collision boxes |
| F3 | Hold the fight still, or let it run |
| F4 | One tick, and hold again |
| F5 | Save this moment |
| F6 | Back to the saved moment |
| Start | Training menu, in Training and Sparring |
| Select | Swap both fighters, in Sparring |
| Start + medium kick | Leave a match |
