# Universal tagging

Swapping the fighter on screen for the partner waiting in standby, on a button,
for **any** character — including the 2,412 in this archive that have never
heard of tagging.

```ini
[Tag]
mode     = off   ; off | button
button   = b+z   ; which buttons, pressed together
cooldown = 60    ; ticks before the same side may tag again
lockout  = 12    ; ticks the arriving fighter cannot act
```

## Why the engine has to own it

`TagIn` and `TagOut` already existed as state controllers and already worked: a
fighter goes to `standby`, keeps its life and meter, and comes back with
`place_on_stage` putting it at the near edge of the view facing the opponent.

But a controller only runs if the **character** calls it, and almost nothing
here does. These characters were written for MUGEN, which has no tag mode, so
there is nobody to write a tag into 2,412 `[Statedef -1]` blocks. The mechanism
was built and nothing could reach it.

So the engine reaches it. That is the same argument the parry makes — *a rule
of the house applies to every character whether or not its author has heard of
it* — and it carries the same conclusion: **off unless switched on**, because a
roster balanced without tagging is not balanced with it.

## What happens on a tag

1. The fighter on screen goes to `standby`, keeping life, meter and position.
2. The partner leaves standby and is placed by `place_on_stage` — near edge of
   the view, on the ground, facing the nearest opponent.
3. The arriving fighter starts from **state 0**, its own idle, rather than
   whatever it was doing when it left.
4. The whole side takes the cooldown; the arrival takes the lockout.

## A knockout brings the partner in

The partner on the bench counts as standing, so knocking out the fighter on
screen does not end the round — and the button tag is only for a fighter who is
alive and in control, so for a while nothing brought the partner on at all. The
first `oxtool sweep` found the side standing empty until the clock ran out in
7,107 of its 48,250 tag matches (14.7%).

Now the partner comes in on their own once the fallen fighter is lying in 5150
(at least 60 ticks after the knockout), or is on the floor 180 ticks after it
however they fell — benched in the air, a corpse would hang there unseen — or
600 ticks after it whatever happened.
The fallen fighter goes to the bench with no life left, so they are never tagged
back in, and when the last fighter of a side falls the side is down as before.
Pinned by `a_knocked_out_fighter_is_replaced_by_the_partner_on_the_bench`.

## What it deliberately does not do

**No assists, no invulnerability, no tag-cancel out of a move.** Each is a
balance decision with a right answer per game and no right answer in general,
and each would need the incoming fighter to interact with the outgoing one's
state. This is the smallest thing that is unambiguously a tag: one fighter
leaves, one arrives, the clock keeps running.

A fighter **cannot tag while being hit**. Without that the tag is a universal
combo breaker, which is a balance decision nobody made — pinned by
`a_fighter_cannot_tag_while_being_hit`.

## The two timers, and why there are two

`cooldown` stops the team ping-ponging while the buttons are held. `lockout`
stops the arrival attacking on the frame it appears, which would make a tag a
free hit from somebody who was not on screen a moment ago.

They are separate because they answer different questions, and the cooldown
**ticks even while the fighter cannot act** — a cooldown that only runs while
you are free would never end for somebody held in a combo.

The button is an **edge**, not a level: held, it would fire again the instant
the cooldown expired.

## Determinism

Everything is a function of the input and existing state, and `standby` was
already in the rollback snapshot because `TagOut` put it there. A tag is
therefore as replayable as a jump and netplay needs no special case — which is
exactly why this is engine state and not a script.

The rules travel with the match the same way the parry rules do, so a replay
records which house rules it was played under.

## In play: Tag Versus

This mechanic is what the **TAG** team form is built on. Choose TAG on the team
card (beside SINGLE, SIMUL and TURNS) and each side fields a team of up to four,
one on the stage and the rest in standby: the whole of the mode is "tag is on,
and the reserves start benched." The engine recognises a side as a tag team on
its own — a tag rule switched on and a partner in standby — and everything above
follows: the button swap, the partner in on a knockout, and the side beaten only
when its last fighter falls. See [Modes](MODES.md).

## Trying it

```
oxtool simulate <root> <char.def> --vs <char.def> --tag --inputs "400:-,3:b+z,150:-"
```

`--tag` switches tagging on for the run and gives player one a partner in
standby, so the feature can be exercised against a real character rather than
only a synthesised one.

## Why `b+z`

Two buttons, because a single one collides with a move on almost every
character in the archive and three is a claw. Of the fifteen two-button
combinations of the six attack buttons, `b+z` (with `c+y`) is the one the
fewest characters bind as a command of its own. Measured over every `.cmd` and
FUSE command block in both game roots:

| chord | base archive (2,616 files) | FUSE root (2,517) |
|---|---|---|
| `b+z` | 35 | 33 |
| `c+y` | 35 | 33 |
| `c+x` | 57 | 55 |
| `c+z` (the old default) | 427 | 356 |
| `a+b` | 1,365 | 1,152 |
| `x+y` | 1,834 | 1,457 |

The old default, `c+z`, was bound by one character file in six, TagBattle5's own
partner change (`troca`) among them, and the comment in `tag.rs` claimed it was
bound by none. Start is out: it opens the pause screen in a match.

And where a fighter's own command *does* fire on the chord — the 35 above, or a
motion that ends in it — the press is the character's and does not tag
(`claimed_by_command`, pinned by `a_tag_press_the_character_binds_is_the_characters`).
Any combination is configurable. A misspelled button name leaves the default in
place rather than producing a combination nobody can press.
