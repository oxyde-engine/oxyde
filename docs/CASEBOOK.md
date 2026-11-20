# The casebook
What goes wrong when building a character, how to tell one cause from another that looks the same, and how to build so it does not happen.

Every fault here was found on a real character while building the engine. None of them is named: the character is the patient, not the lesson. What transfers is the fault. `seen` is how many characters in the development archive showed it — the second and fiftieth case are what turn a hunch into a differential.

## Symptom: stands still

4 causes share this symptom, and 2 of them are not faults at all. The evidence column is what separates them.

### A character walks and jumps before conversion and stands still afterwards, with every state and move still present

**Cause:** the conversion wrote the states but dropped the `[Velocity]` constants, so `velocity.walk.fwd` reads zero and the walk state runs with nothing to move it  
**Evidence:** the loader reports `velocity.walk.fwd` as absent, and the character's pre-conversion files have it  
**Confirm:** `oxtool fusediff <root> --constants` asks the loader for each key rather than comparing section names, so it cannot be fooled by a file that has the right shape and the wrong contents  
**Fix:** `oxtool fusediff <root> --constants --repair`, then re-fight the character to prove it moves  
**Seen:** 691 character(s) in the development archive

### A character enters the walk state with control and stays at zero velocity *(by design — not a fault)*

**Cause:** it asserts `nowalk`, which asks the engine not to move it on a held direction  
**Evidence:** the fighter enters the walk state and holds control there for as long as the direction is held, and the movement constants are all present and non-zero  
**Confirm:** the walk state is entered and control is held — a broken character never reaches the state, a declining one sits in it  
**Fix:** nothing: this is what the flag is for, and reporting it as a failure turns a design decision into a bug  
**Seen:** 4 character(s) in the development archive

### A character covers ground under a held direction but a check reports it cannot walk

**Cause:** the check compared state numbers, and the character walks in a state of its own rather than state 20  
**Evidence:** the fighter covers a hundred units of stage, in a state that is not 20  
**Confirm:** measure the distance travelled, not the state number: a state number is a convention a thousand authors were free not to follow  
**Fix:** fix the check. Distance is the evidence  
**Seen:** 2 character(s) in the development archive

### A character walks but never jumps or crouches, and its idle is not state 0 *(by design — not a fault)*

**Cause:** its own `[Statedef -1]` routes held directions into states of its own, so it never sits in state 0 where the common jump lives — it was written without a jump  
**Evidence:** holding a direction changes to a state in the 200s, and the fighter idles there rather than in state 0  
**Confirm:** look at what a held direction changes to in `[Statedef -1]`, and at which state it idles in  
**Fix:** nothing: it is not a standard fighter, the same way a character that flies is not one that fails to walk  
**Seen:** 1 character(s) in the development archive

## Symptom: missing from roster

2 causes share this symptom. The evidence column is what separates them.

### A character folder is on disk and looks complete, but the character never shows up in the game

**Cause:** two folders whose names differ only in capitalisation, so one shadows the other and the wrong one loads  
**Evidence:** the roster directory contains two entries whose names match case-insensitively  
**Confirm:** list the roster directory case-insensitively and look for collisions  
**Fix:** `oxtool unshadow`, which renames the shadowed folder after its display name  
**Seen:** 48 character(s) in the development archive

### A character fails to load, or loads with no moves, after a conversion

**Cause:** the conversion repointed the `.def`'s cmd/st/cns keys at `.fuse` files it did not write  
**Evidence:** a key in the `.def` names a file that is not on disk  
**Confirm:** `oxtool defrefs <root>` resolves every key in every `.def` and names the ones that go nowhere  
**Fix:** `oxtool defrefs <root> --repair`  
**Seen:** 40 character(s) in the development archive

## Symptom: wildly oversized

A fighter is drawn several times its proper size — a normal-sized opponent reaches only to its ankle. The sprites and animations are right; only the scale is wrong. Content validation names this at load.

### A character renders four times too big, with the right sprites and animations

**Cause:** the constants file the `.def` declares in `[Files] cns` did not load — it is missing, empty, or carries no `[Size]` — so `xscale`/`yscale` are never set and the character falls back to the engine's default scale  
**Evidence:** the character loads, draws and animates, but at default size; the declared `cns =` file is not on disk, or it is present but has no `[Size]` section  
**Confirm:** `oxtool validate <root> --char <def>` — a `def-missing-cns` finding means the declared constants file does not resolve; a `no-size-constants` finding means it loaded but declared no `[Size]`  
**Fix:** restore the declared constants file, or correct the `[Files] cns` path to point at the one that holds `[Size]`. A release that transpiles `.cns`→`.fuse` must ship the `.fuse` the `.def` names, or this is what the roster looks like  
**Seen:** the Arroyo reference fighter, in a release tree that transpiled its states but dropped the `.fuse` the `.def` pointed at

## Symptom: will not block

4 causes share this symptom, and 2 of them are not faults at all. The evidence column is what separates them.

### A character never blocks, or blocks standing but never low or in the air

**Cause:** it defines no state 120, and neither do its common states. 120 is the door the engine sends a fighter through to guard; 130, 131 and 132 are the rooms behind it  
**Evidence:** states 130 and 131 are defined and 120 is not, in the character and in its common states  
**Confirm:** check for state 120 before checking 130/131/132 — a character can drive its own 130 from `[Statedef -1]` and still never reach the door  
**Fix:** supply the common states, or give it a 120 that picks the stance  
**Seen:** 56 character(s) in the development archive

### A character blocks standing but never low, or never in the air *(by design — not a fault)*

**Cause:** it asserts `nocrouchguard` or `noairguard` — a design choice a great many fighting games make  
**Evidence:** state 120 is present, and the character guards reliably in one stance while never guarding in another  
**Confirm:** the flag is in its own files; the engine reports the assertion rather than inferring it  
**Fix:** nothing. Counting this as a failure turns 'we measured a preference' into 'a hundred characters are broken'  
**Seen:** 186 character(s) in the development archive

### A character never blocks low, or never blocks in the air, and also never crouches or never jumps

**Cause:** the posture the check measures is one it cannot reach. Air blocking needs a fighter in the air; low blocking needs one crouching  
**Evidence:** the fighter recorded zero ticks airborne, or never crouched, across the whole run  
**Confirm:** count the ticks it actually spent airborne or crouching — zero means the guard was never the question  
**Fix:** fix the prerequisite, if it is a fault. Reporting both is one limitation counted twice, and sends somebody to look at guard states that are fine  
**Seen:** 54 character(s) in the development archive

### A character is airborne for the whole round but never air-blocks *(by design — not a fault)*

**Cause:** it flies in a state of its own and never passes through state 120, so the guard is never offered  
**Evidence:** the fighter is airborne for hundreds of ticks, all of them in one state of its own below 5000  
**Confirm:** the state it spends its airborne time in. Below 5000 and not a jump state, it is flying; in the 5000 range it is being knocked around, which is the opposite  
**Fix:** nothing, if flight is the design  
**Seen:** 2 character(s) in the development archive

## Symptom: blocking feels wrong

### Blocking works but no block string holds: the defender can act immediately, and every move is hugely minus on block

**Cause:** the guard reaction changed state without clearing control, so guarding cost the defender nothing  
**Evidence:** every move in every character reads unmeasurable or hugely negative on block, including a light jab  
**Confirm:** measure frame advantage on block. If every move in every character reads unmeasurable or hugely negative, it is the engine and not the moves  
**Fix:** clear control when the guard reaction is entered, exactly as every get-hit branch does. The guard state hands it back itself when the hit time is over  
**Seen:** 2412 character(s) in the development archive

## Symptom: measurement not content

2 causes share this symptom. The evidence column is what separates them.

### A check reports a character cannot jump, walk or block, and playing it shows that it can

**Cause:** the check fed its inputs while the fighter was still in its entrance. A fighter can be out of its declared intro and still unable to act — some open the round in a custom get-hit state that never asserts `Intro` at all  
**Evidence:** the trace shows the first input arriving while the fighter was still in a state it entered at round start  
**Confirm:** trace what the probe itself saw, tick by tick, and look at the state the fighter was in when the first input arrived  
**Fix:** wait for idle and in control before the first input, capped so a character that never gets there is still measured rather than hung  
**Seen:** 3 character(s) in the development archive

### A character that never takes a step passes a distance check

**Cause:** the distance was measured from where the round put the fighter, and an entrance moves it  
**Evidence:** the distance was accumulated before any input was delivered  
**Confirm:** take the baseline at the moment the script starts, not at the start of the round  
**Fix:** fix the check  
**Seen:** 2 character(s) in the development archive

## Symptom: move will not come out

4 causes share this symptom. The evidence column is what separates them.

### Pressing a motion produces no animation and no movement, and the state it should reach is present

**Cause:** the command definition and the input disagree about a tick — a hold and the release that follows it share one, so a `/$D,a` style command needs `time = 1` and is unreachable without it  
**Evidence:** the trace shows the command's buffer expiring without the state ever being entered  
**Confirm:** drive the exact input headlessly and trace which state was entered, rather than reading the `.cmd`  
**Fix:** correct the command's `time`, or the engine's buffering if every character shows it  

### A move comes out but never seems to hit

**Cause:** reaching a state and landing a hit are different failures. The state may be entered correctly and the attack box, range or `HitDef` be the problem  
**Evidence:** the fighter reaches the attacking state, and the dummy loses no life at any range  
**Confirm:** report the two separately: did it reach the state, and did it take life off a dummy, at what range  
**Fix:** depends which half failed — that is why they are reported separately  

### A move list offers a combination that cannot actually be performed

**Cause:** the route through the states was proven, but the demonstration of it was never replayed. Proving a route and replaying it are different runs  
**Evidence:** the route through the states was found, and replaying it does not produce the moves  
**Confirm:** replay each offered combination and check it comes out  
**Fix:** gate on both, so an unprovable combination is withheld rather than shown  

### A move list offers a combination whose moves cannot actually combo

**Cause:** the route was accepted on the peak of the hit counter: a late move that hits several times reached the number of moves on its own, as a fresh combo  
**Evidence:** each move comes out and lands, but the opponent recovers between two of them and the hit counter falls back to zero before the last one connects  
**Confirm:** trace the opponent's hit counter tick by tick through the route; a real combo never lets it fall back to zero  
**Fix:** judge every route move by move: each lands before the next begins, and the counter never goes back down in between  
**Seen:** 1 character(s) in the development archive

## Symptom: fighter stuck

3 causes share this symptom, and the evidence column is what separates them — but first rule out the holds that are **not** a bug, because a healthy character can sit in one state for a reason.

### First: is the hold legitimate? (not a bug)

**Rule out before diagnosing:** a self-trap looks identical to several things a working character does on purpose. `oxtool unstick` already excludes the first two automatically; the rest are a judgement the evidence below cannot make for you.

- **The round ended.** A character that KO'd the opponent (or was KO'd) stops acting on purpose — a win pose is not a trap. The audit excludes this already (`frozen = still > 480 && !ko`), so a flagged fighter still has a live, healthy opponent.
- **It is `bonus = 1` content.** A bonus-game prop or a mode controller (the Knuckle-Up / Last-Stand `oxyde_*` entities) sits in one manager or idle state by design. `oxtool unstick` skips these by default and names the count; `--include-bonus` tests them anyway.
- **It is still in a long intro,** or waiting on an input a passive dummy never gives — a charge move, a command grab, a stance that only breaks when the opponent presses something, or AI-gated behaviour that needs the AI flag the audit does not set.
- **It is a tag or assist character run solo,** whose partner-side helpers drive the root (this is the *cause* below, not a false positive — but it means the fix is context, not the character being broken).

Only once none of these explains the hold is it one of the three faults below.

### A fighter freezes mid-round and stands still while the fight continues around it

**Cause:** a throw sent it to a `p2stateno` its own files do not define, so it is parked in a state with no controllers and nothing can end it  
**Evidence:** the frozen fighter's state number is one its own files do not define  
**Confirm:** check that the state number a throw names exists in whichever character the victim reads from  
**Fix:** refuse the redirection when the state does not exist, and rescue a victim left in somebody else's custom state  

### A fighter traps *itself* in a common movement or knockdown state and the round never ends, though the opponent is unharmed

**Cause:** it entered a state whose only exit is a predicate it never satisfies — the backward hop (common state 105) lands only on `Vel Y > 0 && Pos Y >= 0`, reached once gravity turns the hop around, but the fighter's own helpers keep re-setting its velocity so gravity never wins and it rises off the top of the screen forever; or a knockdown (5101) whose get-up is gated on a flag it never clears. Often a tag or assist character run as a solo fighter, its partner-side helpers driving the root  
**Evidence:** it ends the fight in **one** state it has held for hundreds of ticks with no way out, frequently having left the top of the camera, while the opponent keeps full control and full life — it is trapping *itself*, not being stranded by somebody else's throw  
**Confirm:** `oxtool unstick <root> <char>` fights it and names the single state it never leaves; the opponent's intact health and control are what separate this from the throw-stranding cause above  
**Fix:** `oxtool unstick <root> <char> --apply` fits a bounded `[State -1]` escape from exactly that state and keeps it only if a re-fight proves the hang is gone and the fighter is no worse — reversible with `oxtool revert`. In real play the round timer already ends such a round, so this rescues the fighter rather than fixing a crash  

### Fighters walk through walls, slide off screen, stay tilted, or stop being hittable

**Cause:** a controller that expires every tick was latched instead. `Width`, `PlayerPush`, `ScreenBound` and `AngleDraw` all last one tick, and so do get-hit variables  
**Evidence:** the effect is still in force many ticks after the controller last ran  
**Confirm:** check whether the value is reset at the top of each tick or carried  
**Fix:** expire it every tick  

## Symptom: hitboxes wrong

### Attacks pass through a character, or hit from too far away

**Cause:** the size constants were left at the defaults nobody updated when the sprites changed, so derived hurt boxes are the wrong size  
**Evidence:** the size constants match a template's defaults rather than the character's sprites  
**Confirm:** compare the size constants against the sprite dimensions  
**Fix:** update the constants — and try the repairs together as well as apart, because two wrong values can compensate for each other  

## Symptom: plays by itself

2 causes share this symptom, and 1 of them are not faults at all. The evidence column is what separates them.

### A character controlled by a person starts fighting on its own for the rest of the round

**Cause:** the character detects the computer with a hidden `keyctrl` watcher helper, and decided the computer was pressing because the watcher missed a press the character itself saw  
**Evidence:** the engine reports the slot as human, with `AILevel` at 0, while the character's own AI variable reads 1, and only a tap in the last ticks before the round sets it off  
**Confirm:** sweep one scripted tap across the round-start ticks with `oxtool simulate --inputs` and watch the AI variable  
**Fix:** in the engine, a watcher starts with its root's input history; in the character, detect the computer with `AILevel` where the engine has it  
**Seen:** 73 character(s) in the development archive

### A character starts fighting on its own as soon as the round begins *(by design — not a fault)*

**Cause:** nothing is wrong with the character: the slot is driven by the computer, because of a demo, a side set to the computer, or a mode that seats it, and the character's AI is doing its job  
**Evidence:** `AILevel` reads above 0 for that slot  
**Confirm:** read `AILevel` for the slot, and check which side the mode and the options give to the computer  
**Fix:** change who drives the slot, not the character  

## Symptom: which form is at fault

3 causes share this symptom, and 1 of them are not faults at all. The evidence column is what separates them.

### A converted character misbehaves in play

**Cause:** the fault survives the original files, so it is the engine or the character itself, not the conversion  
**Evidence:** the fault reproduces identically when the same character is played from its original files with `--original`  
**Confirm:** replay the same scripted input on both forms with `oxtool ab`; identical faults in both point away from the converter  
**Fix:** fix the engine if the original engine behaves otherwise, which WinMUGEN settles; otherwise it is the character's own behaviour  
**Seen:** 1501 character(s) in the development archive

### A converted character misbehaves in play

**Cause:** only the converted form has the fault, so the conversion or a repair applied after it caused it  
**Evidence:** the original files play correctly and the converted form does not, on the same input and seed  
**Confirm:** reconvert the original into a scratch root and score it again: if the fresh conversion also loses, it is the converter; if not, a repair since then  
**Fix:** fix the converter so every character with the same construction benefits; until then play that character from its original files  
**Seen:** 8 character(s) in the development archive

### A character misbehaves when played from its original files *(by design — not a fault)*

**Cause:** nothing is wrong with the converted form: the conversion or a repair already repaired a fault the author shipped  
**Evidence:** the original files show the fault and the converted form does not  
**Confirm:** look for the repair's backup file beside the character, which records what changed  
**Fix:** keep the converted form  
**Seen:** 5 character(s) in the development archive

---

# Building one that works

The other half. A catalogue of faults can tell somebody their work is broken and never tell them how to make a good one. Each rule names the recorded faults it prevents; a rule that prevents nothing we have seen go wrong is an opinion, and says so by having nothing to point at.

## States

### Make sure every reserved state the engine sends fighters to exists, either in your own files or in the common states you inherit

The engine does not invent a state that is missing. it changes to the number and, if nothing is there, the fighter arrives in a state with no controllers and nothing to leave it. there are 53 reserved numbers and each is a place the engine will send somebody.

**Check:** `oxtool info <root> <char.def>` reports how many states loaded, which includes the inherited ones  
**Prevents:** it defines no state 120, and neither do its common states. 1…, a throw sent it to a `p2stateno` its own files do not define…

## Guarding

### Define state 120 if you define any guard state at all

120 is the door: the engine sends a fighter there to begin guarding and 120 chooses 130, 131 or 132 from the stance. writing the rooms without the door gives a character that can be driven into a guard animation from its own `[statedef -1]` and can never actually block.

**Check:** guard low and in the air against a live opponent, not just standing  
**Prevents:** it defines no state 120, and neither do its common states. 1…

## Constants

### Give every movement constant a value, including the ones for directions you think the character will not use

A missing constant is not an error — it reads as zero. a walk state with `velocity.walk.fwd` absent runs perfectly and moves the fighter nowhere, which looks exactly like a broken state and is not one.

**Check:** `oxtool fusediff <root> --constants` asks the loader for each key individually  
**Prevents:** the conversion wrote the states but dropped the `[Velocity]`…

### Set the size constants to match the sprites you actually drew

Hurt boxes are derived from them when a frame has none of its own, so defaults left over from a template make attacks miss a large character or reach a small one.

**Check:** `oxtool inventory` shows the constants against the sprite dimensions  
**Prevents:** the size constants were left at the defaults nobody updated…

## Commands

### Keep `holdfwd`, `holdback`, `holdup` and `holddown` defined, under those names

The common states read them by name to decide which way a walk goes and which way a jump takes off. renaming them costs the character its directions even though every state is intact.

**Check:** walk and jump in all directions and watch the distance travelled  
**Prevents:** nothing recorded — this one is judgement, not evidence

### Give a command that releases a held direction a `time` of at least 1

A hold and the release that follows it occupy the same tick, so a command written as a hold then a button has no room to complete in the default window and can never fire.

**Check:** drive the exact input headlessly and trace which state was reached, rather than reading the `.cmd` and reasoning  
**Prevents:** the command definition and the input disagree about a tick —…

### Find out whether the computer drives your character with `ailevel`, and keep a hidden watcher helper only for an engine too old to have it

A watcher compares two input histories and decides the computer pressed whatever it did not see. any press it misses, such as one made just before it was born or still live in the command buffer, switches the ai on for a person for the rest of the round. `ailevel` is the engine's own answer, so there is nothing to miss.

**Check:** tap once in each of the ticks around the round start and confirm the AI variable stays at 0  
**Prevents:** the character detects the computer with a hidden `keyctrl` w…

## Attacks

### Make sure the frames you want to hit on carry an attack box **and** that a `hitdef` is live while they play

The engine needs both. a `clsn1` with no `hitdef` behind it cannot hit anybody, and a `hitdef` on a frame with no box cannot either — and neither mistake produces an error, only a move that whiffs.

**Check:** `oxtool frames <root> <char.def>` reports the active window; zero active ticks on a move that plays means one of the two is missing  
**Prevents:** reaching a state and landing a hit are different failures. T…

## Invariants

### Re-assert `width`, `playerpush`, `screenbound` and `angledraw` every tick you want them, rather than setting them once

They last exactly one tick by design, and so do get-hit variables. setting one and expecting it to hold is the same mistake as latching it, and it shows up as fighters through walls, off screen or stuck tilted.

**Check:** hold the fighter in the state for a while and watch whether the effect survives past the first tick  
**Prevents:** a controller that expires every tick was latched instead. `W…

## Throws

### Only send an opponent to a `p2stateno` that exists in whichever character they will read it from

The number is looked up in the victim's own file, where your 820 is somebody else's crouching kick or nothing at all. sending them to nothing parks them in a state no controller can end, for the rest of the round.

**Check:** throw a character that is not yours and watch what it does afterwards  
**Prevents:** a throw sent it to a `p2stateno` its own files do not define…

## Design

### Assert `nowalk`, `noairguard`, `nocrouchguard` or `nostandguard` when the character is meant not to do those things

The assertion is the difference between a design decision and a defect. a character that simply never blocks in the air is indistinguishable from a broken one; a character that says so is reported as having declined.

**Check:** `oxtool justify` separates declined from failed, and only the second needs fixing  
**Prevents:** it asserts `nowalk`, which asks the engine not to move it on…, it asserts `nocrouchguard` or `noairguard` — a design choice…

### Expect a character built on its own movement vocabulary to fail checks written for a standard fighter, and document what it does instead

A character that flies rather than walks, or that routes held directions into its own states, never passes through the states the common ones use. that is not a fault, but nothing can tell it apart from one without being told.

**Check:** look at which state it actually occupies while moving, rather than which state a standard fighter would  
**Prevents:** its own `[Statedef -1]` routes held directions into states o…, it flies in a state of its own and never passes through stat…

## Verification

### Verify a character by making it fight, not by reading its files

Every shape check this project has written has at some point passed a character that did not work and failed one that did. a state can be present, well-formed, reachable on paper and still never run.

**Check:** `oxtool audit <root> --only <name>` fights it and scores what happened  
**Prevents:** the check compared state numbers, and the character walks in…, the route through the states was proven, but the demonstrati…

### Wait until the fighter is idle and in control before feeding it inputs, and take any baseline from that moment

An entrance can run long past the point the round says it is over, and it moves the fighter while it plays. inputs spent during one measure nothing, and distance measured across one is not walking.

**Check:** trace the first tick an input was actually delivered and what state the fighter was in  
**Prevents:** the check fed its inputs while the fighter was still in its…, the distance was measured from where the round put the fight…

### Judge a generated demonstration and a player's attempt with the same code

A verifier and a judge that apply different rules disagree silently. here one accepted a combo the opponent had already recovered from, and the other refused every combo whose first move had start-up, so the trials offered could not be cleared.

**Check:** replay every offered route through the player's judge and require it to clear  
**Prevents:** the route was accepted on the peak of the hit counter: a lat…, the route through the states was proven, but the demonstrati…

### Make a test that two paths agree compare the whole value, not a list of fields somebody chose

A parity test that names its fields cannot notice a field nobody named. comparing five of a command's seven fields let the two command readers default the other two differently for an entire roster, and only playing both forms side by side found it.

**Check:** add a field to the type and confirm the parity test fails until both paths set it  
**Prevents:** only the converted form has the fault, so the conversion or…

### Re-measure the whole roster after changing a check, and compare against the previous run

A well-argued improvement to a measurement has, more than once here, measured worse. the argument is not the evidence; the two numbers are.

**Check:** keep the previous run's output and diff the per-character rows, not just the summary  
**Prevents:** nothing recorded — this one is judgement, not evidence

### When a scored family moves, look at what the answers chose, not only how many were right

A total cannot tell a model that reads the question from one that falls back on the commonest answer. a retrain whose only change was more prose lost twelve points on completing a hitdef, and the totals said nothing more; the choices showed it writing the commonest attr for most rows, including crouching attacks whose state header said type = c.

**Check:** tabulate predicted against expected per family and compare the two runs' tables, not their percentages  
**Prevents:** nothing recorded — this one is judgement, not evidence
