# Modes

Two dozen modes, one state machine. What differs between them lives in `Rules`
-- how many characters a side picks, how many stand on screen, **who drives each
of them**, whether a knocked-out fighter is replaced or the round resets, and
whether there is a ladder behind the current opponent. Expressing it as data
rather than as a code path per mode is what lets online play reuse three of them
without a second implementation, and what let Training, Sparring and Versus
Bonus each be added by changing the flow in one place.

The title menu groups them **by who you play**, so the first screen is a handful
of choices rather than the whole list: **Single Player**, **Versus**, **Online**,
**Training** and **Extras**, with **Options** and **Exit** beside them. Choosing
a group opens a submenu of its modes; **B** returns to the top. Online is the one
group that is an action in its own right -- it opens the netplay submenu it
always had. The grouping is a view over the mode list (`MENU_GROUPS` in
`crates/oxyde-app/src/mode.rs`); moving a mode between groups is a one-line edit
and the engine still draws, scrolls and themes the menu the same way.

Eleven of them are the modes the original engine's `system.def` names, under
its names, so muscle memory carries over. They are **not** in its order: the
original interleaved all four groups, so Team Arcade sat between Versus and
Team Versus and Survival Co-op sat between Survival and Training — sixteen
entries in no order at all. Here they are grouped by who is playing: on your
own, against another person, teams, and then the rest. Arcade still opens the
list and Options and Exit still close it, which is where the hands of anyone
who grew up on the original go first.

| Mode | Picks | On screen | Progression |
|---|---|---|---|
| **Arcade** | 1 | 1 v 1 | Eight CPU opponents, best of 3 each |
| **Survival** | 1 | 1 v 1 | Opponents until you lose |
| **Training** | 1 a side | 1 v 1 | **One player.** You choose your fighter *and* your opponent; life never runs out; a menu configures the other side |
| **Bonus Rush** | 1 | 1 v prop | **One player** through every bonus game, 60 seconds each, then Beat Up |
| **Story** | 1 | 1 v 1 | **One player.** A branching arc of scenes and fights; win or lose changes the path |
| **Versus** | 1 a side | 1 v 1 | One bout, human against human |
| **Sparring** | 1 a side | 1 v 1 | Two-player training; **Select** swaps both fighters |
| **Versus Bonus** | 1 each, both on side one | 2 v the prop | Both players at every bonus game at once, facing each other across the prop; the higher score (then least damage taken) takes it |
| **Online** | varies | varies | Versus, **Tournament**, Team Rumble, Team Tag, **Tag With a Partner** and the three other lobby formats, over the network |
| **Team Arcade** | 4 | 1 v 1 | Eight CPU opponents; your team fights in turns |
| **Team Versus** | 4 a side | 1 v 1 | Two chosen teams, in turns |
| **Team Co-op** | 2 | 2 v 1 | Two players *side by side* against the ladder |
| **Survival Co-op** | 2 | 2 v 1 | Two players, opponents until you both fall |
| **Team Rumble** | 8 a side (2-16) | 3 v 3 (2-4) | A team brawl: each fallen fighter is replaced from the bench where they fell |
| **Team Tag** | 2 | 2 v 1 | Both of yours on screen against an endless run |
| **Roster Rumble** | dealt | 1 v 1 | The roster dealt out between you, nobody twice, last one standing |
| **Knuckle Up** | 1 | 1 v 3 | A belt-scroll brawler: endless waves of the roster, three on screen |
| **Knuckle Up Co-op** | 2 | 2 v 3 | Knuckle Up for two, side by side on one team |
| **Watch** | none | 1 v 1 | The computer fights itself, winner stays on |
| **Replays** | -- | -- | Watch a match that was recorded earlier |
| **Records** | -- | -- | The longest winning streaks on this machine |
| **Options** | -- | -- | Settings, rules and keys |
| **Exit** | -- | -- | Leaves the game |

## Tournament

The fourth entry under **ONLINE**, and the one no other engine in this family
has: up to thirty-two people, a single-elimination bracket, and **everybody who
is not fighting watching the fight that is**.

It reuses two things the engine already had and would be very hard without
either. The bout itself is an ordinary online Versus match, so nothing about the
fight is special-cased. And watching is a *live replay*: the simulation is
deterministic, a match is a seed plus one number per player per frame, so a
spectator is a peer that receives both fighters' inputs and runs the same
simulation. The tape arrives as it is played, and the only change the replay path
needed was a flag meaning "there is more coming — wait rather than ending".

Everything goes through the host, which is also the authority on who won. The
bracket is derived on every machine from one shared seed rather than sent.
[NETPLAY.md](NETPLAY.md) has the protocol, the failure modes and the limits.

## Who drives whom

Every mode answers this question the same way: for each side, and each
position on screen, a `Drive` says whether a human slot, the computer, or a
mirror of another human slot supplies the input.

| | Side 1, first | Side 1, second | Side 2, first |
|---|---|---|---|
| Arcade, Survival | Player 1 | -- | Computer |
| Versus, Team Versus | Player 1 | -- | Player 2 |
| Team Co-op, Survival Co-op | Player 1 | **Player 2** | Computer |
| Team Tag | Player 1 | Mirror of player 1 | Computer |
| Watch | Computer | -- | Computer |
| Training | Player 1 | -- | The dummy, the CPU, or player 2 -- chosen in the practice menu |
| Sparring | Player 1 | -- | Player 2, or the dummy while idle |

This is not a detail. Feeding input slot 1 to match player 1 -- which is the
obvious thing to do, and what this engine used to do -- hands the second
player's controller to their own team mate in every mode that fields two, and
leaves the computer driving the wrong character.

## Arcade

One character against a ladder of eight. Each opponent is a best-of-three bout,
and you are healed between them. `select.def`'s `arcade.maxmatches` sets the
length if it has one; otherwise `ARCADE OPPONENTS` in the options screen does.

A won run plays the winner's own ending (`[Arcade] ending.storyboard`), or the
screenpack's default ending if they have none. With neither, the engine ends
the run on its own card: **THANK YOU FOR PLAYING**, the OXYDE wordmark, the version,
the winner's portrait and name, and how the run went — the mode, opponents
defeated and the time it took. It holds twelve seconds or until a button. A
bonus game slotted into the run is one round, and whatever ends that round —
breaking the prop, the clock — ends the game, so a prop nobody touched no
longer replays its sixty seconds as a drawn round. `oxtool shot . thankyou`
photographs the card.

**The scenery rotates as you climb.** Each rung of the ladder leads with its
*opponent's* paired stage rather than replaying one venue, so a run tours the
roster's stages (bonus-game stages are kept out of the rotation). Before each
bout the ladder plays a **VS card** — the two fighters' portraits and names on
the versus screen — as its handover between fights, exactly the screen Versus
shows. It is gated by the `VERSUS SCREEN` options toggle (see
[CONFIGURATION.md](CONFIGURATION.md)); turn it off and the ladder goes straight
from one fight to the next.

## Versus

One against one, **human against human**, as in MUGEN: both sides are chosen on
the select screen. Playing on your own, set `VERSUS PLAYER 2` to `COMPUTER` in
the options screen and side two is played by the CPU at the configured
difficulty.

Each player chooses their team **on the select screen, with the roster already
showing**: a card in each side's half of the panel between the portraits.
Left and right choose **SINGLE**, **SIMUL** (up to four on the stage at once),
**TURNS** (up to sixteen, the next stepping in as each falls) or **TAG** (up to
four, one on the stage and the rest in reserve, swapped on the button mid-fight);
up and down set how many, shown as a row of pips; A drops that side's cursor into
the roster. Both players answer at the same time. Once a side has chosen, its card
shrinks to a strip of slots that fill with each fighter picked ("2 OF 4").
Both open on SINGLE, so pressing straight through is the one-on-one Versus;
the card is what settles "I'll use one, you take four". B with nothing picked
goes back to the card; B on player one's card leaves.

A side with a reserve is fought the way Team Versus fights one — a round a
fighter, the survivor recovering a little — and when side two is the computer,
player one answers its card after their own. Choosing again after a match
opens on the teams you just fought with. Team Arcade, Team Versus and Team
Rumble ask the same way. Online Versus is one on one and does not ask.

### Tag

**TAG** is the KOF/Marvel team form: both sides field a team but only one
fighter a side stands at a time, the rest waiting in reserve, and you **swap the
active fighter on the tag button** (`b+z` by default) whenever you like — to
rotate a tired fighter out, to answer a matchup, or to escape pressure. A
knocked-out fighter is replaced by the next of its own accord, and a side is
beaten only when its *whole* team is down. The incoming fighter keeps its own
life and meter, and spends a few frames unable to act as it arrives (it can
still be hit), so a tag is a commitment rather than a free switch.

It is the engine's one **universal tag** turned into a team form: the mechanism
belongs to the engine, so every one of the 2,527 characters can be tagged
whether or not its author ever heard of tag play, and because the swap and the
standby are part of the rollback snapshot, a tag is as replayable and as
netcode-safe as a jump. See [Universal tag](TAG.md).

### Player initials and streaks

`SELECT` on the select screen enters three arcade initials for that player —
up and down change a letter, A moves on, B goes back. They are remembered per
controller, so they are entered once. The fight shows each player's initials
under their bar with the winning streak they bring into the match, the result
screen says when a streak grew, ended or set a record, and `RECORDS` on the
title menu lists the ten longest streaks with each player's wins, losses and
the fighter they take most. A streak counts matches won in a row; a ladder
counts every opponent beaten. Practice, bonus runs, Knuckle Up, replays and
online matches do not count. Stats live in `players.cfg` beside the config
file, never in a replay or the online handshake.

## Team Arcade / Team Versus

Pick four. They fight **in turns**: whoever is out there stays out there until
they fall, then the next steps in. A survivor keeps the damage they took and
recovers about a third of a bar between rounds, so a clean win is worth
something. Team Arcade sends them against the ladder; Team Versus against
another chosen team.

## Team Co-op / Survival Co-op

Two people, side by side, against one opponent at a time. Player two drives the
second fighter on *your* side rather than the one opposite. Co-op Survival runs
until both of you are down.

## Survival

One character, opponents forever. You recover a fifth of a bar between fights;
your score is how many you beat.

## Training

Practice, and a **one-player** mode. You choose your own fighter, and then you
choose who to practise against — both on the same controller, one column after
the other, because the person walking into Training is on their own and asking
them to find a second pad to pick a dummy makes no sense.

Nobody can be knocked out, and **Start** opens a menu over the match:

| Setting | What it does |
|---|---|
| `OTHER FIGHTER` | **Dummy**, CPU, or Human |
| `DUMMY` | Stand, Crouch, Jump, Approach, Retreat, **Record**, **Replay** |
| `GUARD` | Never, Always, Random, or After First Hit |
| `P1 LIFE` / `P2 LIFE` | Normal, Refill, Infinite |
| `P1 POWER` / `P2 POWER` | Normal, Refill, Infinite, Empty |
| `ROUND TIMER` | Off by default: practice has no clock |
| `COLLISION BOXES` | The same overlay `F2` toggles |
| `FRAME METER` | What the move just performed was made of, and who recovers first. On by default |
| `INPUT HISTORY` | The last twenty-four inputs for each side, repeats collapsed, scrolling up to the life bars. On by default |
| `FRAME STEP` | Holds the fight still — `F3` — and advances it one tick at a time — `F4` |
| `SAVE STATE` | Remembers this exact moment — `F5` |
| `LOAD STATE` | Puts the fight back to it — `F6` |
| `DAMAGE READOUT` | Holds the combo counter — hits, damage, life share — up long enough to read after the combo ends |
| `PARRYING` | Off, Tap or Hold, for this session — see [PARRY.md](PARRY.md) |
| `ABSORB` | After a parry, tap **down** instead of punishing and take their meter. Greyed out while parrying is off |
| `MOVE LIST` | Every move your fighter has, and the motion for each |
| `MOVE TRIALS` | Every move on its own, then the combos; clearing one starts the next, and **Select** demonstrates it |
| `RESET POSITIONS` | Both fighters back to their starting marks |
| `RANDOM FIGHTERS` | Both become someone else, without leaving the match |
| `CHANGE CHARACTERS` | Back to the select screen |

`REFILL` brings a bar back a moment after the last hit, so a combo can be
measured and the next attempt started without waiting. `AFTER FIRST HIT` is the
guard setting for checking whether a string is a true blockstring.

`OTHER FIGHTER` is who is on the other side. **Dummy** is the default and the
reason the mode exists: the character stands there and does what the `DUMMY`
and `GUARD` rows say. **CPU** hands it to the ordinary computer opponent at the
configured difficulty, for testing a combo route against something that fights
back. **Human** seats a second controller — the same thing Sparring does,
without going back to the title screen for it. Choosing either of the last two
greys out `DUMMY` and `GUARD`, because they no longer drive anything.

### Move list

A MUGEN character never states its move list anywhere. What it has is a `.cmd`
full of named motions and a `[Statedef -1]` full of `ChangeState` controllers
guarded by `command = "name"`; a move is the join of the two, and reading that
join out of the character is what `MOVE LIST` does. Nothing is authored per
character, which is the only way a list can exist for all 2,527 of them.

Each row is a move the character will actually be sent to, with the motion
written the way the key-config screen names the buttons — `D, DF, F, Z`, where
`X Y Z` are the punches and `A B C` the kicks — and the meter it costs where
the entry asks for one. Opening the page also starts **measuring** that
character's frame data against the fighter opposite, on another thread; the
rows fill in with `startup/active/recovery` and whether the move is safe on
block once it lands, a few seconds later.

```
SENBEI          DB, F, X      4/2/9  +1 SAFE
HATA      F, DF, D, DB, B, X  17/30/44
```

Only the moves that can be *performed* headlessly get numbers — a charge move
or one that needs meter never comes out, and 21 of Kuroko's 30 read as no
measurement rather than as a guess. Supers come first, then specials, then normals, then
dashes and taunts. A character that drives itself from its own states rather
than from commands says so instead of showing an empty list.

### A debugger, not just a dummy

Four of the rows are a debugger over a running fight, and the fight is what
makes them work: every one of them is the engine's own machinery turned
outwards rather than a new system.

**Frame step.** `F3` holds the fight still and `F4` advances exactly one tick,
however long the key is held. It is a *debugger's* pause, not `[Pause]` or a
super freeze: those are the simulation pausing itself and they are part of the
fight. This one stops the tick happening at all, so the round flow, the
practice rules and the frame meter stop with it instead of running on against a
simulation that is not moving. Never over an online match, a tournament bout, a
replay or an attract demo — each of those runs on somebody else's clock, and
holding ours would not stop theirs.

**Save and load state.** `F5` remembers the moment and `F6` returns to it, down
to the tick: both fighters, their helpers, their variables, every projectile and
explod, plus the round phase and what is left of the clock. It costs a `clone`
rather than a design, because rollback netplay already snapshots exactly this
every frame. `oxtool shot . fight --mode training --cpu --prove-state` checks
it the only way worth checking: the simulation's own checksum before saving,
after sixty more ticks, and after loading — the first and last have to match and
the middle one has to differ.

**Input history.** The last twenty-four inputs for each side, up the left
and right edges, newest at the bottom, **with repeats collapsed**: `F 12` is
forward held for twelve ticks, one row. A new input slides in at the bottom and
pushes the column up; the rows fade out as they reach the life bars rather than
stopping at a fixed count, and the whole column is drawn at two thirds of the
HUD's size so it reads as an instrument rather than a second HUD. That is what makes a quarter circle
readable at a glance instead of twelve identical lines, and "why did that not
come out" a question somebody can answer by looking. It records what each
*fighter* was told rather than what a keyboard sent, so a dummy's inputs, the
CPU's and a recorded playback's all read the same way.

**A recording dummy.** Set `DUMMY` to `RECORD` and the dummy stands there while
it writes down what you do, for up to ten seconds; set it to `REPLAY` and it
performs that back, mirrored, on a loop. Mirrored because the inputs were
pressed from the other side of the screen: what you did as forward is towards
you when the dummy does it. Re-selecting `RECORD` throws the last take away,
which is how you fix one that went wrong. The tape is the same two bytes a
frame that every replay in this engine is made of.

### The frame meter

MUGEN characters have never had frame data. Two thousand authors wrote two
thousand movesets and nobody could say whether a light punch was four frames or
eleven, or whether a special was safe on block — the original engine never
computed it and no tool since has either.

The meter measures the move that was **just performed, here**: at whatever
range, against whatever the opponent was actually doing, after whatever came
before it. It reads

```
STARTUP 6    ACTIVE 3    RECOVERY 22    ON BLOCK -8
```

with a strip under it of what each of the last ninety ticks was for both
fighters — amber for startup, red for the frames a move can hit, blue for
recovery, violet for stun, grey for being on the floor. A move nobody blocked
says so rather than reporting a zero; a knockdown says `KNOCKDOWN`, because the
exchange is over and the number would only be how long the opponent spends
getting up.

It is drawn by the engine rather than by the motif, for the same reason the
collision boxes are: it is a measuring instrument, and one that only appears
under the screenpack that happens to have an element for it is not one anybody
can rely on.

### Move trials

The same reading, turned into a tutorial, and laid out as a **course from
beginner to advanced**. **Every move on the move list comes first, on its own,
before any combo**: the normals as one block, then each command normal (a
normal pressed with forward or back), the movement (dashes, the taunt), then
the specials and supers easiest first — a family of strengths (`CHARGING STAR
L`, `M`, `H`) as one trial asking for each in turn. Then the two-move combos,
then the combos into a super and the three-move routes. Each trial says which
of the three tiers it belongs to.

A move is taught from wherever it comes out: standing in front of the
opponent, **up close** (a throw, with the direction its entry also asks for),
**charged** (`~30$B, F, x` with back actually held for thirty ticks — the card
draws the first input as a hold and the notation reads `CHARGE B, F, X`), **in
the air** (an air special, after a jump), or **after a hit** — a follow-up, or
a special whose author only wrote the cancel, taught as the normal that sets
it up and then the move.

**A move that needs a setup is taught with it.** Many `[Statedef -1]` entries
only fire out of another move, while a helper or a projectile is out, or once
the character has switched into a mode it keeps in a variable of its own. The
guard says which, and `oxyde_core::routes` reads it: a `StateNo`/`MoveContact`
test names the **parent** move to perform first (a throw's follow-up, through
the `P2StateNo` the throw puts the opponent in), a `NumHelper(id)`/`NumProjID`
test names the move that **sends** that helper or projectile, and a `var(n)`
test names whatever **writes** that variable — a move whose state sets it, or a
mode switch written as a `VarSet` in `[Statedef -1]` behind a command that is
not a move at all. The trial then lists the setup as `SETUP` rows on the card
before the move, labelled `FOLLOW-UP`, `WHILE IT IS OUT` or `IN THAT MODE`.
Every route is performed before it is offered, with the same driver and the
same judge as everything else here, and its Show Me must perform it too; a
candidate that does not bring the move out is never shown. A follow-up's
moment is found by performing it, not guessed: one run plays the move's
motion over and over through the parent and says when it came out, and only
that moment is then proven. A player who is already in the mode, or already
has the helper out, is not made to do the setup again — the move coming out is
the proof. The search has a budget in simulated ticks (as many as placing the
character's moves took, between 4,000 and 15,000), so the trials a character
gets never depend on how busy the machine was.

A move that comes out from none of them is left off, and `oxtool trials` says
why: it only exists against named opponents, it is the computer's, it needs a
helper out, it only comes out of another state (a guard, a throw), or it is
gated on the character's own mode — and `--why` lists every setup route that
was tried for it and what became of it.

Pick one and the match resumes with the trial on a card under the clock, in
the HUD's own smoked glass and ember: which trial of how many, its tier and how
much of the course is cleared, with a progress line; each move as a hexagon
that is ticked off in green when performed, the one being waited for lit in
ember; and the input beside it in the input display's arrows and button icons,
**turned to face the way the fighter is facing** — a fighter on the right
pushes left for forward, and the card shows a left arrow. A long block shows
five rows around the one being waited for. For a combo the card shows how many
of its moves have landed, and a note under it says why a combo dropped. A move
on the character's list that was not the one asked for is named back — `THAT
WAS TELEPORT FWD K` — so a player who did the kick teleport for the punch one
knows what to change. Clearing a trial opens a `TRIAL CLEAR` banner across the
screen; every trial starts with the fighters stood back on their own sides at
the trial's range.

**A move's name and its input are two columns in two languages.** The name is
text; the input is drawn with the same arrows and button icons as the input
display. A great many commands are named after their own input — `fwd_y`,
`QCF_x` — and printed as text next to the notation that read as the input
twice: `FWD Y  HOLD F, Y`. Such a name is replaced with one that says what the
move is, worked out from the command itself: `FORWARD MEDIUM PUNCH`,
`FORWARD LIGHT PUNCH SPECIAL`, `DASHING 2-KICK SPECIAL`. The move list page
uses the same names.

**Clearing one starts the next.** The list is a course to work through, not a
menu to keep coming back to: the "TRIAL CLEARED" banner has its moment and the
next trial sets itself up. Off the end it goes back for anything skipped or
failed earlier, and when nothing is outstanding it says so and stops.

**Every combo route is proven before it is offered.** A character owning a
light punch and owning a fireball does not mean one cancels into the other, and
a tutorial that asks for a route nobody checked is worse than no tutorial — the
player has no way to tell whether they are doing it wrong or whether it never
worked. So each candidate route is performed in a throwaway simulation against
the fighter actually standing opposite, at the range the demonstration uses, and
it becomes a trial only if it connects **as one combo**: every move lands, each
one lands before the next begins, and the opponent is never let out in between
— a hit counter that goes back down, to nothing as they recover or to one as a
fresh combo starts, is a dropped combo however many hits follow.

That last clause is not a detail. The rule used to be only that the counter
reached the number of moves in the route, and a super that teleports off the
screen and comes back with a three-hit kick passed behind any normal that
landed: the opponent had recovered long before the kick arrived, and three hits
is more than two. The same rule now judges the player's attempt, so a route
that is offered can be cleared and a route that is cleared would have been
offered.

Both kinds of link are tried: a **cancel**, where the next motion goes in while
the first move is still playing, and a **link**, where it waits for control to
come back. Most of this archive cannot cancel at all, so routes also open with a
**jump-in** — jump forward and hit on the way down, which leaves the opponent
reeling while the attacker lands and gets control back. Every range and moment
to press is tried, and the one kept is the deepest: the one that lands closest
to touching down. Three-move routes are built by adding one more move to the
end of a two-move route that was already proven.

Proving a character's combos takes between a tenth of a second and about three,
so it runs on another thread, started the moment a practice session begins. Walk
down the menu to `MOVE TRIALS` and it is almost always already there; if it is
not, the page says so. A pairing's set is kept for the rest of the session, so
swapping the opponent and back does not prove the first fighter's trials twice.

### Show me how

**Select** demonstrates the trial that is running. The fighters are stood at the
range the route was proven at and the engine performs it — the tracker's pointer
follows the move being performed rather than the player, and the line under it
reads `WATCHING - SELECT TO TRY IT`.

It is the same driver that proved the route, so what is demonstrated is what was
verified, down to the link timing. It reacts rather than replaying a fixed list
of frames: the next motion goes in when the previous move *lands*, which is what
a player does and what makes the demonstration work at a range nobody measured.

**A demonstration never clears the trial.** Watching the route performed for you
is not performing it, so the attempt is not judged for as long as it is running
and is reset when it ends — what the engine just did to the dummy is not sitting
in your progress waiting to be finished off by one more move.

What counts as done is judged on the simulation, not on the buttons. A move is
performed when the fighter enters **any** state the character's own
`[Statedef -1]` sends that command to — one command is often several moves
(`c` standing, crouching, jumping from a neutral or a forward jump, running),
and only the first entry's target used to count — short of a state that is
some other move's own. A target that hands off to another state on its first
tick still counts, through `PrevStateNo`. A fireball that was input but never
came out does not pass. A combo is cleared by the rule above, read off the
opponent's hit counter — the same counter the damage readout uses — with one
allowance: a move that sends something out (a projectile, a helper) may land
after the next move has begun, because a player who cancels a fireball into a
super before it arrives has done the combo faster than the demonstration, not
dropped it. A hit from the fighter's own boxes only ever lands the move it is
performing. Selecting a
trial sets `GUARD` to `NEVER`, because a blocking dummy makes a combo trial
unclearable for reasons the player cannot see, and gives `P1 POWER` back if it
was set to `EMPTY` and the route needs meter.

Cleared trials are marked with a `*` and written to `trials.cfg` beside
`oxyde.cfg`: one line per character, one digit per trial, written out as each
one is earned rather than on the way out of practice. Progress is filed by
position under `[Trials3]`; a file from before the course order changed keeps
its old `[Trials]` or `[Trials2]` section, which is no longer read, because its digits name
trials by a position they no longer have.

The settings are remembered in `oxyde.cfg` under `[Training]`, so the dummy is
still crouching the next time you sit down. A config written before
`OTHER FIGHTER` existed said `dummy = CPU`; that is read and folded into the
new row rather than showing a behaviour the menu no longer offers.

## Sparring

Training for two people. Neither fighter can be knocked out, the same menu applies, and both bars
behave the same by default rather than one being pinned full.

Sitting down to it alone works too: a second seat that has been untouched for
three seconds becomes the training dummy, and hands control straight back the
moment someone presses something. The menu's `DUMMY` and `GUARD` settings
therefore mean something whether one person is playing or two.

The reason it exists is the **Select** button. Press it and both fighters
become random characters, right where they stand -- no trip back through a
thousand-portrait grid. A roster this size is only worth having if trying the
next matchup costs a button; an hour of Sparring is an hour of matchups you
would never otherwise have picked.

Select is `Tab` for player one and `` ` `` for player two by default, and the
pad's Select/Back button. Rebind it in the options screen like any other key.

## Bonus Rush

One player, alone, through every bonus game `select.def` declares
(`bonus = 1`), in order, each on its own stage, then **Beat Up**: a round against
a random roster fighter the computer drives, in which you cannot be knocked
out. Every one is **60 seconds**, whatever the options say. Only player one
picks; the run decides what stands opposite, and the prop is never drawn as a
player two — no second life bar, no portrait, no VS card. The results table
lists each game with the time it took to break or the damage it took.

## Versus Bonus

The same games for two players **at once**: both pick a fighter **at the same
time** (each in their own column, like a Versus match), and both are on the
stage together — facing each other across the shared prop — each credited with
what their own hits (moves, helpers and projectiles) land on it. The higher
**score** takes the game: whoever dealt the prop the most damage, with a tie
broken by whoever took the least damage, and level on both a draw. Landing the
breaking blow no longer wins a game by itself. Each player's damage sits either
side of the clock, and a line under the band says who took it. Neither can be
knocked out. Most games taken wins the run. Local only.

The two players go at the props simultaneously, not taking turns: the idea of
versus bonus is for both players at once.

Bonus Rush is the one-player run;
`--mode versus-bonus` names the two-player version. A replay of a bonus
game with one player on side one, from either mode, is rebuilt as a Bonus Rush
bout; one with the pair stays Versus Bonus.

An installation that declares no bonus games gets the engine's procedural run
instead: two players competing over eight stages in a **random order**, each
scored, and the most stages taken wins the run — level on stages is a draw. The
two fighters can hit each other the whole way through, and neither can be
knocked out. See [BONUS.md](BONUS.md).

## Story

A **branching story arc**, Oxyde's own. You pick one hero; the opponents, stages
and scenes come from the arc rather than the select screen. It is a graph of
storyboards and fights where winning takes one path and losing another, so there
is no fixed ladder — the arc decides what follows each bout (another fight, a
scene, or an ending). It is walked at the flow level by `story::Walker`
(`crates/oxyde-app/src/story.rs`) rather than run inside the simulation. Arcs are
`.story` files (`install/stories/`); `oxtool story` checks and lists them.

## Watch

The computer plays both sides and picks both characters. Useful for seeing what
a character does before choosing it, and for leaving the game running on a
screen.

**King of the hill.** Whoever wins stays on, a fresh challenger is drawn
against them, and the HUD counts the champion's defences. It never ends by
itself: there is no "you" in a mode nobody is playing, so nothing that happens
in it is a defeat.

It used to be a ladder of eight with the first side standing in for the player,
which meant the whole mode stopped on **YOU LOSE** the first time that side
went down — about half of the first fights, the computer playing both ends.

**Start or B leaves**, and the HUD says so. A deliberate press rather than any
button at all: one stray key should not end ten minutes of watching.

## Team Rumble

**A team brawl: three of yours on the stage against three of theirs, out of a
team of eight a side.** Both teams are picked before the match. Each player
drives one fighter; the two beside them are the computer's, fighting the
nearest of the other team. When anyone falls, their knockout plays out, they
leave the stage taking everything they own with them — helpers, projectiles,
effects — and the next team mate off the bench walks in from that side's edge
of the picture about a second and a half later. Everybody else carries on. The
first team with nobody left standing and nobody on the bench loses. There are
no rounds: it is one fight from the first bell to the last knockout.

**Your fighter falls, you take the next one in.** Whoever was driving the
fallen fighter drives their replacement, so a player is never left watching
their partners finish the match. The fighter a person is driving keeps the
front bar on the HUD.

**The numbers are yours.** `TEAM RUMBLE ON SCREEN` on the options screen sets
how many a side fight at once — 2, 3 or 4 — and `TEAM RUMBLE TEAM` how many
each side brings, bench included, from 2 to 16 (`[Game] teamrumbleonscreen`
and `teamrumblesize`). The team menu then asks each side its own team size,
opening on that number; a team smaller than the on-screen count fields all of
itself. Two against two out of four is a short scrap; four against four out of
sixteen is an evening.

Nobody heals, nothing resets — not the camera, not the positions — and the
meter each fighter built stays with them. The only thing that resets is the
clock, because a single 99-second round shared by sixteen fighters would decide
nearly every rumble on time over; each fighter who steps in brings a fresh one.

**The HUD** shows every fighter on the stage — the front one in full, their
team mates in the theme's three- and four-a-side bars — and under each side's
bars a running `KO n   BENCH n`: how many of the other team this side has put
down, and how many of its own are still to walk in.

This is the difference from MUGEN's Turns mode, which Team Arcade and Team
Versus still are: there, one fighter a side is on the stage, a knockout **ends
the round**, the screen resets, the survivor is healed and a fresh ROUND is
announced over the top. Roster Rumble keeps Team Rumble's old one-at-a-time
shape: one fighter a side, the next stepping over the last without the round
stopping.

**Local only, as a brawl.** Online Team Rumble is still one fighter a side on
the stage, eight a side: the bench substitution is the app's, outside the
rollback snapshot, and the one-a-side shape is the one the netcode has been run
against.

Duplicates are allowed. Eight of the same character is a legitimate team.

## Team Tag

Two of yours on screen at once against a single opponent, replaced endlessly as
you knock them down. Both of your fighters must fall for the run to end.

Offline the two share one controller -- that is what "two on screen" means when
one person is playing. Online, Team Tag is two a side.

## Roster Rumble

**The roster itself, dealt out between the two of you, and nobody appears
twice.** The whole installed roster is shuffled once, then split into two
hands of the same size out of that one pool — which is what makes the
no-repeats guarantee free rather than a search — and the two hands fight it
out by attrition until one side has nobody left.

It asks exactly one question, on a card of its own, and asks it once rather
than once a side: **how much of the roster**. There is no roster to pick from,
so unlike the team modes it is not asked on the select screen; the card shows
the number, how much of everything installed that deals, and A deals. Both hands come out of the same
shuffle, so asking each player separately would be asking the same thing
twice. The dial stops at 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384,
512 and 1024, clamped to what the roster can actually deal two hands of; a
range with a step of one is unusable when the range runs to five hundred.

Sixteen a side is the default and is about forty minutes. Dealing *all* of
1,051 is 526 each and several hours without a save point — which is a thing
somebody may well want, and is the top of the dial rather than the only
setting on it.

There is no form to choose: a mode that is attrition by definition is always
`TURNS`.

## Knuckle Up

**A belt-scroll brawler — Final Fight and Streets of Rage, played with the
roster.** One player walks a scrolling stage and clears waves of the roster's
own characters as enemies. It is a *configuration* of the engine, not a special
case: everything below is behind the `belt` match rule, so with the mode off the
MUGEN plane is exactly as it was.

- **Depth movement.** Up and down walk into and out of the screen along the
  engine's own depth axis (`pos_z`), instead of jumping and crouching. A hit
  lands when the two fighters are roughly lined up in depth — get on their row,
  then hit them.
- **Waves and a camera gate.** Three enemies stand at once; the view will not
  scroll past a living wave, and releases once you clear it, when the next wave
  walks in.
- **Pickups.** Health and weapons sit on the floor to be walked over — health
  heals, a weapon arms you to hit harder until it runs out.
- **Campaigns.** A run is described by a campaign file
  (`knuckleup/campaigns/*.knuckle`; the legacy `data/campaigns/` is still read)
  listing its stages, waves, boss, pickups, music and stage logic — the enemy
  line-up comes from there, and clearing it wins the run. The mode's stages,
  props, weapons, music and settings live beside it in `knuckleup/`, which no
  other mode reads. `oxtool campaign <file>` checks one, `oxtool campaign
  --root <root>` all of them. See [KNUCKLE-UP.md](KNUCKLE-UP.md).
- **Co-op.** **Knuckle Up Co-op** is the same run for two: both players fight
  side by side on one team against the same waves — the same belt-scroll mode
  with a second hero seat (`Human(0)`, `Human(1)` on side one). It is the exact
  seating a future online co-op reuses over the wire, since the whole run is
  inside `step()` and therefore the same two `u16`s a frame. Player two can
  also join a solo Knuckle Up on the select screen with START: both players
  pick at once, each on their own cursor, and the run becomes Co-op. Each
  player has their own lives and score; the continues are shared, and a player
  who lets their CONTINUE? run out drops out while the other plays on. No
  versus screen, no round clock (unless the campaign sets a `time`), and a lost
  run reads YOU LOSE / GAME OVER.
- **Enemies that get hit.** Enemies decide once per attack whether to block it
  (`[KnuckleUp] enemyguard`) and a string of blocks breaks their guard
  (`guardbreak`), with a GUARD BREAK! cue.

## Online

`ONLINE` opens a submenu -- Versus, **Tournament**, Team Rumble, Team Tag,
**Tag With a Partner**, King of the Hill, Relay, Round Robin and Watch a Lobby
-- and then Host or Join. Every *person* on either side is a person: there is no
CPU ladder online, and online Team Tag is two a side rather than two against the
computer.

**Tag With a Partner** is the one online mode with a computer fighter in it, and
it is there on purpose: two a side where the team mate nobody is holding is the
engine's own opponent rather than a copy of the same stick. The seat lives in the
simulation, so it rolls back, it is in the checksum, and both machines derive the
same fighter from the same seed with nothing on the wire for it. The *level* is
the one number that has to be agreed: it comes from each machine's difficulty
setting and is folded into the setup hash, so two players who disagree are told
they cannot play rather than quietly playing two different fights. It is the
last setting on this channel that works that way — the four that decide the
rest of the fight are declared by the host and adopted by everybody else, see
[NETPLAY.md](NETPLAY.md) — and it should probably follow them.

The computer can also fill a **bye** in a tournament -- see
[NETPLAY.md](NETPLAY.md) -- which is a hole in the evening rather than a mode:
`ADD A COMPUTER` and `FILL THE BYES WITH COMPUTERS` in the lobby.

See [NETPLAY.md](NETPLAY.md) for the rollback details, and
[Tournament](#tournament) above for the bracket.

## Replays

Every match is recorded, because recording one costs nothing: the simulation
is deterministic, so a whole match is the seed it started from plus one number
per player per frame — a couple of kilobytes. `REPLAYS` lists what was kept,
newest first, and plays one back.

The decision worth making is therefore not whether to record but whether to
**keep**, which you can only judge once you have seen the fight. `[Replay]
record` takes `ask` (record everything, offer to save it afterwards — the
default), `auto` (record and save everything) or `off`. `keep` is how many are
held before the oldest is dropped, and `dir` is where they go.

A replay is also a test: playing one back re-runs the simulation and checks it
still reproduces, so a replay that has stopped matching is a regression report.
`oxyde --replay <file>` does the same thing from the command line.

**Saving.** The result screen offers *SELECT TO SAVE THE REPLAY*. During a
match, **Start** pauses on the move list page, whose first row is **SAVE
REPLAY** (A on it, or Select anywhere): it keeps the tape *so far*, which is
what a long run — a Knuckle Up campaign above all — needs when something goes
wrong halfway. And the most recent match is always kept as
`replays/last-run.oxr`, overwritten by the next, written when a match ends or
is quit; `last-run` is never counted against `keep` nor pruned.
`oxyde --headless ... --save-replay <file>` writes a scripted run's tape.

**Videos.** A replay can be turned into a video file. On the REPLAYS screen,
**C** is **EXPORT VIDEO** on the selected tape; on the result screen the line
under the menu reads *SELECT TO SAVE THE REPLAY - C TO SAVE VIDEO*, and C saves
the fight just seen. The export runs on a background thread with its own copy
of the game, so the menus — and a new match — carry on; a progress bar in the
bottom-right corner (on the result screen, the prompt line itself) counts it
through the tape and then says `VIDEO SAVED videos/<name>`. Videos go in
`videos/` beside `replays/` (`[Replay] videodir`), named exactly like the
replay with the video's extension, at `[Replay] videosize` (default 1280x720)
and `videoquality` (`high`, `medium`, `small`). `[Replay] videocodec = auto`
writes H.264 + AAC `.mp4` when an `ffmpeg` is found next to the game, in the
game root or on `PATH`, and AV1 + Opus `.webm` — built in, royalty-free — when
not; `av1`, `h264` and `gif` force one. A tape that no longer reproduces on this
build still exports, and the toast says so. From the command line, `oxtool
replay video` does the same with a time range, `--no-hud` and a size; see
[TOOLS.md](TOOLS.md#replay-video) for the codecs, the checks and measured
speeds.

**File names** say when, what and who, so the folder sorts and reads without
the game: `date_time_mode_players[_context].oxr`.

| Mode | Example |
|---|---|
| Versus and the other two-sided modes | `2026-10-10_1430_versus_kfm-vs-ryu.oxr` |
| Teams | `2026-10-10_1431_teamversus_kfm+ryu-vs-ken+guile.oxr` |
| A ladder (arcade, survival) | `2026-10-10_1432_arcade_kfm_vs-ryu.oxr` — the opponent it opened on |
| Knuckle Up | `2026-10-10_1426_knuckleup_mech-sagat_rust-city_stage2.oxr` — campaign and stage reached |

The date and time are local and in ISO order, so alphabetical is chronological.
The mode is its slug (what `--mode` takes). Only the player side's fighters are
named, `+`-joined; names are lower-case ASCII with any run of anything else —
spaces, `/\:*?"<>|`, accents — folded into one dash, cut to 24 characters, and
a name with no ASCII at all falls back to the character's folder. The whole
stem is capped at 80 characters, cutting the opponents first; two saves in the
same minute get `-2`, `-3`. Pruning reads each file's header for when it was
recorded, so files named under the old `<unix-time>-<everyone>.oxr` scheme are
kept and pruned alongside the new ones.

**Runs.** Format 4 tapes also carry the decisions the app takes outside the
step — each fighter's `AILevel` as it changes and a button that cut an
introduction short — because inputs alone cannot reproduce them, and a Knuckle
Up tape carries its campaign and house rules. See
[KNUCKLE-UP.md](KNUCKLE-UP.md#saving-and-sending-a-replay).

## Records

The ten longest winning streaks on this machine, from the initials players
entered on the select screen — see [Player initials and streaks](#player-initials-and-streaks).

## Options

Difficulty, rounds, time limit, life scale, game speed, who plays side two in
Versus, arcade ladder length, sound and music volume, the select grid, damage
balancing, the box overlay, and both players' key bindings. `SAVE AND RETURN`
writes them to `oxyde.cfg`; `RETURN WITHOUT SAVING` puts back what was there
when you opened the screen. See [CONFIGURATION.md](CONFIGURATION.md).

## Running a mode without a window

Every mode can be driven headlessly, which is how they are regression-tested.
Mode names are matched on letters and digits alone, so `team-co-op`,
`teamcoop` and `"TEAM CO-OP"` all work:

```bash
oxyde --root . --headless --mode team-rumble --frames 20000 --ai 6 \
      --p1 chars/ryu/ryu.def --p2 chars/kfm/kfm.def
```

`--bonus-stage <name>` opens a Bonus Rush or Versus Bonus run on the stage you name rather
than playing the others first: an installed bonus game by folder or name
(`car2`, `ff2breakcar`), `beat-up`, or — when none are installed — a procedural
stage: `break-the-car`, `barrel-drop`, `drum-stack`, `oxyde-junk-pile`,
`power-test`, `glass-wall`, `skeet`, `keep-it-up`.

A headless run puts the computer on **every** seat, including the ones a person
would hold, so `--mode training` exercises a fight rather than one character
standing still. Named characters are repeated to fill a team, so a Team Rumble
run does not need eight arguments. The report at the end gives the screen
reached, rounds won, how many of each team is still standing, how many
opponents were defeated, and -- in a bonus run -- the stage and the score:

```
team-rumble    screen Fight | rounds 0 - 0 | teams 5/8 vs 6/8 | defeated 0
team-tag       screen Fight | rounds 0 - 0 | teams 2/2 vs 1/1 | defeated 10
team-co-op     screen Fight | rounds 0 - 0 | teams 2/2 vs 1/1 | defeated 0
training       screen Fight | life 1000/1000 both sides after 9000 frames
versus-bonus   screen Result | defeated 8 | run 4 - 4 over eight stages
```
