# Bonus stages

There are two kinds here, and they are not the same thing.

**Bonus games** are the MUGEN kind: a character file that is really a prop —
the car, the barrel stack, the drum — which you break for points between
arcade matches. MUGEN has no way to say that a roster entry is one, so every
such file sits on the character select grid between two real fighters and can
be picked for a versus match it has no attacks for. The next section is the
system that fixes that.

**Bonus Rush** and **Versus Bonus** are the two modes on the title menu named
after them. Both play the bonus games your installation declares — every one,
in `select.def` order, each on its own stage, sixty seconds each — and finish
with **Beat Up**: a round against a random fighter from the roster. Bonus Rush
is one player alone; in Versus Bonus both players are at each game **at the
same time**, facing each other across the shared prop, and the higher **score** —
the damage each deals the prop — takes it. An installation that declares none gets the
engine's nine procedural stages instead, two players at once, and the two of
them can hit each other the whole way through. That is the rest of this page.

### A prop is not player two

A bonus game's character is fielded on side two because that is where MUGEN
puts it, but nothing about it is drawn as an opponent. There is no VS card
before the run, and the fight HUD is replaced by a band of its own, drawn in the
fight HUD's language (`crates/oxyde-app/src/bonus_ui.rs`): the player on the
left with their portrait in an octagon, a `P1` chip, their name and their one
life bar; the clock in its octagon in the middle, with a tab hanging from it
that says which game of the run this is and its name; and on the right, on a
glass plate, the damage landed on the prop — the prop *and* every helper it
fields, since a barrel stack's root keeps a full bar until the last barrel
breaks — with the target and a progress foot when there is one, or, once it is
down, how long it took. In Versus Bonus player two takes the right-hand corner,
mirrored, each player's damage on a plate under their own bar, and once the game
is decided a banner says who took it. A card introduces each game while the
round is called: what it is and what to do.

Everything the band draws across the middle of the screen ends above line 35
of 240, so a prop that draws its own counter there — the OXYDE Bonus Trials'
`TITAN 02 / 06` is a screen-space explod at line 36 — reads as the next line
under the clock's tab at every window size (`bonus_ui::band_clears_the_prop_counter`).

The run's results fit the window: the headline at the top, the prompts along
the bottom, and one row per game between them — in two columns when eighteen
games will not fit in one — rather than a table that ran off the bottom.

### Versus Bonus: two players, one prop, at once

Both players pick their fighter **at the same time**, each in their own column
with their own cursor, exactly as a Versus match does — not one after the other.
Both are then fielded on side one, but on **opposite sides facing in**, with the
prop centred between them, so the mode plays as a duel for the same target rather
than two people smashing side by side. The prop on side two is nobody's. Each is
credited with what **their own** hits land: the fighter's moves, their helpers'
and their projectiles', counted against the root whose move it was
(`Player::dealt_damage`, kept by the simulation as each hit lands).

The winner is decided on **score**, not on the breaking blow: whoever dealt the
prop the most damage takes the game. A tie on score goes to whoever took the
**least damage**, and level on both is a draw; a game that runs out the clock is
settled the same way on the standing scores. Landing the blow that breaks the
prop no longer wins a game by itself. Most games taken wins the run.

The two **cannot knock each other out** — both are held immortal so a prop can
never end a go (`shield_bonus_player`) — but the damage each takes is still
counted, because it is the tiebreak when two scores are level. Beat Up is the
same: both against one computer fighter, neither able to be knocked out, scored
the same way.

Versus Bonus is **local only**: it is not one of the online modes, so the seating
and the scoring never cross a link. The scoring reads only what the simulation
already decided, so a replay of a run scores it the same way again.

**Broken** means knocked out. A go that runs out the clock is scored on damage,
even when the prop has lost more of its bar than the player has: a round
decided on life is not a prop broken in sixty seconds.

---

## Bonus games: telling the engine a roster entry is a prop

Add `bonus = 1` to the entry in `select.def`, exactly where you would write
`order` or `ai`:

```
[Characters]
kfm, stages/stage0.def
car2, stages/carbg2.def, bonus = 1
```

or, if you would rather keep them together, list them in a `[BonusGames]`
section, which takes the same entry format and needs no keyword:

```
[BonusGames]
car2, stages/carbg2.def
barrels
```

A bonus entry keeps everything a character entry has — its stage, its music,
its palettes, its `.def`. The stage is the one the game is played on, even when
the player's fighter has a stage of its own in `select.def`: the prop's side is
asked first (otherwise Ryu, paired with `stages/flames.def`, would break every
prop on Flames of Destiny). What it loses is its place among the fighters:

* it is **not on the select grid**, and typing its name into the search finds
  nothing;
* it is **never drawn at random** — not for a random slot, not as an arcade
  opponent, not in Watch, not in the attract-mode demo;
* the roster counter counts what you can pick, so it does not count this.

### Where they are played

In the arcade ladder, between fights. `[Options] bonus.interval` says how many
opponents are beaten between one bonus game and the next; it defaults to three,
which is where the arcade games this archive imitates put theirs, and `0`
switches them off. The declared games are taken in `select.def` order and wrap,
and two never run back to back.

A bonus game is one round of **sixty seconds** however the match is set up, and **it cannot end
your run in either direction**: beating the prop does not shorten the ladder,
and failing to break it before the clock runs out is not a defeat. The round
banner says `BONUS STAGE` instead of `OPPONENT 4 / 8`.

**A prop that hits back can knock you out.** The OXYDE Bonus Trials' titan,
drones, robots, reactor, train, conveyor and gas all hit to knock out
(`kill = 1`), and a player whose bar reaches zero is knocked out as in any
fight: the go ends there and is scored as a knockout — `KO 340 DMG` in the
results, `KNOCKED OUT` on the band — rather than going on at one point of
life. It is still not a defeat: the run goes on to the next game. In Versus
Bonus a player who is knocked out sits out the rest of that game while the
other carries on; the game ends when the prop is broken, the clock runs out or
both are down, and a player still standing at the end takes it over one on the
floor, whatever the damage (two knocked out: the damage decides). Knuckle Up's
bonus rounds between stages never cost a life, so there the heroes' bars stop
at their last point instead.

### The ones in this archive

Seven, all declared `bonus = 1` in `data/select.def`, and the interval there is
the default three — so an arcade run plays one after the third fight, the sixth
and so on. Change `[Options] bonus.interval` to `2` for more of them, or `0`
for none.

| Entry | What it is |
|---|---|
| `car2` | `displayname = "Mercedes Benz"`: a car with no attacks, whose own readme tells you to add it to `[Characters]` because in MUGEN there is nowhere else to put it |
| `sf2bricks` | the SNES Street Fighter II brick pyramid |
| `oildrumbonus` | SFII's oil drums — breaking the bottom one drops the stack |
| `bonus2` | barrels and panes of glass, by SUGIO |
| `SUV` | SFIII 3rd Strike's car, built on the same prop as `car2` |
| `FF2BreakCar` | Final Fight 2's car, with its own stage and music |
| `PunchingBag` | a heavy bag that takes anything and hits nothing back |

### When a bonus game is complete

A game is **cleared the moment the prop is completely broken** — every brick,
every barrel, the whole car — and the time it took is what is scored. A prop
partly broken when the clock runs out is scored on the damage done. Every prop
in this archive says "completely broken" the same way: its own root fighter,
which is invisible and stands off to one side, takes its life to zero once its
last piece is gone. So the engine needs no list of props; it needs the prop's
own logic to run as MUGEN runs it.

| Entry | Its pieces | Completely broken when | Measured |
|---|---|---|---|
| `car2` | the car itself | its life runs out | broken in 32.4 s by the computer |
| `sf2bricks` | five brick layers, as helpers | the root falls with the last layer | 15–25 s by the computer (Kung Fu Man, Ryu, Mech Sagat, Guile; one time-out in eight), at 450 life a layer |
| `oildrumbonus` | six drums, as `helpertype = player` helpers | no drum is left (`NumHelper` of all six is 0) | 16.0 s with one-hit drums, so the end is not an artefact of skill |
| `bonus2` | barrels and glass it drops from a perch | its life runs out | 39.1 s by the computer |
| `SUV` | the car, its doors and glass, as helpers | its life runs out | at 36.2 s under a scripted attacker |
| `FF2BreakCar` | grill, both sides and a window, as helpers with five stages of damage each | grill, right side and window all on their last stage | 40.5 s under a scripted attacker at 180 a stage |
| `PunchingBag` | the bag | **a damage target**, below | — |

Several engine behaviours are what let these props reach their ending, and a
prop author relies on them:

* a UTF-8 byte-order mark in front of `[Data]` is skipped, so a file that opens
  with one still has its constants read — without that, `FF2BreakCar`'s parts
  read their life as 0 and fall apart as they are built;
* a helper whose life runs out is kept in the round, as MUGEN keeps it, running
  its states with `Alive` reading 0, so half-broken car parts do not vanish;
* `GetHitVar(damage)` reads the last hit for one tick only, so one kick advances
  a part by a single damage stage rather than running it through all five; and a
  hit a `HitOverride` catches costs life even when the state it leads to is not a
  get-hit state, which is how the car's parts count damage in a var;
* `NotHitBy value = SCA, AA, AP, AT` reads the `A` ("all") attack class, so it
  protects as written — otherwise the car's invisible pusher takes a special and
  flies off the stage;
* and a knocked-out fighter who never lands — `bonus2`'s dead dropper hangs in
  the air — does not hold the round open for ever, because the wait for the
  landing is not capped on a clock that same wait stops.

Three more behaviours matter for breakable helpers and invisible roots:

* the rescue that removes a helper knocked into the common get-hit states counts
  only the common standing, crouching, walking and landing states as "back on
  its feet", not *any* state under 200: `sf2bricks`'s layers live in their own
  states 1–4 and catch every hit into their own `movetype = H` state 5005, and
  counting any low state would remove every layer two ticks after the first hit
  landed on it — a 12-damage jab taking a 250-life layer, and the pyramid
  falling in 1.6 to 5.2 seconds;
* a `HitDef` whose owner's `movetype` is I is held back until the state is A or H
  (and kept armed), as WinMUGEN does: `sf2bricks`'s "hit fall detector" holds
  one up every tick a fighter stands on the pyramid and lets it land only when
  they walk off the edge, so without this the fighter is re-hit into 5000 every
  tick and frozen in the air for the rest of the game;
* the rescue that hands control back to a fighter idle in state 0 leaves alone a
  fighter whose own code takes control away every tick, such as `oildrumbonus`'s
  invisible root. Were it handed control, the computer would walk the root, its
  `stand.friction = 100` multiplying the walk to infinity, and the root — the
  thing a fighter turns to face — would swing from one end of the stage to the
  other every tick.

### A damage target: the punching bag

A prop with nothing to break is cleared by dealing a set amount of damage in the
sixty seconds instead. The band reads `DAMAGE 1234 / 2000` while it runs and
`TARGET MET IN 41.3S` once it is met; the card says `DEAL 2000 DAMAGE IN 60
SECONDS`. In Versus Bonus the two players' damage counts **together** to meet
the target, but the game still goes to whoever's own score was higher when it
was met, not to whoever landed the hit that reached it.

Declare it in `select.def` with `bonus.target`:

```
PunchingBag, stages/sf2tbonus.def, bonus = 1, bonus.target = 2500
```

With nothing declared, a prop with more than 4,000 life — nothing in this
archive that is meant to be broken has more than 1,200, and the bag has 5,000 —
gets the default target of **2,000**. That number was measured: 48 fighters
drawn from the roster, each set on the bag by the computer for the full sixty
seconds, dealt between 332 and 5,000 — eight broke the bag outright — with a
median of 3,542, and 40 of the 48 reached 2,000. The computer is a clumsy
player, so a person who keeps hitting the bag clears it, and one who stands
about does not.

All but `car2` were installed from `bonus/` by `bonus/install_bonus.py`, which
writes the block between the `--- begin bonus games ---` markers in
`select.def`. Adding another is one line in that file with `bonus = 1` on it;
nothing else has to change.

### Building one: the OXYDE Bonus Trials

The OXYDE Bonus Trials are built by the bonus-pack pipeline into
`install/` (`install/README-bonuspack.md` lists them and how to add them).
The first ten wear the `new_content/replacements/` art; three more
(Ironmaw Excavator, Reward Drum Drop, Traffic Panic) are built from
sprite-sheet source packs read through `newpacks.py`, and the Ironmaw
Excavator adds a telegraphed **debris hazard** in stage FUSE
(`StageHazard`, the volatile-prop pattern in `docs/STAGE-LOGIC.md`) that
hits every fighter in reach, capped and non-lethal.
They wear replacement art (`new_content/replacements/<Game>/`): painted
sprites, resampled to three pixels per world unit and split by the bonus-pack
pipeline into solid art (dark soft edges kept by an ordered dither) and light
(fire, sparks and energy premultiplied onto black and drawn `trans = add`, so
the glow keeps its gradient under the engine's on/off transparency), on
painted stages. They are written to one pattern, and it is a fair template for
a new prop:

* the **root** is invisible and cannot be hit, and it ends the game by taking
  its own life to zero once the last piece is gone;
* everything breakable is a **helper** the root fielded, so the band counts it,
  and each hit is caught by a `HitOverride` into the piece's own
  `movetype = H` state — which is what charges the life — rather than the
  common get-hit states a crate has no animations for;
* the root **stands at the piece nearest the player**, because the computer
  walks at and swings at its opponent's root;
* the root lives in a state other than 0 and takes `ctrl` away every tick: a
  root idle in state 0 without control is handed control back after a second,
  and with control the computer's inputs walk it into its guard and jump
  states;
* anything the prop throws at the player can knock them out (`kill = 1`,
  `guard.kill = 0`): a knockout is how a go fails (with `kill = 0` a bar stops
  at one point and reads as a game that could not be lost);
* a prop's attacks may be written in FUSE beside the generated CNS: the
  titan's punch, slam and core beam are `oxyde_titan_attacks.fuse`, a helper
  of the root that has no hurt box, telegraphs every attack (a warning beside
  the titan's head and a wind-up you can see) and only then strikes;
* a piece the root fields is **counted on a flag latched before the
  `Helper`**, not on the same `NumHelper(id) = 0` the spawn used: the new
  helper makes that false in the same tick, so a count written after it never
  fires (only one piece was ever up, in three of the first ten);
* state 0 sends a *helper* home (`var(59)`) rather than into the root's state:
  an attacker's custom state that gets past a `HitOverride` usually ends
  `SelfState value = 0`, and a piece that walked into the root's state became
  a second root.

---

# Versus Bonus

## The stages

| Stage | What it asks of you | Clock | Scored by |
|---|---|---|---|
| **Break the Car** | Sustained damage on a fixed target | 30s | *Race:* first to wreck it |
| **Barrel Drop** | Reactions -- they fall faster as the clock runs down | 30s | Barrels broken before they land |
| **Drum Stack** | Combos: break the bottom and the rest come down | 25s | *Race:* first to clear |
| **Oxyde Junk Pile** | A tall heap of mixed scrap — crates, drums and barrels — smashed top to bottom; knock out a lower piece and the rest come down | 40s | Scrap broken |
| **Glass Wall** | Coverage -- wide and multi-hit attacks clear rows | 30s | *Race:* first to clear |
| **Power Test** | One enormous hit | 20s | Best single hit |
| **Skeet** | Anti-airs and projectiles | 30s | Points, more for a higher hit |
| **Keep It Up** | Juggling -- do not let it touch the ground | 45s | Longest rally |
| **Temper** | A strength test: fill a gauge, strike at the mark to break the obstacle, climb the ladder to harder ones | 40s | Obstacles broken |

These are the **fallback**: they are what Versus Bonus plays when
`select.def` declares no bonus games. An installation that ships real ones —
this archive ships seven — plays those instead, then Beat Up (below).

> **What you can author, and what you can't.** You *can* add bonus-game
> **characters** — the car, the barrel stack, the drum — as data: a character
> folder with `bonus = 1` in `select.def` (see [Bonus games: telling the engine
> a roster entry is a prop](#bonus-games-telling-the-engine-a-roster-entry-is-a-prop)),
> and a campaign names them with `bonusgames =`. Those replace the fallback.
> You *cannot* author a new **procedural minigame type**: the nine types here
> (Break the Car, Barrel Drop, Drum Stack, Oxyde Junk Pile, Power Test, Glass
> Wall, Skeet, Keep It Up, Temper) and their physics and procedural art are
> engine-side — `Kind::ALL` in `crates/oxyde-app/src/bonus.rs`. Adding another
> type means editing that Rust (see [Adding one](#adding-one)), not dropping in
> a file. The line is: a bonus *character* is authorable content; a procedural
> *minigame type* is engine code. (A type may still expose its *own* authorable
> knobs — Temper reads its obstacle ladder from a file; see [Temper](#temper).)

All nine are played every run, **in a random order**. Nine, always, and each
one exactly once: a competition in which one player draws Power Test twice and
the other draws Skeet twice is not a competition. What the seed changes is the
order, which is enough that two runs never open the same way and that neither
player can learn "stage four is the one I am good at". The seed is the match
seed, so a replay of a bonus run replays the same nine stages in the same
order, and both peers of a netplay match agree on them without exchanging
anything.

Each player gets their **own** copy of the props, in their own half of the
screen, so nobody is waiting for a turn and neither can steal or block the
other's target. The camera does not move: a race you can only see half of is
not a race.

A stage ends when the clock runs out, or the moment one player finishes.

Three of them — Break the Car, Drum Stack and Glass Wall — hand both players an
identical, finite set of props, which makes them **races**. On a race the first
player to clear their own half wins the stage outright and ends it there;
scoring them on props broken instead would make every one of them a draw, since
both sides have exactly four panels to break. The HUD shows each player's
finishing time in place of their score once they have one.

The other six have no race finish and are scored on points, so the clock runs
out and the higher score takes it. A tie counts for neither.

## Temper

A **strength test**, the arcade one: a gauge fills, and your strike lands with
whatever force the bar held when you threw it. Break the obstacle in front of
you and the next one up a **ladder** takes its place — each rung asking for a
fuller bar than the last. The score is how far you climbed.

It unifies the two arcade strength tests as one mechanic, chosen per rung by its
**drive**:

* **Sweep** (Art of Fighting's bottles): a **rack of bottles** stands beside a
  **vertical gauge**, and a cursor runs that column up and down on its own;
  strike when it is near the top. The skill is timing the peak, and the bar is
  *graded* — the higher you catch it, the more force. Each good strike takes one
  bottle off the rack.
* **Mash** (Mortal Kombat's "Test Your Might"): a heavy block under a
  **horizontal bar** that drains on its own, hammered back up by a button. The
  skill is speed; strike once it is over the mark.

Each style wears its arcade's own furniture — AOF's upright meter and row of
bottles, MK's flat bar over a block — but it is one gauge and one strike
underneath.

The strike spends the **gauge**, not the fist: every character hits for exactly
what the bar held, so Temper is a test of the bar and not of who has the bigger
punch (the same reasoning as Power Test). A strike bites only if it clears the
mark — a weak one bounces off and you rebuild the bar.

An obstacle takes **three good strikes** to destroy: each strike past the mark
**chips it one state further** — intact → cracked → broken → gone — so progress
shows on the obstacle itself, and one mistimed strike is a setback, not a reset.

**Progression is the mark rising.** A harder rung simply sets its mark higher
(and may run the cursor faster or drain quicker), so the bar has to be fuller to
break it. That is the whole of "harder props": a number per rung, not new code.

### Authoring the ladder

The ladder is **content, not code**. Drop `data/bonus/temper.def` and the stage
climbs your rungs instead of the built-in five — one rung per line, easiest
first:

```text
; data/bonus/temper.def
; piece, need (1..1000), drive (mash|sweep), rate, family
pane,   300, sweep, 0.022, racks/cyan
crate,  450, mash,  0.009, might/oxyde_armored_crate
pane,   600, sweep, 0.034, racks/amber
crate,  780, mash,  0.013, might/pressurized_reactor_cell
crate,  940, sweep, 0.048, might/high_voltage_transformer
```

`piece` is the procedural fallback shape, drawn only when the art `family` is
missing (unknown names draw a crate). `need` is the force the strike must clear,
out of 1000 — this is where the mark sits, so a rising `need` is a rising bar.
`rate` is how fast the sweep cursor travels, or how fast the mash bar drains.
`family` names the obstacle's **art** (see below). Blank lines and `;`/`#`
comments are skipped; a missing or malformed file keeps the built-in ladder, so
the stage is never left with nothing to break.

### Obstacle art

Each rung's **`family`** is a folder under `data/bonus/art/` holding four loose
PNGs — one per break state. The first two are shared; the third and fourth are
named for how the material gives way — a heavy prop *breaks* and crumbles to
*rubble*, a bottle *bursts* and leaves *debris*:

```text
; a heavy prop (a might/* family)
data/bonus/art/<family>/<stem>_00_intact.png
                        <stem>_01_cracked.png
                        <stem>_02_broken.png
                        <stem>_03_rubble.png

; a single bottle (a bottles/* family)
data/bonus/art/<family>/<stem>_00_intact.png
                        <stem>_01_cracked.png
                        <stem>_02_burst.png
                        <stem>_03_debris.png

; a rack of bottles (a racks/* family) — counts bottles lost, not cracks,
; and prefixes the file with oxyde_rack_ (<stem> is the colour, e.g. cyan)
data/bonus/art/racks/<stem>/oxyde_rack_<stem>_00_loaded.png
                            oxyde_rack_<stem>_01_one_broken.png
                            oxyde_rack_<stem>_02_two_broken.png
                            oxyde_rack_<stem>_03_empty_wreck.png
```

where `<stem>` is the family's own leaf name (so
`might/oxyde_armored_crate/oxyde_armored_crate_00_intact.png`, and
`racks/cyan/oxyde_rack_cyan_00_loaded.png`). The engine draws the state the
obstacle is on as it is chipped. They are **ordinary PNGs**, read loose — no SFF
packing — so adding or reskinning a family is dropping four files in and naming
it in the ladder, with no engine change. A rung with no `family`, or whose art
will not load, falls back to the procedural prop and still plays.

The engine ships an industrial set: `racks/*` (the Art of Fighting sweep rungs, a
row of bottles that empties one at a time), `bottles/*` (a single-bottle variant)
and `might/*` (the heavy Mortal Kombat mash rungs).

### The break

When an obstacle is destroyed it does not simply blink out. The break throws a
one-shot **effect** where it stood — a glass shatter for a bottle, a shower of
sparks for a heavy prop — shoves the camera for a few frames, and kicks out a
heavier puff of debris, so the hit has weight. The effects are their own loose
sprite sheets under `data/bonus/art/`, six frames each:

```text
data/bonus/art/fx_bottle/<name>/<name>_00.png … _05.png   ; bottle breaks
data/bonus/art/fx_might/<name>/<name>_00.png … _05.png    ; heavy-prop breaks
```

All of this is **presentation**: the Temper stage, like every bonus game, runs
in the app layer off a shared read of the simulation, never writing it, so the
effects, the shake and the debris cost the netcode nothing and cannot touch a
replay's checksum.

## Beat Up

The last rung of a run of installed bonus games, and the one that is a fight.
Its opponent is **a real fighter from the roster** — drawn the way a random
slot is, so never a prop, and from the match seed, so a replay meets the same
one — fought on an ordinary stage rather than one a bonus game is paired with.

* The **computer** drives the opponent, at the usual difficulty: it fights
  back.
* **You cannot be knocked out.** Your bar stops at its last point, because a
  bonus is never a defeat. The opponent can be: put them down and the stage
  ends there.
* The clock is **60 seconds whatever the options say**, like every bonus game.
  An unlimited round against a player who cannot fall would never end.
* The banner reads `BEAT UP` instead of `BONUS STAGE`.

Its opponent is a roster character rather than a built-in figure. An earlier
design fielded a drawn armoured robot — the same challenge for every character —
but from play-testing a roster character reads better than a generic one, so no
run fields the robot.

## Who wins

The run goes to whoever takes the most stages, and **level on stages is a
draw** — it is a nine-stage competition between two people, and a tie is
not a win for whichever of them the engine happens to call "player one".

The result screen prints the whole table: one row per stage, in the order they
were played, each row showing what each player scored — or how long they took,
on a race — and which of them took it. "3 - 4 STAGES" does not say which three.

## Hitting each other

The two fighters are on **opposite teams** and can hit each other exactly as
they would in a fight: attacks connect, hitstun applies, and being knocked down
costs you the seconds you would have spent on your own props. That is the whole
appeal of it — otherwise the mode is two people playing solitaire side by side.

Nobody can be knocked out. There is nothing for a knockout to end here: a stage
ends on its clock or when somebody clears their props, and a fighter lying on
the floor for the last twenty seconds is not a result. So life never reaches
zero, and it comes back on its own at about a bar every ten seconds once a
fighter is out of hitstun — fast enough that no stage is decided by the first
exchange, slow enough that being cornered still costs something. The bonus HUD
carries a thin life pip under each score to show it; there are no life bars,
because a life bar promises a knockout that is not coming.

This is the same rule Training and Sparring use, and it is applied from the app
layer rather than from inside `Match::step`, so it cannot desynchronise a
rollback.

## How they are scored, and why

A bonus stage here has to work with **any** of the 2,527 characters in this
archive, authored by a thousand people over twenty years. That rules out
anything assuming a particular special move, a particular reach, or a
particular damage scale — a jab in this roster ranges from 12 to 400.

So six of the nine count **events, not damage**: a barrel broken is a barrel
broken whether it took one hit or six. Where the raw number *is* the point --
Power Test -- it is scaled by the attacker's own `attack` multiplier, and only
the single best hit counts, so mashing gains nothing. Skeet pays one point at
head height and three at the top of the screen, so an anti-air beats a standing
poke. Keep It Up scores the longest rally, not the total, so a lucky flurry
does not beat a controlled juggle.

The same one-hit-per-move rule the engine applies to hitting a person applies
here: an attack scores once and is not armed again until it ends. Without that,
a two-frame jab held out scores every tick it is active and every stage becomes
a mashing contest.

## How they are built

Targets are **not players**. They are not in the simulation at all: they are
stepped from the app layer against `Match::attack_boxes`, the same `Clsn1`
boxes that hit a person.

That choice buys three things. The netcode never sees them, so they cannot
desynchronise a rollback. A character's CNS cannot reach them, so no amount of
exotic scripting breaks a stage. And they cost nothing when no bonus stage is
running. What it costs is that a target cannot hit *back* — which no stage here
wants to do anyway.

The props are drawn procedurally, like the HUD, and for the same reason: there
is no car sprite in this archive and there never will be one that suits all 195
stages it might be standing in front of.

`crates/oxyde-render/src/bonusfx.rs` draws anti-aliased polygons and ellipses lit from one direction
— up and to the left, the same as the HUD's bevels and as most of this
archive's sprite art — so a barrel is a cylinder with a rim, a hoop and a
contact shadow, a pane of glass has reflections and cracks that spread as it is
worked on, and the car is a car: a chassis, wheels with rims and spokes, a
bonnet that slopes, a cabin with a windscreen and a flank with the wheel arches
cut out of it. Break the panels in any order and what is left still reads as
the same car with pieces missing, which is the point of the stage. Damage shows
as dents in fixed places rather than as a smudge.

It costs a few thousand blended pixels a frame against a rasteriser that
already redraws the whole stage sixty times a second, and it does not show up
in a frame time.

Two rules keep the two halves honest, and both are enforced by tests:

* every prop starts within 40 units of its own lane centre, so no stage can put
  something in the other player's half;
* both players' props are built from the same numbers rather than mirrored — a
  stack that leans the other way is not the same stack.

## Looking at one

A run plays its stages one after another, so reaching the last would otherwise
mean playing every other first. `--bonus-stage` opens on the one you name — an
installed bonus game by folder or name, or Beat Up:

```
oxyde --root . --headless --mode versus-bonus --p1 kfm --p2 kfm \
      --bonus-stage car2 --frames 600 --shot car.png
oxyde --root . --headless --mode versus-bonus --p1 kfm --p2 kfm \
      --bonus-stage beat-up --frames 700 --shot beatup.png
```

or, where none are installed, a procedural stage:

```
oxyde --root . --headless --mode versus-bonus --p1 kfm --p2 kfm \
      --bonus-stage skeet --frames 400 --shot skeet.png
```

The names are the stage labels, lower-cased and hyphenated:
`break-the-car`, `barrel-drop`, `drum-stack`, `oxyde-junk-pile`, `power-test`,
`glass-wall`, `skeet`, `keep-it-up`.

## Adding one

This is adding a new **procedural minigame type**, and it is an engine change —
editing Rust, not dropping in data. (To add a bonus-game *character* instead,
which is pure data, see [Bonus games](#bonus-games-telling-the-engine-a-roster-entry-is-a-prop).)

`crates/oxyde-app/src/bonus.rs`. A stage is a `Kind` with a label, a one-line
brief, a scoring unit and a clock; a `build` arm that lays out its props for
one player; optionally a `spawn` arm if it keeps sending things; and an `award`
arm saying what a hit is worth. `Kind::ALL` is the pool a run is shuffled from,
and the tests assert that a run is all of it exactly once.

If the stage needs a prop that does not look like anything already here, give
`Piece` a new value and `bonusfx.rs` a `draw_*` for it. A prop's `variant` is
there for the art alone — it is what tells a bonnet from a boot and gives a
stack of six drums three different blues — and nothing in the scoring or the
physics reads it.

The tests will hold a new stage to the same two rules — lane budget and
symmetry — without being told about it.
