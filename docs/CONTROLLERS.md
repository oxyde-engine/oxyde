# State controllers

Every controller this engine accepts, its parameters, and how much of the
archive uses it. The controller list and the parameter lists are read out of
the compiler, so they cannot disagree with what the engine will take. The
descriptions are written; a controller without one says so.

Surveyed against 300 characters.

---

## `changestate`

Sends the fighter to another state. The single most-written controller in the archive — one call in five.

Used by **300** of 300 characters (100%).

**Parameters** (21): `alive`, `anim`, `attr`, `ctrl`, `elem`, `id`, `juggle`, `keyctrl`, `movetype`, `pausemovetime`, `physics`, `slot`, `sparkxy`, `sprpriority`, `supermove`, `supermovetime`, `tirgger9`, `trggier2`, `v`, `value`, `velset`

From a character in this archive:

```fuse
ChangeState(value: 1100)
```

---

## `hitdef`

Declares that the fighter is attacking this tick, and everything about what a connection does. A fifth of all FUSE by volume.

Used by **300** of 300 characters (100%).

**Parameters** (186): `absolute`, `affectteam`, `air.anim`, `air.animtype`, `air.cornerpush`, `air.cornerpush.veloff`, `air.ctrlime`, `air.fall`, `air.fall.recover`, `air.fall.yvelocity`, `air.hittime`, `air.juggle`, `air.pausetime`, `air.recover`, `air.slidetime`, `air.type`, `air.velocity`, `airguard.cornerpush.veloff`, `airguard.ctrltime`, `airguard.dist`, `airguard.hittime`, `airguard.slidetime`, `airguard.vel`, `airguard.velocity`, `anim`, `animtype`, `attack.depth`, `attr`, `bindtime`, `bounce`, `bounce.recover`, `can.recover`, `chainid`, `cornerpush.veloff`, `damage`, `down.animtype`, `down.bounce`, `down.cornerpush.veloff`, `down.fall`, `down.hittime`, `down.recover`, `down.slidetime`, `down.velocity`, `env.shake`, `envshake`, `envshake.ampl`, `envshake.freq`, `envshake.phase`, `envshake.time`, `facep2`, `fall`, `fall.animtype`, `fall.bounce`, `fall.damage`, `fall.envshake`, `fall.envshake.ampl`, `fall.envshake.freq`, `fall.envshake.phase`, `fall.envshake.time`, `fall.kill`, `fall.recover`, `fall.recovertime`, `fall.type`, `fall.xvelocity`, `fall.yvel`, `fall.yvelocity`, `flag`, `forceair`, `forcenofall`, `forcestand`, `getpower`, `givepower`, `ground.animtype`, `ground.cornerpush`, `ground.cornerpush.veloff`, `ground.fall`, `ground.fall.recover`, `ground.hit`, `ground.hittime`, `ground.recovertime`, `ground.slide`, `ground.slidetime`, `ground.type`, `ground.velocity`, `groundguard.velocity`, `guard`, `guard.cornerpush.veloff`, `guard.ctrltime`, `guard.dist`, `guard.hittime`, `guard.kill`, `guard.pause`, `guard.pausetime`, `guard.slide`, `guard.slidetime`, `guard.sparkno`, `guard.type`, `guard.vel`, `guard.velocity`, `guardflag`, `guardpause`, `guardsound`, `hitanim`, `hitcountpersist`, `hitdefpersist`, `hitflag`, `hitonce`, `hitsound`, `hitspark`, `hitsparkno`, `hittime`, `id`, `juggle`, `kill`, `liedown.time`, `maxdist`, `mindist`, `nochainid`, `numhits`, `offset`, `ownpal`, `p1facing`, `p1getp2facing`, `p1sprpriority`, `p1stateno`, `p2facing`, `p2getp1facing`, `p2getp1state`, `p2getp1stateno`, `p2stateno`, `p2statetype`, `p2turn`, `palfx`, `palfx.add`, `palfx.color`, `palfx.invert`, `palfx.invertall`, `palfx.mul`, `palfx.sinadd`, `palfx.time`, `pausemovetime`, `pausetime`, `persistance`, `postype`, `poweradd`, `priority`, `projanim`, `projcancelanim`, `projedgebound`, `projheightbound`, `projhitanim`, `projhits`, `projid`, `projmiss`, `projmisstime`, `projpriority`, `projremanim`, `projremove`, `projremovetime`, `projscale`, `projshadow`, `projsprpriority`, `projstagebound`, `random`, `recover`, `recover.time`, `recovertime`, `recovery`, `removeongethit`, `remvelocity`, `sinadd`, `slidetime`, `snap`, `spark.postype`, `spark.sprpriority`, `sparkno`, `sparkxy`, `sprpriority`, `supermove`, `supermovetime`, `superpause`, `velmul`, `velocity`, `velset`, `volume`, `yaccel`

From a character in this archive:

```fuse
HitDef(
            attr: S, NA,
            damage: 25,
            animtype: Light,
            guardflag: MA,
            hitflag: MAF,
            priority: 3, Hit,
            pausetime: 7,
            hitsound: S1, 3,
            guardsound: S1, 10,
            sparkno: S7000,
            guard.sparkno: S7002,
            sparkxy: -10, -25,
            ground.type: High,
            ground.slidetime: 12,
            ground.hittime: 12,
            ground.velocity: -2.8,
            air.type: High,
            air.velocity: -1, -3,
            air.hittime: 12,
        )
```

---

## `hitby`

The inverse of `NotHitBy`: makes the fighter hittable *only* by attacks matching the attribute, for a number of ticks.

Used by **299** of 300 characters (100%).

**Parameters** (5): `pausemovetime`, `supermove`, `supermovetime`, `time`, `value`

From a character in this archive:

```fuse
HitBy(value: SCA, time: 1)
```

---

## `nothitby`

Makes the fighter untouchable by attacks matching the given attribute, for a number of ticks.

Used by **299** of 300 characters (100%).

**Parameters** (9): `ctrl`, `movetime`, `pausemovetime`, `slot`, `supermove`, `supermovetime`, `time`, `value`, `value2`

From a character in this archive:

```fuse
NotHitBy(value: SCA, time: 1)
```

---

## `playsnd`

Plays a sound from the character's own `.snd`, or from the shared `fight.snd` with an `F` prefix.

Used by **299** of 300 characters (100%).

**Parameters** (38): `abspan`, `air.velocity`, `anim`, `animtype`, `attr`, `bindtime`, `channel`, `ctrl`, `damage`, `fall`, `freqmul`, `ground.hittime`, `ground.slidetime`, `ground.type`, `ground.velocity`, `guardflag`, `guardsound`, `hitsound`, `loop`, `lowpriority`, `ownpal`, `pan`, `pausemovetime`, `pausetime`, `postype`, `priority`, `removeongethit`, `removetime`, `sparkxy`, `sprpriority`, `supermove`, `supermovetime`, `v`, `value`, `volume`, `volumescale`, `x`, `y`

From a character in this archive:

```fuse
PlaySnd(value: 12, 2, volume: 120)
```

---

## `assertspecial`

Asserts an engine flag for one tick: hide the life bar, disable the timer, mute the music.

Used by **291** of 300 characters (97%).

**Parameters** (9): `flag`, `flag2`, `flag3`, `flag4`, `flag5`, `pausemovetime`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
AssertSpecial(flag: Intro)
```

---

## `velset`

Sets velocity outright, discarding whatever it was.

Used by **291** of 300 characters (97%).

**Parameters** (14): `ctrl`, `flag`, `pausemovetime`, `postype`, `redirectid`, `removetime`, `sprpriority`, `supermove`, `supermovetime`, `value`, `vel`, `x`, `y`, `z`

From a character in this archive:

```fuse
VelSet(x: 4.5, y: 0)
```

---

## `changeanim`

Switches the animation, restarting its element clock.

Used by **287** of 300 characters (96%).

**Parameters** (9): `ctrl`, `elem`, `flag`, `ignorethiapuse`, `pausemovetime`, `sprpriority`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
ChangeAnim(value: 183)
```

---

## `pause`

Freezes the game without the super flash.

Used by **286** of 300 characters (95%).

**Parameters** (14): `anim`, `ctrl`, `darken`, `endcmdbuftime`, `move`, `movetime`, `p2defmul`, `pausebg`, `pausemovetime`, `pos`, `sound`, `sprpriority`, `supermovetime`, `time`

From a character in this archive:

```fuse
Pause(
            time: 15,
            darken: 0,
            anim: 7004,
            pos: 0, -20,
        )
```

---

## `veladd`

Adds to the current velocity rather than replacing it.

Used by **280** of 300 characters (93%).

**Parameters** (7): `pausemovetime`, `sprpriority`, `supermovetime`, `value`, `x`, `y`, `z`

From a character in this archive:

```fuse
VelAdd(x: -0.2)
```

---

## `superpause`

Freezes the screen for a super. Every author in the archive opens a super with one.

Used by **277** of 300 characters (92%).

**Parameters** (25): `anim`, `bindtime`, `channel`, `ctrl`, `darken`, `id`, `move`, `movetime`, `ontop`, `ownpal`, `p2defmul`, `pausebg`, `pausemovetime`, `pos`, `postype`, `poweradd`, `removeongethit`, `sound`, `sprpriority`, `supermove`, `supermovetime`, `under`, `unhittable`, `value`, `volume`

From a character in this archive:

```fuse
SuperPause(
            time: 15,
            darken: 0,
            anim: 7004,
            pos: 0, -20,
        )
```

---

## `explod`

Spawns a free-standing animation — a spark, a shockwave, a flash. It is not a fighter and has no state machine.

Used by **275** of 300 characters (92%).

**Parameters** (77): `accel`, `air.velocity`, `airguard.velocity`, `alpha`, `angle`, `anim`, `animtype`, `attr`, `bindid`, `bindtime`, `damage`, `darken`, `down`, `explodtype`, `facing`, `flag`, `getpower`, `givepower`, `ground.hittime`, `ground.slidetime`, `ground.type`, `ground.velocity`, `guard.velocity`, `guardflag`, `guardsound`, `helpertype`, `hidewithbars`, `hitsound`, `id`, `ignorehitspark`, `ignorepause`, `ignorepausetime`, `ignoresuperpause`, `juggle`, `keyctrl`, `loop`, `name`, `offset`, `ontop`, `ownpal`, `p2stateno`, `pausemove`, `pausemovetime`, `pausetime`, `persist`, `pos`, `postype`, `priority`, `projshadow`, `random`, `removeongethit`, `removeonhit`, `removetime`, `scale`, `shader`, `shadow`, `size.shadowoffset`, `size.xscale`, `size.yscale`, `space`, `sparkxy`, `sprpriority`, `stateno`, `supermove`, `supermovetime`, `superpausetime`, `trans`, `trans.alpha`, `trans.type`, `turn`, `under`, `unhittable`, `value`, `vel`, `velocity`, `velset`, `vfacing`

From a character in this archive:

```fuse
Explod(
            anim: 1004,
            sprpriority: 3,
            id: 1007,
            postype: P1,
            pos: 35, -20,
            ownpal: 1,
        )
```

---

## `varset`

Writes one of the character's own variables.

Used by **275** of 300 characters (92%).

**Parameters** (15): `add`, `command`, `framegap`, `length`, `palbright`, `palcontrast`, `palmul`, `pausemovetime`, `sinadd`, `supermove`, `supermovetime`, `sysvar`, `trans`, `v`, `value`

From a character in this archive:

```fuse
VarSet(fv: 2, value: 0.0)
```

---

## `posadd`

Moves the fighter by an offset, ignoring physics for the tick.

Used by **268** of 300 characters (89%).

**Parameters** (6): `pausemovetime`, `postype`, `supermovetime`, `value`, `x`, `y`

From a character in this archive:

```fuse
PosAdd(x: 1-2 * (time % 2))
```

---

## `posset`

Places the fighter at an absolute position.

Used by **266** of 300 characters (89%).

**Parameters** (10): `facing`, `movecamera`, `pausemovetime`, `pos`, `postype`, `supermove`, `supermovetime`, `value`, `x`, `y`

From a character in this archive:

```fuse
PosSet(x: (enemy(0).Pos X), y: -20)
```

---

## `ctrlset`

Gives control back to the player, or takes it away.

Used by **265** of 300 characters (88%).

**Parameters** (4): `ctrl`, `pausemovetime`, `supermovetime`, `value`

From a character in this archive:

```fuse
CtrlSet(value: 1)
```

---

## `selfstate`

Returns a fighter to its *own* state machine after being held in someone else's custom state.

Used by **265** of 300 characters (88%).

**Parameters** (7): `alive`, `anim`, `ctrl`, `ignorepause`, `pausemovetime`, `supermovetime`, `value`

From a character in this archive:

```fuse
SelfState(ctrl: 1, value: 0)
```

---

## `changeanim2`

Like `ChangeAnim`, but selects the animation from the *attacker's* file. How a custom-state throw shows the victim an animation the victim does not own.

Used by **261** of 300 characters (87%).

**Parameters** (5): `ctrl`, `elem`, `id`, `sprpriority`, `value`

From a character in this archive:

```fuse
changeanim2(value: 820)
```

---

## `lifeadd`

Adds to, or takes from, the fighter's own life.

Used by **259** of 300 characters (86%).

**Parameters** (4): `absolute`, `ctrl`, `kill`, `value`

From a character in this archive:

```fuse
lifeadd(value: -78)
```

---

## `turn`

Faces the fighter the other way, immediately.

Used by **256** of 300 characters (85%).

**Parameters** (4): `pausemovetime`, `supermovetime`, `value`, `y`

From a character in this archive:

```fuse
Turn()
```

---

## `helper`

Spawns a second fighter under the character's control — a fireball, a tracking effect, a second body.

Used by **254** of 300 characters (85%).

**Parameters** (53): `air.back`, `air.front`, `alpha`, `anim`, `bindtime`, `ctrl`, `facep2`, `facing`, `ground.back`, `ground.front`, `helpertype`, `id`, `immortal`, `juggle`, `keyctrl`, `name`, `offset`, `ontop`, `ownpal`, `pausemove`, `pausemovetime`, `pausetime`, `pos`, `postype`, `preserve`, `priority`, `random`, `removeongethit`, `removetime`, `scale`, `shadow`, `size.air.back`, `size.air.front`, `size.ground.back`, `size.ground.front`, `size.head.pos`, `size.height`, `size.mid.pos`, `size.proj.doscale`, `size.shadowoffset`, `size.xscale`, `size.yscale`, `sprpriority`, `standby`, `stateno`, `supermove`, `supermovetime`, `superpausetime`, `trans`, `under`, `value`, `vel`, `velocity`

From a character in this archive:

```fuse
Helper(1300)
```

---

## `afterimage`

Leaves a trail of past frames behind the fighter.

Used by **253** of 300 characters (84%).

**Parameters** (28): `add`, `afterimagetime`, `alpha`, `color`, `framegap`, `gap`, `invartall`, `length`, `ownpal`, `paladd`, `palbright`, `palcolor`, `palcontrast`, `palfx`, `palfx.add`, `palfx.time`, `palinvertall`, `palmul`, `palpostbright`, `pausemovetime`, `removeongethit`, `removetime`, `sprpriority`, `supermove`, `supermovetime`, `time`, `timegap`, `trans`

From a character in this archive:

```fuse
AfterImage(
            time: 220,
            timegap: 1,
            framegap: 1,
            length: 220,
            palbright: 0, 0, 245,
            palcontrast: 0, 0, 245,
            trans: add,
        )
```

---

## `destroyself`

Removes a helper. Has no effect on a real fighter.

Used by **248** of 300 characters (83%).

**Parameters** (6): `ctrl`, `id`, `pausemovetime`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
DestroySelf()
```

---

## `palfx`

Tints, brightens or inverts the fighter's palette for a number of ticks.

Used by **243** of 300 characters (81%).

**Parameters** (21): `add`, `bright`, `color`, `contrast`, `ignorepausetime`, `invert`, `invertall`, `mul`, `ontop`, `palfx.color`, `palfx.mul`, `palfx.sinadd`, `pausemovetime`, `removeongethit`, `sinadd`, `sprpriority`, `supermove`, `supermovetime`, `time`, `trans`, `value`

From a character in this archive:

```fuse
PalFX(
            add: 49, 173, 231,
            mul: 13, 179, 199,
            time: 1,
        )
```

---

## `targetbind`

Moves whoever this fighter has hit to a position relative to itself. How every throw holds its victim.

Used by **243** of 300 characters (81%).

**Parameters** (8): `bindtime`, `edge`, `id`, `pos`, `postype`, `sprpriority`, `x`, `y`

From a character in this archive:

```fuse
targetbind(pos: 28, 0)
```

---

## `envshake`

Shakes the screen.

Used by **234** of 300 characters (78%).

**Parameters** (15): `ampl`, `bindtime`, `decay`, `fall.recover`, `freq`, `freqmul`, `frequency`, `ground.cornerpush.veloff`, `pausemovetime`, `phase`, `removeongethit`, `removetime`, `supermovetime`, `time`, `value`

From a character in this archive:

```fuse
EnvShake(
            time: 10,
            ampl: -3,
            freq: 30,
            phase: 30,
        )
```

---

## `playerpush`

Turns the push box on or off for one tick.

Used by **220** of 300 characters (73%).

**Parameters** (3): `pausemovetime`, `supermovetime`, `value`

From a character in this archive:

```fuse
PlayerPush(value: 0)
```

---

## `poweradd`

Adds to, or spends, the power bar.

Used by **218** of 300 characters (73%).

**Parameters** (5): `absolute`, `pausemovetime`, `supermovetime`, `v`, `value`

From a character in this archive:

```fuse
PowerAdd(value: 15)
```

---

## `screenbound`

Says whether the camera must keep this fighter on screen, and whether the stage edge stops it.

Used by **213** of 300 characters (71%).

**Parameters** (5): `movecamera`, `pausemovetime`, `stagebound`, `supermovetime`, `value`

From a character in this archive:

```fuse
screenbound(value: 0, movecamera: 0, 0)
```

---

## `varadd`

Adds to a variable rather than replacing it.

Used by **213** of 300 characters (71%).

**Parameters** (14): `framegap`, `fv`, `ignorepausetime`, `length`, `paladd`, `palbright`, `palcontrast`, `palmul`, `pausemovetime`, `supermove`, `supermovetime`, `trans`, `v`, `value`

From a character in this archive:

```fuse
varAdd(fv: 2, value: 0.1570796)
```

---

## `varrandom`

Writes a random number into a variable, inside a range. Seeded by the match, so a replay reproduces it.

Used by **206** of 300 characters (69%).

**Parameters** (8): `add`, `pausemovetime`, `range`, `sinadd`, `supermove`, `supermovetime`, `v`, `value`

From a character in this archive:

```fuse
VarRandom(v: 1, range: 0, 180)
```

---

## `width`

Widens or narrows the push box for one tick. It expires every tick, like every controller of its kind.

Used by **202** of 300 characters (67%).

**Parameters** (6): `channel`, `edge`, `pausemovetime`, `player`, `supermovetime`, `value`

From a character in this archive:

```fuse
width(value: 10, 0)
```

---

## `sprpriority`

Sets which fighter draws in front when sprites overlap. Higher draws nearer the viewer.

Used by **200** of 300 characters (67%).

**Parameters** (6): `layerno`, `pausemovetime`, `redirectid`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
sprpriority(value: 5)
```

---

## `projectile`

Fires a projectile with its own animation, hit properties and lifetime.

Used by **197** of 300 characters (66%).

**Parameters** (166): `accel`, `affectteam`, `afterimage.framegap`, `afterimage.length`, `afterimage.paladd`, `afterimage.palbright`, `afterimage.palcontrast`, `afterimage.palinvertall`, `afterimage.palmul`, `afterimage.palpostbright`, `afterimage.time`, `afterimage.timegap`, `afterimage.trans`, `air.anim`, `air.animtype`, `air.cornerpush.veloff`, `air.fall`, `air.fall.recover`, `air.hittime`, `air.juggle`, `air.recover`, `air.slidetime`, `air.type`, `air.velocity`, `airguard.cornerpush.veloff`, `airguard.ctrltime`, `airguard.velocity`, `animtype`, `attr`, `bindtime`, `bounce`, `chain.id`, `chainid`, `damage`, `delta`, `down.bounce`, `down.cornerpush.veloff`, `down.hittime`, `down.recover`, `down.velocity`, `envshake.ampl`, `envshake.freq`, `envshake.phase`, `envshake.time`, `facing`, `fall`, `fall.animtype`, `fall.damage`, `fall.envshake.ampl`, `fall.envshake.freq`, `fall.envshake.phase`, `fall.envshake.time`, `fall.kill`, `fall.recover`, `fall.recovertime`, `fall.xvelocity`, `fall.yvelocity`, `forcestand`, `getpower`, `givepower`, `ground.animtype`, `ground.cornerpush.veloff`, `ground.hit`, `ground.hittime`, `ground.slide`, `ground.slidetime`, `ground.type`, `ground.velocity`, `groundguard.velocity`, `guard`, `guard.cornerpush.veloff`, `guard.ctrltime`, `guard.dist`, `guard.hittime`, `guard.kill`, `guard.pausetime`, `guard.slidetime`, `guard.sparkno`, `guard.type`, `guard.velocity`, `guardflag`, `guardsound`, `helpertype`, `hit.sparkno`, `hitflag`, `hitonce`, `hitsound`, `hitspark`, `hitsprak`, `id`, `juggle`, `kill`, `name`, `nochainid`, `numhits`, `offset`, `ontop`, `ownpal`, `p1getp2facing`, `p2facing`, `p2getp1facing`, `p2getp1state`, `p2getp1stateno`, `p2stateno`, `palfx.add`, `palfx.color`, `palfx.invert`, `palfx.invertall`, `palfx.mul`, `palfx.sinadd`, `palfx.time`, `pausemovetime`, `pausetime`, `pos`, `posset`, `postype`, `poweradd`, `priority`, `proj.add`, `proj.color`, `proj.invertall`, `proj.sinadd`, `proj.time`, `projairguard.velocity`, `projanim`, `projcancelanim`, `projcanceltime`, `projdepthbound`, `projedgebound`, `projguard.velocity`, `projguardanim`, `projheightbound`, `projhitanim`, `projhits`, `projid`, `projmissanim`, `projmisstime`, `projnumhits`, `projpriority`, `projremanim`, `projremove`, `projremoveanim`, `projremovetime`, `projscale`, `projscreenbound`, `projshadow`, `projsprpriority`, `projstagebound`, `random`, `recover`, `removeanim`, `removeongethit`, `removetime`, `remvelocity`, `scale`, `sinadd`, `sparkno`, `sparkxy`, `sprpriority`, `supermovetime`, `vel`, `velmul`, `velocity`, `volum`, `volume`, `yaccel`

From a character in this archive:

```fuse
Projectile(
            projid: 715,
            hitflag: P,
            projanim: 715,
            projhitanim: 715,
            projremanim: 715,
            projcancelanim: 715,
            projremove: 1,
            projremovetime: 1,
            velocity: 0, 0,
            projhits: 1,
            pos: 10, 0,
            postype: p1,
            projshadow: 0, 0, 0,
            numhits: 0,
        )
```

---

## `velmul`

Multiplies the current velocity rather than setting or adding to it — friction, or a sudden boost, without knowing the speed.

Used by **196** of 300 characters (65%).

**Parameters** (4): `supermove`, `x`, `y`, `z`

From a character in this archive:

```fuse
velmul(x: .9)
```

---

## `removeexplod`

Removes explods this fighter created, all of them or by id.

Used by **191** of 300 characters (64%).

**Parameters** (14): `anim`, `bindtime`, `ctrl`, `id`, `name`, `ownpal`, `pausemovetime`, `pos`, `postype`, `removeongethit`, `sprpriority`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
RemoveExplod(id: 7012)
```

---

## `targetlifeadd`

Adds to, or takes from, the life of whoever this fighter has hit.

Used by **188** of 300 characters (63%).

**Parameters** (7): `absolute`, `anim`, `fall.kill`, `guard.kill`, `id`, `kill`, `value`

From a character in this archive:

```fuse
targetlifeadd(value: -78)
```

---

## `targetstate`

Sends whoever this fighter has hit into one of *this* character's states. The other half of a throw.

Used by **185** of 300 characters (62%).

**Parameters** (7): `ctrl`, `elem`, `id`, `pausemovetime`, `pos`, `supermovetime`, `value`

From a character in this archive:

```fuse
targetstate(value: 821)
```

---

## `afterimagetime`

Changes how long an afterimage already running will last. It does not start one — `AfterImage` does that.

Used by **183** of 300 characters (61%).

**Parameters** (14): `add`, `ctrl`, `framegap`, `length`, `paladd`, `palbright`, `palcontrast`, `palmul`, `palpostbright`, `pausemovetime`, `supermove`, `time`, `trans`, `value`

From a character in this archive:

```fuse
AfterimageTime(time: 2)
```

---

## `posfreeze`

Holds the fighter still for a tick without changing its velocity.

Used by **181** of 300 characters (60%).

**Parameters** (3): `value`, `x`, `y`

From a character in this archive:

```fuse
PosFreeze(value: 1)
```

---

## `null`

Does nothing, deliberately. Authors use it to disable a controller without deleting it.

Used by **171** of 300 characters (57%).

**Parameters** (165): `absolute`, `abspan`, `accel`, `add`, `affectteam`, `air.animtype`, `air.cornerpush.veloff`, `air.fall`, `air.hittime`, `air.juggle`, `air.recover`, `air.type`, `air.velocity`, `airguard.cornerpush.veloff`, `airguard.velocity`, `alpha`, `ampl`, `anim`, `animtype`, `attr`, `bindtime`, `channel`, `color`, `ctrl`, `damage`, `darken`, `down.bounce`, `down.hittime`, `down.velocity`, `edge`, `elem`, `envshake.ampl`, `envshake.freq`, `envshake.phase`, `envshake.time`, `facing`, `fall`, `fall.recover`, `fall.recovertime`, `fall.xvelocity`, `fall.yvelocity`, `first`, `flag`, `flag2`, `forcestand`, `framegap`, `freq`, `freqmul`, `gap`, `getpower`, `givepower`, `ground.cornerpush.veloff`, `ground.hittime`, `ground.slidetime`, `ground.type`, `ground.velocity`, `guard.cornerpush.veloff`, `guard.ctrltime`, `guard.dist`, `guard.hittime`, `guard.kill`, `guard.pausetime`, `guard.slidetime`, `guard.sparkno`, `guard.velocity`, `guardflag`, `guardsound`, `helpertype`, `hitflag`, `hitonce`, `hitsound`, `hittime`, `id`, `invertall`, `juggle`, `keyctrl`, `kill`, `last`, `length`, `loop`, `movecamera`, `movetime`, `mul`, `name`, `numhits`, `offset`, `ontop`, `ownpal`, `p2facing`, `p2stateno`, `paladd`, `palbright`, `palcolor`, `palcontrast`, `palfx`, `palfx.add`, `palfx.color`, `palfx.invertall`, `palfx.mul`, `palfx.sinadd`, `palfx.time`, `palmul`, `palpostbright`, `params`, `pausemove`, `pausemovetime`, `pausetime`, `phase`, `physics`, `pitch`, `player`, `pos`, `postype`, `poweradd`, `priority`, `projanim`, `projcancelanim`, `projedgebound`, `projheightbound`, `projhitanim`, `projhits`, `projid`, `projmisstime`, `projpriority`, `projremanim`, `projremove`, `projremovetime`, `projscale`, `projshadow`, `projsprpriority`, `random`, `range`, `removeongethit`, `removetime`, `remvelocity`, `reversal.attr`, `scale`, `shadow`, `sinadd`, `size.xscale`, `size.yscale`, `slidetime`, `slot`, `sound`, `sparkno`, `sparkxy`, `sprpriority`, `stateno`, `statetype`, `supermove`, `supermovetime`, `text`, `timegap`, `trans`, `trggier2`, `under`, `unhittable`, `v`, `value`, `vel`, `velocity`, `velset`, `vfacing`, `x`, `y`

From a character in this archive:

```fuse
null()
```

---

## `envcolor`

Floods the screen with a colour for a number of ticks. What a super flash is made of.

Used by **169** of 300 characters (56%).

**Parameters** (20): `add`, `background`, `behind`, `col`, `color`, `darken`, `ignorepausetime`, `invertall`, `loop`, `mul`, `ontop`, `ownpal`, `pausemovetime`, `removeongethit`, `sinadd`, `sprpriority`, `supermove`, `supermovetime`, `under`, `value`

From a character in this archive:

```fuse
EnvColor(
            value: 0, 0, 0,
            under: 1,
            time: 45,
        )
```

---

## `hitoverride`

Diverts a hit matching an attribute into a state of the author's choosing, instead of the usual reaction.

Used by **169** of 300 characters (56%).

**Parameters** (12): `attr`, `ctrl`, `forceair`, `hitflag`, `pausemovetime`, `pausetime`, `slot`, `stateno`, `supermove`, `supermovetime`, `time`, `velset`

From a character in this archive:

```fuse
HitOverride(
            time: 130,
            attr: SCA,
            slot: 0,
            stateno: 5050,
            forceair: 1,
        )
```

---

## `statetypeset`

Changes what the engine considers the fighter to be doing — standing, crouching, airborne — without changing state.

Used by **168** of 300 characters (56%).

**Parameters** (11): `ctrl`, `movetype`, `pausemovetime`, `physics`, `sprpriority`, `state`, `statetype`, `statetypeset`, `supermovetime`, `value`, `velset`

From a character in this archive:

```fuse
StateTypeSet(
            statetype: A,
            movetype: A,
            physics: A,
        )
```

---

## `hitvelset`

Applies the velocity of the hit currently being taken, on either axis.

Used by **161** of 300 characters (54%).

**Parameters** (4): `value`, `x`, `y`, `z`

From a character in this archive:

```fuse
hitvelset(x: 1, y: 1)
```

---

## `displaytoclipboard`

Prints to the debug clipboard, replacing whatever was there.

Used by **149** of 300 characters (50%).

**Parameters** (3): `params`, `text`, `value`

From a character in this archive:

```fuse
DisplayToClipboard(text: "damge = %d - CC = %d - P2dist = %.0f - Super Cancel = %d", params: Var(32), Var(15), p2bodydist x, Var(12))
```

---

## `bgpalfx`

The same, applied to the stage only.

Used by **142** of 300 characters (47%).

**Parameters** (17): `add`, `bindtime`, `color`, `id`, `invertall`, `mul`, `pausemovetime`, `scale`, `sinadd`, `sincolor`, `sinmul`, `sprpriority`, `supermove`, `supermovetime`, `time`, `under`, `value`

From a character in this archive:

```fuse
bgpalfx(time: 60, sinadd: -200, -200, -200, 180)
```

---

## `stopsnd`

Stops a sound this fighter is playing, by channel.

Used by **140** of 300 characters (47%).

**Parameters** (2): `channel`, `value`

From a character in this archive:

```fuse
StopSNd(channel: 4)
```

---

## `makedust`

Draws the small dust puff the common states use on landing.

Used by **124** of 300 characters (41%).

**Parameters** (5): `pos`, `postype`, `random`, `spacing`, `sprpriority`

From a character in this archive:

```fuse
MakeDust(pos: -25, -2, spacing: 1)
```

---

## `forcefeedback`

Rumbles the pad. Ignored when the pad cannot, which is most of them.

Used by **123** of 300 characters (41%).

**Parameters** (4): `ampl`, `sprpriority`, `time`, `waveform`

From a character in this archive:

```fuse
ForceFeedback(
            waveform: sinesquare,
            ampl: 128, -3, -.2, .005,
            time: 20,
        )
```

---

## `bindtoparent`

Pins a helper to whatever spawned it, which for a nested helper is not the root.

Used by **122** of 300 characters (41%).

**Parameters** (19): `add`, `alpha`, `bindtime`, `facing`, `id`, `ignorepause`, `pausemovetime`, `pos`, `postype`, `prpriority`, `scale`, `sinadd`, `sprpriority`, `supermove`, `supermovetime`, `trans`, `value`, `x`, `y`

From a character in this archive:

```fuse
BindToParent(
            facing: 1,
            pos: 55, -115,
            time: 1,
        )
```

---

## `gamemakeanim`

Draws one of the shared `fightfx` animations, rather than one of the character's own.

Used by **121** of 300 characters (40%).

**Parameters** (9): `bindtime`, `ontop`, `ownpal`, `pos`, `postype`, `random`, `sprpriority`, `under`, `value`

From a character in this archive:

```fuse
GameMakeAnim(
            value: 60 + (sysvar(1) > 5) + (sysvar(1) > 14),
            pos: 0, 0,
            under: sysvar(1) <= 10,
        )
```

---

## `attackmulset`

Scales the damage of everything this fighter does from now on.

Used by **119** of 300 characters (40%).

**Parameters** (4): `pausemovetime`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
AttackMulSet(value: 0.8)
```

---

## `parentvarset`

Writes a variable belonging to the fighter that spawned this helper.

Used by **112** of 300 characters (37%).

**Parameters** (4): `pausemovetime`, `supermovetime`, `v`, `value`

From a character in this archive:

```fuse
parentvarset(v: 59, value: 1)
```

---

## `hitadd`

Adds to the combo counter without a hit having landed.

Used by **107** of 300 characters (36%).

**Parameters** (2): `kill`, `value`

From a character in this archive:

```fuse
HitAdd(value: 1)
```

---

## `gravity`

Applies the character's own `yaccel` constant for one tick. What the common air states use to fall.

Used by **102** of 300 characters (34%).

**Parameters** (2): `value`, `y`

From a character in this archive:

```fuse
Gravity()
```

---

## `hitfalldamage`

Applies the fall damage of the hit that is currently being taken.

Used by **102** of 300 characters (34%).

From a character in this archive:

```fuse
HitFallDamage()
```

---

## `angledraw`

Draws the fighter rotated, for one tick.

Used by **96** of 300 characters (32%).

**Parameters** (5): `pausemovetime`, `scale`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
angledraw()
```

---

## `defencemulset`

Scales the damage this fighter takes from now on.

Used by **96** of 300 characters (32%).

**Parameters** (1): `value`

From a character in this archive:

```fuse
DefenceMulSet(value: .75)
```

---

## `reversaldef`

Declares that this fighter *catches* an incoming attack matching an attribute, rather than being hit by it. How a parry or a counter-throw is written.

Used by **95** of 300 characters (32%).

**Parameters** (50): `air.animtype`, `air.fall`, `air.type`, `air.velocity`, `animtype`, `attr`, `channel`, `damage`, `envshake.ampl`, `envshake.freq`, `envshake.phase`, `envshake.time`, `fall`, `fall.recover`, `fall.yvelocity`, `forcestand`, `getpower`, `givepower`, `ground.hittime`, `ground.slidetime`, `ground.type`, `ground.velocity`, `guard.pausetime`, `guard.sparkno`, `guardflag`, `guardsound`, `hitflag`, `hitonce`, `hitsound`, `id`, `kill`, `numhits`, `p1facing`, `p1sprpriority`, `p1stateno`, `p2facing`, `p2getp1state`, `p2sprpriority`, `p2stateno`, `palfx.add`, `palfx.time`, `pausetime`, `poweradd`, `priority`, `reversal.attr`, `snap`, `sparkno`, `sparkxy`, `sprpriority`, `yaccel`

From a character in this archive:

```fuse
ReversalDef(
            reversal.attr: SCA, NA, SA, HA,
            pausetime: 8, 96,
            palfx.time: 10,
            palfx.add: 128, 128, 255,
        )
```

---

## `fallenvshake`

Shakes the screen with the parameters the current hit asked for, when the victim lands.

Used by **90** of 300 characters (30%).

From a character in this archive:

```fuse
FallEnvShake()
```

---

## `hitfallset`

Changes whether the hit currently being taken makes the victim fall.

Used by **86** of 300 characters (29%).

**Parameters** (5): `pausemovetime`, `supermovetime`, `value`, `xvel`, `yvel`

From a character in this archive:

```fuse
HitFallSet(value: 1)
```

---

## `varrangeset`

Writes a run of variables at once. Capped at 2,500 per use, as Ikemen GO caps it.

Used by **81** of 300 characters (27%).

**Parameters** (5): `first`, `fvalue`, `last`, `supermovetime`, `value`

From a character in this archive:

```fuse
VarRangeSet(value: 0)
```

---

## `modifyexplod`

Edits an explod already on screen rather than spawning another.

Used by **76** of 300 characters (25%).

**Parameters** (24): `accel`, `alpha`, `angle`, `anim`, `bindtime`, `facing`, `id`, `ignorepausetime`, `index`, `ontop`, `ownpal`, `pausemovetime`, `pos`, `postype`, `random`, `removeongethit`, `removetime`, `scale`, `shadow`, `sprpriority`, `supermove`, `supermovetime`, `trans`, `vel`

From a character in this archive:

```fuse
modifyexplod(id: 1301, scale: ifelse(time <= 6, time / 6.0, 1 + (time-6) / 40.0), ifelse(time <= 6.0, time / 6.0, 1 + (time-6) / 40.0))
```

---

## `angleset`

Sets the drawing angle outright.

Used by **68** of 300 characters (23%).

**Parameters** (2): `scale`, `value`

From a character in this archive:

```fuse
angleset(value: 0)
```

---

## `hitfallvel`

Applies the fall velocity of the hit currently being taken.

Used by **65** of 300 characters (22%).

From a character in this archive:

```fuse
HitFallVel()
```

---

## `allpalfx`

The same, applied to everything on screen.

Used by **60** of 300 characters (20%).

**Parameters** (8): `add`, `color`, `invertall`, `mul`, `pausemovetime`, `sinadd`, `supermove`, `supermovetime`

From a character in this archive:

```fuse
AllPalFX(
            time: 10,
            add: 0, 0, 100,
            sinadd: 5, 5, 100, 30,
        )
```

---

## `bindtotarget`

Pins this fighter to whoever it has hit — the attacker moving to the victim, rather than the other way round.

Used by **59** of 300 characters (20%).

**Parameters** (3): `bindtime`, `id`, `pos`

From a character in this archive:

```fuse
BindToTarget(pos: 0, 0, head)
```

---

## `movehitreset`

Clears `movehit`, `moveguarded` and `movecontact`, so the next contact registers as new. The attack in hand is not re-armed: only executing a `HitDef` again lets it land on someone it has already hit.

Used by **57** of 300 characters (19%).

**Parameters** (5): `pausemovetime`, `supermove`, `supermovetime`, `under`, `value`

From a character in this archive:

```fuse
movehitreset()
```

---

## `angleadd`

Adds to the drawing angle set by `AngleDraw`.

Used by **56** of 300 characters (19%).

**Parameters** (5): `anim`, `pausemovetime`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
angleadd(value: -30)
```

---

## `bindtoroot`

Pins a helper to the character that spawned it.

Used by **50** of 300 characters (17%).

**Parameters** (8): `facing`, `pausemovetime`, `pos`, `supermove`, `supermovetime`, `value`, `x`, `y`

From a character in this archive:

```fuse
BindToRoot(time: 1, pos: 56, -72)
```

---

## `powerset`

Sets the power bar outright.

Used by **40** of 300 characters (13%).

**Parameters** (4): `pausemovetime`, `supermove`, `supermovetime`, `value`

From a character in this archive:

```fuse
Powerset(value: 1000)
```

---

## `parentvaradd`

Adds to a variable belonging to the fighter that spawned this helper.

Used by **39** of 300 characters (13%).

**Parameters** (3): `fv`, `v`, `value`

From a character in this archive:

```fuse
ParentVarAdd(v: 12, value: 1)
```

---

## `trans`

Sets the transparency mode the fighter draws with for a tick.

Used by **33** of 300 characters (11%).

**Parameters** (3): `alpha`, `trans`, `value`

From a character in this archive:

```fuse
trans(trans: add)
```

---

## `targetfacing`

Turns whoever this fighter has hit to face a given direction.

Used by **32** of 300 characters (11%).

**Parameters** (2): `id`, `value`

From a character in this archive:

```fuse
TargetFacing(value: 1)
```

---

## `appendtoclipboard`

Prints to the debug clipboard, keeping what was there.

Used by **30** of 300 characters (10%).

**Parameters** (2): `params`, `text`

From a character in this archive:

```fuse
AppendToClipBoard(text: "\nXP= (%d)- Pergaminho - %d", params: Var(49), Var(50))
```

---

## `targetpoweradd`

Adds to the power bar of whoever this fighter has hit.

Used by **26** of 300 characters (9%).

**Parameters** (2): `id`, `value`

From a character in this archive:

```fuse
TargetPowerAdd(value: -45)
```

---

## `targetvelset`

Sets the velocity of whoever this fighter has hit.

Used by **22** of 300 characters (7%).

**Parameters** (2): `x`, `y`

From a character in this archive:

```fuse
TargetVelSet(x: -(Vel X), y: Vel Y)
```

---

## `lifeset`

Sets life outright.

Used by **20** of 300 characters (7%).

**Parameters** (3): `absolute`, `kill`, `value`

From a character in this archive:

```fuse
LifeSet(value: 1000)
```

---

## `targetdrop`

Forgets some or all of the targets this fighter has hit, so later controllers stop affecting them.

Used by **19** of 300 characters (6%).

**Parameters** (3): `excludeid`, `id`, `keepone`

From a character in this archive:

```fuse
TargetDrop()
```

---

## `targetveladd`

Adds to the velocity of whoever this fighter has hit.

Used by **16** of 300 characters (5%).

**Parameters** (2): `x`, `y`

From a character in this archive:

```fuse
TargetVelAdd(x: .5, y: 0)
```

---

## `attackdist`

Changes the guard distance of the `HitDef` in flight — how close the opponent must be to start blocking.

Used by **10** of 300 characters (3%).

**Parameters** (2): `supermovetime`, `value`

From a character in this archive:

```fuse
AttackDist(value: 170)
```

---

## `sndpan`

Moves a sound already playing across the stereo field.

Used by **9** of 300 characters (3%).

**Parameters** (4): `abspan`, `channel`, `pan`, `value`

From a character in this archive:

```fuse
SndPan(channel: 0, pan: 0)
```

---

## `offset`

Shifts where the sprite draws, without moving the fighter.

Used by **6** of 300 characters (2%).

**Parameters** (2): `x`, `y`

From a character in this archive:

```fuse
Offset(y: -50)
```

---

## `explodbindtime`

Changes how long an explod stays bound to the fighter that made it.

Used by **1** of 300 characters (0%).

**Parameters** (1): `id`

From a character in this archive:

```fuse
explodbindtime(time: -1, id: 2200)
```

---

## `anglemul`

Multiplies the drawing angle.

Not used by any character in this archive.

---

## `assertanalogvector`

Asserts an analogue stick position rather than a digital direction.

Not used by any character in this archive.

---

## `assertcommand`

Asserts a command as though the player had performed it.

Not used by any character in this archive.

**Parameters** (2): `buffer.time`, `name`

---

## `assertinput`

Asserts a button or direction as though the player pressed it. An Oxyde and Ikemen extension.

Not used by any character in this archive.

**Parameters** (4): `flag`, `flag2`, `flag3`, `redirectid`

---

## `camera`

Moves or constrains the camera directly.

Not used by any character in this archive.

---

## `changemovelist`

Switches which move list the training screen shows for this character.

Not used by any character in this archive.

---

## `clearclipboard`

Empties the debug clipboard.

Not used by any character in this archive.

---

## `depth`

Sets the fighter's position on the third axis, which this engine has and MUGEN does not.

Not used by any character in this archive.

**Parameters** (1): `player`

---

## `dialogue`

Runs a scripted exchange between fighters before a round.

Not used by any character in this archive.

**Parameters** (3): `text1`, `text2`, `text3`

---

## `dizzypointsadd`

Adds to the stun the fighter has taken.

Not used by any character in this archive.

**Parameters** (2): `absolute`, `value`

---

## `dizzypointsset`

Sets the stun the fighter has taken.

Not used by any character in this archive.

**Parameters** (1): `value`

---

## `dizzyset`

Puts the fighter into, or out of, the dizzy state directly.

Not used by any character in this archive.

**Parameters** (1): `value`

---

## `gethitvarset`

Writes one of the engine's get-hit variables directly.

Not used by any character in this archive.

**Parameters** (6): `down.recover`, `down.recovertime`, `fall.recover`, `hitshaketime`, `xvel`, `yvel`

---

## `groundleveloffset`

Shifts where the fighter considers the ground to be, for stages whose floor is not at zero.

Not used by any character in this archive.

**Parameters** (2): `redirectid`, `value`

---

## `guardbreakset`

Breaks, or restores, the fighter's guard directly.

Not used by any character in this archive.

**Parameters** (1): `value`

---

## `guardpointsadd`

Adds to the guard meter.

Not used by any character in this archive.

**Parameters** (2): `absolute`, `value`

---

## `guardpointsset`

Sets the guard meter.

Not used by any character in this archive.

**Parameters** (1): `value`

---

## `height`

Overrides the height the engine uses for the fighter, for one tick.

Not used by any character in this archive.

---

## `lifebaraction`

Drives a life-bar animation — the flash on a counter hit, a portrait reaction.

Not used by any character in this archive.

**Parameters** (4): `redirectid`, `spr`, `timemul`, `top`

---

## `loadfile`

Reads persistent data written by `SaveFile`.

Not used by any character in this archive.

---

## `mapadd`

Adds to a named variable.

Not used by any character in this archive.

**Parameters** (2): `map`, `value`

---

## `mapreset`

Clears named variables back to zero.

Not used by any character in this archive.

---

## `mapset`

Writes a *named* variable. Unlike `var(3)` a map entry is addressed by name, so a character can say what it means.

Not used by any character in this archive.

**Parameters** (3): `map`, `redirectid`, `value`

---

## `matchrestart`

Restarts the match.

Not used by any character in this archive.

---

## `modifybgctrl`

Edits a stage's own background controller.

Not used by any character in this archive.

**Parameters** (2): `id`, `value`

---

## `modifybgctrl3d`

The same for a glTF stage's 3D background.

Not used by any character in this archive.

---

## `modifybgm`

Changes the music already playing — volume, loop points.

Not used by any character in this archive.

---

## `modifyhitdef`

Edits the `HitDef` already in flight rather than declaring a new one.

Not used by any character in this archive.

---

## `modifyplayer`

Changes another fighter's life, power or name. An Oxyde and Ikemen extension, absent from MUGEN.

Not used by any character in this archive.

**Parameters** (3): `attack`, `hitpausetime`, `lifemax`

---

## `modifyprojectile`

Edits a projectile already in flight.

Not used by any character in this archive.

**Parameters** (3): `id`, `index`, `projdepthbound`

---

## `modifyreflection`

Changes the fighter's reflection on a reflective stage floor.

Not used by any character in this archive.

**Parameters** (2): `intensity`, `redirectid`

---

## `modifyreversaldef`

Edits the `ReversalDef` currently declared, the way `ModifyHitDef` edits a `HitDef`.

Not used by any character in this archive.

---

## `modifyshadow`

Changes the fighter's shadow — colour, intensity, offset.

Not used by any character in this archive.

**Parameters** (3): `color`, `intensity`, `redirectid`

---

## `modifysnd`

Changes a sound already playing.

Not used by any character in this archive.

**Parameters** (2): `channel`, `volumescale`

---

## `modifystagebg`

Changes a stage background layer at runtime.

Not used by any character in this archive.

**Parameters** (5): `actionno`, `alpha`, `delta.x`, `id`, `trans`

---

## `modifystagevar`

Changes a stage parameter at runtime — bounds, scaling, the floor.

Not used by any character in this archive.

**Parameters** (2): `camera.boundleft`, `camera.boundright`

---

## `modifytext`

Edits text already on screen.

Not used by any character in this archive.

---

## `overrideclsn`

Replaces the collision boxes for one tick with ones given here.

Not used by any character in this archive.

---

## `parentmapadd`

Adds to a named variable on the parent.

Not used by any character in this archive.

---

## `parentmapset`

Writes a named variable on the fighter that spawned this helper.

Not used by any character in this archive.

---

## `playbgm`

Starts a piece of music.

Not used by any character in this archive.

---

## `printtoconsole`

Prints to the engine console. A debugging aid, not something to ship.

Not used by any character in this archive.

**Parameters** (1): `text`

---

## `redlifeadd`

Adds to the recoverable portion of the life bar.

Not used by any character in this archive.

---

## `redlifeset`

Sets the recoverable portion of the life bar.

Not used by any character in this archive.

**Parameters** (1): `value`

---

## `remappal`

Swaps one palette for another at runtime.

Not used by any character in this archive.

**Parameters** (2): `dest`, `source`

---

## `remapsprite`

Substitutes one sprite for another at draw time, by group and number.

Not used by any character in this archive.

---

## `removetext`

Removes text this fighter drew.

Not used by any character in this archive.

---

## `rootmapadd`

Adds to a named variable on the root.

Not used by any character in this archive.

---

## `rootmapset`

Writes a named variable on the root.

Not used by any character in this archive.

---

## `rootvaradd`

Adds to a variable belonging to the root.

Not used by any character in this archive.

---

## `rootvarset`

Writes a variable belonging to the root — the real character at the top of a chain of helpers.

Not used by any character in this archive.

---

## `roundtimeadd`

Adds to the round clock.

Not used by any character in this archive.

---

## `roundtimeset`

Sets the round clock.

Not used by any character in this archive.

---

## `savefile`

Writes persistent data that survives the match.

Not used by any character in this archive.

---

## `scoreadd`

Adds to this fighter's score.

Not used by any character in this archive.

**Parameters** (2): `redirectid`, `value`

---

## `sendtostage`

Moves the fighter to a different stage mid-match. This engine's own; Ikemen GO has no equivalent.

Not used by any character in this archive.

---

## `shaderset`

Selects the shader the fighter is drawn with.

Not used by any character in this archive.

---

## `shiftinput`

Rewrites the fighter's input for one tick — swapping directions, or suppressing a button.

Not used by any character in this archive.

---

## `stagebreakfloor`

*Not yet described.* The parameters below are still authoritative — they are the ones the compiler accepts.

Not used by any character in this archive.

---

## `stagehazard`

Run by a stage's own FUSE state machine, not a fighter: damages every root fighter standing in a horizontal `zone`; `launch = 1` knocks them down, `2` staggers them (a shock). Oxyde's own; see docs/STAGE-LOGIC.md.

Not used by any character in this archive.

---

## `storyboard`

Plays a storyboard.

Not used by any character in this archive.

---

## `tagin`

Brings a tagged-out partner back in. See the tag section of EXTENSIONS.md.

Not used by any character in this archive.

**Parameters** (3): `leader`, `redirectid`, `stateno`

---

## `tagout`

Sends this fighter out and a partner in.

Not used by any character in this archive.

**Parameters** (1): `stateno`

---

## `targetadd`

Adds a fighter to this one's target list by id, so the target controllers reach it.

Not used by any character in this archive.

---

## `targetdizzypointsadd`

Adds stun to whoever this fighter has hit.

Not used by any character in this archive.

---

## `targetguardpointsadd`

Adds to the guard meter of whoever this fighter has hit.

Not used by any character in this archive.

---

## `targetredlifeadd`

Adds to the recoverable life of whoever this fighter has hit.

Not used by any character in this archive.

---

## `targetscoreadd`

Adds to the score of whoever this fighter has hit.

Not used by any character in this archive.

---

## `teammapadd`

Adds to a named variable shared by the team.

Not used by any character in this archive.

---

## `teammapset`

Writes a named variable shared by everyone on this fighter's side.

Not used by any character in this archive.

---

## `text`

Draws text on screen.

Not used by any character in this archive.

**Parameters** (7): `align`, `font`, `layerno`, `pos`, `removetime`, `scale`, `text`

---

## `transformclsn`

Scales or moves the collision boxes to match a transformed sprite.

Not used by any character in this archive.

**Parameters** (1): `scale`

---

## `transformsprite`

Scales, rotates or flips the drawn sprite without moving the fighter.

Not used by any character in this archive.

---

## `victoryquote`

Selects which victory quote this fighter says, by index.

Not used by any character in this archive.

---

## `zoom`

Zooms the camera in or out.

Not used by any character in this archive.

---

