# Make your own Knuckle Up

This is the author kit for [Knuckle Up](KNUCKLE-UP.md), Oxyde's belt-scroll
brawler. It is for someone who has art of their own — a crate, a barrel, a
reactor-panel icon — and wants it in the mode without writing a line of CNS.

Everything here is **content you drop into the game root**: a prop is a folder
of PNGs and one `prop.ini`; a pickup skin is a folder of PNGs; a difficulty is
a handful of keys in your `.knuckle` campaign. The engine ships alone — none of
this is an engine patch — and every piece is checked before anyone plays it:
`oxtool props build` fields the prop it just wrote, `oxtool props` and `oxtool
campaign` measure the result, and a headless run plays it for real.

- The campaign format itself is [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md).
- Building a long street with waves and a boss placed along it is
  [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md).
- The player-side house rules these difficulty keys meet are in
  [CONFIGURATION.md](CONFIGURATION.md#knuckle-up).

Everything below is demonstrated end to end by the shipped example campaign
`knuckleup/campaigns/template.knuckle` and the example prop
`knuckleup/props/kit_cargo_crate/`.

## The folder layout

At the game root:

```text
knuckleup/
  campaigns/<your>.knuckle        your run (KNUCKLE-UP-CAMPAIGNS.md)
  props/<name>/                   a prop you build
    prop.ini                      what it is
    art/                          the pictures (and optional sounds)
      intact.png damaged.png critical.png broken.png
      debris1.png debris2.png burst.png hit.png
      hit.wav break.wav           optional
    <name>.def .cns .cmd .air .sff (.snd)   written by `oxtool props build`
  pickups/<folder>/<kind>.png     a campaign's pickup art
  stages/ music/ logic/ ...       the rest of the mode's own folder
```

A prop lives in `knuckleup/props/`, so it is a prop to the roster: never on the
select screen, never drawn at random. The street dresser parks it by stage
theme, and a campaign can park it itself.

## (a) A custom prop — `oxtool props build`

A prop is a breakable (or kickable, or explosive, or a timed hazard) object a
fighter smashes in the street for a reward. You give the kit the standing
pictures and a `prop.ini`; it trims them, resamples them to three pixels a world
unit, makes the alpha binary, quantises and packs them, and writes a working
MUGEN character (`.def .cns .cmd .air .sff`, and `.snd` if you gave it sounds).

### 1. The pictures — `art/`

Paint them at whatever resolution you like; the kit resamples down and never
upscales. Transparent background.

| file | what it is |
|------|------------|
| `intact.png` | the prop, undamaged (**required**) |
| `damaged.png`, `critical.png`, … | the same prop, more broken each step |
| `broken.png` | the remains left on the floor after it breaks |
| `debris1.png`, `debris2.png`, … | shards it throws when hit and when it breaks |
| `burst.png` | the flash on each damage step and the break |
| `hit.png` | an extra heavy-hit flash (optional) |
| `hit.wav`, `break.wav` | sounds, if you have them (optional) |

Only `intact.png` is required. With no `broken.png` the kit cuts the remains
from the last standing picture along a ragged edge; with no `damaged`/`critical`
the prop simply pops when it breaks.

Numbered files group: `debris1.png`, `debris2.png` are one set of shards.

### 2. The description — `prop.ini`

```ini
[Prop]
name    = OXYDE Cargo Crate (kit)   ; display name; default: the folder name, prettified
kind    = breakable                 ; breakable | kickable | volatile:fire|gas|shock | hazard:steam|fire|shock
life    = 320                       ; how many hit points; default 320 (breakable)
width   = 54                        ; world units across; default 54 (a fighter stands ~100 tall)
height  = 52                        ; where sparks/effects sit; default: the art's own height
axis    = 277, 520                  ; the foot of the art, in its own pixels; default: bottom centre
damage  = 2/3, 1/3                  ; life left at which damaged.png, then critical.png, take over
shadow  = 1                         ; a contact shadow under it; default on
faces   = right                     ; which way the art reads; default right
rewards = health:15*3, score:1500*3, power:25*2   ; what breaking it pays (weights after *)
limit   = 2                         ; most of it one street holds; default 2 (hazards 1)
back    = 0                         ; parked at the back of the street; default off
```

Keys are case-insensitive. The reward specs are the same ones a campaign uses
(`health:N`, `score:N`, `power:N`, `weapon:N`, `oneup`, `jackpot`,
`multiplier:N`, `mystery`, `random`, …; see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#prop-rewards)). Leave
`rewards` out and the kind picks a sensible default.

`kind` beyond `breakable`:

- `kickable` — flies when kicked.
- `volatile:fire|gas|shock` — explodes when broken, with a fuse. Extra keys
  `fuse = 40` (ticks), and `blast.*` to tune the blast (see below).
- `hazard:steam|fire|shock` — bursts on its own clock after a warm-up a player
  can see. Extra keys `cycle`, `warm`, `active` (ticks; needs
  `warm + active < cycle`).

Tuning a blast or a lingering cloud (optional; the kind supplies defaults):

```ini
blast.damage   = 90      ; and blast.reach, blast.depth
blast.reaction = launch  ; launch | stun | life
linger.ticks   = 180     ; a cloud that keeps hurting: and .reach .depth .damage .every .props
```

These go verbatim into the prop's own `[KnuckleUp]` declaration in the `.def`,
which is what the street reads — so a prop the engine has never heard of still
blows up, bursts or pays into the floor exactly like a built-in one. The same
`[KnuckleUp]` block can be written by hand on any prop `.def`; it is the full
reference below.

### The `[KnuckleUp]` declaration (writing it by hand)

A prop's street behaviour lives in a `[KnuckleUp]` section in its `.def`. The
kit writes it for you from `prop.ini`, but you can add it by hand to any prop
`.def` — a bonus-game character, or a prop you already have — and the street
will field it. A prop with no `[KnuckleUp]` section keeps whatever the built-in
[catalog](KNUCKLE-UP.md) entry for its folder name says, or pays as props always
did if the engine has never heard of it. (Read by `street::declared`; the keys
are case-insensitive.)

```ini
[KnuckleUp]
kind    = volatile          ; breakable | kickable | volatile | hazard
rewards = score:1000*2, health:10
limit   = 2                 ; most of it one street holds
back    = 0                 ; parked at the back of the street (the car)
blast   = fire              ; which built-in prop's blast numbers to start from
blast.damage = 90           ; override any of the blast's numbers
blast.reaction = launch     ; launch | stun | life
linger.ticks = 180          ; a cloud/fire the blast leaves behind
```

| key | values | default | what it does |
|-----|--------|---------|--------------|
| `kind` | `breakable`, `kickable`, `volatile`, `hazard` | `breakable` | `breakable`/`kickable` just break for rewards (they carry no blast here — a kickable's *flying* physics come from its own CNS, which the kit writes); `volatile` explodes when it breaks; `hazard` is a timed street hazard that is never hit, pays nothing, and bursts on its own clock. |
| `rewards` | comma list of `spec` or `spec*weight` | none | What breaking it pays, drawn weighted from the run's seed. Same spec grammar as a campaign (see [prop rewards](KNUCKLE-UP-CAMPAIGNS.md#prop-rewards)). **Written by hand, a prop with no `rewards` pays nothing** — unlike the kit, which fills a sensible default per kind. |
| `limit` | 1–8 | `2` | The most of this prop one street holds. |
| `back` | `1`/`yes`/`true`/`on` | off | Park it at the back of the street (where the car goes), not anywhere on it. |
| `blast` | volatile: `fire`, `gas` (`toxic`), `shock`, `car` (`big`) · hazard: `steam`, `fire`, `shock` | volatile `fire`, hazard `steam` | Picks the built-in prop whose blast/hazard numbers this one starts from. Ignored for `breakable`/`kickable`, which have no blast. |
| `blast.reach` | 1–400 units | from `blast` | How wide the blast reaches. |
| `blast.depth` | 1–200 units | from `blast` | How deep (into the lane) it reaches. |
| `blast.damage` | 0–1000 | from `blast` | Damage the blast deals. |
| `blast.reaction` | `launch` (`knockdown`), `stun` (`stagger`), `life` (`damage`) | from `blast` | How it hits whoever is caught. |
| `linger.ticks` | 0–3600 | 180 | A cloud or fire the blast leaves behind, that keeps hurting. Writing **any** `linger.*` key creates one (starting from reach 30, depth 22, ticks 180, damage 3, every 15, props off); `linger.ticks = 0` removes it. |
| `linger.reach` | 1–400 units | 30 | How wide the cloud reaches. |
| `linger.depth` | 1–200 units | 22 | How deep the cloud reaches. |
| `linger.damage` | 0–200 | 3 | Damage each bite. |
| `linger.every` | 1–600 ticks | 15 | How often it bites. |
| `linger.props` | `1`/`yes`/`true`/`on` | off | Whether the cloud reaches other props too (fire lights a drum; gas does not). |

`blast` takes the numbers of the built-in prop of that kind, and the dotted keys
change any of them — so the quickest custom blast is a `blast =` plus one or two
overrides. The declaration is pure: the same text gives the same prop, so a
replay and both co-op players read it identically.

### 3. Build it

```sh
oxtool props build <game-root> <name> [--against <prop>] [--dry-run] [--no-check]
oxtool props build <game-root> --all
```

It writes the five (or six) files beside `prop.ini`, reads its own `.sff` back
to be sure the sprites decode, then fields the prop the way `oxtool props`
does — stands it beside Kung Fu Man and checks it stands where it is put, draws
itself, and stays broken. For the example crate:

```text
built   kit_cargo_crate: 21 sprites
  check usable: stands where it is put, draws itself, stays broken
```

`--against <prop>` compares the result with another prop, line for line and
sprite for sprite — how the example proves the kit reproduces the shipped crate
(see [The example prop](#the-example-prop)).

### What makes a prop usable in a street

A street prop has to be a *thing*: it stands where it is put, draws itself, and
breaks for good. A bonus-game character is free to be something else — one draws
its own backdrop, one builds a car out of helpers around a root parked off to
the side, one zeroes its own life and leaves — and all of that reads fine on its
own bonus stage but wrong parked in a street. So the engine does not trust the
files: it *fields* each prop mid-fight the way the mode does — after the round
has begun, on the enemy team, marked a prop, beside a fighter who does nothing —
and watches it (`crates/oxyde-tool/src/props.rs`). A prop is **usable** only if
it does none of these:

| fault | what the probe measures |
|-------|-------------------------|
| dies on arrival | its root's life is gone within the first half second (30 ticks). |
| wanders | its root ends up more than **40 units** from where it was put — it must stay put. |
| draws nothing itself | its root shows no sprite, so whatever is seen is only its helpers — it must draw from its own root. |
| draws a backdrop | it, or one of its helpers, shows a sprite at least **480 world units** wide (a scene, not an object). Measured as drawn — the sprite's pixels times the character's `[Size]` scale and `localcoord` — so art made large and shown small is judged by its size on the stage. |
| does not stay broken | brought to zero life, it has life again later — a prop that heals itself cannot pay out once. |

Run the check yourself:

```sh
oxtool props <game-root>            # every bonus = 1 character and every knuckleup/props/ prop
oxtool props <game-root> --only <name>
```

It prints `usable` or `no` per prop, and for each `no` the reasons above. `oxtool
props build` runs the same probe on the prop it just wrote, so a prop built with
the kit is already known to pass.

### 4. Use it

Name it like any other prop. In a campaign, park it:

```ini
prop1 = kit_cargo_crate, at 900, score:2000   ; at a spot, or `prop1 = name, <wave>, <reward>`
```

or let the street dresser use it, per stage or for the whole run:

```ini
streetprops = kit_cargo_crate, oxyde_fuel_drum, oxyde_oil_drum
```

### 5. Auto-dress it by theme — `streetthemes.def`

To have a custom prop placed automatically in every stage of a matching theme
— without naming it in each campaign — add it to `knuckleup/streetthemes.def`.
The dresser reads this plain `.def` and parks props by stage theme:

```ini
[Theme docks]
keywords = dock, harbor, pier      ; substring-matched (case-insensitive) against
                                   ; the stage's file name; first theme to match wins
props    = my_neon_crate:2, oxyde_oil_drum:1   ; the breakable mix, name:weight
hazards  = oxyde_steam_vent:1                  ; timed hazards (optional)

[Theme generic]                    ; the fallback when no keywords match
props    = oxyde_cargo_crate:1
```

The file **merges onto the built-in themes**, so you only write what you change:
naming a built-in theme (e.g. `docks`) overrides it field by field — a line you
include replaces that field, a line you omit keeps the built-in's, a present-but-
empty line clears it; a new theme name is *added* and matched before the built-ins
in file order (so a more specific keyword wins). An absent or empty file leaves the
built-in dressing exactly as shipped. A prop name in `props`/`hazards` is a folder
under `knuckleup/props/`; what the prop *pays and does* (rewards, blast) stays in
that prop's own `.def [KnuckleUp]` section — the theme file only decides *where* it
appears.

### The example prop

`knuckleup/props/kit_cargo_crate/` is the kit's worked example: the PNGs that
OXYDE Cargo Crate was made from, handed to the kit as an author would. Building
it with `--against oxyde_cargo_crate` shows the kit does what the Python
generator that made the shipped crate did:

```text
cns: differs — scale on the burst effect only (the example's burst art is one
     still, shown larger; the crate's own logic is the same)
air: identical (37 lines that mean something, comments aside)
cmd: identical
sff: 21 sprites against 21; 21 in both
     standing pictures (groups 0, 6022, 6030, 6031) overlap 96–100%
```

The behaviour — life, damage steps, hitboxes, rewards, break — is the same; the
only difference is the look of the break flash, whose source art differs.

> The example `art/` is generated from the bonus-game source art by
> the kit pipeline (it also writes the template campaign's
> pickup skins). An author does not need that script; it is only how the kit's
> own example art is kept in step with the shipped crate.

## (b) A custom pickup skin

The floor pickups a run drops — health, power, score and the rest — are drawn
with built-in art. A campaign can replace any of them with its own PNG, without
touching the match: it is presentation only, so a replay plays the same with any
skin or none, and two online co-op players need not agree on it.

1. Make a folder `knuckleup/pickups/<folder>/` and drop a PNG per kind you want
   to reskin, named by the kind:

   ```text
   knuckleup/pickups/template/
     health.png    score.png    power.png
   ```

   The kind names are: `health`, `weapon`, `power`, `oneup`, `score`,
   `mystery`, `heal`, `fullhealth`, `charge`, `fullpower`, `boost`, `speed`,
   `shield`, `magnet` — fourteen in all. Any kind without a PNG keeps its
   built-in case. Paint at any size; the renderer resamples to the size it
   draws (the built-in cases are kept 112 pixels tall).

2. Point the campaign at the folder:

   ```ini
   [Campaign]
   pickups = template
   ```

   (The folder is looked for in `knuckleup/pickups/`, then beside the campaign
   file, then at the root.)

`oxtool campaign <file> --root <root>` lists which kinds it resolved:

```text
pickup      health -> knuckleup/pickups/template/health.png (knuckleup)
pickup      power  -> knuckleup/pickups/template/power.png  (knuckleup)
pickup      score  -> knuckleup/pickups/template/score.png  (knuckleup)
```

This is separate from the house-rules `pickups = full | classic` in
[CONFIGURATION.md](CONFIGURATION.md#knuckle-up), which chooses *which kinds* a
run drops. `[Campaign] pickups = <folder>` chooses *how they look*.

## (c) Difficulty

A campaign can say how hard its run is, with a preset and any number of
overrides, for the whole run in `[Campaign]` and for one stage in `[Stage x]`.

```ini
[Campaign]
difficulty = normal   ; easy | normal | hard
continues  = 4        ; continues after the last life; -1 = unlimited ([Campaign] only)
ailevel    = 5        ; how well the computer plays the enemies, 1-8
; enemylife = 110%    ; every enemy's life, bosses included (on top of `life`); 25%–400%
; enemyguard = 50     ; how readily enemies block, 0-100
; guardbreak = 3      ; blocks in a row before a hit breaks their guard; 0 = never
; guardbreakboss = 6  ; the same for a boss
; attackers = 2       ; enemies that close in and attack at once; 0 = all
```

The three presets set every knob at once:

| knob | easy | normal | hard |
|------|------|--------|------|
| `enemylife` | 75% | 100% | 130% |
| `enemyguard` | 25 | 50 | 75 |
| `guardbreak` | 2 | 3 | 5 |
| `guardbreakboss` | 4 | 6 | 8 |
| `attackers` | 1 | 2 | 3 |
| `ailevel` | 3 | 4 | 6 |
| `continues` | 5 | 3 | 1 |

A key you write overrides the preset; `normal` *is* the house default, so a key
over `normal` just moves that one knob.

### The rule: the player may make it easier, never harder

Whatever you set, a player who finds it too hard can turn their own Knuckle Up
Options down and the run eases; a player who turns their Options *up* changes
nothing you wrote. Each knob the campaign writes reads the player's option as a
nudge from NORMAL: an option set *easier* than the default eases your value by
as much (a multiplier by the same factor); an option at or above NORMAL leaves
your value alone. A knob you do **not** write stays entirely the player's, as it
always was — so a campaign that writes no difficulty at all plays exactly as it
did before this kit, and so does every tape of one.

`lives` joins the rule only on a campaign that writes a difficulty: there the
player's LIVES can add lives, never take them.

## (d) A boss

A Knuckle Up boss is **an ordinary self-contained character** — there is no
boss engine hook to write against. You make a boss the way you make any
character (see [BYOC.md](BYOC.md) and the FUSE/CNS docs); the campaign turns it
into a boss by naming it, and all the boss *framing* is campaign-side:

```ini
[Stage 3]
boss       = my_boss, 2.5     ; the character folder, and its life x its own
boss.at    = 1350             ; stage x where the boss arena is; screen locks there until it falls
boss.from  = right            ; which way it walks in
boss.music = boss.mp3         ; a track that takes over when it walks in
```

`boss`, `boss.at`, `boss.from`, `boss.music` and the life multiplier (clamped
1.0–20.0) are all read by the campaign — see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md). The mode gives the boss the
big bar along the bottom and holds the camera until it falls. Nothing about
being a boss is hardcoded in the engine.

**Special behaviour — phases, summoning — goes in the boss's own CNS/FUSE, not
in the engine.** The shipped `oxyde_hive_core` boss is the worked example: its
phases and its summon beam live entirely in its own FUSE
(`chars/oxyde_hive_core/`), driven by a convention an author can copy with
their own variable choices:

- `root.var(40)` — a **pose signal** the boss writes for its body to read: the
  anim to show, or `0` to let the body pick one from its damage stage.
- `root.var(41)` — the **phase** the body reports back (`0` awakened, `1`
  armour-cracked, `2` core-exposed), so moves can gate on how hurt it is.
- `root.var(42)` — a **summon counter**: the boss bumps it each time it fires
  its summoning beam, and a campaign wave or an engine/Lua hook that wants to
  beam a fighter in reads it. The signal is the variable; the beam, the portal
  ring and the ground hazard are all the boss's own states.

Pick your own `var` numbers — the convention is "write a signal your body and
the mode can read", not these exact indices. The boss stays a plain character:
it works in a normal match too, and a campaign is all that makes it a boss.

## How to test

Test every piece before you ship it; each check is also how the engine proves
it to itself.

```sh
# The prop builds, reads back, and can stand in a street:
oxtool props build <root> <name>            # builds + fields it
oxtool props <root> --only <name>           # "usable" / why not

# The campaign is well-formed and everything it names is installed:
oxtool campaign <root>/knuckleup/campaigns/<file>.knuckle --root <root>
#   resolves stages, props, enemies, music, pickup skins; reports difficulty

# Play it for real, headless, and save a tape you can replay bit-for-bit:
oxyde --headless --mode knuckleup --root <root> --frames 500 \
      --save-replay run.oxr --shot frame.png
OXYDE_KNUCKLE_CAMPAIGN=<name> oxyde --headless --mode knuckleup --root <root> ...
oxyde --headless --root <root> --replay run.oxr   # exits 1 if it diverged
```

Useful switches for a headless run:

- `OXYDE_KNUCKLE_CAMPAIGN=<name>` picks the campaign without the menu.
- `OXYDE_KNUCKLE_PICKUPS=<frame>` drops one of every pickup on that frame, so a
  `--shot` of it shows your pickup skins in play.
- `OXYDE_KNUCKLE_MASH=props` plays player one as a scripted fighter who walks up
  the street breaking every prop — a quick way to see a prop in action.
- `OXYDE_KNUCKLE_TRACE=1` prints the effective difficulty rules per stage
  (`attackers`, `enemyguard`, `enemylife`, …), so you can see a preset or an
  override take effect.

Nothing a difficulty adds is new replay state: the effective rules are a pure
function of the player's house rules (already on every Knuckle Up tape), the
campaign (whose identity a tape checks, and into which a written difficulty is
folded) and the recorded computer level — so a tape of any difficulty replays
bit-for-bit, and the replay format did not change. A pickup skin is presentation
and never reaches the tape at all.
