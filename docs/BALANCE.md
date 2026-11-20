# Balance

A thousand characters by a thousand authors do not agree on how much damage a
punch does, or how much life a fighter has. This is the single biggest obstacle
to a large mixed roster being *fun* rather than merely playable.

## The problem, measured

```
$ oxtool balance .

--- the roster as authored ---
  life           min      600  p10     1000  median     1000  p90     1300  max      9999
  typical hit    min        1  p10       25  median       49  p90      104  max     50000
  strongest hit  min        5  p10       77  median      200  p90     1500  max     99999
  hits to kill   min        0  p10       10  median       20  p90       40  max      1000

  the strongest hit in the roster is 100x the median character's whole life bar
  a round lasts between 5 and 69 hits depending on who is fighting
```

A round between two median characters takes about 20 hits. A round involving
one of the outliers takes one hit, or three hundred. Neither is a fight.

## The fix

`oxtool balance` measures every character and writes a table of per-character
damage multipliers that equalise how many hits a round takes:

```
$ oxtool balance . --target-hits 22 --out balance.cfg

--- with the balance table applied ---
  hits to kill   min        0  p10       22  median       22  p90       22  max       333
  spread narrows from 13x to 1.1x

wrote balance.cfg: 799 of 965 characters need adjusting
```

Then in `oxyde.cfg`:

```ini
[Balance]
enabled = 1
table = balance.cfg
```

It is **off by default**, because it changes how characters were authored to
play. Turning it on is a choice about what kind of roster you want.

## What each rule does

| Rule | Effect |
|---|---|
| `lifenormalisation` | Moves each character's life bar this fraction of the way towards `targetlife`. `0` keeps the author's value, `1` forces everyone to the same. Default `0.5`. |
| Per-character damage table | Scales one character's outgoing damage so a typical hit takes a comparable share of a life bar. Clamped to 0.2x-3.0x so a character is never turned into a different one. |
| `damagescale` | A global multiplier applied after the table, for making all fights longer or shorter. |
| `maxhitfraction` | No single hit may remove more than this fraction of a life bar. This is the rule that neutralises 50,000-damage instant kills. |

## The strength lever

The options screen has one row, `BALANCING STRENGTH`, over the three numbers
that do the balancing — they only mean anything moved together, and three
separate rows are three ways to build a combination that makes no sense. The
lever sets all of them, and the file keeps whatever it is set to, so a
hand-edited `oxyde.cfg` is still the last word; the screen finds the stop
nearest what the file holds.

| Stop | `lifenormalisation` | `damagescale` | `maxhitfraction` |
|---|---:|---:|---:|
| `LIGHT` | 0.25 | 1.00 | 0.50 |
| `MEDIUM` | 0.50 | 1.00 | 0.35 |
| `STRONG` | 0.75 | 0.80 | 0.22 |
| `SEVERE` | 1.00 | 0.60 | 0.12 |

`MEDIUM` is what balancing used to be fixed at. The top of the scale is there
because a roster this wide has characters it cannot reach from `MEDIUM`: a
4,000-life boss against a 1,000-life shoto is still a boss at half
normalisation, and the 1,000-damage single hits this archive is full of still
take a whole bar under a 35% cap. `SEVERE` puts everybody on one life bar,
cuts every hit to two thirds of its authored size, and lets nothing take more
than an eighth of a bar at a time.

Moving the lever turns balancing on, since that is plainly what moving it is
asking for.

Attack and defence multipliers from the character's own `[Data]` section
(`attack`, `defence`) are always applied — those are authored balance, not
accident, and the table is computed on top of them.

## How the measurement works

For each character, every `HitDef` and `Projectile` with a *constant* `damage`
parameter contributes a sample. Expression-driven damage is left alone, since
it depends on run-time state.

The representative figure is the **median**, not the mean. A character whose
normals do 40 and who has one 9,999-damage instant-kill super has a mean that
describes neither; the median describes how the character actually plays.

The multiplier is then `(target_life / target_hits) / typical_damage`, clamped.

## Reading the table

`balance.cfg` is plain INI, matched case-insensitively against the character's
name, and hand-editable:

```ini
[Damage]
Adolf Hitler = 0.200
Akuma = 0.200
Athena = 0.200
Ralf 2002 = 3.000
Urien = 3.000
```

If two characters share a name, the first wins; edit the file to disambiguate.

## Limitations

* It cannot measure a character whose damage is entirely expression-driven.
  Those keep a multiplier of 1.0.
* It equalises *damage per hit*, not how easily a character lands hits. A
  character with a fast, safe, long-range poke is still stronger than one
  without; no static analysis can fix that.
* Characters clamped at the 0.2x or 3.0x limits are still outliers, just much
  smaller ones. The `min 0` and `max 333` in the "after" row are those cases.
