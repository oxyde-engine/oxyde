# Parrying

A tap toward an attack, in the moment before it lands, that consumes it
outright: no damage, no chip, no block stun, and the attacker left committed to
their own recovery while you are free several frames earlier.

**Neither M.U.G.E.N nor Ikemen GO has this.** Both can be made to *look* as
though they do — a `ReversalDef` catches an attack, and several characters in
this archive use one — but a reversal is authored per move, by one character,
against attributes it lists in advance. A parry is a rule of the house: it
applies to every attack in the game, from every character, whether or not either
author has heard of it.

**It is off by default.** That is not timidity, and the reasons are in
[Why it is off](#why-it-is-off).

```ini
[Parry]
mode = tap        ; off | tap | hold
window = 8
cooldown = 12
```

That line, or the `PARRYING` row on the training menu, is the whole of what a
player has to do.

---

## How it plays

| | |
|---|---|
| Input | Tap **toward** the opponent for a high or mid attack; tap **down** for a low one; toward, in the air, for an air parry. A *tap*, not a hold — the direction must have been released beforehand. |
| Window | `window` frames from the tap. Any attack that connects inside it is parried. |
| Cooldown | `cooldown` frames after the window closes before another tap opens one. Mashing toward must not be a permanent shield, and this is the whole reason it exists. |
| Red parry | A later hit of a string whose earlier hit you **blocked**, on the tighter `redwindow`. Worth more frame advantage, and drawn hotter. |
| Result | No damage, no chip, no guard meter, no combo for the attacker. Both fighters freeze; the attacker freezes for longer. |
| Multi-hit | Each hit is parried separately. Parry the first hit of a five-hit super and the other four still land. |
| Throws | Cannot be parried. |
| Projectiles | Can be, by default. They already count as attacks to guard against. |

The attack is also **spent** against you: the same active frames cannot connect
again on the next tick. Without that a parry buys one frame rather than the
exchange — and a move that can reach two opponents still reaches the other one.

---

## What it looks like

There is a hard constraint here that does not exist in a game built around
parrying: **not one of this archive's 1,051 characters has a parry animation.**
Nobody authored one, because no MUGEN-family engine has ever had the feature. So
the engine supplies the entire presentation, the way it already supplies the
round banners, the combo counter and the hyper flash.

* **The moment.** A short freeze, through the same `hit_pause` path a hit already
  uses — so a parry and a hit cannot disagree about who is frozen, and rollback
  re-runs it correctly.
* **The mark.** A sharp arc struck on the defender's front, expanding and
  thinning over about a fifth of a second, in that side's accent colour — amber
  on the left, cyan on the right, the same pairing the life bars use. Drawn
  procedurally in `crates/oxyde-render/src/parryfx.rs`, so it is crisp at
  320x240 and at 4K. A red parry is drawn hotter and a touch wider.
* **The palette.** Two frames of white-blue on the defender's own palette, so the
  fighter reads as *having done something* rather than as having been skipped.
* **The sound.** A `fightfx` effect of its own, set by `[Parry] sound`, distinct
  from the block sound because the two have to be told apart by ear at speed.
* **The HUD.** Nothing. A parry is felt in the frame advantage it hands you, and
  a counter over the fighters would have you reading about it instead of
  playing.

In training, more — because the window is the one thing nobody can learn by
feel:

* a parry counter per side,
* **"EARLY BY *n*f"** on the frame it lands, which is the window remaining read
  the other way round,
* and the window itself as a shrinking bar under the fighter.

---

## Why it is off

Three reasons, all concrete.

1. **Balance.** A thousand characters tuned against an engine with no parry are
   not tuned against one with it. A character whose whole game is a
   three-hit-confirm loses it; a character with one slow overhead gains a
   matchup.
2. **The computer.** An AI that cannot parry is an AI that only ever *gets*
   parried. `[Parry] ai` defaults to `-1`, which follows the session difficulty,
   precisely so that switching parrying on does not quietly make the computer
   easier to beat. Setting it to `0` and leaving it there is single-player easy
   mode, and that is a choice rather than an accident.
3. **Taste.** The window is the most taste-dependent number in any fighting
   game. A frame too generous and every match is a parry contest; a frame too
   tight and nobody can use it. Eight frames at 60fps is a touch more generous
   than *3rd Strike*'s seven and a good deal less than the twelve some ports
   use. It is a setting because that sentence is not evidence.

---

## Every setting

| Key | Default | |
|---|---|---|
| `mode` | `off` | `off`, `tap` (3rd Strike), `hold` (the direction held parries — easier, same cooldown) |
| `window` | `8` | Ticks a tap opens the window for |
| `cooldown` | `12` | Ticks before another tap may open one |
| `freeze` | `10` | Ticks both fighters freeze |
| `advantage` | `6` | Extra ticks the **attacker** freezes. The frame advantage the whole mechanic exists to hand over |
| `redwindow` | `4` | The tighter window after a block. `0` switches red parries off |
| `projectiles` | `1` | Whether a fireball can be parried |
| `throws` | `0` | Whether a throw can be. **Leave this off**: every throw in this archive is a `p2stateno` with a throw attribute, and a consumed hit never reaches the state change |
| `unblockable` | `0` | Whether an attack with no guard flag at all can be parried |
| `power` | `0` | Power granted for a parry |
| `guardpoints` | `0` | Guard meter refunded, for a house that runs the guard meter |
| `ai` | `-1` | How well the CPU parries, `0`–`8`. `-1` follows the difficulty |
| `effect` | `1` | Draw the arc and flash the palette |
| `sound` | `5, 0` | The `fightfx` sound, as `group, number` |

---

## Absorb

A parry hands over frame advantage, which is worth a punish. **Absorb offers a
different exchange for the same read**: give the punish up, tap **down**, and
take a share of the meter the parried move cost them.

    [Absorb]
    enabled = 1

Parry a jab and nothing happens. Parry a three-bar super and you walk away with
a bar and a half while they have nothing to show for the bar they spent.

### Why the reward is scaled to their spend

This is the part that is not standard. Defensive rewards in this genre are
almost always flat — a fixed slice of meter for a good block, whatever was
blocked — so reading a super correctly pays exactly what reading a jab pays,
and the risk the attacker took is reflected nowhere. Scaling makes the reward
proportional to *their* commitment, which is the thing the defender actually
read.

And the spend is **measured, not declared**. What a move "costs" is not written
down anywhere a thousand authors agree on: the `Power >= n` in a `[Statedef -1]`
trigger is a *requirement*, and the real spend is whatever `PowerAdd` the state
gets around to running. So the engine watches the attacker's power go down and
takes a share of that. It needs no per-character analysis, it is right for a
move whose price is conditional, and it falls out correctly for a move that
costs nothing at all.

It also disposes of the multi-hit trap for free. A thirty-two hit super parried
thirty-two times would hand over sixteen bars if every hit carried the whole
cost; absorbing *consumes* the record of the spend, so the meter can be taken
once, because it was only spent once.

### Why the gesture is a down-tap

The idea this grew from used a **taunt**, which is the right instinct — a taunt
is the universal "I am not hitting you" — and the wrong input for this archive.
**28 of 1,000 characters here define a taunt command at all.** A mechanic keyed
on one would be available to 3% of the roster and would make those characters
strictly better: a balance problem created by an authoring accident. Every rule
of the house has to be one the engine can supply for all of them, exactly as
the parry supplies a presentation nobody ever animated.

A second tap *toward* would have been the natural choice — the same input again
— and it is the one thing that cannot be used, because `F, F` is a dash
command. Characters with a dash would get a free step-in on top of the meter
and characters without one would not: the same inequity wearing a different
hat.

Tapping **down** conflicts with nothing, because crouching is free for
everyone, and it reads on screen as a nod.

### Why the window is short

Twenty ticks, a third of a second. A generous window is not a decision: after a
parry the correct play is to punish, and a window long enough to punish *and
then* absorb is a bonus with an execution tax attached. At twenty ticks the two
compete, which is the whole point — **damage now, or meter for later**.

Pressing any attack button withdraws the offer immediately. You chose.

### What it costs

Absorbing hands the parry's frame advantage back to the attacker
(`costsadvantage`). Without that the trade is *punish and meter* rather than
*punish or meter*, and a mechanic that pays out whatever you do is not a
mechanic.

### The life variant

`lifeshare` grants a percentage of a life bar per full power bar absorbed — as
**recoverable life only**. It tops you back up towards the red-life ceiling and
no further, so it can return damage you have already taken and can never
manufacture health.

It is `0` by default, and that is a recommendation rather than caution. Meter is
a means; life is the win condition. A defensive mechanic that hands over a
quarter of a life bar for one correct read will decide matches on its own, and
it breaks every character's damage arithmetic in an archive where a single hit
ranges from 10 to 900.

### Every setting

| Key | Default | |
|---|---|---|
| `enabled` | `0` | Off. Also inert whenever `[Parry] mode` is `off` |
| `window` | `20` | Ticks the nod is accepted for |
| `share` | `50` | Percent of their spend granted as power |
| `mincost` | `250` | The smallest spend worth taking. Below it nothing happens and nothing is drawn |
| `lifeshare` | `0` | Percent of a life bar per full bar absorbed, as recoverable life only |
| `costsadvantage` | `1` | Absorbing hands the parry's frame advantage back |
| `effect` | `1` | The mark and the palette flash |
| `sound` | `5, 1` | The `fightfx` sound, as `group, number` |

Training has an `ABSORB` row beside `PARRYING`, greyed out while parrying is
off, and the practice readout shows `DOWN TO ABSORB n` while the offer stands
and `ABSORBED n` once it is taken. Neither is drawn in an ordinary match: in a
match the tell is that you watched them spend the bar, and knowing there is
meter on the table is the read.

---

## What a character can ask

| | |
|---|---|
| `Parry` | `1` on the frames a parry freeze is running |
| `ParryWindow` | Ticks left on this fighter's window |
| `ParryCount` | Parries taken this round |
| `Parry Kind = High\|Low\|Air\|None` | What the open window covers |

These are Oxyde's own: neither other engine has the mechanic, so neither has a
name for it. All four answer zero with `mode = off`, which is the default.

---

## Seeing it work

A headless run says so, when the house runs parries at all:

```
$ oxyde --root . --headless --p1 kfm --p2 ryu --ai 6 --frames 3000
  rounds won 2
  parries    0 - 3   (mode tap, window 10)
```

The line is absent with `mode = off`, which is the default — so its presence is
itself the check that the setting was read.

---

## How it is built

Four touch points, none large.

1. **Input.** `crates/oxyde-core/src/parry.rs` — a tap detector over the
   existing `InputHistory`, beside the command matcher rather than inside it.
   `Player.parry` holds five counters that tick down once a frame like every
   other one-tick counter, and all of them are in the netplay checksum.
2. **The hit.** One branch in `Match::resolve_hits`, beside the `HitBy` filters
   and the juggle check, and the same branch again in the projectile path. It is
   closest in shape to the `HitOverride` slot, which also redirects a hit that
   has landed — except that this one takes the hit *off the table* rather than
   rerouting it, which is the difference between a parry and armour.
3. **The presentation.** `crates/oxyde-render/src/parryfx.rs`, drawn over the
   fight and under the bars.
4. **The rules.** `[Parry]` in `oxyde.cfg`, the `PARRYING` row on the training
   menu (which takes effect on the live match, because a window is a number
   nobody can pick without trying it against a real attack), and `[Parry] ai`
   feeding the baseline opponent in `crates/oxyde-core/src/cpu.rs`.

### Decisions worth knowing

* **A parry needs `ctrl`.** No parrying out of hit stun, out of a throw, while
  dizzied, or during a freeze. This is the line between a parry and armour, and
  the whole of why a parry is a read rather than a get-out.
* **Throws are unparryable by default** and should stay that way: a consumed hit
  never reaches the `p2stateno` change, so a parryable throw is a throw that
  does not work.
* **`guardflag` decides what a window covers**, so a parry and a block can never
  disagree about what an attack *is*. An attack with no guard flag at all is a
  separate question with its own answer, `unblockable`.
* **The AI reads the attack's guard flags**, which is exactly what a player has
  to guess at — so `ai` is what stops it being perfect. At `8` it parries nearly
  everything it sees; at `1`, about one attack in eight.
