# Knuckle Up campaign format (`.knuckle`)

A campaign is one file that describes a belt-scroll run: its stages, and per
stage the title card and story, the waves of enemies, the boss, the props to
smash, the pickups, the music and the stage logic. It is **declaration, not behaviour** — a flat manifest the mode reads,
with the per-stage *logic* delegated to FUSE. This keeps the same split the rest
of the engine uses: `.knuckle` (and `system.def`, `select.def`) declare *what*;
FUSE and CNS script *how*.

- **Format:** INI, parsed by the same reader `system.def` uses
  (`crates/oxyde-app/src/campaign.rs`). Keys are case-insensitive; section
  names are `[Campaign]` and `[Stage <name>]`.
- **Where it lives:** `knuckleup/campaigns/` at the game root — the mode's
  own folder, with its stages, music, intros, logic, props, weapons and
  settings beside it (see [The `knuckleup/` folder](#the-knuckleup-folder)).
  The legacy `data/campaigns/` is still read, after it.
- **Validate one:** `oxtool campaign <file.knuckle> [--root <game-root>]` —
  parses it, prints what it declares, and reports any fault that would make it
  unplayable. With `--root` it also checks the campaign against the
  installation (stages, placements, props) and says where each path it names
  was found. `oxtool campaign --root <game-root>` checks every installed
  campaign. This is the executable spec; if a campaign disagrees with this
  page, trust the tool.
- **Play one:** choose Knuckle Up on the title menu. With more than one
  campaign installed, a list of them comes up; with one, it plays.
  `OXYDE_KNUCKLE_CAMPAIGN=<path, file name or campaign name>` picks one
  without the menu, and with no campaign at all the mode plays
  `rust_city.knuckle` (from `knuckleup/campaigns/`, else `data/campaigns/`).
- **Building a side-scrolling level** — a long street with waves, props and
  the boss placed along it — is [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md).
- **Making your own props, pickup skins and difficulty** — the author kit, with
  `oxtool props build` step by step — is
  [KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md).

Character and boss names are **roster folder names** (matched case-insensitively
against each installed character's folder or display name). A name that matches
nothing installed is dropped and reported, so a campaign still runs with
whoever it does have; a wave that resolves to nobody falls back to the mode's
own random draw.

---

## `[Campaign]`

| key | type | meaning |
| --- | --- | --- |
| `name` | text | The run's title. |
| `stages` | comma list | The stage section names, in play order — each needs a matching `[Stage <name>]`. Each stage is played on its own set, with its own card; the player's life carries over. |
| `lives` | number | Extra lives (default 2). A knockout with a life left brings the player back where they fell, on full life and briefly untouchable, instead of ending the run. The player's Options → KNUCKLE UP → `LIVES` can override it; continues, extra lives by score, enemy life, how many enemies attack at once, wave size and bonus props between stages are the player's too (see [CONFIGURATION.md](CONFIGURATION.md#knuckle-up)). |
| `life` | multiplier | The grunts' life, as a multiple of each character's own (`0.5`, `x0.5` or `50%`; 0.1–20). Default 1.0. |
| `time` | seconds | A clock on every stage, restarted with each wave; running out costs a life. Absent or `0` → untimed, the default: a brawler has no round clock, and the options' `[Rules] roundtime` is not used. Folded into the identity only when set. |
| `bonusgames` | `random`, `street` or a comma list | Where this run's bonus stages come from (see [Bonus stages between stages](#bonus-stages-between-stages)): any installed bonus game on its own stage, a prop parked in the street just cleared, or one of the named bonus games (`oxyde_crusher, oxyde_titan, car2`). Used when the player's `bonusgames` is `auto`, the default. Unwritten → `random`. |
| `bonusreward` | reward | What clearing a bonus stage pays, when the player's `bonusreward` is `auto`: any [prop reward](#prop-rewards). Unwritten → `mystery`. |
| `variety` | `full`, `light` or `off` | How far the player's [wave variety](#wave-variety) may recast this campaign's waves. It can only turn it down: `off` for a campaign whose line-ups are the point, `light` to keep each stage's own cast. Unwritten → the player's setting. Folded into the identity only when written. |
| `pool` | comma list | More fighters any stage's waves may be recast with, after that stage's own cast and its neighbours'. Never fielded unless a repeat needs replacing. Folded into the identity only when written. |
| `streetprops` | `auto` or `off` | Whether the player's [street props](#street-props) may dress this campaign's streets. It can only turn them off. Unwritten → the player's setting. Folded into the identity only when written. |
| `pickups` | folder name | The campaign's own art for the floor pickups: `knuckleup/pickups/<folder>/<kind>.png`, each kind falling back to the built-in case (see [Pickup skins](#pickup-skins)). Presentation only — not part of the identity, and never on a tape. Distinct from the house-rules `pickups = full/classic` in [CONFIGURATION.md](CONFIGURATION.md#knuckle-up), which chooses *which* kinds drop. |
| `difficulty` | `easy`/`normal`/`hard` | A preset for how hard the run is (see [Difficulty](#difficulty)). Folded into the identity only when written. |
| `continues` | number | Continues after the last life; `-1` unlimited. `[Campaign]` only. Over the preset. |
| `enemylife`, `enemyguard`, `guardbreak`, `guardbreakboss`, `attackers`, `ailevel` | number / multiplier | Individual difficulty knobs, each over the preset (see [Difficulty](#difficulty)). Each folded into the identity only when written. |

## `[Stage <name>]`

| key | type | meaning |
| --- | --- | --- |
| `title` | text | The heading on the stage's card. Empty → the section name (`rust_alley` reads RUST ALLEY). |
| `story1`, `story2`, … | text | Lines of story on the card, shown before the stage while the round waits. |
| `stage` | stage name or path | The MUGEN stage to fight on: a `.def` by path, looked for in `knuckleup/stages/` first (`stages/07_old_town/07_old_town.def` and `07_old_town/07_old_town.def` both find `knuckleup/stages/07_old_town/07_old_town.def`; so does `07_old_town`), then beside the campaign, then in the shared `stages/`; or the name of an installed stage, matched like `oxtool shot --stage` (`dock`). A path need not be in `select.def`, and a stage in `knuckleup/stages/` never appears in any other mode. Empty → the mode's default stage. |
| `life` | multiplier | This stage's grunt life, over the campaign's. |
| `time` | seconds | This stage's clock, over the campaign's `time`. |
| `pool` | comma list | More fighters this stage's waves may be [recast](#wave-variety) with, counted as the stage's own cast. Folded into the identity only when written. |
| `music` | filename | The stage's track, replacing the stage file's `bgmusic`. Looked for in `knuckleup/music/` (a leading `sound/` is read as "the music folder"), beside the campaign, then `data/campaigns/`, the archive and `sound/`. |
| `logic` | `*.fuse` | The stage's FUSE logic — hazards, breakable floors, reactive backgrounds — found in `knuckleup/logic/`, beside the campaign, or in `data/campaigns/`. It replaces any `[StageInfo] states` the stage names, for this campaign only. Empty → the stage's own, if any. |
| `intro` | `*.def` | A MUGEN storyboard played before the stage, found in `knuckleup/storyboards/`, beside the campaign, or in `data/campaigns/`; its sprites are read beside it. Empty → none. |
| `wave1`, `wave2`, … | `count, name, name, …` | One wave: a count, then the characters in it. Every name walks on together — `3, a, b, c, d` fields four — and the count is kept for the format (and the identity) but not read by the mode. A name may carry its own life: `aba*0.35`. Numbered from 1; read until the first missing number. There is no limit on how many waves a stage has — the demo's have seven and eight. With [wave variety](#wave-variety) on, a name may be recast. |
| `wave2.at`, … | stage x | The wave waits up the street until the leading player reaches this x, then walks in and the screen locks until it is down. Wave 1 opens the stage and ignores it. See [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md). |
| `wave2.from`, … | `right` / `left` | Where the wave walks in from: ahead (default) or behind the player. |
| `boss` | `name, mult` | The stage's boss and its life multiplier over its *own* life (`2.0` on a stage of `life = 0.5` grunts is four times a grunt). The boss is fought after the stage's waves, gets the big bar along the bottom of the screen, and the camera holds until it falls. `mult` clamps to 1.0–20.0. |
| `boss.at`, `boss.from` | stage x, `right`/`left` | As for a wave: where the boss arena is, and which way the boss walks in. |
| `boss.music` | filename | A track that takes over when the boss walks in; found like `music`. |
| `prop1`, `prop2`, … | `name, wave, reward` or `name, at X, reward` | A breakable prop — a prop character in `knuckleup/props/<name>/`, else a bonus-game character from the roster such as `car2` — parked in front of the player when wave `wave` walks in, or at stage x `X` from the start of the stage. Breaking it is optional and pays `reward`. It never holds the camera or the wave. `oxtool props` says which bonus props can do this. |
| `streetprops` | comma list, or `off` | What the player's [street props](#street-props) dress this stage with, instead of its theme's mix: names of props in `knuckleup/props/` (the dresser still draws three or four of them, by the run's seed; a timed hazard named here is placed as one), or `off` for none on this stage. Folded into the identity only when written. |
| `difficulty`, `enemylife`, `enemyguard`, `guardbreak`, `guardbreakboss`, `attackers`, `ailevel` | as in `[Campaign]` | This stage alone, over the campaign's difficulty (see [Difficulty](#difficulty)). `continues` is the whole run's, so it is `[Campaign]` only. Each folded into the identity only when written. |
| `pickup1`, `pickup2`, … | `kind, after_wave, amount` | A pickup that drops when a wave is cleared. `kind` is one of the kinds below, or `random` for a draw from the run's table; `after_wave` is the 1-based wave it drops after (`0` = at the start); `amount` is the effect's size (see below; `0` or nothing takes the kind's default). |

### Pickup kinds

| kind | effect |
| --- | --- |
| `health` | Restores `amount` life, up to the fighter's maximum. |
| `weapon` | Arms the fighter for `amount` ticks — they hit for half again as much until it runs out. |
| `power` | Fills `amount` of the super gauge. |
| `oneup` | `amount` extra lives (at least one). |
| `score` | `amount` points. |
| `heal` | `amount` **percent** of the fighter's life back (default 25) — sized to whoever takes it. Drawn as the health case with its cross half lit. |
| `fullhealth` | Life to full. The health case white-hot, with a MAX plate. |
| `charge` | `amount` percent of the super gauge (default 50). The power case half lit. |
| `fullpower` | The super gauge to full. The power case white-hot, with a MAX plate. |
| `boost` | POWER UP for `amount` seconds (default 15): the fighter's hits land for half again as much. |
| `speed` | SPEED for `amount` seconds (default 15): walking, along the street and up and down it, half again as fast. |
| `shield` | SHIELD for `amount` seconds (default 15): hits taken do half their damage. |
| `magnet` | MAGNET for `amount` seconds (default 20): pickups within 260 units drift to the fighter. |
| `rapidfire` | RAPID FIRE for `amount` seconds (default 12; also `rapid`): once a move has let its projectile go, the rest of it — the recovery — plays at double speed, and the super gauge is held full, so EX and super projectiles cost nothing. The character's own rules still hold: if it refuses a second fireball while one is out (`NumProjID`, `NumHelper`), it still refuses. A helper the hero makes in the move counts as the shot once it is a travelling attacker. The 1UP case with a Target Lab plasma bolt fired three times across it, in plasma aqua. |
| `random` | One drawn from the run's wave table (below). |

The kinds from `heal` down, and every kind other than `weapon` coming out as
itself, need `[KnuckleUp] pickups = full` — the default. Under `classic`, the
rule every run had before (and what a replay older than format 8 plays on), a
cleared wave drops 150 life unless the campaign names a drop, and a named drop
other than `weapon` comes out as `health` with the campaign's amount. The five
timed kinds wear their colour round the fighter while they run — a ring at
their feet and a spark circling them, blinking through the last two seconds —
and show under the hero's plate as their case and the seconds left.

**The run's drop table** (`pickups = full`). A cleared wave the campaign named
no drop for (or `random`) drops one of these, drawn from the run's seed, the
stage and the wave — so a replay meets the same drop: 25% health (23 in 100),
50% health (14), full health (6), 50% power (12), full power (6), POWER UP 15 s
(8), SPEED 15 s (7), SHIELD 15 s (7), MAGNET 20 s (6), RAPID FIRE 12 s (7),
2,500 points (4) — `knuckle::WAVE_TABLE_RAPID`, under `[KnuckleUp] droptable =
rapidfire` (the default). Under `droptable = weapon`, and on every replay older
than format 10, it is the table before RAPID FIRE: 25% health 26, 50% power 14,
points 6, the rest as above (`knuckle::WAVE_TABLE`). And
one fallen grunt in five drops something small where it lay — 500 points (40
in 100), 1,000 points (20), 10% health (25), 25% power (15) — never the boss.
The tables are `knuckle::WAVE_TABLE` and `knuckle::KO_TABLE`.

### Prop rewards

| reward | effect |
| --- | --- |
| `random` | One of the next four, drawn from the run's seed — the same run breaks the same car for the same prize. |
| `oneup` | One extra life. |
| `health:N` | N percent of each player's life back (default 50). `fullheal` is `health:100`. |
| `power:N` | N percent of each player's super gauge (default 100). |
| `score:N` | N points (default 5000). |
| `continue` | One more continue — or, when continues are unlimited, 10,000 points. |
| `invincible:N` | Nothing can hurt the heroes for N seconds (default 10). |
| `multiplier:N` | Every point scored counts twice for N seconds (default 20); also `double`. |
| `surge:N` | The super gauge stays full for N seconds (default 15). |
| `weapon:N` | The heroes are armed for N seconds (default 20): they hit half again as hard, as a weapon pickup arms them. |
| `rapidfire:N` | RAPID FIRE for N seconds (default 12) on every hero standing, as its floor pickup gives it; also `rapid`. |
| `jackpot` | Half a bar of life, a full gauge and 10,000 points at once. |
| `mystery` | Any of the above, drawn from the run's seed: the everyday rewards twice as often as a 1UP, a continue, a full heal, the surge or the jackpot. Under `droptable = rapidfire` (the default) the draw that was the weapon is RAPID FIRE 12 s. |

**The weapon is out of the tables for now.** No weapon art has been added yet,
so the WEAPON pickup armed a hero with nothing to see. `[KnuckleUp] droptable =
rapidfire`, the default, puts RAPID FIRE in its place wherever a *table* drew it
— a street prop's prize, the mystery draw, the pickup waiting beside the
opening health at the start of every street — and adds it to a cleared wave's
table. A campaign, a prop or a `bonusreward` that **names** `weapon` still gets
the weapon, and `droptable = weapon` puts the tables back as they were. The
setting is on the tape (replay format 10); a tape older than that plays on the
weapon tables it was recorded with.

Every prop broken is also worth 3,000 points. The timed rewards show as small
cases under the hero's plate with their seconds, carry from stage to stage and
count down only while a stage is being fought, so one paid by a bonus between
stages is spent on the next stage. `random` keeps its four outcomes, drawn
exactly as before, so a tape recorded before the newer rewards existed pays
what it paid.

A prop has to be a self-contained breakable that stands where it is put and
breaks when its life runs out. `car2` (the Mercedes) is. Of the other bonus
props in this archive, `sf2bricks` and `bonus2` draw their own backdrop,
`FF2BreakCar` builds the car out of helpers around a root parked off to one
side, and `oildrumbonus`'s root zeroes its own life and leaves the screen the
moment it starts — all of them only make sense on their own bonus stage. A prop
whose life is already gone when it is first seen pays nothing.

### Bonus stages between stages

Now and then — the player's `bonus` setting: never, sometimes, after every
stage — the run stops between two campaign stages for a sixty-second bonus.
Which one, and where, is `bonusgames` (the player's, else the campaign's):

* **`random`** (what `auto` comes to when the campaign says nothing): an
  installed bonus game — every `select.def` entry with `bonus = 1`: the ten
  OXYDE bonus games, the car, the barrels, the bricks, the bag — drawn from
  the run's seed and **played on its own stage**, as in Bonus Rush. The hero's
  life carries over, nobody from the campaign is fielded, the round is played
  on the plane (up jumps and down crouches, as the bonus games ask), and it is
  cleared when the bonus game is broken or, for a damage game such as the
  bag, when its damage target is met. A bonus game with no stage of its own
  (`car2`) is parked in the street just cleared.
* **a list** — `bonusgames = oxyde_crusher, oxyde_titan, car2` — the same, drawn
  only from those (folder names; one the roster does not have is passed over).
* **`street`**: a prop the campaign parks somewhere, or `car2`, parked in the
  street just cleared — what every run did before the setting existed.

Cleared, it pays `bonusreward` (the player's, else the campaign's, else
`mystery`), 3,000 points and 100 points for every second left on its clock;
`TIME UP` pays the damage done. Then the run goes on to the next stage. A
bonus game counts its sixty seconds down on the round clock (a street is
untimed) and never costs a life.

**In co-op** the reward and the 3,000 go to whoever landed the breaking blow,
as a parked prop's do; the time bonus is the team's, shared between the
players still in the run; health and power reach every hero standing; and the
timed rewards (invincible, double points, surge, armed) are the team's — every
hero standing is covered, and double points doubles what each player scores
for themselves.

Online co-op keeps the street. A tape recorded before these settings existed
(before replay format 6) carries none and is played back with `street` and
`random`, so it meets the bonus it met.

### The score

A point for every point of life taken off an enemy, 500 for a knockout, 5,000
for a boss, and half a point per point of damage to a prop. Lives and score sit
under the player's count on the HUD; every enemy carries a slim bar with its
name over its head, longer for more life.

---

## A worked example

```ini
[Campaign]
name   = Knuckle Up: Rust City
stages = rust_alley, rust_docks
lives  = 2
life   = 0.5                ; grunts on half their own life

[Stage rust_alley]
title   = Rust Alley
story1  = The Rust gang runs the old quarter now.
stage   = bckalley          ; a real installed stage
wave1   = 2, aba*0.35, abubo*0.35
wave2   = 3, Acid, aba, abubo
prop1   = car2, 2, random   ; a parked Mercedes during wave 2
pickup1 = health, 1, 250    ; 250 life, dropped after wave 1
boss    = adon, 2.0         ; four times a grunt

[Stage rust_docks]
title   = The Docks
stage   = dock
life    = 0.6
wave1   = 2, adel, kfm
pickup1 = oneup, 1, 1
boss    = Guy, 2.4
```

Check it (the demo at `knuckleup/campaigns/rust_city.knuckle` is the full
three-stage version):

```
$ oxtool campaign knuckleup/campaigns/rust_city.knuckle
campaign  Knuckle Up: Rust City
identity  0x…
lives     2
stages    3
  rust_alley       2 wave(s), 5 enemies, boss adon x2.0, 1 pickup(s), prop car2 (wave 2, BONUS), life x0.35-0.50
                   "Rust Alley"
  …
OK — well-formed.
```

## Wave variety

A campaign lists every wave's enemies by name, and a themed stage has a small
cast: OXYDE: Long Run gives each stage six to nine grunts for its 27 slots, by
rotating through them, so each wave shares names with the last. As written,
90 of its 270 grunt slots are someone from the wave before, 193 are someone
already fought on the same stage, and a fighter is typically back two waves
later. The player's `[KnuckleUp] wavevariety` (Options → KNUCKLE UP → `WAVE
VARIETY`) recasts those slots when a run is built:

| setting | what it takes out | Long Run (any seed) |
| --- | --- | --- |
| `full` (default) | the same fighter twice on screen; anyone from the last two waves; anyone already fought on this stage, while the campaign has someone left to send | 0 from the wave before, 0 again on a stage; back after 18 waves typically (3 at least) |
| `light` | the same fighter twice on screen; anyone from the last three waves. Prefers the stage's own cast, so the theme holds | 0 from the wave before, 76 again on a stage; back after 5 waves typically (4 at least) |
| `off` | nothing: the waves exactly as written | 90 from the wave before, 193 again on a stage; back after 2 waves typically (1 at least) |

A slot keeps the fighter the campaign wrote for it when that one passes; one
that does not is recast from the campaign's own grunts — the stage's own cast
first (with `full` whoever has fought least on the stage and then in the run),
then its neighbours' (an earlier stage before a later one), then the
`[Campaign] pool`. What stays as written: the bosses (never recast, and never
cast as a grunt), each wave's size, where and when it walks in and from which
side, and each slot's life and toughness tier. Props and the heroes are never
cast. WAVE SIZE's extra enemies, which repeat the wave's own names, are recast
too, so a bigger wave is not the same grunt twice. When nobody else is left,
the written fighter stays — variety never empties a slot.

The recast is drawn from the run's seed (a replay carries it, so a tape plays
the same line-up back, and both co-op players get the same one) and keyed by
each fighter's path, not its place in the roster. `OXYDE_KNUCKLE_TRACE=1`
prints every wave as it will walk on (`kwave`), with `new<-written` for each
recast slot; `oxtool campaign --root R [--seed N]` prints the numbers above
for any campaign:

```
repeats:
  written   270 slots, 77 fighters: 0 twice on screen, 90 from the wave before, 193 again on the same stage, 193 again in the run; back after 1 wave(s) at least, 2 typically
  light     270 slots, 77 fighters: 0 twice on screen, 0 from the wave before, 76 again on the same stage, 193 again in the run; back after 4 wave(s) at least, 5 typically; 204 slot(s) recast from a cast of 77
  full      270 slots, 77 fighters: 0 twice on screen, 0 from the wave before, 0 again on the same stage, 193 again in the run; back after 3 wave(s) at least, 18 typically; 197 slot(s) recast from a cast of 77
```

"Again in the run" cannot fall without more fighters: 270 slots from a cast of
77 is each one three or four times. A campaign widens its cast with `pool`
(`[Campaign] pool = …` for any stage, `[Stage x] pool = …` for one) — names
that are fielded only when a repeat needs replacing — and narrows the recast
with `[Campaign] variety = light` or `off`. Both are folded into the identity
only when written, so the shipped campaigns, and every tape of them, are
unchanged.

## Street props

Streets are for fighting and breaking things and getting bonuses. A campaign
parks what it wants with `propN`; on top of that the
player's `[KnuckleUp] streetprops` (Options → KNUCKLE UP → `STREET PROPS`,
`auto` by default, or `off`) dresses every street with three or four breakable
props and, where the street has them, one or two timed hazards, chosen by the
stage's theme. The props are built from the bonus-game art
(through the bonus games' own pipeline)
and live in `knuckleup/props/`:

| prop | what it is | breaking it |
| --- | --- | --- |
| `oxyde_cargo_crate`, `oxyde_strongbox`, `oxyde_gold_crate` | Conveyor Carnage cargo, in its four damage states | drops a small, a medium or a score-heavy prize |
| `oxyde_oil_drum` | **kickable**: hit, it flies away from you and knocks down the first fighter in its path, enemy or hero — then settles, to be kicked again until it breaks | a small prize |
| `oxyde_fuel_drum` | **volatile**: a hit (or a blast) lights it — sparks, a flicker that speeds up — and two-thirds of a second later it explodes | a fireball that knocks down everyone close, and a small fire |
| `oxyde_toxic_drum` | **volatile**: bursts into a gas cloud | four seconds of gas that eats at whoever stands in it |
| `oxyde_power_cell` | **volatile**: a Reactor Meltdown node | a shock ring that stuns everyone in reach |
| `oxyde_armoured_car` | the Crusher Yard car, at the back of the street, in four damage states, throwing its parts | the big prize, a big explosion, and a wreck that burns for six seconds |
| `oxyde_steam_vent`, `oxyde_fire_vent`, `oxyde_shock_plate` | **timed hazards**, never hit or broken: each hisses, smoulders or sparks for about a second, then bursts | a knockdown (the vents) or a stagger (the plate) for whoever stands on it |

**What each street gets** is decided by the first word in the stage's file
name that matches a theme (`oxyde_app::street::THEMES`): docks and streets get
the car, cargo and fuel; the foundry fuel drums and fire vents; the sewer and
the wasteland toxic drums; the research facility and the core power cells and
shock plates; the old town crates and the car. A stage matching none gets
crates and drums. `oxtool campaign --root R [--seed N]` prints, per stage, the
theme and what a run on that seed is dressed with.

**Where.** Spread along the street from a little way past where the heroes
start to just short of its end, off the campaign's own props, each at a depth
drawn from the run's seed (the car at the back). A timed hazard stands to one
side of the walkable strip, never across it, so there is always a way past.
Props never push or block anybody.

**What it pays.** Each prop's prize is drawn from the run's seed from its own
table (`street::CATALOG`): a crate drops 15% health, points or a little power;
the gold cargo a lot of points; the car 60% health, RAPID FIRE, a 1UP, points
or the jackpot (the strongbox and the car listed the weapon, and still give it
under `droptable = weapon`). A street prop's prize **drops where it stood as the
floor pickups a wave leaves** — health, power, points, a 1UP, RAPID FIRE or a
weapon; the jackpot as three
of them — and only a timed reward (DOUBLE POINTS, a surge) is paid at once,
with its banner. Breaking one is worth 3,000 points as any prop is.

**Blasts** (`oxyde_core::blast`) are neutral: they hit enemies and heroes
alike, so luring a wave onto a drum is the point and standing next to it is the
risk. A blast lands as a real hit — a knockdown thrown away from it, or a
stagger for a shock — through each fighter's own get-hit states and
invulnerability; its damage is capped at a fifth of a bar and it never knocks
anybody out. A blast never breaks a prop: it dents a crate, and lights any
volatile prop in reach, which blows on its own fuse — a chain reaction with a
beat between links. Every enemy caught is worth 750 points (BLAST BONUS) to
whoever set it off; one caught by a timed hazard, to the hero nearest it.

**Replays.** The setting is on the tape (format 9); a tape from before it reads
`off` and plays its streets exactly as recorded. The dressing comes only from
the campaign, the run's seed and the stage's bounds, so a replay — and both
co-op players — meet the same props in the same places. Online co-op parks no
props at all.

## Difficulty

A campaign can say how hard its run is, instead of leaving all of it to the
player's house rules. A preset sets every knob at once, and any knob key over it
changes just that one — in `[Campaign]` for the whole run, in `[Stage <name>]`
for one stage over the campaign's.

```ini
[Campaign]
difficulty = hard     ; easy | normal | hard
continues  = 2        ; [Campaign] only; over the preset

[Stage the_docks]
difficulty = hard     ; this stage harder than the rest
attackers  = 3        ; and one knob over even that
```

The presets:

| knob | easy | normal | hard | meaning |
|------|------|--------|------|---------|
| `enemylife` | 75% | 100% | 130% | every enemy's life, bosses included, on top of `life` (25%–400%) |
| `enemyguard` | 25 | 50 | 75 | how readily enemies block (0–100) |
| `guardbreak` | 2 | 3 | 5 | blocks in a row before a hit breaks their guard (0 = never) |
| `guardbreakboss` | 4 | 6 | 8 | the same for a boss |
| `attackers` | 1 | 2 | 3 | enemies that close in at once (0 = all) |
| `ailevel` | 3 | 4 | 6 | how well the computer plays them (1–8) |
| `continues` | 5 | 3 | 1 | continues after the last life (−1 = unlimited) |

`normal` is the house default, so a key over `normal` moves only that knob.

**The player may make it easier, never harder.** For every knob the campaign
writes, the player's own Knuckle Up option is read as a nudge from `normal`: an
option set *easier* eases the author's value by as much (a multiplier by the
same factor); an option at or above `normal` leaves it alone. A knob the
campaign does **not** write stays entirely the player's, exactly as before — so
a campaign that writes no difficulty plays as it always did, and so does every
tape of one. On a campaign that writes a difficulty, the player's `LIVES` can
only *add* lives. (See `crate::difficulty` for the arithmetic.)

**Replays.** Nothing here is new tape state. The effective rules are a pure
function of the player's house rules (on every Knuckle Up tape), the campaign
(whose identity a tape checks, and into which a written difficulty is folded)
and the recorded computer level — so a tape of any difficulty replays
bit-for-bit and the replay format did not change.

## Pickup skins

`[Campaign] pickups = <folder>` draws the floor pickups with the campaign's own
art instead of the built-in cases: a PNG per kind at
`knuckleup/pickups/<folder>/<kind>.png`, with every kind that has no PNG keeping
its built-in case. The kind file-stems are `health`, `weapon`, `power`,
`oneup`, `score`, `mystery`, `heal`, `fullhealth`, `charge`, `fullpower`,
`boost`, `speed`, `shield` and `magnet`. The folder is looked for in
`knuckleup/pickups/`, then beside the campaign, then at the root.

This is **presentation only**: the match never sees it, so it is not part of the
identity, it never reaches a tape, and two online co-op players need not agree
on it — a replay plays the same with any skin or none. It is separate from the
house-rules `pickups = full/classic` ([CONFIGURATION.md](CONFIGURATION.md#knuckle-up)),
which chooses *which* kinds a run drops. Making the PNGs is in
[KNUCKLE-UP-AUTHORING.md](KNUCKLE-UP-AUTHORING.md).

## The `knuckleup/` folder

Everything that belongs to Knuckle Up and to no other mode has one home, a
folder at the game root:

```
knuckleup/
  knuckleup.cfg    the mode's settings ([KnuckleUp]); overrides oxyde.cfg's
  campaigns/       *.knuckle, or <name>/<name>.knuckle with its own files beside it
  stages/          belt stages, one folder each; never offered by another mode
  props/           prop characters only Knuckle Up parks (<name>/<name>.def);
                   <name>/prop.ini + art/ is a prop built with `oxtool props build`
  pickups/         pickup skins: <kind>.png, and <folder>/<kind>.png for `[Campaign] pickups`
  weapons/         weapon pickups (<name>/<name>.def; data/weapons/ is the legacy home)
  music/           campaign and boss tracks
  storyboards/     stage intros and their sprites
  logic/           per-stage FUSE logic
  README.md        a short authoring guide
```

**How a path is found.** Every path a campaign names — `stage`, `music`,
`boss.music`, `intro`, `logic`, a prop — is looked for in this order:

1. `knuckleup/<kind>/`. A leading legacy folder in the value is read as "the
   folder for this kind": `stages/x/x.def` finds `knuckleup/stages/x/x.def`,
   `sound/a.mp3` finds `knuckleup/music/a.mp3`. A stage or prop can also be
   named by its folder (`stage = 07_old_town`).
2. The campaign's own folder (for `knuckleup/campaigns/town/town.knuckle`,
   `knuckleup/campaigns/town/`).
3. The legacy places: `data/campaigns/`, the root, `stages/` (and the installed
   stage list, by name), `sound/`, `data/weapons/`, the roster.

So an install with no `knuckleup/` folder plays exactly as before, and a
campaign that names a shared stage (`stage = dock`) still gets it. A stage in
the folder joins the stage list only for the run that plays it, and is gone
again when another mode starts; a prop in `knuckleup/props/` is a prop to the
roster, so the select screen, every random draw and the bonus games skip it.

**Why a campaign keeps its spelling.** A campaign's paths are part of its
content identity (`oxtool campaign` prints it), which a Knuckle Up replay
records and an online co-op peer compares. Reading `stages/` in a campaign as
"the stage folder" is what lets content move into `knuckleup/` without editing
the campaign — so every tape recorded before the move still finds and checks
its campaign, and a peer who has moved their content can still play one who
has not. A tape that names `data/campaigns/rust_city.knuckle` finds
`knuckleup/campaigns/rust_city.knuckle`, and failing that, any installed
campaign with the recorded identity.

**The campaign list** is `knuckleup/campaigns/` (and one folder down), then
`data/campaigns/`; a legacy file with the same file name or the same content
as one in the folder is listed once, from the folder.

**Moving an older install in:**

```
oxtool knuckle migrate <game-root> --dry-run    # what it would do
oxtool knuckle migrate <game-root>              # copy it in
oxtool knuckle migrate <game-root> --move       # and remove the legacy copies
oxtool knuckle migrate <game-root> --out DIR    # write the folder somewhere else
```

It copies, for every campaign in `data/campaigns/`, the campaign itself, the
belt stages it names by path (a stage's whole folder, or a loose `.def` alone),
its music, intros and logic, private props, and the `data/weapons/` set. It
leaves alone what another mode uses — a stage `select.def` lists or a stage
named by name, a prop `select.def` lists (a bonus game), a track another stage
also plays — and prints which legacy copies are then duplicates nothing else
needs. Campaigns are copied unedited, and the report shows each identity
unchanged. It writes `knuckleup.cfg` from the root's `oxyde.cfg [KnuckleUp]`
if it has one, else as the all-commented template.

## What makes a campaign unplayable

`oxtool campaign` reports these as faults (and the loader refuses on them):

- No stages at all.
- A stage with no waves and no boss (nothing to fight).
- A wave with zero enemies.
- An unknown pickup kind.
- A prop with an unknown reward, or parked for a wave the stage does not have.
- A `[Campaign] bonusreward` that is not a reward.
- A `[Campaign] variety` that is not `full`, `light` or `off`.
- A wave or boss `from` that is neither `left` nor `right`.

It also prints **notes** — things that play but are probably not meant: a
`wave1.at` (ignored), a placement behind the one before it, and with `--root`
a stage that is not installed, a placement past where a fighter can walk (in
the stage's own coordinates), a prop that cannot stand in a street, an enemy
or boss name that matches nobody in the roster, a name that an earlier
character's display name captures (`slash` resolves to `eslash` on this
archive: write the folder name), and a `music`, `boss.music`, `intro` or
`logic` file that is not installed. With `--root` it also prints a
**resolved** block: each path the campaign names, the file it found, and
where (`knuckleup`, `beside campaign`, `legacy`, `installed stage`).

A *missing character* is not a fault — it is dropped (and, with `--root`,
noted), so a campaign is portable across installs that have different rosters.

---

## Where behaviour lives (so you know what goes where)

- **In the `.knuckle`:** the run's shape — which stages, which enemies and on
  how much life, the boss, the props and pickups, the lives, the cards, the
  music and intro references.
- **In FUSE (`logic = *.fuse`):** the stage's *behaviour* — hazards, breakable
  floors, reactive backgrounds. See [STAGE-LOGIC.md](STAGE-LOGIC.md). This runs
  inside `step()` and is deterministic, so a campaign played in co-op or over a
  link behaves identically on both machines.
- **In Lua / MUGEN assets:** presentation — the `music` and `intro` a campaign
  names are played and shown outside `step()`.

See [KNUCKLE-UP.md](KNUCKLE-UP.md) for the mode's design and the determinism
boundary that decides which side of this line each feature falls on.
