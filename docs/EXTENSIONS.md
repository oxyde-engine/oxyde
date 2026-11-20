# Extensions

Everything Oxyde understands that M.U.G.E.N does not.

[COMPATIBILITY.md](COMPATIBILITY.md) is the other half of this document: what
of MUGEN is implemented, and every place the engine deliberately behaves
differently. [VS-ENGINES.md](VS-ENGINES.md) puts all three engines side by side.
This one is the language *beyond* MUGEN — **148 triggers, five trigger redirections, 70 state controllers**
— plus hundreds of parameters on Elecbyte's own, two global states, five
command symbols, five gameplay systems and a handful of engine rules.

Those three numbers are re-derived, not maintained. Every row of the engine's
trigger and controller tables carries a `Provenance`
(`crates/oxyde-cns/src/trigger.rs`) saying whether Elecbyte's manuals document
the name, Ikemen GO introduced it, this engine did, or nobody can be shown to
have. The split is **Elecbyte 133 / Ikemen GO 138 / Oxyde 10 / unattributed 0**
for triggers, **90 / 66 / 0 / 2** for controllers and **8 / 5 / 0 / 0** for
redirections, and `oxtool docs` fails this document if any of it drifts.

The vocabulary is Ikemen GO's wherever Ikemen GO has a name for the thing, so
that content written for that engine has a chance of working here and nobody
has to learn two spellings of the same idea. **Every state controller name and
every trigger name in Ikemen GO's documentation is recognised here** — that is a
mechanical claim, checked mechanically: the names are extracted from the wiki
and diffed against the engine's own tables, and one test fires every added
controller in a single state and asserts that none of them reaches the
"documented and not done" counter.

Where the *behaviour* behind a name is not something this engine can do, the
difference is stated rather than hidden — [What is not here](#what-is-not-here)
lists all of it, by name, at the end.

---

## The rule this is all built on

**Nothing here can change how an existing character plays.**

Every trigger and controller below was a compile error before it existed. A
`.cns` in this archive cannot be reading one by accident, because if it were,
it would already be reporting an error — so the whole set is reachable only by
content written after it. `oxtool soak` counts the states the roster reaches;
it reads the same number with all of this in as it did without.

The four gameplay systems are the one place where that argument does not hold
on its own, because they act on characters that have never heard of them. So
they are **off unless switched on**, and the switch is a line in `oxyde.cfg`
that a person has to write.

---

## Contents

| | |
|---|---|
| [Four meters](#four-meters) | Red life, dizzy, guard break and score |
| [Parrying](#parrying) | The fifth system, and the one no other engine has |
| [The third axis](#the-third-axis) | `Pos Z`, `Depth`, `attack.depth` |
| [The camera](#the-camera) | `Zoom`, `Camera`, and the stage's own `autozoom` |
| [Looking at your own things](#looking-at-your-own-things) | `ExplodVar`, `ProjVar`, `ClsnVar` and the rest |
| [Named effects](#named-effects) | `ShaderSet` without a GPU |
| [Named variables](#named-variables) | `Map(name)` and the nine controllers that write it |
| [Reaching further](#reaching-further) | `RedirectID`, `ModifyPlayer`, `ModifyHitDef`, `GetHitVarSet` |
| [Two more global states](#two-more-global-states) | `[Statedef -4]` and `[Statedef +1]` |
| [Command file](#command-file) | `\|`, `L`, `R`, `N`, `$N`, `/30`, `steptime` |
| [Input](#input) | SOCD resolution, button assist, `AssertInput`, `ShiftInput` |
| [Saying something](#saying-something) | `Text`, `PrintToConsole` |
| [The round on the HUD](#the-round-on-the-hud) | `[WinIcon] p1.empty`, `[RoundCounter]`, win kinds |
| [The combo panel](#the-combo-panel) | `[Combo] style = panel`: damage, share, tags, best |
| [The title screen](#the-title-screen) | `[Title Info] title.style = oxyde` |
| [Engine rules](#engine-rules) | Processing order, and the new `AssertSpecial` flags |
| [Trigger reference](#trigger-reference) | All 148, by subject |
| [Controller reference](#controller-reference) | All 70, and the parameters |
| [What is not here](#what-is-not-here) | Named, so nobody has to guess |

---

## Four meters

Red life, dizzy, guard break and score are the mechanics commercial fighting
games settled on years after MUGEN was written, and that a MUGEN character
therefore cannot ask for: there is no constant to declare, no `HitDef`
parameter to fill in, and no state to be sent to. An author who wants stun has
to build the whole thing out of `var`s, and almost nobody does, because it only
works against an opponent who built the same thing.

So they belong to the engine. All four are computed from numbers every
character already has — the `damage` on a `HitDef`, the `[Data] life` constant
— which is the only way a rule can apply to a roster of a thousand files
written by people who never agreed on anything.

```ini
[Meters]
redlife    = 1
dizzy      = 1
guardbreak = 1
score      = 1
```

That is the whole of what a player has to do. Every number behind them is a
setting; [CONFIGURATION.md](CONFIGURATION.md) lists them, and
`oxyde --write-config` writes them out commented.

### Red life

Each fighter starts the round with a red bar equal to their maximum life. A
hit takes a *fraction* of its damage off it — half, by default — so the red bar
sits above the life bar and the gap between them is the damage that can still
be recovered. While a fighter is left alone, life climbs back towards the red
bar and never past it.

Drawn as a darker red layer inside the life bar, outside the damage trail.

### Dizzy

A hit costs stun resistance in proportion to its damage. Run out and the
fighter is dizzied: control is taken away for three seconds, their own standing
or crouching animation plays, and the next hit ends it. Points come back after
a couple of seconds without being hit or blocking — the clock is the
*opponent's* to reset, which is what makes a stun bar about pressure rather
than about time.

There is no state to send a dizzied fighter to, because a thousand characters
here have nothing authored at 6565 or anywhere else for one. What they all
*do* have is an idle state and an engine that will not let them act without
`ctrl`, so that is what this uses. A character that wants something better can
write it and drive it off the `Dizzy` trigger.

Drawn as a violet bar under the life bar, filling towards the dizzy.

### Guard break

The same, for blocking: a blocked attack costs guard resistance in proportion
to the damage it *would* have done unguarded, so what a guard costs does not
depend on how generous the author was with chip damage. Run out and the guard
breaks — the block ends, control goes for a second, and the meter refills.

Drawn as a blue bar under the power gauge, emptying towards the break.

### Score

Points for damage dealt, for each hit of a combo past the first, for taking a
round, for taking one untouched, and for landing the round's first attack. The
score belongs to the *side*, not the fighter, so it does not reset when a team
mate steps in, and it carries across rounds and matches.

A `HitDef` that names its own `score` takes the hit out of the default reward
entirely, which is what lets a character score its own way.

### What a character can ask, and set

| | |
|---|---|
| Triggers | `RedLife`, `Dizzy`, `DizzyPoints`, `DizzyPointsMax`, `GuardBreak`, `GuardPoints`, `GuardPointsMax`, `Score`, `ScoreTotal` |
| Controllers | `RedLifeAdd`, `RedLifeSet`, `DizzySet`, `DizzyPointsAdd`, `DizzyPointsSet`, `GuardBreakSet`, `GuardPointsAdd`, `GuardPointsSet`, `ScoreAdd` |
| On a target | `TargetRedLifeAdd`, `TargetDizzyPointsAdd`, `TargetGuardPointsAdd`, `TargetScoreAdd` |
| `HitDef` parameters | `redlife`, `dizzypoints`, `guardpoints`, `score = p1, p2` |
| `[Data]` constants | `dizzypoints`, `guardpoints` — both default to `life` |
| `AssertSpecial` | `NoRedLifeDamage`, `NoDizzyPointsDamage`, `NoGuardPointsDamage`, `NoScore` |
| `fight.def` | `[Stunbar]`, `[Guardbar]`, `[Score]` — the same element vocabulary as `[Lifebar]` |

A `fight.def` with no `[Stunbar]` simply shows no stun bar; that is every
`fight.def` written before these sections existed. Oxyde's own theme has all
three, and the engine's built-in HUD (`screenpack = 0`) draws them without
needing any.

---

## Parrying

The fifth gameplay system, and the one neither M.U.G.E.N nor Ikemen GO has at
all: a tap toward an attack in the moment before it lands consumes it outright.

```ini
[Parry]
mode = tap
```

Off by default, like the four meters and for one more reason on top of theirs:
the computer has to be taught to parry before it stops being free damage in one
direction. `[Parry] ai` defaults to following the session difficulty precisely
so that switching parrying on does not quietly make the CPU easier to beat.

A character can read `Parry`, `ParryWindow`, `ParryCount` and
`Parry Kind = High|Low|Air|None`, all of which answer zero with the system off.
The whole of it — the rules, the presentation, the training readout, and why
each number is a setting — is in [PARRY.md](PARRY.md).

---

## The third axis

MUGEN's world is a plane. Ikemen GO added a real depth axis and Oxyde implements
it: not a draw order, a direction a fighter can walk in.

```ini
; In the stage's .def
[PlayerInfo]
topbound = -40
botbound =  40
[Scaling]
depthtoscreen = 0.6
```

Equal bounds — which is the default and every stage in this archive — pin every
fighter to the MUGEN plane and the whole axis is inert. A stage that declares
them gives `Pos Z` and `Vel Z` somewhere to go, and `[Scaling] depthtoscreen`
decides how far up the screen a unit of depth moves a fighter and how much
smaller it makes them.

| | |
|---|---|
| Position | `Pos Z`, `Vel Z`, and a `z` component on `PosSet`, `PosAdd`, `VelSet`, `VelAdd`, `VelMul`, `TargetVelSet`, `TargetVelAdd`, `HitVelSet`, `BindToTarget` and `TargetBind` |
| Distance | `P2Dist Z`, `P2BodyDist Z`, `ParentDist Z`, `RootDist Z`, `TopBoundDist`, `BotBoundDist` and their `Body` forms |
| Size | `Depth` (the `Width` of the third axis, one tick), `[Size] depth`, `Helper size.depth` |
| Reach | `HitDef attack.depth`, and the `z` component of `ground.velocity`, `air.velocity`, `guard.velocity`, `down.velocity`, plus `fall.zvelocity` and `zaccel` |
| Get-hit | `GetHitVar(zvel)`, `(zaccel)`, `(zoff)`, `(fall.zvel)` |

Two fighters on different planes do not push each other and cannot reach each
other, and both of those tests collapse to "yes" when every depth is zero — so
the plane behaves exactly as it always did.

---

## The camera

MUGEN has one camera: it follows the fight, it never scales, and a character
cannot touch it.

```ini
; In the stage's .def
[Camera]
autozoom   = 1
zoomin     = 1.15
zoomout    = 0.85
zoomanchor = bottom
```

```ini
; In a character's .cns
[State 1000, frame the super]
type = Zoom
trigger1 = Time = 0
scale = 1.4
time  = 60
lag   = 0.15
pos   = 0, -20
```

`autozoom` pulls in when the fighters are close and out when they are apart —
which is what every commercial fighting game since the nineties does, and what
makes a big stage feel big. `zoomanchor` decides what stays put while the view
tightens; the floor, usually, because a camera that zooms about the centre of
the screen lifts the ground out from under the fight.

`Zoom` gives a move its own framing and wins while its timer runs; `lag` is how
slowly the view chases the number, which is the difference between a camera push
that reads as deliberate and one that snaps. `Camera` hands the whole thing over:
`view = "Free"` and a character drives the position directly, and then — as
Ikemen GO's documentation is careful to say — `ScreenBound` and `MoveCamera` stop
influencing anything, because two things steering one camera is a fight nobody
wins.

`ZoomVar(scale)`, `(pos.x)`, `(pos.y)`, `(lag)` and `(time)` read it back. The
camera's scale is in the netplay checksum, because `Zoom` is a state controller
and two peers disagreeing about it is a desync worth catching.

**Every default is "no zoom at all", which is MUGEN's camera**, so the 195 stages
in this archive are framed exactly as they always were.

### Breaking into another stage

A stage can name another stage to **break into**: knock somebody through the
wall at the corner and the fight carries on somewhere else, behind a
breaking-wall animation. The `[Break]` section is Oxyde's own, and a stage that
does not write one has ordinary walls. Most stages in this archive now name a
break target, so breaking is on by default; `[Options] wallbreak` (CONFIGURATION)
is the player's master switch to turn it off. Stage breaking is a **local and
versus** feature only — it is never armed over netplay, because serving a break
loads the destination stage mid-match, which two machines cannot be kept in step
on. With it off, or online, the simulation is identical to a stage that names no
break, so the switch moves no checksum.

```ini
; In the stage's .def
[Break]
next   = stages/rooftop.def   ; the stage to break into, relative to the game root
damage = 60                   ; how hard a hit, taken against the wall, breaks it
```

`next` is the stage this one breaks into. `damage` is how much a single hit
taken against the wall must deal to put somebody through it; the default is
`100`, so a stray jab will not do it, and `0` means any hit will. Read by
`Stage::parse` in `crates/oxyde-render/src/stage.rs`.

#### Styling the transition

The swap is sold by a brief flash: a short pop on the breaking hit, and a longer
one across the few ticks the backdrop changes on, so the new arena arrives
*inside* a hit-flash rather than behind an opaque cover. A stage can recolour,
retime or silence that flash from the same `[Break]` section — all of it is
**presentation only**, read at draw time off the checksummed break timer, so it
never touches the simulation, a replay or a netplay peer:

```ini
[Break]
next        = stages/rooftop.def
damage      = 60
flash       = 1             ; draw the flash at all (default 1); 0 = bare swap
flashcolor  = 255, 40, 20   ; its tint (default 255, 250, 240 — warm white)
flashtime   = 6             ; half-width in ticks of the swap flash (default 3)
flashbright = 180           ; peak alpha 0..255 of the swap flash (default 210)
impactflash = 1             ; the short pop on the breaking hit (default 1)
```

Every key defaults to the built-in transition, so a `[Break]` that names only
`next`/`damage` looks exactly as before. Setting `flash = 0` leaves the swap
bare — for an author who wants to supply their own effect (their own stage
animation or lighting) over an otherwise-clean cut. Values are clamped
(`flashtime` to `0..=60`, the rest to `0..=255`), and the whole block is read by
`BreakFxSpec` in `crates/oxyde-render/src/stage.rs` and drawn by `draw_break_fx`
in `crates/oxyde-app/src/game.rs`. `oxtool cornerbreak` renders the result, so
an author can preview their styling headlessly.

This is a **versus corner-break** — one arena flowing into the next during an
ordinary fight. It is *not* how Knuckle Up belt stages are ordered: a Knuckle Up
campaign's stage order is the campaign's own `stages =` list (see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md)), and belt stages do not
branch through a `[Break]` section.

---

## Looking at your own things

MUGEN lets a character ask `NumExplod`, `NumHelper`, `NumProjID` and nothing
else. It can *count* what it owns; it cannot look at any of it. An author who
wants to know where their own fireball is has to store the answer in a variable
at the moment they fired it and keep it up to date by hand — and with two in
flight, cannot.

```ini
; Where is my third fireball, and is it about to hit?
trigger1 = ProjVar(1000, 2, pos x) > 0
trigger2 = ProjClsnOverlap(2, enemy, ID, clsn2)
```

| | |
|---|---|
| Things you made | `ExplodVar(id, index, param)` · `ProjVar(id, index, param)` · `HelperVar(param)` · `SoundVar(channel, param)` |
| Geometry | `ClsnVar(type, index, elem)` · `ClsnOverlap(mine, id, theirs)` · `ProjClsnOverlap(index, id, box)` · `SpriteVar(param)` |
| The world | `StageBGVar(id, index, param)` · `NumStageBG(id)` · `NumText(id)` · `BgmVar(param)` · `EnvShakeVar(param)` · `PalFXVar(param)` · `ZoomVar(param)` |
| The session | `GameVar(param)` · `GameOption(param)` · `MotifVar(param)` · `MotifState(param)` · `FightScreenVar(param)` · `FightScreenState(param)` · `IsHost` |
| Yourself | `HitByAttr(state, kind)` · `Analog(axis)` · `XAngle` · `YAngle` · `Xshear` · `RunOrder` · `GroundAngle` · `IsClsnProxy` · `SpritePlayerNo` · `SelfCommand` · `InDialogue` · `Shader` |

Two notes on the ones Ikemen GO warns about. `SoundVar` there reads a live audio
device and is documented as not network-safe; here it answers from the *request*
the simulation made, so it is deterministic. `BgmVar` answers from a mirror the
host publishes once a frame, for the same reason.

`ExplodVar` and `ProjVar` take `-1` as the ID to iterate over everything you own,
and the parameter name is read forgivingly: `vel x`, `vel.x` and `velx` are the
same parameter, because the documentation and the shipped content between them
spell it all three ways.

---

## Named effects

`ShaderSet` names a GLSL program in Ikemen GO. Oxyde's default is a
deterministic path that compiles nothing: the software rasteriser resolves the
**name** against a table of sixteen built-in effects instead. (A character may
additionally opt in to a real `.wgsl`, or a `.frag` under the `glsl` build
feature, painted on the hardware fighter draw — see the `[Shaders]` note below.)

The sixteen built-ins take the same sixteen `shaderparam.pN` floats:

```
greyscale  sepia     invert     tint
posterize  pixelate  silhouette outline
dissolve   hue       saturate   contrast
brightness chromashift scanlines bloom
```

```ini
[State 1000, fade out]
type = ShaderSet
trigger1 = 1
shader = "dissolve"
shaderparam.p0 = time / 60.0
time = -1
```

A `[Shaders]` block in the character's DEF, or in the screenpack, names a shader
for an author's own name. When that is a real `.wgsl` (or a `.frag` with the
`glsl` feature built), it runs on the hardware fighter draw as an opt-in
cosmetic lane, excluded from the simulation checksum; it degrades to the nearest
built-in with no GPU, in a headless render, or when it will not compile. A bare
rename, or any name this table does not have, resolves to the nearest built-in,
or to nothing — and `Shader` then answers `""`, so a `.cns` can tell.

In exchange every one of these runs identically on a machine with no GPU at all,
cannot fail to compile, and is part of the deterministic simulation rather than a
property of the display — so a replay and a netplay peer see the same picture.
Eleven of the sixteen are pure palette transforms, which on 256-colour indexed
art cost 256 operations per sprite and nothing per pixel.

`Explod` and `Projectile` take `shader` too.

---

## Named variables

MUGEN gives an author sixty integers and forty floats, addressed by number,
shared with every piece of code in the file and with whatever `common1.cns` is
doing. A name is not a luxury: it is the difference between a helper being able
to keep state at all and an author having to reserve `var(43)` and hope.

```ini
; In the character's DEF
[Map]
birthyear = 1964
ansatsuken = 1
```

```ini
[State 0, charge]
type = MapAdd
trigger1 = command = "holddown"
map = "charge"
value = 1

[State 0, release]
type = ChangeState
trigger1 = Map(charge) >= 60
value = 1000
```

`MapSet` and `MapAdd` write the player's own; `ParentMapSet`/`ParentMapAdd`,
`RootMapSet`/`RootMapAdd` and `TeamMapSet`/`TeamMapAdd` write somebody else's;
`MapReset` clears them, putting anything the DEF declared back to what it
declared, and keeping any name containing one of up to eight `exclude` strings.

`RootVarSet` and `RootVarAdd` complete MUGEN's set: it has `ParentVarSet` and
`ParentVarAdd` and no way for a helper three levels deep to reach the fighter
it belongs to.

Maps are ordered, so the simulation checksum — and therefore netplay — does not
depend on iteration order.

---

## Reaching further

### `RedirectID`

An optional parameter on **every** state controller, Elecbyte's included. It
runs the controller as the player with that ID.

```ini
; A poison that takes a point of life a second, without a custom state,
; without a helper, and without the opponent agreeing to anything.
[State -2, poison]
type = LifeAdd
trigger1 = enemy, Map(poisoned) && TimeMod = 60, 0
value = -1
kill = 0
redirectid = enemy, ID
```

The ID is evaluated in the *caller's* context, so `redirectid = enemy, ID`
means what it reads as. An ID nobody has makes the controller do nothing:
silently acting on yourself is the one outcome no author wants from a mistyped
redirect. A `ChangeState` through a redirect moves the other player and leaves
the caller's own state running, which is what makes it usable from `-2`.

### `ModifyPlayer`

The parameters that have no controller of their own and no business having one
each: `ailevel`, `alive`, `attack`, `defence`, `lifemax`, `powermax`,
`dizzypointsmax`, `guardpointsmax`, `teamside`, `helpervar.ID`, `helpername`,
`movehit`, `moveguarded`, `movereversed`, `movecountered`, `hitpausetime`,
`pausemovetime`, `supermovetime`, `unhittabletime`.

`unhittabletime` is worth calling out: MUGEN spells invulnerability as a
`NotHitBy` covering every attribute, which costs one of the two filter slots
and has to be renewed every tick. This is the plain form of the same thing.

### `ModifyHitDef`

Updates the parameters named on an already-active `HitDef` and leaves the rest
alone — the same parameter names as `HitDef` itself.

```ini
[State 200, harder on the second hit]
type = ModifyHitDef
trigger1 = AnimElem = 5
damage = 140, 30
hitflag = MAF
```

### `GetHitVarSet`

Writes the defender's `GetHitVar`s without a hit having happened: `hittime`,
`fall.recovertime`, `xvel`, `fall.kill` and the rest of the documented set,
plus `redlife`, `dizzypoints`, `guardpoints` and `guardcount`.

### `TargetAdd`

Adds a player to the caller's target list by ID, so that `TargetState`,
`TargetBind` and the rest reach somebody the caller never actually hit.

---

## Tagging out

`TagIn`, `TagOut` and `SendToStage`.

Neither `TagIn` nor `TagOut` has ever had a specification from Elecbyte.
WinMUGEN listed `TagIn` among its controllers and never wrote a reference
section for it; the 1.1 manual mentions neither. Ikemen GO's wiki is the only
specification either name has, so it is the one implemented.

`TagOut` puts a fighter into **standby**: on the team, off the stage. The wiki's
list of what that means is exactly four things, and all four are honoured:

| | |
|---|---|
| unhittable | `is_untouchable` |
| cannot hit or push | `push_players` |
| the camera does not follow | `update_camera` |
| invisible to `Enemy` and `P2` | the redirections |

That last one matters more than it sounds: a character's own targeting must not
pick the fighter waiting in the wings.

`TagIn` is the same controller with the flag cleared, plus `ctrl`, `leader` and
the ability to hand control back. Both accept `self`, `partner`, `stateno`,
`partnerstateno`, `partnerctrl` and `memberno`; `memberno` reseats a fighter in
its team rather than moving it, and `leader` moves what `TeamLeader` answers —
which used to be derived and could not be steered.

Neither requires a partner. The archive's own copies of the old text warn that
MUGEN "crashes if triggered without a partner being present"; this does not.

A fighter coming back on does not reappear wherever standby left it — after a
round of the partner being pushed around the stage that is routinely off-screen.
It enters at the near edge of the view, on the ground, facing the nearest
opponent.

### `SendToStage`, and a guess stated as one

**`SendToStage` is specified nowhere.** It is absent from Elecbyte's 1.1
documentation, absent from Ikemen GO, and used by none of the 2,527 characters
in this archive; the name reached this engine's table from a bare list with no
reference section behind it. Neither of the two sources this project normally
appeals to — the manual, and counting what a thousand authors wrote — has
anything to say.

So rather than invent a specification, it is implemented as the one operation
its name can only mean and that the tag system actually needs: **the inverse of
`TagOut`.** It puts a fighter back on the stage — standby cleared, position
inside the camera, state optionally changed — and is what `TagIn` calls to do
its half of the same job. `id`, `pos`, `ctrl` and `stateno` are accepted.

If a specification ever turns up and disagrees, this is the paragraph to come
back to.

## Perspective

`xangle`, `yangle`, `projection` and `focallength` on `AngleDraw`, and the same
four plus `angle` and `xshear` on stage background elements. Ikemen GO's names,
spelled the same way.

These used to be drawn as a squash of the axis being turned about — exactly
right at 0 and 180 degrees, and a lie in between, because the squash happens in
*sprite* space and so disagrees with any in-plane `angle` applied after it. The
rasteriser now does the real thing: four corners placed in space, rotated,
projected, and mapped through the homography onto the resulting quadrilateral.

`orthographic` is the default and Ikemen's; it gives exactly `cos(angle)`.
`perspective` measures depth from the centre of the *screen*, so a row of tilted
panels all lean the same way. `perspective2` measures it from each sprite's own
axis, so each is upright in its own right.

One extension beyond Ikemen: `projection` and `focallength` are accepted on
`AngleDraw` as well as on backgrounds. A fighter tipping towards the camera is
the same picture as a backdrop doing it.

Nothing in this archive writes any of them, so none of it can change a character
or a stage that already works. See [RENDERING.md](RENDERING.md).

## Two more global states

MUGEN's three global states all have a hole in them. `-3` stops inside a
throw, `-2` and `-1` stop for a helper, and all three stop under a super
freeze — which between them mean there is nowhere in the language to put code
that must *always* run.

**`[Statedef -4]`** runs every tick for everything: players, helpers with and
without `keyctrl`, fighters inside somebody else's custom state, and everybody
under a `Pause` or a `SuperPause`.

**`[Statedef +1]`** is the same, except that it runs *after* the player's own
current state rather than before it — the only place from which the result of
this tick's own state can be read.

The execution order is `-4`, `-3`, `-2`, `-1`, the current state, `+1`.

The leading `+` is the whole of what distinguishes `[Statedef +1]` from
`[Statedef 1]`, which is an ordinary state a great many characters use; both
are kept, under their own numbers.

---

## Command file

### `|` — alternatives

```ini
command = x | y | z     ; press x, or y, or z
```

`+` is AND and `|` is OR. In MUGEN this has to be written as three separate
commands with three separate names, and then checked three times in
`[Statedef -1]`.

### `L`, `R` — absolute directions

MUGEN's whole direction alphabet is relative: `B` and `F` mean different sides
of the screen depending on which way you are turned. `L` and `R` do not.

```ini
[Command]
name = "QCR_x"
command = ~D, DR, R, x
```

The absolute diagonals `DL`, `DR`, `UL`, `UR` come with them.

### `N` — no direction

```ini
command = ~60N, F+a     ; forward and A, after a full second of neutral
```

### `$N` — any press or release of any key

```ini
command = $N            ; anything at all happened this tick
```

`N` asks about the *stick*; `$N` asks about the whole controller, buttons
included, and about a *change* to it rather than a state of it. A press counts
and so does a release, and two changes on consecutive ticks are two hits —
there is no requirement for a still tick in between, which is what makes it
usable as "press any key" while a button is being mashed.

MUGEN has no `N` symbol at all — its `$` is documented as "direction-only:
detect as 4-way", and `kfm.cmd`'s own header lists eight directions and six
buttons — so `$N` is an extension on an extension. The reading is Ikemen GO's,
quoted: "for backward compatibility purposes and because it would otherwise
lack any meaning, `$N` stands for any press or release of any key". Its code
adds that MUGEN "somehow returns *any change*" here, and emulates that.

Nothing in this archive, and nothing in Ikemen GO's own content, uses it. So
this is the documented reading implemented straight, with nothing bent to match
a character — and `~$N`, which Ikemen GO quietly makes a synonym for `$N`, is
left as this engine's generic release reading until something needs otherwise.

### `/30` — a charge that is true while it is held

`~30B` is true on the frame the charge is *released*; `/30B` is true for as
long as it is kept. MUGEN has only the first.

### `steptime`

```ini
[Command]
name = "Super"
command = ~D, DF, F, D, DF, F, y
time = 60      ; 60 frames for the whole motion, no matter what
steptime = 10  ; but only 10 between one input and the next
```

MUGEN gives one window for the whole motion, so a long super has to be given a
long `time` — and that same long window then applies to every gap inside it,
which is what makes a 60-tick double quarter-circle fire off two unrelated
quarter-circles half a second apart.

### `buffer.hitpause`, `buffer.pauseend`

Set either to `0` and the command's buffer does not ride out a hit pause, or
the `endcmdbuftime` window at the end of a `Pause` / `SuperPause`. MUGEN keeps
every command buffered through both, which is what makes a move "come out on
its own" after a long hit stop.

All four have `[Defaults]` entries: `command.steptime`,
`command.buffer.hitpause`, `command.buffer.pauseend`.

---

## Input

### SOCD resolution

A stick cannot press left and right at once. A keyboard, a hitbox controller
and a loose d-pad all can, and MUGEN passes both through — which lets a player
hold both and be un-crossable and blocking in both directions at the same time.

```ini
[Input]
socdresolution = 4
```

`0` both register (MUGEN exactly) · `1` most recent wins · `2` forward beats
back and up beats down · `3` first pressed keeps the axis · `4` neither
registers (default).

This is the one setting on this page whose default is *not* MUGEN's: `4` is
what Oxyde already did on the horizontal axis, and it now applies to the
vertical one too. `0` restores MUGEN exactly.

### Button assist

```ini
[Input]
buttonassist = 1
```

Delays every button press by one frame so that two pressed a frame apart
register together. MUGEN's input path was loose enough that this happened by
accident most of the time, and a good deal of shipped content — every `x+y`
command in the archive — is written expecting it. Directions are not delayed:
a motion input is a sequence of edges, and holding one back does nothing for
it.

### `AssertInput`, `ShiftInput`, `AssertCommand`

```ini
[State 0, hold forward]
type = AssertInput
trigger1 = 1
flag = F

[State 0, invert the stick]
type = ShiftInput
trigger1 = 1
input  = L
output = R

[State 0, throw a fireball on my own]
type = AssertCommand
trigger1 = Time = 10
name = "QCF_x"
buffer.time = 5
```

`AssertInput` raises up to eight input flags for one tick, as if the keys were
pressed. `ShiftInput` remaps one key to another for one tick, `none` disabling
it; `input = none, output = none` clears the remapping. `AssertCommand` marks
a command as detected without the motion; with an empty name it picks one of
the character's commands at random, which is a one-line AI.

`InputTime(key)` answers how long a key has been held, or minus the ticks since
it was released. Case matters, as it does everywhere in MUGEN's key alphabet:
`B` is the back direction and `b` is the medium punch.

---

## Saying something

MUGEN has no way for a character to write on the screen. The clipboard is a
debug tool behind Ctrl+D, and everything else has to be drawn as a sprite —
which means an author who wants to show a number ships a font as an animation
and assembles it a digit at a time. Several characters here do exactly that.

```ini
[State +1, readout]
type = Text
trigger1 = 1
id = 1
text = "charge %d / 60"
params = Map(charge)
pos = 160, 40
font = -1, 0, 0     ; index, bank, align: 0 centres, 1 left, -1 right
removetime = 2
layerno = 2         ; 2 draws in front of the bars as well as the fight
```

`ModifyText` edits a text already on screen by `id`, `RemoveText` takes it
away. `PrintToConsole` writes the same printf format to the terminal.

All of them share the clipboard's formatter: `%d`, `%i`, `%f`, `%F`, `%e`,
`%E`, `%g`, `%G`, `%%`, the escapes `\n`, `\t`, `\\` and `\"`, and up to
sixteen `params` expressions — Elecbyte documents six, and nothing depends on
the limit being exactly six.

---

## The round on the HUD

MUGEN shows rounds won as a row of icons and nothing else: one appears per
round taken, the row starts empty, and "ROUND 2" is said once before the
fight and never again. Unless a pack's icons are large and placed well, a
player cannot tell that the row is there at all. Two `fight.def` additions,
both ignored by MUGEN, make the round readable for the whole of it:

```ini
[WinIcon]
p1.empty.spr = 59, 0     ; drawn in every slot a win could fill
p2.empty.spr = 59, 0

[RoundCounter]
pos            = 640, 120
bg0.spr        = 31, 0             ; the plate behind it, like [Time] bg0
counter.font   = 2, 7, 0
counter.text   = "ROUND %i"
final.text     = "MATCH POINT"     ; when either side is one round away
```

* **`pN.empty`** is drawn once per round it takes to win the bout (capped by
  `useiconupto`), before the won icons go over it, so the row reads "one of
  two" from the first frame.
* **`[RoundCounter]`** stays on screen for the whole round. Practice, a bonus
  game and the one-long-round modes have no rounds, and show neither the
  counter nor the empty slots.
* **The win kinds are honoured.** MUGEN's `n`, `s`, `h`, `c`, `t`, `throw` and
  `perfect` icons are each drawn for the round they describe, read off the last
  hit the loser took: a throw, a hyper, a special, chip through the guard, a
  time over, or a round won untouched. A pack that defines only `n` gets `n`
  for all of them, as before.

The built-in HUD (`screenpack = 0`) draws the same two things: rimmed round
slots beside each name and the round, or MATCH POINT, under the clock.

A `fight.def` authored wider than the window, such as Oxyde's own 1280x720 HUD
in a 4:3 window, keeps whatever it places in the top half of its canvas at the
top of the window and whatever it places in the bottom half at the bottom,
instead of sliding the whole HUD down to the floor.

---

## Who is playing, on the HUD

`[PlayerTag]` is an Oxyde section of `fight.def`: the initials of whoever
holds a side's controller, and the winning streak they are on. MUGEN has no
idea who is playing, so a pack without the section shows neither.

```ini
[PlayerTag]
streak.min        = 2            ; one win is not yet a streak
p1.pos            = 0, 0
p1.tag.bg0.spr    = 32, 0        ; a chip behind the initials
p1.tag.font       = 2, 7, 0
p1.tag.offset     = 469, 67
p1.tag.text       = "%s"
p1.streak.bg0.spr = 34, 0        ; a flame
p1.streak.font    = 2, 2, 1
p1.streak.offset  = 514, 67
p1.streak.text    = "%i STREAK"
```

`p2.*` takes the same keys. The tag is drawn only when a player has entered
initials, and the streak only from `streak.min` up. The engine's own HUD
(SCREENPACK OFF) draws both beside the round marks without being asked.

### Animated HUD pieces keep their blend

A `fight.def` or `system.def` element given an `anim` is drawn with that
animation frame's blend, as MUGEN draws it: `AS128D128` is see-through and
`S` darkens what is under it. Oxyde used to draw every motif element solid.
The built-in theme uses it for the HUD's smoked glass: action 201/202 is a
grey sprite drawn with `S`, a scrim fading down from the top edge plus the
inside of each bar, so the stage stays visible behind them.

## The combo panel

`[Combo] style = panel` is Oxyde's: instead of the pack's `counter`/`text`
pair, the engine draws its own combo panel at `pos` (player two's mirrored to
the other side). MUGEN ignores the key, so a pack can carry both.

```ini
[Combo]
style   = panel     ; Oxyde; MUGEN draws counter/text below instead
pos     = 36, 148   ; the panel's outer edge and top
```

Read top to bottom: the hit count, large and popping on each new hit, with
`HITS` beside it (`HIT COMBO` once it has ended); the damage and the share of
the defender's life it took; a mini life bar with what they have left; tag
chips — `COUNTER` when the first hit landed while the defender was attacking,
`JUGGLE` when a hit landed on them in the air; and the round's best combo, or
`NEW BEST` in gold the moment it is beaten. A finished combo stays as its
summary and fades. In a continuous match the panel starts under the KO/BENCH
or LIVES/SCORE plate. The engine's own HUD (SCREENPACK OFF) draws the same
panel. All of it is read from the match and drawn outside it.

## The title screen

`[Title Info] title.style = oxyde` is Oxyde's: the pack hands its title screen
to the engine, which draws its own — the OXYDE wordmark, every mode on screen
at once, the highlighted one in Oxyde orange, the line explaining it, and an
animated backdrop at the window's own resolution. The rows keep the pack's
names (`menu.itemname.*`) and its cursor sounds. MUGEN ignores the key and lays
the menu out from the rest of `[Title Info]` over `[TitleBG]`, so a pack can
carry both. The built-in theme sets it; every other pack's title is drawn as
its author laid it out.

```ini
[Title Info]
title.style = oxyde   ; Oxyde; MUGEN uses menu.pos and the TitleBG below
```

## Engine rules

### Character processing order

MUGEN walks the player table from the top, so player 1 always thinks before
player 2 and every helper thinks after every root. That is a real, measurable
advantage: on the tick both fighters swing, P1's `HitDef` is on the table when
P2 is asked whether it has been hit, and P2's is not.

Oxyde sorts by what each fighter is *doing* first and falls back on the index
only inside a tier:

1. players attacking
2. helpers attacking
3. players idle
4. players being hit
5. helpers idle
6. helpers being hit

Whoever is attacking is read first whichever side of the screen they stand on,
which is the whole point. `AssertSpecial flag = RunFirst` and `RunLast` let a
character opt out in either direction, and `[Rules] indexprocessingorder = 1`
restores MUGEN's table order for the whole session.

### New `AssertSpecial` flags

`AssertSpecial` takes eight flags rather than three, and `enabled = 0` takes
one back rather than raising it.

| Flag | |
|---|---|
| `AnimateHitpause` | the animation advances during a hit pause |
| `AnimFreeze` | the animation does not advance at all |
| `AutoGuard` | guard without holding back, standing or crouching to suit |
| `CameraFreeze` | the camera holds still |
| `NoKO`, `GlobalNoKo` | this fighter, or everybody, cannot be killed |
| `NoGuardKO` | no death from chip damage through a guard |
| `NoKOFall` | a lethal hit does not force a fall |
| `NoHitDamage`, `NoGuardDamage` | the hit lands and does no life damage |
| `NoRedLifeDamage`, `NoDizzyPointsDamage`, `NoGuardPointsDamage`, `NoScore` | one per meter |
| `NoJump`, `NoAirJump`, `NoCrouch`, `NoStand`, `NoBrake` | switch off one engine-owned transition each |
| `NoHardcodedKeys` | all of those, plus `NoWalk` and the three guards |
| `NoInput` | ignore the controller entirely |
| `NoCornerPush` | no give in the corner — asserted by the attacker they are not pushed back, asserted by the defender nobody is pushed off them |
| `NoDestroySelf` | `DestroySelf` does nothing |
| `NoTurnTarget` | the opponent does not turn to face this fighter |
| `NoIntroReset` | not pushed to the starting mark by the round call |
| `SizePushOnly` | push on size boxes alone, as most fighting games do |
| `RunFirst`, `RunLast` | this fighter's code runs before, or after, everyone else's |
| `SkipRoundDisplay`, `SkipFightDisplay`, `SkipKODisplay`, `SkipWinDisplay` | skip a round announcement |
| `PostRoundInput` | inputs keep working after the round is decided |
| `DrawUnder` | draw beneath the shadows and the bars |

`IsAsserted(flag)` answers whether any of them — or any of Elecbyte's — is up.

### Two MUGEN triggers that now answer

Not extensions: `StageVar` and `StageConst` are Elecbyte's, and Oxyde used to
return a constant zero for both, which is worse than not having them. They now
read the stage's own `.def`. `StageVar` takes a `section.key` path —
`StageVar(camera.boundleft)`, `StageVar(stageinfo.zoffset)` — over `[Info]`,
`[Camera]`, `[PlayerInfo]`, `[Scaling]`, `[Bound]`, `[StageInfo]`, `[Shadow]`,
`[Reflection]`, `[Music]` and `[Constants]`.

And `select.def` now finds a character named as a path. MUGEN documents entries
as relative to `chars/`, so `kfm/kfm.def` means `chars/kfm/kfm.def`; a path
from the game root is tried after it, because that is what somebody
hand-editing the file usually writes.

---

## Trigger reference

148 triggers beyond MUGEN, plus five new redirections. Everything below is
answered from state this engine already had, except where the note says
otherwise.

### Redirections

`P2,` · `Player(n),` · `PlayerIndex(n),` · `HelperIndex(n),` · `StateOwner,`

`P2` is the same opponent the whole `P2*` family answers about, so the two
cannot disagree. `Player(n)` takes a player *number* — a seat at the table,
stable for the round, and the seats **alternate sides**: 1, 3, 5, 7 on the left
and 2, 4, 6, 8 on the right, so `Player(2)` is an opponent and `Player(3)` is
your partner. That is the manual's own P1..P4 continued — `trigger.html`
defines `P3Name` as the player's *teammate* and `P4Name` as the *secondary
opponent* — and it is what the archive's screenpacks assume: of the 46
`[Simul Lifebar]` sections here, all 15 whose bar positions are far enough
apart to tell put `p3` beside `p1` and `p4` beside `p2`, none the other way.
A seat nobody is in is `SFalse`, which is why `PlayerNoExist(n)` is a question
about the seats and not a head count: one against three fills 1, 2, 4 and 6, so
four fighters exist and player 3 does not. `PlayerIndex(n)` takes a raw index into the player list,
helpers included, which is the handle a loop over every entity on the stage
needs and nothing else should use. `HelperIndex(0)` is the root.

### Maths

`Max(a,b)` · `Min(a,b)` · `Clamp(v,lo,hi)` · `Lerp(a,b,t)` · `Sign(x)` ·
`Deg(x)` · `Rad(x)` · `Atan2(y,x)` · `Round(v,places)` · `Float(x)` ·
`RandomRange(lo,hi)`

Int in, int out; a float anywhere makes the answer a float, which is how
MUGEN's own arithmetic works. All of them fold at compile time when their
arguments are constants.

### Identity and the player list

`PlayerNo` · `Index` · `NumPlayer` · `PlayerNoExist(n)` ·
`PlayerIndexExist(n)` · `HelperIndexExist(n)` · `HelperName = "..."` ·
`DisplayName = "..."` · `StateOwner` · `AnimPlayerNo` · `ParentExist` ·
`MemberNo` · `TeamSize` · `TeamLeader` · `Standby`

### State, animation and presentation

`PrevAnim` · `PrevStateType` · `PrevMoveType` · `Physics` · `SprPriority` ·
`LayerNo` · `Scale x/y` · `Offset x/y` · `Alpha source/dest` · `Angle` ·
`DrawPal group/index` · `AnimLength` · `AnimElemVar(param)` · `InCustomState` ·
`InCustomAnim` · `SelfStateNoExist(n)` · `IsAsserted(flag)` · `IntroState` ·
`OutroState`

`AnimElemVar` reads the current frame out of the `.air`: `group`, `image`,
`time`, `xoffset`, `yoffset`, `hflip`, `vflip`, `numclsn1`, `numclsn2`,
`alphasource`, `alphadest`, `angle`, `xscale`, `yscale`.

### Combat

`JugglePoints` · `HitOverridden` · `MoveCountered` · `ReceivedDamage` ·
`ReceivedHits` · `GuardCount` · `ComboCount` · `FirstAttack` · `PauseTime` ·
`AirJumpCount` · `LastPlayerID` · `HitDefVar(param)` · `MoveHitVar(param)` ·
`ReversalDefAttr` · `Attack` · `AttackMul` · `DefenceMul` · `AILevelF` ·
`HasFlag(set, flags)`

`HitDefVar` reads the player's own active `HitDef` or `ReversalDef` by the
controller's parameter names — `hitdamage`, `guarddamage`, `pausetime`,
`sparkno`, `ground.velocity.x` and so on. `MoveHitVar` reads what the last hit
to connect actually did: `frame`, `playerid`, `playerno`, `sparkx`, `sparky`,
`uniqhit`, `overridden`, `cornerpush.veloff`.

The counters are not part of the opt-in meter set — a character may read
`ComboCount` or `ReceivedDamage` whatever the house rules say.

#### `HasFlag` — membership in a flag set

Two of those parameters do not answer a number but a *set* — `hitflag` and
`guardflag` — and they do so on `HitDefVar`, on `GetHitVar` and on `ProjVar`
alike. The only useful question about a set is whether it contains something,
and that is what `hasFlag` asks:

```ini
trigger1 = hasFlag(HitDefVar(guardflag), L)   ; can this be blocked crouching
trigger2 = !hasFlag(P2, HitDefVar(hitflag), D) ; their blow cannot hit me down
trigger3 = hasFlag(ProjVar(1000, 0, guardflag), MA)
```

The letters are `H` high, `L` low, `M` mid (which is `H` and `L` together),
`A` air, `F` falling, `D` down, and the `+`/`-` modifiers — the same alphabet
the `HitDef` controller's own `hitflag` is written in. The test is
**membership**: the set shares any of the letters named. Several letters
therefore read the way `statetype = SC` and `hitdefattr = SCA` already do, and
`= M` keeps matching a `guardflag` of `L`, which is the only reason `M` is
worth having. "Contains all of these" is the two tests it is:
`hasFlag(x, H) && hasFlag(x, L)`.

The comparison spelling Ikemen GO uses is read too, and means the same thing:

```ini
trigger1 = HitDefVar(guardflag) = L
trigger2 = HitDefVar(guardflag) != H
```

Three differences from Ikemen GO's version, all deliberate:

* **It is one mechanism, not one per trigger.** Ikemen GO bakes the comparison
  into the triggers that needed it — a dedicated opcode each, and `ProjVar`'s
  copy disagrees with `HitDefVar`'s about what `!=` means. Here the *alphabet*
  is named once and any trigger that answers a flag set joins by being listed
  in one table, which is all it took to give `ProjVar` the same question and
  all it will take for the next one.
* **`!=` is one rule.** "Contains none of these", everywhere.
* **The set is still a number.** Ikemen GO's flag triggers push a boolean and
  the mask itself is never visible to an expression. Here `HitDefVar(hitflag)`
  remains the bitmask Oxyde has always answered — one bit per letter, so `&`,
  `|` and `~` work on it, and `HitDefVar(hitflag) = 15` is still the numeric
  comparison it was.

Ikemen GO also takes a `P` flag, for an attack that cancels projectiles. This
engine's `hitflag` has no such bit, so asking about it is a compile error
naming the alphabet rather than a test that is quietly always false.

### The four meters, and the fifth system

`RedLife` · `Dizzy` · `DizzyPoints` · `DizzyPointsMax` · `GuardBreak` ·
`GuardPoints` · `GuardPointsMax` · `Score` · `ScoreTotal`

`Parry` · `ParryWindow` · `ParryCount` · `Parry Kind = High/Low/Air/None`

The parry four are Oxyde's own — no other engine in this family has the
mechanic, so no other engine has a name for it. All four answer zero with
`[Parry] mode = off`, which is the default.

### Looking at what you made

`ExplodVar(id, index, param)` · `ProjVar(id, index, param)` ·
`HelperVar(param)` · `SoundVar(channel, param)` · `SpriteVar(param)` ·
`ClsnVar(type, index, elem)` · `ClsnOverlap(mine, id, theirs)` ·
`ProjClsnOverlap(index, id, box)` · `StageBGVar(id, index, param)` ·
`NumStageBG(id)` · `NumText(id)` · `PalFXVar(param)` · `EnvShakeVar(param)` ·
`ZoomVar(param)` · `BgmVar(param)` · `HitByAttr(state, kind)`

### The session

`GameVar(param)` · `GameOption(param)` · `MotifVar(param)` ·
`MotifState(param)` · `FightScreenVar(param)` · `FightScreenState(param)` ·
`IsHost` · `InDialogue` · `RunOrder` · `Shader = "..."` ·
`SelfCommand = "..."`

### The third axis and the fighter's own geometry

`Pos Z` · `Vel Z` · `P2Dist Z` · `P2BodyDist Z` · `ParentDist Z` ·
`RootDist Z` · `TopBoundDist` · `BotBoundDist` · `TopBoundBodyDist` ·
`BotBoundBodyDist` · `XAngle` · `YAngle` · `Xshear` · `GroundAngle` ·
`IsClsnProxy` · `SpritePlayerNo` · `Analog(axis)`

### Match, round and stage

`RoundsWon` · `ConsecutiveWins` · `DecisiveRound` · `WinClutch` · `WinHyper` ·
`WinSpecial` · `RoundTime` · `StageTime` · `FightTime` · `TimeElapsed` ·
`TimeRemaining` · `TimeTotal` · `GameMode = "..."` · `DebugMode` ·
`GroundLevel` · `StageConst(name)` · `StageBackEdgeDist` ·
`StageFrontEdgeDist` · `TopBoundDist` · `BotBoundDist` · `TopBoundBodyDist` ·
`BotBoundBodyDist` · `LocalCoord x/y` · `Const1080p(v)` · `InputTime(key)` ·
`Map(name)` · `IkemenVersion(part)` · `MugenVersion(part)` ·
`OxydeVersion(part)`

`GameMode` answers with Ikemen GO's spelling where a mode of theirs matches one
of ours — `arcade`, `versus`, `teamarcade`, `training`, `watch` — and Oxyde's
own lowercased name where it does not: `sparring`, `teamrumble`,
`rosterrumble`.

`IkemenVersion` answers `0`. A MUGEN character is, by construction, not an
Ikemen one, and a character asking is entitled to a straight answer rather than
a flattering one; `OxydeVersion(major/minor/patch)` is the honest one.

`LocalCoord` reads the character's `[Info] localcoord` — read, but not yet
applied: Oxyde draws every fighter in one coordinate space, as WinMugen does.
`Const1080p` is therefore the identity, for the same reason `Const240p` is.

---

## Controller reference

70 controllers beyond MUGEN. Every one of them accepts `RedirectID`, and so do
Elecbyte's 90 controllers.

| | |
|---|---|
| Named variables | `MapSet` `MapAdd` `MapReset` `ParentMapSet` `ParentMapAdd` `RootMapSet` `RootMapAdd` `TeamMapSet` `TeamMapAdd` `RootVarSet` `RootVarAdd` |
| Red life | `RedLifeAdd` `RedLifeSet` `TargetRedLifeAdd` |
| Dizzy | `DizzySet` `DizzyPointsAdd` `DizzyPointsSet` `TargetDizzyPointsAdd` |
| Guard break | `GuardBreakSet` `GuardPointsAdd` `GuardPointsSet` `TargetGuardPointsAdd` |
| Score | `ScoreAdd` `TargetScoreAdd` |
| Reaching further | `ModifyPlayer` `ModifyHitDef` `GetHitVarSet` `TargetAdd` |
| Shape and ground | `Height` `GroundLevelOffset` |
| The round clock | `RoundTimeAdd` `RoundTimeSet` |
| Input | `AssertInput` `ShiftInput` `AssertCommand` |
| Saying something | `Text` `ModifyText` `RemoveText` `PrintToConsole` |
| The third axis | `Depth` |
| The camera | `Zoom` `Camera` |
| Sprites and boxes | `TransformSprite` `TransformClsn` `OverrideClsn` `RemapSprite` `ShaderSet` `ModifyShadow` `ModifyReflection` |
| The stage | `ModifyStageVar` `ModifyStageBG` `ModifyBGCtrl` `ModifyBGCtrl3D` |
| The stage's own logic | `StageHazard` `StageBreakFloor` — run by the stage's FUSE state machine, not a fighter; see [STAGE-LOGIC.md](STAGE-LOGIC.md) |
| Sound and music | `PlayBgm` `ModifyBgm` `ModifySnd` |
| Other people's things | `ModifyProjectile` `ModifyReversalDef` |
| The match itself | `MatchRestart` `Storyboard` `Dialogue` `LifebarAction` `ChangeMovelist` |
| Persistence | `SaveFile` `LoadFile` |
| Analog sticks | `AssertAnalogVector` |

`Height` adds to the push box for one tick, the way `Width` does — positive
grows it, negative shrinks it. `GroundLevelOffset` moves the `y` this one
fighter treats as the floor, which is what a platform is. `Depth` is `Width` on
the third axis and expires the same way.

`LifebarAction` is the announcement band commercial fighting games put over the
bars — FIRST ATTACK, COUNTER, TECHNICAL — and MUGEN has no way to show at all.
It is drawn by the engine rather than out of the lifebar's own `[Action]`
sprites, because not one `fight.def` in this archive has that section: every
one of them was written before it existed.

| | |
|---|---|
| `text` | The message. Up to four are on screen at once, stacked |
| `time` | Ticks it stays, multiplied by `timemul`. It slides in over the first eight and out over the last eight |
| `snd` | `group, number` out of the *fight* bank, on the caller's channel |
| `font.color` | `r, g, b` — otherwise the engine's own amber |
| `font.align` | `0` centres, `1` left, `-1` right, against a one-eighth margin |
| `refreshtype` | `0` stacks duplicates, `1` refreshes the timer, `2` (the default) also re-enters from off screen, and plays the sting again once the message had finished arriving |
| `top` | Put it at the head of the queue rather than the tail |

`refreshtype` exists because a message driven from a state without
`persistent = 0` is posted every tick, and sixty identical FIRST ATTACKs a
second is not a feature.

### And several hundred parameters

The other half of the language work, and the half that is invisible in a count
of names: **parameters Elecbyte's own controllers gained.** A short list of the
ones that change what can be written, rather than how it is spelled:

* `HitDef` — `keepstate` (the hit lands and the defender stays put, which is
  what every armour move in the game is trying to say), `forcecrouch`,
  `sparkangle` / `sparkscale` and their guard forms, `hitsound.channel`,
  `ignorereversaldef`, `missonoverride`, `p2clsncheck` / `p2clsnrequire`,
  `guard.dist.width` / `.height`, `stand.friction` / `crouch.friction`,
  `envshake.mul` / `.dir`, `xaccel`, `down.recover` / `.recovertime`,
  `teamside`, `unhittabletime`, `attack.depth` and the `z` component of every
  velocity.
* `Helper` — `immortal`, `preserve`, `clsnproxy`, `ownclsnscale`,
  `ownprojectile`, `inheritjuggle`, `inheritchannels`, `kovelocity`,
  `extendsmap`, `map`, `size.depth`.
* `Explod` — `friction` (MUGEN has `accel` and nothing that slows an effect),
  `animfreeze`, `removeonchangestate`, `hidewithbars`, `xshear`, `window`,
  `layerno`, `palfx.*`, `shader`.
* `PalFX` — `hue`, `invertblend`, `sinmul`, `sincolor`, `sinhue`.
* `EnvShake` — `mul`, `decay`, `dir`, `diradd`: a shake that dies away and
  turns, where MUGEN's rattles on one axis until its timer runs out.
* `PlaySnd` — `loopstart`, `loopend`, `startposition`, `loopcount`,
  `volumescale`, `priority`, `stopongethit`, `stoponchangestate`.
* `HitOverride` — `forceguard`, `keepstate`, `guardflag`.
* `ReversalDef` — `reversal.guardflag` and its `.not`.
* `ChangeState` — `continue`, so the rest of the state still runs.
* `PlayerPush` — `priority` and `affectteam`, plus `[Size] pushfactor`: MUGEN
  splits every overlap evenly, so a boss twice the size of its opponent is
  shoved around the stage by them.
* `AttackMulSet` — one multiplier per meter. `DefenceMulSet` — `multype` and
  `onhit`. `AttackDist` — a box rather than one forward distance.
* `SprPriority` — `layerno`, a coarser ordering above sprite priority, so
  something that wants to draw over the HUD does not have to out-bid every
  sprite in the game.
* Every `Target*` controller — `index`, so a move that hit three opponents can
  address one of them.
* `ScreenBound` — `stagebound`, so a teleport can leave the screen and still
  stop at the wall of the stage.

`GetHitVar` gained thirty-odd parameters with them, which between them are the
difference between a custom gethit state that has to be written blind and one
that can read what actually happened to it.

### Variables past sixty

Two different numbers get confused here, so both are stated plainly.

**How many slots.** MUGEN gives a character sixty integers and forty floats.
Ikemen GO removed the ceiling entirely — `varSet` there checks only that the
index is not negative and writes into a `map[int32]int32`, so its real limit is
`int32`. This engine allows **65,536 of each**, indices `0` through `65535`, and
is therefore **more restrictive than Ikemen GO here**. The first sixty (and first forty) live in a flat array as
MUGEN's do; everything past them is held **sparsely**, so `var(12345)` costs
one map entry rather than twelve thousand words per fighter. Ordered, so the
netplay checksum does not depend on iteration order. The ceiling exists because
the index comes out of an expression the `.cns` controls, and an unbounded one
is an allocation an author can ask for by accident.

**How big each slot is.** A `var()` holds a **signed 32-bit integer**,
−2,147,483,648 to 2,147,483,647, and an `fvar()` holds a 32-bit float. That is
MUGEN's width, Ikemen GO's width and this engine's width — `Value::Int(i32)` in
`oxyde-cns`. **Nobody has ever widened the value; what Ikemen widened was the
count.**

So "Ikemen is int32" and "Oxyde allows 65,536" are both true and are not in
tension: one is the size of each box, the other is how many boxes there are.

| | highest index | how many slots | width of each |
|---|---:|---|---|
| MUGEN | 59 / 39 | 60 / 40, flat | int32 / float32 |
| Ikemen GO | 2,147,483,647 | unbounded | int32 / float32 |
| Oxyde | **2,147,483,647** | 60 / 40 flat **+ 65,536 sparse each** | int32 / float32 |

Oxyde and Ikemen address the same range. Oxyde additionally bounds how much a
single fighter can allocate, which Ikemen does not.

### What warns you

A literal index past MUGEN's sixty raises `var-beyond-mugen`, at hint level:
the character will not run on MUGEN itself, which is worth knowing and is not a
mistake here. There is no longer an index ceiling to warn about.

If a fighter ever exhausts its 65,536 extended slots, further *new* slots are
refused silently, because nothing irreversible happens inside `Match::step` and
a warning is state. No character in this archive comes close — the most any one
uses is a few dozen.

`oxyde_cns::VAR_EXT_SLOTS` is the single definition, re-exported by `sim.rs`.

---

## A worked example

A probe that puts everything on screen. Drop it in a character's DEF as an
extra state file (`st1 = probe.st`) and run the character.

```ini
[Statedef -4]
type = U

[State -4, name the map]
type = MapSet
trigger1 = RoundTime = 1
map = "probe"
value = 42

[State -4, count]
type = MapAdd
trigger1 = 1
map = "ticks"
value = 1

[Statedef +1]
type = U

[State +1, report]
type = Text
trigger1 = 1
id = 1
text = "map(probe)=%d ticks=%d score=%d redlife=%d stun=%d/%d guard=%d combo=%d playerno=%d"
params = Map(probe), Map(ticks), Score, RedLife, DizzyPoints, DizzyPointsMax, GuardPoints, ComboCount, PlayerNo
pos = 160, 30 + 12 * (PlayerNo - 1)
font = -1, 0, 0
removetime = 2
layerno = 2
```

---

## What is not here

Named, because a list of what an engine does not do is worth more than a list
of what it does.

Earlier revisions listed ZSS, Lua, glTF 3D backdrops, video backgrounds and
`SendToStage` here as missing. All of them ship now:

* **ZSS and Lua** are both here, on opposite sides of the simulation boundary.
  `.zss` is a recognised character front-end, compiled beside `.cns` and `.fuse`
  (`crates/oxyde-cns/src/zss.rs`), including `common1.cns.zss`. Lua runs the
  *mod* layer outside `Match::step` — seven hooks (`modes`, `ai`, `flow`, `hud`,
  `layout`, `rules`, `matchup`), with declarative Lua modes and a
  `layout(screen)` hook that re-describes the title, select, versus and result
  screens over `system.def`, which stays the base. See [MODDING.md](MODDING.md).
* **glTF stage backdrops and video backgrounds** draw on the hardware path:
  `model = stage3d.glb` renders a glTF backdrop (`crates/oxyde-gpu/src/model.rs`,
  with `KHR_materials_unlit`, `KHR_lights_punctual` and glTF animation), and a
  `type = video` layer plays a `.webm` through the normal background draw
  (`crates/oxyde-app/src/videobg.rs`). No stage in the base archive uses either.
* **`SendToStage`** is implemented as the inverse of `TagOut` (see
  [Tagging out](#tagging-out)). Undocumented in either manual, so its parameter
  set is a stated guess, and no character in this archive reaches it.

**Implemented differently**, on purpose. Each of these is a name Oxyde accepts
and a behaviour that is not quite Ikemen GO's:

* **Shaders.** `ShaderSet`, `Shader` and `[Shaders]` all work against a table of
  **sixteen named built-in effects** the software rasteriser implements, the
  deterministic default; a character may also ship a real `.wgsl` (or a `.frag`
  under the `glsl` feature) as an opt-in cosmetic lane on the hardware draw,
  which falls back to the nearest built-in with no GPU. See
  [Named effects](#named-effects) for what that buys and what it costs.
* **`xangle` / `yangle`.** Drawn as foreshortening of the corresponding axis —
  exact at 0 and 180 degrees, an approximation between — because a software
  rasteriser has no perspective divide. `projection` and `focallength` are read
  and recorded and do not bend the sprite.
* **`ModifyBGCtrl3D`** is accepted and recorded; glTF 3D backdrops are drawable
  (above), but no stage in this archive has a 3D background node for it to move.
* **Movelists.** Ikemen GO reads a `movelist` file named in the DEF; exactly one
  character in this archive ships one. Oxyde *derives* a list from every
  character's own `.cmd` and `[Statedef -1]`, so all 2,527 have one — and where
  an author has written a file, their names and their ordering win and the
  derived list follows underneath it. `ChangeMovelist` picks between several.
  See [MODES.md](MODES.md).
* **`SaveFile` / `LoadFile`.** Ikemen GO writes Go `gob` to disk inside a frame.
  Oxyde writes into an engine store that the *host* moves to and from disk
  between matches: a write inside `step()` is re-run by every rollback and a
  read is a syscall whose result the checksum would then depend on. A `.gob`
  written by Ikemen GO is not readable here.
* **Tag team.** `TagIn` and `TagOut` are executed, and Team Tag is a mode, but
  `TagIn`'s `leader` parameter is not: `TeamLeader` is derived from who is
  still standing rather than stored.
* **Dizzy and guard break states.** Ikemen GO sends a dizzied fighter to state
  6565300, defined in `dizzy.zss`. Oxyde takes control away instead, because
  nothing in this archive has a 6565300 to be sent to.
* **`Dialogue`.** The exchange is parsed in full — every `<pXname>`,
  `<pXface>`, `<sound>`, `<anim>`, `<state>`, `<map>`, `<displayname>` and
  `<wait>` token, with all six redirections — and queued. What draws it is the
  engine's own presentation rather than a screenpack `[Dialogue Info]` block.
* **`HitDefVar(hitflag)`** and **`(guardflag)`**, and the same two on
  `GetHitVar` and `ProjVar`, answer a **bitmask** where Ikemen GO's push a
  boolean and never show the mask at all. Ikemen GO's `= L` comparison is read
  and means what it means there; the general form is
  [`HasFlag`](#hasflag--membership-in-a-flag-set), which is one mechanism for
  every flag set rather than one per trigger, and which gives `!=` a single
  reading where Ikemen GO has two.
* **`$N`** — "any press or release of any key" — is the whole controller's
  edge, buttons included, and is *not* edge-triggered a second time on top of
  that: two changes on consecutive ticks are two hits. Ikemen GO arrives at the
  same reading from the age of the most recent change of any key, and calls
  MUGEN's behaviour here a bug it is emulating. `~$N` is left as this engine's
  generic release reading rather than aliased to `$N` the way Ikemen GO aliases
  it; no content anywhere writes either.
* **`buffer.shared`** and **`autogreater`** are read and **warn that they do
  nothing**, rather than being silently ignored. Oxyde's
  command matcher does not reset one command's buffer on another's completion,
  and does not expand `F, F` into `F, >~F, >F` — its elements are edge
  triggered, so `F, F` already needs two presses.

**Partly there:**

* **`localcoord`** is read and answered by the trigger; every fighter is still
  drawn in one coordinate space, as WinMugen does. `Const1080p` is therefore the
  identity, for the same reason `Const240p` is.
* **fightfx actions.** The `F` prefix selects the shared effects file for
  `Explod`, `PlaySnd` and `SuperPause`, as MUGEN documents. Ikemen GO extends it
  to `Statedef anim`, `ChangeAnim`, `ChangeState` and `Projectile`; those are a
  compile error here rather than a silent misreading.
