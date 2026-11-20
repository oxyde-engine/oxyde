# oxtool

Offline diagnostics over a whole MUGEN archive. Everything runs across all
cores, so a scan of 1,051 characters takes seconds rather than minutes.

```
oxtool verify   <game-root> [--limit N] [--jobs N] [--show N] [--quiet]
oxtool doctor   <game-root> [--limit N] [--show N]
oxtool info     <game-root> <char.def>
oxtool dump     <game-root> <char.def|file.sff> <group> <image> <out.png> [--pal N]
oxtool frame    <game-root> <char.def> [--vs <char.def>] [--tick N] [--scale N] [--boxes] [--out FILE]
oxtool select   <game-root> [--cursor N] [--filter TEXT] [--scale N] [--out FILE]
oxtool simulate <game-root> <char.def> [--vs <char.def>] [--ticks N] [--seed N] [--corner]
oxtool soak     <game-root> [--limit N] [--ticks N] [--render]
oxtool sweep    <game-root> [--sample F | --full] [--threads N] [--out DIR] [--drive-moves] | --report | --repro KEY
oxtool sweep    --combine <pass-dir> <pass-dir> [--out DIR]
oxtool sweep    <game-root> --referee <findings.tsv> [--top N] [--kind K,K] [--runs N] [--workers N]
oxtool linger   <game-root> [--limit N] [--only NAME] [--vs <char.def>] [--shot OUT.png --move MOVE]
oxtool stagescale <game-root> [--only TEXT] [--all] [--tsv]
oxtool superfx-audit <game-root> [--aspect 4:3|16:9|both] [--sample N] [--jobs N] [--out DIR]
oxtool stress   <game-root> [--limit N] [--ticks N] [--vs <char.def>] [--seed N]
oxtool netcheck <game-root> <p1.def> <p2.def> [--frames N] [--latency N] [--loss N] [--delay N]
oxtool balance  <game-root> [--target-hits N] [--out FILE] [--show N]
oxtool splash   [--image FILE] [--width N] [--height N] [--progress F] [--out FILE]
oxtool fuse     <file.zss|file.cns|file.fuse> [--out FILE] [--verify]
oxtool fuse     <game-root> --roster [--out DIR] [--limit N] [--verify]
oxtool eval     build <game-root> --out DIR [--limit N] [--tasks N] [--seed N]
oxtool eval     baseline <DIR> --kind empty|copy|retrieve [--out FILE]
oxtool eval     score <DIR> <completions.jsonl> [--show N] [--csv FILE]
oxtool eval     rules

oxtool gate         <game-root> <char.def> [--min-accept N] [--min-warn N] [--quiet] [--tsv]
oxtool dedupe       <root> [--limit N] [--out FILE] [--compare <results.tsv>] [--strict]
oxtool troubleshoot <root> <char.def> [--symptom TEXT] [--tsv]
oxtool normalize    <root> <char.def> [--apply] [--tsv]
oxtool complete     <root> <char.def> [--apply] [--tsv]
oxtool fuseify      <installation-root> [--limit N] [--log FILE]
oxtool fuse-verify  <root> <before.tsv> <after.tsv> [--revert]
oxtool coverage     [<game-root>] [--limit N]
oxtool campaign     <file.knuckle> [--root R] # parse + validate a Knuckle Up campaign
oxtool campaign     --root R                  # ...every campaign installed under R
oxtool knuckle      migrate <root> [--dry-run] [--out DIR] [--move] # gather Knuckle Up content into knuckleup/
oxtool props        <root> [--only NAME]      # which bonus props can stand in a Knuckle Up street
oxtool replay       info|verify|export <file> # inspect a recorded match as a bug report
oxtool replay       video <file> [--root R] [--out P] [--size WxH] [--from T] [--to T] [--last S]
                    [--codec av1|h264|gif] [--quality high|medium|small] [--no-hud] [--quick]
                                              # play a tape into a video file (see `replay video`)
oxtool pack         <root> <char.def> [--out f.oxc] # bundle a character to one portable file
oxtool unpack       <file.oxc> [--into dir]       # read a bundle back, verify its content hash
oxtool ab           <root> <character> | --roster [--check base.tsv] [--apply-fallback] [--out P]
                                              # the FUSE form against the original files
```

A second binary, `oxyde-lsp`, is the language server for FUSE and ZSS; see
[the end of this document](#the-language-server).

## verify

Loads every character and stage, reporting what parsed and what did not.
Findings are grouped and classified so systemic problems stand out from
one-off typos.

```
$ oxtool verify . --quiet
characters
  loaded          2527
  playable        2527
  failed to load  0
  loaded with warnings 386

content
  sprites         1613917
  animations      522789
  sounds          125406
  states          417222
  state controllers 3155935
  commands        183317
  CNS trigger errors 2111
  CNS parameter notes 37412

stages
  parsed          204
  unreadable      0
  no art found    0

took 16.89s (147 characters/s, 95533 sprites/s indexed)
```

`--show 50` lists the first fifty characters with findings plus a frequency
table by kind. Exit status is non-zero only if a character failed to load at
all; damaged-but-loadable content is the normal state of a large archive.

## doctor

Classifies each character by playability and reports what the loader repaired.

```
$ oxtool doctor .
oxtool doctor
  characters 2527

--- playability ---
  perfect      2101   84.4%
  playable      384   15.4%
  repaired        4    0.2%
  unplayable      0    0.0%
  broken          0    0.0%

  2489 of 2527 characters are playable (100.0%)
  scanned in 16.23s

--- repaired at load (4) ---
chars/Empty_TX/Empty_TX.def
    supplied 50 missing common states from data/common1.cns
chars/SUV/SUV.def
    supplied 48 missing common states from data/common1.cns
chars/omega tom hanks/omega tom hanks.def
    supplied 32 missing common states from data/common1.cns
chars/tremor/TremorMO.def
    sprite file "tremor/tremor.sff" unusable; using Tremor.sff from the character folder
    animation file "tremor/tremor.air" unusable; using Tremor.air
```

| Class | Meaning |
|---|---|
| perfect | Loads and fights with no findings at all |
| playable | Fights, with cosmetic or inert problems |
| repaired | Made playable by a loader repair |
| unplayable | Loads but cannot fight (no sprites, animations or states) |
| broken | The `.def` could not be read |

## audit

    oxtool audit <game-root> [--limit N] [--ticks N] [--quick] [--only TEXT]
                 [--out FILE] [--cards]

`doctor` answers "does this character load", and in this archive the answer is
1,045 out of 1,045 — which is the first question and not the interesting one.
`audit` answers **how much of each character works**, by running a scripted
battery against Kung Fu Man and scoring what happened. Ninety seconds for the
whole roster.

```
$ oxtool audit . --out audit.csv
--- summary ---
  audited in     80.2s
  mean function  92.0%   (deep battery)
  mean operation 98.1%   (the six shared with the WinMUGEN sweep)
  loads             1045  100.0%
  draws             1043   99.8%
  acts              1044   99.9%
  deals damage      1013   96.9%
  takes damage       965   92.3%
  lands a hit       1032   98.8%
  can be hurt       1016   97.2%
  completes         1037   99.2%
  walks             1031   98.7%
  crouches          1011   96.7%
  jumps             1021   97.7%
  turns             1044   99.9%
  blocks            1018   97.4%
  falls             1030   98.6%
  gets up           1013   96.9%
  3+ attacks         998   95.5%
  FROZE                8    0.8%
```

Two numbers per character:

* **operation** — six checks (loads, draws, acts, deals damage, takes damage,
  completes) measured from one thirty-second computer-versus-computer fight and
  from nothing else. They are the six the original engine can also be scored on
  *from the outside*, off its own screen, which is what makes the two
  comparable. `metrics/` in the archive has both columns side by side.
* **function** — everything above plus the battery: walk forward and back,
  crouch, jump, turn to face an opponent who moved, block (holding Back **and**
  on each button, because Mortal Kombat conversions block on a button), be
  knocked down, get up, each of the six attack buttons, whether those connect,
  and every special move in the command list. This is the number to sort a
  roster by.

### Two columns that tell a choice from a fault

`air_state` / `air_state_ticks` record the state a fighter spent most of its
airborne time in during the air-block probe. Without them a flyer and a broken
guard look identical: `SonGoku SSJ4` spends all 585 of its airborne ticks in
its own state 1510 and never passes through 120, the guard door. It is not
failing to air-block; it is not jumping in the first place. `oxtool justify`
reads these two columns and says so.

### Watching the probe itself

```
$ OXYDE_AUDIT_TRACE=1 oxtool audit . --only "JUDA" --out /dev/null
    t150  state 0    Stand pos ( -99.10,  0.00) vel ( 0.00, 0.00) ctrl 1 input 0008 dx 0.0
    air-block probe: airborne 363 tick(s), guarding 98, both 0, opponent attacked 532
      airborne states: 50x180 5050x110 5030x32 5020x24 5000x17
```

Every tick the probe fed an input for, and what the fighter did with it. Reach
for this before concluding a character cannot do something — so far the probe
has been what was wrong every single time. It is what showed that
`JUDA-(NERICYA)` opens the round in a custom `movetype = H` state and was being
scripted while it was still being hit.

`--cards` prints one line per character carrying every flag above, which is
how two runs get compared. A mean that moves by half a point is three
characters; the summary cannot say which three and this can:

```
$ oxtool audit rootA --cards > a.txt
$ oxtool audit rootB --cards > b.txt
$ diff <(sort a.txt) <(sort b.txt)
```

That is the whole method behind the three-way common-states comparison in
`metrics/engine-comparison.md`: three roots that symlink the same `chars/` and
differ only in `data/common1.*`.

---

## validate

    oxtool validate <game-root> [--char <def>] [--limit N] [--only TEXT]
                    [--all] [--strict]

`audit` asks how much of a character *works*; `validate` asks whether a
character's files are **what they claim to be** — a read-only health report that
changes nothing. It is the pull side of the same validation the engine runs
quietly at load (see [VALIDATION.md](VALIDATION.md)):

* **Reference integrity** — every file a `.def` names in `[Files]` exists. A
  declared-but-missing constants file is the oversized-render bug; this is what
  catches it before it ships.
* **Content coherence** — each script file really is the language its extension
  claims. A `.cns` renamed `.fuse` without conversion (foreign), or two
  languages in one file (mixed), is named rather than mis-run.
* **Freshness** — no transpiled `.fuse` is older than its `.cns`/`.zss` source.

```
$ oxtool validate .
oxtool validate
  characters  1051

chars/Brian Battler/Brian.def
  WARN [content-mixed] BrianNA.cns: more than one state language in one file …

summary:
  1051 characters, 6 with findings
  by severity: 0 fatal, 7 warn, 0 note
  by kind:
       6  content-mixed
       1  def-missing-state
```

`--char chars/kfm/kfm.def` checks one character; `--only TEXT` narrows a sweep to
the paths that match; `--all` lists the clean characters too; `--strict` exits
non-zero if anything at all is found, for a build gate. It never converts or
repairs — the fix is always yours to make with `oxtool fuse`, on purpose.

---

## ask

    oxtool ask "<question>"

Search the documentation from the command line. It is a retrieval index over the
shipped docs, not a model: it returns the passages that answer a question, so a
setting, a controller or a tool can be found by describing what it does rather
than by already knowing its name. It only ever hands back text that is written
down, so it cannot invent an option that does not exist.

```
$ oxtool ask "how do I make the game run on a weak machine"
── docs/PERFORMANCE.md › Tuning for a weak machine
   frameskip = 1 … keep the simulation at 60 Hz, drop rendered frames …
```

---

## assist, instruct, scenarios — the assistant tier

Three commands sit above `ask` as the engine's answer-generating tier, each
backed by the same shipped docs and the deterministic tools, so an answer can be
checked rather than trusted:

- **`oxtool assist "<question>" [--route convert|diagnose|write|explain]`** —
  routes a question to the right engine tool and writes the answer; `--stdin`
  pipes a state block in for a diagnosis.
- **`oxtool instruct <game-root>`** — derives instruction/answer pairs from a
  roster, each one true by construction; `--verify` performs the moves it claims.
- **`oxtool scenarios build | audit | oracle | score | list`** — the
  assistant-tier benchmark: engine-and-roster questions whose answers the tools
  settle exactly, used to score the tier against the tools it must beat.

These three are developer and training tools; the retrieval `ask` above is the
one most users want.

---

## `oxtool mechanics` — proving a universal mechanic against the roster

    oxtool mechanics <game-root> [--limit N] [--only TEXT] [--chip F]
                     [--ticks N] [--seed N] [--rows]

Oxyde's universal opt-in mechanics are ruleset knobs that give every character
in the archive something its author never wrote: `chip_damage`, a fraction of
an attack's damage taken on block; `universal_recovery`, a knockdown tech for
characters that declare no `recovery` command; `burst`, a bar spent to leave a
combo (hold back + `c+y` in hit stun); and `push_block`, meter spent to shove an
attacker out of a blockstring (`a+b` while guarding). All are off by default.
chip and recovery make the promise **add what the character did not say, never
overrule what it did** — each has an authored counterpart it must leave alone.
burst and push-block have none (no character writes either input), so their
whole promise is the other half: fire when asked, and stay dead when off.

A knob that changes nothing is a knob that does not work, and a knob that
improves the game and breaks forty characters is not ready. Neither can be
settled by reading the code, because both depend entirely on what a thousand
authors happened to write. This runs each one over the whole roster and
answers two questions per mechanic: *does it fire*, and *does the roster still
work with it on*. For burst and push-block, which have no authored behaviour to
disturb, the second question is instead *does it stay inert when switched off* —
measured by driving each character into the situation the mechanic answers, with
the knob off, and confirming no meter is ever spent.

```
# over the archive's 2,527 characters
$ oxtool mechanics .
  characters   2527
  opponent     Kung Fu Man

--- chip_damage = 0.125 ---
  had a move blocked             1015   96.6%  of 1051   <- the rest cannot be asked
  chipped on at least one move    862   84.9%  <- the mechanic firing
  moves blocked                  7777
    of those, chipped            5049   64.9%
  blocked hits                  92595
    took nothing, now chip      67592   73.0%
    author wrote guard damage   25003   27.0%
      left exactly alone        24991  100.0%  <- the promise holding
      took more                    12    0.0%  (ambiguous: a co-landing hit chips on the same tick)
      took less                     0         <- must be 0; chip can only add
  chip per chipped hit              6.93  life

--- universal_recovery ---
  wrote their own `recovery`     1008   95.9%  of 1051
  knocked into a fall            1015   96.6%  <- the rest cannot be asked
  teched with it off              870   85.7%
  teched only with it on           35    3.4%  <- the mechanic firing
  of the   41 who wrote none:      35   85.4%  gained the tech  <- the population the rule is for
  authors who wrote it, asked     974  of whom 0 answered differently  <- must be 0

--- the roster with each one on ---
                                 off        chip    recovery
  mean function               90.49%      90.51%      90.49%
  froze                           10           9          10
  could not act                    1           1           1
  identical fight                  -         588        1051
  score moved                      -           6           0
```

Read across the bottom table: `chip_damage` is a real change to the game —
nearly half the roster's fights came out differently — and `universal_recovery`
changed **not one fight in 1,051**, because 96% of this archive already
declares its own `recovery` command in the `.cmd` file it inherited from Kung
Fu Man. The 41 that do not are almost entirely Mortal Kombat conversions,
which use a different template, and 35 of them gained the tech.

### Why the probes are scripted on both sides

The first version of the chip probe held guard against the computer for twelve
seconds and compared the life bars. It reported Kung Fu Man losing *less* life
with chip switched on, which is impossible. Chip changes the life bar, the AI
reads the life bar, and two runs that start identical stop being the same
fight within a second: the measurement was reading the divergence, not the
mechanic.

So the attacker performs one scripted move, the dummy holds guard, and nothing
in either run is deciding anything. Two further rigs were needed to keep the
two runs comparable, and both were found by a character disagreeing with the
probe:

* **The dummy is pinned.** Holding Back is how a dummy guards and also how it
  walks away; over a slow startup it backs out of range and the move is never
  blocked at all.
* **The dummy cannot die.** `Super Dizzy` has a move that stays blocked for
  175 hits. With chip on, the extra damage killed Kung Fu Man two seconds in,
  so the last 64 hits landed on a corpse and took nothing — and the probe read
  that as chip *reducing* 64 authored numbers. The knob may not decide how
  long the run is.

### Hit by hit, not move by move

`chip_damage` only applies where `HitDef damage`'s second field is zero, so
the promise is a per-`HitDef` statement and has to be checked per hit.
Summed over a whole move it is not checkable at all: `0Captcave_90` has a
flurry whose authored hit takes 1 and whose co-landing hit chips 2, which as a
move total reads as an authored 1 becoming 3.

Even per tick, two `HitDef`s that land on the same frame are one life-bar
reading from outside the engine, so the table has three rows rather than two.
`left exactly alone` is the promise holding, `took less` is the promise
broken — `guard_damage` can only ever add — and `took more` is the handful
that cannot be told apart. Twelve hits in 92,595.

### A fight that moved is not a character that broke

The roster half fights each character three times from one seed: both knobs
off, chip on, recovery on. `identical fight` counts the runs that came out
tick for tick the same, which is the only statement that needs no
interpretation — there, the mechanic provably did nothing.

Everything else is a fight that went differently, and one point of chip on the
first blocked jab makes the rest of the round a different round. So the columns
to read are `froze` and `could not act`, and for the six characters whose score
moved, `--seed`:

```
$ oxtool mechanics . --only "itachi,sonson" --seed 7
  score moved                      -           0           0
```

Both dropped 7.3 points at the default seed and neither moves at all on four
others. The whole roster run again at `--seed 7` moves one character, upwards,
and froze and could-not-act come out at exactly the counts they have with both
knobs off. That is divergence, and `--seed` is how it gets told from damage.

`--rows` prints one line per character carrying every count above, for the
same diff-two-runs method `audit --cards` exists for.

---

## `oxtool frames` — frame data nobody in this family has ever had

    oxtool frames <game-root> <char.def> [--vs <char.def>] [--limit N] [--tsv]
                  [--live] [--roster]

Startup, active, recovery and frame advantage for every move in a character's
move list — **derived by performing each move**, in the same headless driver
the audit uses. Nothing is parsed out of the CNS and nothing is estimated.

```
$ oxtool frames . chars/kfm/kfm.def
Kung Fu Man  — frame data, derived

MOVE                       INPUT            STARTUP   ACTIVE RECOVERY  TOTAL  ON HIT ON BLOCK
TRIPLEKFPALM               D, DF, F, D, DF…       8        3       22     33     +74       -9
UPPER X                    F, D, DF, X            3      2+4       22     31      KD       -8
A                          A                      4        3        8     15      +1       +1
B                          B                      7        8       10     25      -2       -2
X                          X                      4        3        5     12      +2       +2
```

A tick is **active** when the fighter has a live `HitDef` *and* the current
animation frame carries an attack box. Both halves matter: a `Clsn1` with no
`HitDef` behind it cannot hit anybody. `2+4` means two separate hitting
windows, so a multi-hit move reads as its hits.

**Advantage** is the defender's actionable tick minus the attacker's, measured
against a dummy standing at point-blank. Positive means the attacker recovers
first. A dash means it never connected — an advantage nobody measured is not a
zero.

**A move starts where the move starts, not where the motion does.** Counting
from the first input put the quarter-circle inside the startup: `QCF X` read 11
for a move that is 8 frames after the button, and every special move in the
archive was inflated by the length of its own command. The origin is the first
tick the fighter is attacking with no control — the state taking over, which
for a single-button move is the button's own tick. Normals are not affected
and do not move.

### `--live`: the two measurements, checked against each other

There are now two pieces of code that will answer "what is this move's frame
data": this tool, which derives it from a scripted run, and the **in-game frame
meter**, which measures whatever just happened in a real match. They share what
a frame *is* — one `observe`, one `Observed`, in `oxyde-app/src/framemeter.rs`
— but not how they count.

`--live` feeds both from the same ticks and prints them side by side:

```
$ oxtool frames . chars/kfm/kfm.def --live
Kung Fu Man  — derived against the in-game meter

MOVE                          STARTUP d/live     ACTIVE d/live   RECOVERY d/live
QCF X                                  8 / 8             3 / 3           22 / 22
A                                      4 / 4             3 / 3             8 / 8

18 move(s): the meter and the derivation agree on every one
```

It exits non-zero when they differ, because a difference of one would be
invisible in play and wrong in every table. Both faults above were found by its
first run: the meter was missing the one-tick calibration and the derivation
was counting the motion.

### The oracle

The numbers are only worth having if they are right, so the tool is pinned
against a synthetic character whose animation *states its own frame data*:
elements of 5, 3 and 7 ticks must read back as 5 startup, 3 active, 7 recovery
and 15 total, across seven different shapes. It earned itself on the first run,
catching the input script's lead-in leaking into startup.

It also caught a one-tick calibration that matters: a probe reads state after
`Match::step`, by which point the animation has advanced — but `resolve_hits`
ran earlier in that same step. So the boxes read after tick *N* are the ones
the engine hits with on *N+1*. That was measured against the engine rather than
argued: the dummy loses control exactly one tick after the boxes read live.

### What it found

Deriving this exposed a bug nothing else could see: **guarding never cleared
`ctrl`**, so a fighter that blocked could act on the very next tick. No block
string held anywhere and pressure did not exist for any of the 2,412
characters. Before the fix every move's on-block column was a dash; after it,
Kung Fu Man's jab is +2 and his specials are −7 to −10.

---

## `oxtool justify` — why the rest fall short

    oxtool justify <installation-root> <audit.csv> [--tsv]

"2,296 of 2,412 work" is a statistic. It does not say whether the other 116 are
broken, deliberately limited, or merely badly measured — and this project has
spent a lot of time discovering how often the third one is the answer. So every
shortfall gets a reason drawn from the character's own files or from the
engine's own report, ranked most specific first:

```
$ oxtool justify . audit.csv
230 character(s) fall short of something, 459 shortfall(s)

   125  blocks in air: by design: the character asserts `noairguard`
    55  blocks low: by design: the character asserts `nocrouchguard`
    47  jumps back: it overrides state 40 with its own, which is what runs
    ...
     1  blocks in air: it flies in its own state 1510 (585 airborne ticks
        there), so it never passes through state 120

  3 shortfall(s) with no reason found
```

The kinds of reason, and what each is guarding against:

| Reason | Means |
|---|---|
| **declined** | The character asserts `nowalk`, `noairguard`, `nocrouchguard`, `nostandguard` or `noautoturn`. It asked; it did not fail. |
| **missing constant** | `velocity.jump.fwd` and the like is absent, so the value reads zero. |
| **missing state** | The state the engine would send it to does not exist, in its files or its common states. State **120 is the guard door** and is checked before 130/131/132 — a character can drive its own 130 from `[Statedef -1]` and still never reach the door. |
| **own state** | It overrides that state, and its version is what runs. |
| **own air state** | It *flies*. Read from the audit's `air_state` column, not guessed: the 5000 range is excluded, because being knocked around in the air is the opposite of flying and excusing a guard failure with it would hide the fault. |
| **prerequisite** | The posture the check measures is one it cannot reach — air blocking needs a fighter in the air, low blocking needs one crouching. One limitation, not two. |
| **unexplained** | Nothing found. Deliberately **not** counted as justified. |

That last row is the point of the tool. "Unexplained" is an honest answer and
"probably fine" is not, so the count is reported on its own line and chasing it
down is the work.

Four of the rows are the same question asked two ways, and the gap between each
pair is the interesting part. **deals damage** and **takes damage** are read off
the free computer-versus-computer fight — whatever the two AIs happened to do to
each other in thirty seconds, which is not proof either way: a character that
dominated the fight was never hit, and one that lost badly never had to be
good. **lands a hit** and **can be hurt** are the same two questions put
deliberately. `lands a hit` presses each of the six buttons and then runs every
special in the command list against a dummy, and holds if *any* of them
connected. `can be hurt` stands the character on a quarter of their life in
front of an opponent who is attacking, which is the knockdown probe, and asks
whether their life moved. A character that can be hurt but did not *take* damage
in the free fight is a range or an AI finding, not a broken character — and the
score counts the pair as one check, satisfied by either.

**3+ attacks** counts characters with at least three of the six buttons
producing an attack. It is the line below which a fighter is thin rather than
broken, and it is the row to read next to a low **function** score.

`--only kfm,ryu` narrows a whole-roster finding to the handful it named, and
`--out` writes a per-character CSV with every individual check plus the state a
frozen fighter was stuck in and for how long — which is the address to take to
`oxtool simulate --ai 8 --trace`.

A low score is usually not a bug. Most of the bottom of the table is characters
that are simply thin.

## soak

Simulates every character in a mirror match and, with `--render`, draws a frame
too. This is the regression test that no synthetic fixture can replace: a
crash, hang or unwind anywhere in the archive shows up here.

```
$ oxtool soak . --ticks 600 --render
simulated       2527 mirror matches
distinct states 28027
sprites drawn   18315
took 41.53s (599 character-seconds of gameplay per wall second)

--- state controllers reached but not implemented ---
      1218  helper (HelperMax reached)
```

That last table is the roadmap: it ranks remaining gaps by how often real
content actually reaches them.

## kusoak

The brawler sibling of `soak`. Where `soak` runs a 1v1 mirror match, `kusoak`
fields every character through the **real Knuckle Up paths** — once as a wave
enemy and once as a scaled boss — and checks the three things only a brawler
exercises: the wave clears when the enemy is defeated, a scaled boss ends the
round when KO'd, and the time-over verdict is decided correctly against an
unequal life bar. It separates engine faults from character faults with a 1v1
baseline per character (a detector kind the character already trips on its own
is not blamed on the engine), so the output is signal rather than every broken
character in the archive.

```
oxtool kusoak <game-root> [--limit N] [--shard I/N] [--out FILE]
              [--hero PATH] [--only TEXT] [--repro '<key>'] [--compare A.tsv B.tsv]
```

Each run is seeded and byte-deterministic, so a flagged row's `--repro` key is a
reproducible bug report, and `--shard I/N` fans the roster across machines.
`--compare` diffs a CNS sweep against a FUSE sweep to catch a character that
behaves differently once converted. It is cheap enough to run the whole roster
in well under a minute, which makes it a regression tripwire: it would catch a
reintroduced wave-stall or verdict inversion structurally.

## sweep

`oxtool sweep` fights every character against a **panel of ~30 different
characters**, in all four form pairings (CC, FF, CF, FC: subject form first; C
is the original `.def.cns-backup`, F the files as they are), in five modes, on
stages drawn from the root's own list, and watches every tick with read-only
detectors.

```
oxtool sweep <root> --panel-only                 # pick the panel, write panel.tsv + features.tsv
oxtool sweep <root> --plan --sample 0.27         # how many matches, per mode
oxtool sweep <root> --sample 0.27 --threads 10   # the pass (resumable: rerun to continue)
oxtool sweep <root> --report [--doc FILE]        # rebuild report.md from matches.tsv
oxtool sweep <root> --repro 'KEY' [--trace]      # re-fight one match, tick by tick
oxtool sweep <root> --sample 0.27 --drive-moves  # ...then drive every command state the fights missed
oxtool sweep --combine DIR DIR [--out DIR]       # both roots' passes in one report
oxtool sweep <root> --referee findings.tsv --top 10   # ask WinMUGEN about a sample of findings
tools/sweep2-overnight.sh [--estimate]           # the whole second pass, both roots, unattended
```

**Why.** Every other gate fights a character against a copy of itself:
`regress`, `soak` and `ab` are all mirror matches, one on one. The three engine
faults Knuckle Up found (a thrower hit mid-throw keeping its
victim bound, a helper hit into the root's common states, a held fighter's own
`ChangeState` looked up in the thrower's file) each needed a *second, different*
character doing something to the first. This is the gate for that class.

**The panel** is a greedy set cover over features read from each character's
*compiled* states in both forms — a throw into the attacker's own states
(`p2stateno`), `TargetBind`, `TargetState`, `ChangeAnim2`, hittable helpers and
hittable helpers bound to their root, `BindToParent`, `SelfState`,
`ReversalDef`, `HitOverride`, freezes longer than 100 ticks, `EnvColor`, odd
sizes and gravity, no `stcommon`, mugenversion 1.x, and a dozen more — until
each feature has two carriers, then filled for diversity (a feature carried by
k members is worth 1/(1+k)²) with no character taken twice under another
folder name. Only characters both of whose forms load, walk, guard, land a
normal and behaved identically in `metrics/ab-baseline.tsv` are eligible.

**The modes**, each fielded the way the app fields it: **versus** (1v1),
**simul** (2v2), **belt** (one hero against a wave of three, with Knuckle Up's
belt rules and stages), **turns** (continuous, like Team Rumble: the fallen are
retired and the next jumps in mid-round, `field_fighter` + `enter_by_jump`;
even seeds bring the subject in second) and **tag** (universal tag, a partner
in standby; the computer never presses the tag button, so the harness takes the
seat for two ticks every four seconds and presses the tag combination, `b+z`
by default). Versus takes every
panel member, the team modes groups of three, so versus is the largest share.
Every root is the simulation's own computer seat at level 8, the entrance runs
until `fight_should_begin`, the stage goes through the app's own
`apply_stage_camera`, and a `zoffsetlink` stage is stepped every tick.

**The detectors** never steer (the one write is draining `Match::log`, which
nothing in the simulation reads; `the_observer_does_not_change_the_fight`
compares the checksum every tick with and without them): the engine's rescue
log lines (`missing state`, `abandoned in`, `nothing has changed`, `knocked
flat`, `released from a throw`, `lost outside the world`, `state loop`), with a
held fighter's *own* state looked up in the holder's file split out as
`held-own-state-lookup`; `Match::orphans()`; held in another's custom state
over 240 ticks (120 in the first pass); a state the file being read does not define; a helper hit into
the common states and still standing about in them after 120 ticks (the clone
fault); an afterimage alive over 600 ticks; non-finite or absurd root physics;
stuck (same state and animation, no control, not being hit, 300 ticks); the
Helper/Explod/Projectile limits; life out of range; a knocked-out fighter
still airborne after 300 ticks; a round that does not end; an entity whose
state code panicked (`faulted`); and for stages, a fighter off the picture for
three seconds, standing 40 units off the floor with engine physics, and a
camera that stays put while a fighter is beside the view. Panics escaping the
engine are caught per match with the backtrace; a match that hangs is caught by
a watchdog that exits so the next run records it.

**Outputs** go to `metrics/sweep/` beside the game root: `matches.tsv` (one row
per match: key, mode, forms, seed, stage, subject, panel, ticks, outcome, life,
every detector hit with its first tick, and the subject's states reached),
`report.md`, `findings.tsv` (every signature, ranked by distinct characters),
`coverage.tsv`, `stages.tsv`, `subjects.tsv`, `panel.tsv`, `features.tsv`, `meta.txt`. The
key is the repro: `oxtool sweep <root> --repro 'KEY'` re-fights exactly that
match and prints every root's state, custom-state owner, state time, position,
life and control around each detection (`--helpers` adds every live
helper, with its get-hit `yaccel`, hit pause and physics). `--recheck
findings.tsv --kind K --top N` re-fights the example of each of the top N
findings of one detector with the current build: when a detector learns to say
more — the abandoned rescue now says whether the state it ended had a way out
of its own, and how far into it the victim was — the findings already on file
can say it without another pass. The per-stage table is ranked by stage hits
per 100 matches, because the belt's eleven stages are drawn four times as
often as any versus stage; every stage is in `stages.tsv`.

A full pass over a large roster runs to over a million matches — roughly
1,351,000, about eighteen hours on ten threads; a pass is a stratified sample
(`--sample F`): for every subject and mode the same fraction of pairings, chosen
by hash, each kept in all four form pairings so the CC-vs-FF comparison exists
for every one. `--plan` prints the match counts and a wall-time estimate (at
roughly 473 ms a match, `--ms-per-match` to change it).

### The second pass (sweep2)

Five things the first pass's triage asked for:

- **Bonus props are not subjects.** Every roster entry `Assets` marks as a prop
  — `bonus = 1` in `select.def`, and Knuckle Up's private props — is left out
  as a subject and as a sparring partner, and listed in `skipped.tsv`.
  FF2BreakCar and oildrumbonus multiplied their own velocity to infinity when
  fought as fighters. `--keep-props` fights them anyway.
- **`custom-state-long` at 240 ticks** (`--custom-ticks N`). At 120 it was the
  noisiest detector, mostly authored holds. The hit's count is now the longest
  hold in ticks, so `--report --custom-ticks 360` re-cuts a finished pass at a
  higher bar without fighting again (a first-pass folder, which did not record
  hold lengths, says so and is left alone).
- **Drive-moves** (`--drive-moves` after the fights, `--drive-only` alone): for
  each subject form, every command state (the derived move list) the fights
  never reached is performed the way `oxtool moves --try` performs a move —
  the command played back a tick at a time, from the ground and after a jump,
  held one and two ticks, from 60 and 170 units — against one panel member
  (chosen by hash, standing still) on a stage from the root's list, with power
  pinned full and the same detectors watching for 600 ticks after the state is
  reached. The entrance is run once per subject form and the moment the round
  is called is kept (`Match` is `Clone`), so every attempt starts from the same
  snapshot and a driven state reproduces from its key alone
  (`--repro 'drive|CC|<state>|<stage>|<subject>|<opponent>'`). Rows go to
  `drive.tsv`, in `matches.tsv`'s columns with mode `drive`, the state number
  in the seed column and `reached`/`unreached` as the winner; the report gains
  a *Driven moves* section (coverage before and after, findings seen only
  while driving) and ranks drive findings with the rest. Resumable like the
  fights (`drive-inflight.log`). A state none of those attempts reaches is
  then tried through its **setup routes** — the candidates
  `oxyde_app::trials::route_candidates` reads off its guards with
  `oxyde_core::routes`, the same module the trials use: the command with its
  charge held, a parent move first, the move that sends the helper it needs,
  or the mode switch, each performed by the trials' reactive driver from both
  distances (at most six routes a state). The phase's summary line says how
  many states were reached only that way.
- **Either root.** A root with no `.def.cns-backup` anywhere — the base archive
  — is detected as *CNS-only* (`--cns-root` forces it): every character there
  is the CNS its author wrote, so it is fought CC only, a `C` in a key loads the
  `.def` as it is, and the panel is fielded in CNS too. `--panel-from FILE`
  reuses another pass's panel so the two roots meet the same sparring
  partners. `--combine DIR DIR` reads both passes (fights and drives) and
  writes `report.md`, `findings.tsv` and `passes.tsv`: signatures ranked by
  distinct characters across both roots (a character is its path under the
  root, so the same character seen from both roots counts once), matches per
  root, and a repro naming the root it re-fights in. The Knuckle Up belt
  stages are found in `knuckleup/stages/` as well as `stages/`.
- **A WinMUGEN referee** (`--referee findings.tsv --top N`). Findings of the
  classes where Oxyde and MUGEN might disagree — holds (custom states, binds,
  throws, abandoned and stuck fighters), clones (helpers hit into the common
  states) and knockouts/win poses — are re-fought 1v1, because WinMUGEN can
  only play 1v1: a Versus CC match of the pass that showed the signature, else
  the two fighters the example match names, both from the characters WinMUGEN
  loads (`metrics/raw_winmugen.jsonl`, `metrics/winmugen-originals.jsonl`).
  Up to eight times `--top` candidates are first re-fought in Oxyde, Versus CC
  on KFM's stage (`stages/kfm.def`; `stage0` is `hires = 1`, which WinMUGEN
  draws doubled) for `--seeds K` seeds (4), and the *decidable* ones are
  referred first: Oxyde shows the signature in at least half its seeds and, for
  a hold, the hold lasted until the engine's 300-tick rescue in a state with no
  exit of its own. (A hold whose state has its own exit lasts in MUGEN, which
  has no rescue, as long as its author wrote; a few seconds of quiet life bars
  is ordinary play, so nothing in the pixels can rule on it.) `Winmugen.exe`
  plays each pairing `--runs N` times (2; findings sharing a pairing share its
  runs), plus a kfm-vs-kfm baseline and a control per character (it against
  KFM, so a character whose idle is one still frame does not read as a clone),
  through a Python helper carried in the binary
  (`crates/oxyde-tool/assets/winmugen_referee.py`, written beside the results;
  `python3 -I winmugen_referee.py --selftest` checks its measurements on
  synthetic frames). The helper builds a private root of symlinks with a
  private `data/` (mugen.cfg: 320x240 windowed, normal blit, no stretch,
  `DoubleRes = 0` — the archive's 4 draws a zoomed quarter with no life bars —
  the stock motif, sound off, a 60-count clock) and a private `stages/` holding
  `referee.def` — KFM's stage with the camera held still, because a camera that
  follows the fighters scrolls the parallax layers and no pixel stays put long
  enough to look for a sprite left standing — a private wine prefix
  (`--prefix-template DIR` to copy one) and a private `Xvfb` per worker
  (`--workers N`), so nothing is written into the archive; they are removed
  when the run ends (results and shots stay). Symptoms come from
  the pixels only: the longest time neither life bar moved (*stall*), the
  longest time the playfield did not change (*frozen*), the time from a
  knockout (a bar that empties and stays empty) to the process exiting
  (*ko-hang*), and the largest region that changed and then stayed
  pixel-identical for eight seconds and differs from what that spot shows the
  rest of the run (*persist*: background a fighter walked off does not count).
  Each finding is classed **MUGEN does it too** (a run showed the class's
  symptom beyond the baseline and both controls), **Oxyde only** (no run showed
  it, every run loaded and fought, and the finding is decidable — "not seen in
  N MUGEN runs", not a proof that MUGEN never does it), or **inconclusive**
  with the reason. `referee.md` and `referee.tsv` link a contact sheet per run
  (and a frame with the persisting region boxed); `--kind K,K` refers only
  those detectors; the Oxyde side uses the pass's own `custom-state-long`
  threshold (its `meta.txt`, 120 for the first pass, `--custom-ticks` to say);
  `--dry-run` writes `jobs.json` without playing.

**Overnight.** `tools/sweep2-overnight.sh` runs the lot on both roots: the FUSE
root into `metrics/sweep2/`, the base root into `metrics/sweep2-base/` (both
with `--drive-moves` and the first pass's panel), `--combine` into
`metrics/sweep2-combined/`, then the referee on each root's findings. Each step
reruns until it exits cleanly (the watchdog's exit is resumed), writes a
`.done` marker under `metrics/sweep2-logs/`, and is skipped on a rerun; it is
`nohup`-safe and reads `SAMPLE`, `THREADS`, `REFEREE_TOP`, `REFEREE_WORKERS`,
`PREFIX_TEMPLATE` and `OUT` from the environment. `--estimate` prints the plan
for the chosen sample and for the full pass.

## linger

Answers *what does a move leave on the screen once it is over?* Every entry in
each character's move list is performed against a standing KFM (`--vs` picks
another), the match is left until both fighters have been idle for 90 ticks,
and three things are counted:

- **tint left**: a palette effect on either fighter with no timer left to end
  it that still changes a colour — the opponent who "turns white until they get
  hit again";
- **trail left**: an afterimage held by a helper that no longer exists, which
  nothing records into and nothing expires — a still copy of the fighter left
  standing on the stage;
- **borrowed anim**: ticks the opponent spent playing the attacker's action
  (`ChangeAnim2`). Not a fault in itself; it is the set of moves the
  victim-keeps-their-own-sprites rule applies to.

None of the three is simulation state a trigger reads, so the sim regression
cannot see them. `--shot OUT.png --only NAME --move MOVE` draws one move twice
side by side: during it, and once settled.

```
$ oxtool linger <game-root>
tint left       5 characters
trail left      0 characters
borrowed anim   1501 characters
```

The tint and trail counts flag a `PalFX` or `HitDef` palette timer that came
out at zero and was kept as an effect with no end, or a destroyed helper's
trail that is still drawn. The five left here are `time = -1` effects their
authors chose.


## `oxtool stagescale`: which stages change a fighter's size

A fighter's size belongs to the fighter, never to the stage. Two things in
Oxyde can still change it: the STAGE FIT zoom (`stagezoom = 1`), which moves in
on a stage whose art is narrower than the window, and a stage's own camera
(`[Camera] startzoom`, or `zoomin` with `autozoom = 1`). This reports both for
every stage, at 4:3, 720p, 1080p and 21:9, with the share of the window the art
leaves to the gutter fill at the ordinary scale. It exits 1 when a stage asks
for a zoom of its own, since that one applies whatever the setting.

It also says where each stage's **floor** sits — the screen row the fighters
stand on, after the stage's own background controllers have run for two
seconds, so a `zoffsetlink` dummy that starts ten thousand rows down and is
moved into place on tick 1 is read where it settles. A floor above row 20 or
below row 260 puts the fighters out of the picture; those stages are listed as
`FLOOR OFF SCREEN` and the exit status is 1. With the old reading of
`zoffsetlink` it listed exactly the two stages that showed no fighters
(`MK-OutWorldVortex`, `BlackDahliaCruiser_sin`); now it lists none. `--tsv`
adds the `floor_min` and `floor_max` columns.

The numbers are the renderer's own: the art is measured as the game measures it
on loading the stage, and the zoom is `Viewport::fit_stage` over
`Viewport::fit`. They were checked against pixels. KFM measured 150 px wide on
187 stages at 1280x720 and 180-200 on exactly the ten this lists at x1.23-x1.33.

```
$ oxtool stagescale <game-root>
201 stages measured
  a fighter is the same size on every stage with STAGE FIT = NORMAL SIZE (the default),
  except where the stage's own camera asks for a zoom: 0
  1280x720: with STAGE FIT = ZOOM 10 stages draw fighters bigger (up to x1.33); ...
  2560x1080: with STAGE FIT = ZOOM 30 stages draw fighters bigger (up to x1.36); ...
```

## `oxtool superfx-audit`: how much of the screen a character's super art covers

Fights every character on the roster against Kung Fu Man with a full meter, so
the computer throws its supers, once on a 4:3 playfield in a 640x480 window
and once on a 16:9 playfield at 854x480, and on every frame of player one's
supers measures what the character drew for itself. The measurement is the
one the super effect's AUTO mode acts on (`Scene::probe_art`): the caller's
explods, helpers, projectiles and trails rasterised on a coarse grid over
black and over white, so an opaque plate counts in full and an additive glow
by how bright it is, plus an `EnvColor` or strong `BGPalFX` held through the
pause as whole-screen art. At 16:9 every frame is measured twice, with FIT
SUPER ART TO SCREEN on and off.

Each run is the real game — `oxyde --headless --superfx-log`, one child
process per character and screen, so a character that crashes or hangs costs
its own row — and it stops after `--supers` supers (two by default) or
`--frames` frames. `--sample N` takes N characters evenly spaced through the
roster; `--only TEXT` filters by path or name.

It writes `superfx-audit.tsv` (one row per character: supers seen, peak
coverage at 4:3, at 16:9 fitted and at 16:9 as authored, side gaps found at
each, whether an `EnvColor` was involved, the lowest strength AUTO chose, and
the explod, helper or state responsible with the file that state is written
in) and `summary.txt` to `--out`, `<root>/metrics/superfx-audit` by default.
A **side gap** is a run of columns at least 55% of the screen wide that the
art covers top to bottom, with nothing but bare columns from its ends to the
screen's edge on at least 3% of the width — the signature of a plate drawn for
320 units on a 427-unit screen — seen on at least two frames. The findings for
the whole roster are in [SUPER-EFFECTS.md](SUPER-EFFECTS.md).

## stress

Answers one question: *does hitting everything at once break anything?*

Each character is run twice over the same seed, the same opponent and the same
number of ticks, differing in exactly one thing — what player one's pad is
doing. The **control** run presses nothing. The **mash** run holds impossible
chords (every attack button at once, both directions at once) and presses
hardest on the ticks where the character has **no control**: hit stun, the
knockdown chain, the get-up, and the air. Anything that goes wrong in the mash
run and not in the control run was caused by the input.

Impossible chords are the point rather than a shortcut. A real pad cannot send
Left and Right together and a real hand cannot send six attack buttons on one
frame, but a keyboard can send the first and two people on one keyboard can
send the second — and more to the point, the engine must not care. Every one of
them is a legal `InputState`.

```
$ oxtool stress . --ticks 1200
mashing 1045 characters for 1200 ticks each, against Kung Fu Man
  control run presses nothing; mash run holds every button at once

--- summary ---
  tested          1045
  took            12.0s
  broken by input 47   4.50%
  ...and unhittable while stuck 1

--- broken by mashing and not otherwise ---
  Bojack       stuck 1110 in state 330  (control 0) end 330  untouchable 0
  Jhun         stuck 1087 in state 1055 (control 0) end 1055 untouchable 0
  ...
  Blue Mary    stuck 420  in state 255  (control 0) end 200  untouchable 0
  Tenszin      stuck 420  in state 735  (control 0) end 201  untouchable 0
```

Read the state numbers before reading the count. Nearly every row this turns up
is a **power-charge state** — `Tien`'s 735, `Blue Mary`'s 255, `Kei`'s 750 —
whose only exit the author wrote is *"the player let go of the button"*.
Holding everything means never letting go, so the character does exactly what
it was told to. `stuck 420` is the engine's own deadlock rescue firing at seven
seconds and pulling them out of it.

Rows worth chasing are the ones where `untouchable` is also high: frozen *and*
unhittable is the shape a real engine bug takes, because nobody can hit the
fighter out of it.

## moves

    oxtool moves <game-root> <char.def> [--try] [--vs <char.def>] [--power N]
                 [--range N]

Prints the move list the engine reads out of a character: every `[Command]`
that a `[Statedef -1]` entry actually acts on, the state it leads to, the
motion written the way the key-config screen names the buttons, and any meter
the entry asks for. This is the same reading the training move list, the move
trials and the computer opponent all use, so it is also how to check what any
of the three will see.

`--try` is the useful half. The list says what the author *wrote*; performing
each motion headlessly says what a player gets, and the two differ often
enough that the list alone cannot answer "why does this character not do its
moves". Each move is attempted across a small grid of realistic timings, with
the meter pinned full unless `--power` says otherwise, against a standing
dummy at a spread of starting distances — close enough to touch, a walk apart,
and most of a screen.

Reaching a state and landing a hit are different failures with different
causes, so both are reported. "There is a special where he runs towards the
opponent and it never gets the opponent" is a report about the second one, and
a tool that only says `ok` cannot be pointed at it.

    $ oxtool moves . chars/mech_sagat/mech_sagat.def --try --range 170
      SUPER     RAGING TIGER      X, X, F, A, Z    -> 6200  [3000 power]  ok, connects (0 dmg at 46u)
      SUPER     TIGER RAID        D, DB, B, A+B    -> 4500  [1000 power]  ok, WHIFFS (closest 170u)
      SPECIAL   TIGER CLAW L      D, DB, B, A      -> 2400                ok, connects (75 dmg at 110u)
      ...
    performed 46 of 71 moves
      2 of them put an attack on the screen and touched nothing at any
      of the distances tried - the ones worth looking at first.

`--range N` pins one starting distance instead of trying the spread, which is
how to ask "does this only work point-blank". A throw counts as connecting: a
command grab takes its damage from the state it puts the victim in, so nothing
has been subtracted on the tick it lands.

Neither result is proof of a fault on its own. A move that is not reached is
often gated on the character's own mode, meter or AI variables; a move that
whiffs at 170 units may simply be a close-range move. What the command *is*
good for is the move that whiffs at *every* distance, comparing one character
against a known-good one, and comparing the same character across two builds.

## gate

Decides whether one character belongs on a roster, by fighting it.

A score is the wrong instrument on its own: measured across 300 characters, 29
have no special that ever comes out and **27 of them still score 60 or
better**, because walking, jumping, blocking and turning carry the average.
So `gate` separates *broken* from *incomplete* and refuses only the first.

**Refused** — froze, a value went to NaN, left the playfield, never took
damage, never dealt damage, or not one attack connected. **Warned** — no
specials, specials that never connect, cannot block, too few states.

```
$ oxtool gate . "chars/Ryu/Ryu.def"
Ryu  by Warusaki3
  function score  96%   (roster mean 92%)
    loads yes  draws yes  acts yes  deals damage yes  takes damage yes
ACCEPT  Ryu — 96%
```

Exit status is `0` accept, `1` warn, `2` refuse, so it drops straight into a
shell loop. `--tsv` prints one line per character for batch sweeps, carrying
the raw outcomes as well as the verdict:

```
$ oxtool gate . "chars/Ryu/Ryu.def" --tsv
chars/Ryu/Ryu.def  Ryu  Warusaki3  ACCEPT  96  0  0  9  9  6  22  14  1  1  1  0  0  0
```

Fields after the verdict: score, refusals, warnings, specials connecting,
specials reached, attack buttons landing, distinct states, specials declared,
then `takes deals blocks frozen nan offscreen`, then the reasons. `why` is
always last, so a reader that takes the final field keeps working as columns
are added.

> **Each collection is its own root.** A character is scored against
> `chars/kfm/kfm.def` *in the root it is given*. Point the sweep at a folder
> that merely contains installations and every character refuses at 0% — the
> same character scored `REFUSE 0%` one way and `ACCEPT 88%` the other.

## dedupe

Finds the same character twice across a tree, and says which copy to keep.

Identity uses three signals in decreasing strength: an identical sprite file
(size plus a hash of the first and last 64 KB), the same normalised name *and*
author, and a near-identical name — never the last on its own, because `Ryu`
and `Evil Ryu` are different characters. Normalising strips release debris
(`v2`, `final`, `(2008)`) but **keeps digits**: `Android 16`, `17`, `18` and
`20` differ in the number alone.

Three tiers are reported separately, because they mean different things:

| tier | meaning |
|---|---|
| byte-identical sprites | certainly redundant |
| same character, same author | redundant; keep the best |
| same character, **rival authors** | a *choice*, not redundancy |

Nineteen authors' Ryus are nineteen takes on Ryu, not eighteen mistakes.
Collapsing those needs `--strict`.

`--compare <results.tsv>` reads a `gate --tsv` sweep and ranks the copies by
**fighting them**: verdict first — a working character beats a broken one at
any score — then fewer warnings, then specials that connect, then attacks that
land, then score. It writes `dedupe-plan.tsv` and **moves nothing**.

## troubleshoot

Turns a symptom into the line that causes it.

`gate` answers *should this go on a roster*; an author already knows the move
does not come out and wants to know **why**. Every cause here is read out of
the character's own files — a missing `Clsn2`, an unconditional `NotHitBy`, a
`[Statedef -1]` with nothing to launch a move — and a symptom whose cause none
of the checks can establish is reported as exactly that.

```
$ oxtool troubleshoot . "chars/x/x.def" --symptom "it never took damage"
  symptom   it cannot be hit
  cause     animation 0 — the one it stands in — has no Clsn2 on any of its 8 frames
  evidence  2413 Clsn2 boxes in the file overall, but 0 of 8 frames of animation 0
  fix       add a `Clsn2Default` block to animation 0 in the .air file
```

A finding whose cause contradicts its own evidence is refused rather than
printed — an early version claimed a character "declares no commands" while
reporting 363 of them in the same sentence.

The `it froze` symptom is the author's pre-ship freeze check: it names the two
faults that share it — the character traps *itself* in a state it cannot leave,
or a throw stranded it in a `p2stateno` its own files never define — tells the
author to rule out the legitimate holds first (a finished round, a bonus prop, a
long intro, a charge or command-grab stance, AI a passive dummy never triggers,
a tag/assist run solo), and points at `oxtool unstick` to name the exact state
and, with `--apply`, fit a reversible escape. The full differential is
docs/CASEBOOK.md "fighter stuck".

## normalize

Repairs a fault of omission, and proves the repair by fighting.

A state marked `movetype = A` whose animation has boxes drawn but no
`Clsn2Default` is not a bad character; it is a finished one with a one-line
omission. `normalize` derives a hurt box from the character's own
`size.ground.back/front` and `size.height`, writes it into the `.air`, **then
re-fights the character and keeps the change only if a refusal disappeared and
the score did not fall**. Otherwise the file is restored byte for byte and the
backup deleted.

Proven: a healthy character stripped of every `Clsn2` drops to `REFUSE 85%`,
unkillable, and `normalize` returns it to `ACCEPT 98%`.

**It repaired 0 of 256 real candidates**, and that is the useful finding:
characters that fail the gate are not failing from a missing collision box.

## unstick

Finds a fighter that traps itself in one state it never leaves, and fits a
bounded escape.

Some characters enter a state whose only exit is a predicate they never satisfy
— the backward hop (common state 105) lands only on `Vel Y > 0 && Pos Y >= 0`,
reached once gravity turns the hop around, but a tag or assist character run
solo keeps re-setting its own velocity through its partner-side helpers, so
gravity never wins and it rises off the top of the screen forever; or a
knockdown (5101) whose get-up is gated on a flag it never clears. The opponent
stays healthy and the sim is faithful — in a real match the round timer ends the
round — but against the untimed audit dummy it sits in that one state and `gate`
reports it as `froze`. `unstick` reuses the audit's own record of *which* state
(`end_state`) and for how long (`stuck_ticks`) to name it.

With `--apply` it writes a `[State -1, oxyde-unstick]` watchdog into the
character's command state that changes out of **exactly** that state once it has
been held past a bound (`--after`, default 150 ticks) to a neutral state
(`--escape`, default 0). Because it targets only the one state the fight proved
it hangs in, it cannot fire during any state the character leaves on its own,
and **the change is re-fought and kept only if the hang is gone and the fighter
is no worse** — otherwise the command file is restored byte for byte and the
backup deleted. Reversible: `oxtool revert --kind unstick`.

Proven on the SvC 2023 import: Necalli `REFUSE 91% → ACCEPT 100%`, Elias
`REFUSE 88% → ACCEPT 97%`. A character whose hang is a *loop* through several
states rather than one stuck state is correctly left untouched — the fix it
cannot prove, it does not make.

`--roster` sweeps every character. Before it calls a hold a fault it excludes
the ones that are not one: a finished round (a KO) the audit already rules out,
and `bonus = 1` props and mode controllers — which sit in one manager or idle
state by design — which `unstick` **skips by default** and reports as a count
(`--include-bonus` tests them anyway). The holds it cannot rule out
mechanically — a long intro, a charge or command-grab stance, AI the passive
dummy never triggers, a tag/assist run solo — it names as hints to check by
hand. The full differential is docs/CASEBOOK.md "fighter stuck".

## complete

Writes the `HitDef` for an attack the author drew but never wired up.

The timing is not guessed: the `HitDef` triggers on the first animation
element carrying a `Clsn1`, because that is the frame the author drew as the
blow landing. The numbers come from the character's own other `HitDef`s, and
failing that from the median of **28,045 real ones** across the archive —
`damage = 40`, `pausetime = 9`, `ground.hittime = 16`, `attr = S, NA`,
`guardflag = MA`.

Every completion is fought and kept only if attacks or specials now connect,
or it now deals damage, and nothing regressed. Of 126 characters rejected for
not hitting, it finished 8 and 6 of those then passed the full gate.

## fuseify

Converts a whole installation to FUSE, permanently and in place.

Each converted file keeps its original extension with `.fuse` appended —
`bob_ex.cns` becomes `bob_ex.cns.fuse` — because using the stem alone made
`bob_ex.cmd` and `bob_ex.cns` collide and silently destroyed a command set.
The original `.def` is kept as `<name>.def.cns-backup` and **never
overwritten**, so a second run cannot back up an already-converted file over
the original.

Two safeguards run per character: the converted text must compile before it
replaces anything, and the character's *shape* — its state count and move
count — must be unchanged, or the `.def` goes back.

> Shape is not behaviour. Use `fuse-verify` as well; see below.

## props

`oxtool props <root>` answers one question for a Knuckle Up author: which of
the installation's bonus-game characters (`bonus = 1` in `select.def`) can be
parked in a stage with `prop1 = name, at X, reward`. Each is fielded mid-fight
the way the mode parks a prop, beside a fighter who does nothing, and watched
for 300 ticks; then it is brought to zero life and watched again. A prop is
`usable` when none of these is seen:

| fault | what was measured |
| --- | --- |
| dies on arrival | its root's life is gone within the first 30 ticks |
| wanders | its root ends more than 40 units from where it was put |
| draws nothing itself | its root shows no sprite: what is seen is helpers |
| draws a backdrop | it or a helper shows a sprite 480 or more world units wide, as drawn (pixels times its `[Size]` scale and `localcoord`) |
| does not stay broken | after reaching zero life, it has life again |

On the development archive, 1 of 7 is usable — `car2`, the Mercedes. The
others are built for their own bonus stage. `oxtool campaign <file> --root R`
runs the same measurement on every prop a campaign names, and prints what the
[street props](KNUCKLE-UP-CAMPAIGNS.md#street-props) dress each stage with
for a run seed (`--seed N`, default 1): the stage's theme, each prop with the
prize it drops, and the timed hazards. The street props are all usable; their sprites are made
at three pixels a world unit and shown at a third, which is why the backdrop
test measures sprites as drawn rather than by their pixels.

## knuckle migrate

Knuckle Up keeps its own content in `knuckleup/` at the game root (campaigns,
belt stages, props, weapons, music, intros, logic and `knuckleup.cfg`; see
[KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#the-knuckleup-folder)).
`oxtool knuckle migrate <root>` gathers an older install's content into it:
every campaign in `data/campaigns/`, the belt stages those campaigns name by
path (a stage's folder, or a loose `.def`), their music, intros and logic,
private props, and the `data/weapons/` set. It leaves shared what another mode
uses — a stage `select.def` lists or a campaign names by name, a prop that is
also a bonus game, a track another stage plays — and lists the legacy copies
that are then duplicates nothing else needs. Campaigns are copied unedited:
the engine reads a leading `stages/` or `sound/` as the mode's folder first,
so every campaign's identity, and every replay recorded on it, survives; the
report prints each identity. `--dry-run` writes nothing, `--move` removes the
legacy duplicates after copying, `--out DIR` writes the folder elsewhere (the
root itself is only read).

On a large roster: both campaigns, the ten *Long Run* streets and
`knuckle_rust_street.def` move, with the pipe; `dock`, `kof2k-factory` and
`car2` stay shared; the twenty campaign tracks are all played by other stages
too, so they stay in `sound/`.

`oxtool campaign --root <root>` (no file) then checks every installed
campaign and prints, for each path it names, where it was found
(`knuckleup`, `beside campaign`, `legacy`, `installed stage`).

## ab

`oxtool ab` loads each converted character twice — its FUSE files and the
original files the converter kept — and puts the two through the same
deterministic battery: the audit's capabilities, two scripted runs compared
tick by tick, every compiled state, constant and command compared, Oxyde's own
load report, and whether WinMUGEN would refuse the original. It reports both
directions (what the conversion or a later repair *fixed*, and what it
*broke*), classifies every loss by experiment, and can enforce the guarantee
that no character plays worse than it was written: `--check <baseline.tsv>`
fails like `regress --check`, and `--apply-fallback` holds any character whose
FUSE form loses on its original files until the loss is fixed. The method, the
definition of "worse", and what it found are in
[FUSE-CONVERSION.md](FUSE-CONVERSION.md#is-it-the-conversion-oxtool-ab).
`--original` on any other command asks its question of the original form.

## fuse-verify

Proves a conversion changed nothing, or undoes it.

```
oxtool gate <root> <char.def> --tsv     # sweep before
oxtool fuseify <root>
oxtool gate <root> <char.def> --tsv     # sweep after
oxtool fuse-verify <root> before.tsv after.tsv --revert
```

Degradation is judged on what matters, not the score alone: losing
hittability, losing damage, starting to freeze or leave the playfield, falling
to `REFUSE`, or losing two or more specials. A drop of a point or two is
timing noise and is ignored.

Two traps when scripting around it: the backup's extension is lowercased, so
`AOSHI.DEF` has `AOSHI.def.cns-backup`; and removing the `.fuse` files alone
makes things **worse**, because `fuseify` repoints the `.def` at them —
restoring the `.def` is the revert.

> **Hold the opponent constant.** `chars/kfm/kfm.def` is both the benchmark
> dummy and a roster character. Converting it between the two sweeps moves the
> ruler with the thing being measured, and made 100 unrelated characters look
> newly broken.

## coverage

Audits FUSE against MUGEN and Ikemen GO on three axes, and fails on a gap.

```
$ oxtool coverage .
controllers   160 in the engine, all writable in FUSE
triggers      281 in the engine, all readable in FUSE
...
scanned 8776 state files across 2152 characters
  covered by FUSE         222968
  no section used 5 or more times is missing from FUSE.
```

The third axis is the point. FUSE had no syntax for a character's constants
for months while both other counts read "complete", because nothing compared
the **file sections** real content contains against what the language could
express. Exits non-zero if any section used five or more times cannot be
expressed, so it belongs in CI.

## `oxtool demo` — film an online session, both players at once

    oxtool demo <game-root> [--out DIR] [--p1 NAME] [--p2 NAME]
                [--host-name N] [--join-name N] [--every N] [--zoom N]

Drives **two real `Game`s** on a simulated link and photographs both of them on
every frame: the same `Game::update` the window calls and the same
`Game::render` it draws with, side by side, with a caption saying what is
happening. A scripted session — a match, the post-match vote, a line of chat
each way, and the rematch that starts on the connection the first match was
played on.

```
$ oxtool demo .. --out demo --p2 ken
533 frame(s) of 1601 simulated, in demo/
  1288x508 each, one every 3 frame(s)
  frames.txt lists what is happening in each
  room: host bout 2 chat 3 | joiner bout 2 chat 3
  session: host frame 1083 | joiner frame 1079
```

Those last two lines are why this is a tool and not a screen recording. `bout 2`
on both peers is the rematch having happened; one session frame on each, four
apart, is the two of them still on the same link with one predicting ahead of the
other. **A run of this is also a check** — the same driver as the online test
harness, pointed at a framebuffer instead of at assertions.

Frames land as numbered PNGs plus a `frames.txt` naming each one and its caption.
Turning them into a GIF or a video is deliberately not this command's business —
it has no business shelling out to an encoder that may not be installed.
`model/gif.py` is one way:

```
python3 model/gif.py demo/ online.gif --fps 20 --width 966
```

### What the script is, and why it is data

The session is a list of beats, each carrying its own caption *and* the input
that earns it, so the two cannot drift apart. Beats wait on a predicate rather
than a frame count — "until both peers are on the result screen" — so the film
still makes sense when a round takes a different number of frames than it did
last week.

Two things it sets deliberately. The round clock is **8 seconds**, because at the
archive's own 99 a round nobody wins runs 5,940 frames and the film is about what
happens *after* a match. And waiting is photographed four times as coarsely as
the rest, because a time-over is most of the run and none of the interest.

## `oxtool docs` — do these documents still say true things?

    oxtool docs <repo-root> [--root <archive>] [--list] [--history]
                            [--unchecked] [--prose] [--refused] [--fix]

Re-derives every checkable number in `docs/**`, `README.md` and `BUILDING.md`
from the code, the workspace manifest and the game's own loader, and exits
non-zero on a claim that disagrees. It names the file, the line, the claim and
the true value.

`--prose` prints the structural claims — *"X depends on Y"*, *"N crates"*,
*"the workspace declares Rust N"* — with the verdict on each, and `--refused`
prints the claim shapes this command declines to check together with the
measurement that refused them. The second list is the honest half: a checker
nobody can see the edge of reads as a guarantee it never gave.

Documentation numbers drift as the code changes: a test count that was true in
one place and stale in another, a line-of-Rust figure that no longer matches, a
command count that agrees with neither the documented total nor the dispatched
one. Fixing them by hand does not keep them fixed — any workstream that adds
code can move a figure out from under the prose that quoted it. This command
catches that drift by re-deriving each checkable number straight from the code.

```
$ oxtool docs .
what the code reports
  tests             2981   #[test] in 275 .rs files under crates/
  rust-lines      298238   lines in 274 .rs files under crates/
  crates              14   [workspace] members in Cargo.toml
  controllers        160   SctrlKind::NAMES.len()
  triggers           281   TriggerId::NAMES.len()
  commands            77   Some("…") arms in main()'s dispatch
  roster            2527   playable roster entries under <game-root>
  roster-fuse          —   no secondary roster given (pass --fuse-root)
  stages             215   stages select.def offers

59 document(s), 937 claim(s) extracted, 58 checked against the code
  709 of them numbers no probe covers (--unchecked lists them)
nothing in these documents disagrees with the code.
```

Forty-two checkable claims out of 751 numbers is not a shortfall to hide: the
other 709 are percentages and per-sweep counts ("268 of 2,443 characters",
"90.5%") whose probe would be the sweep itself, which takes minutes to hours. A
checker that takes an hour is a checker nobody runs, so they are counted and
listed rather than quietly dropped.

Each probe is measured, never asserted: the controller and trigger counts come
out of the engine's own `NAMES` tables — the same two `oxtool coverage` prints
— and the roster is weighed by `Assets::open`, the loader the game itself uses,
rather than by counting lines in `select.def`.

**History is not checked**, because a checker that cries wolf gets switched
off. `CHANGELOG.md` is not read at all. Elsewhere a number is left alone when
it is under a heading that records history, when the line dates its own number
("as of", a `2026-09-18`), when the sentence is in the past tense, or when it
is one end of a recorded change (`280 -> 281`). Dating a figure is therefore
the supported way to write one that will age. `--history` prints everything the
rule stood down, with today's value beside it, so the filter can be argued
with.

**The opposite failure is worse**: an extractor that matches nothing passes
forever. The footer always prints how many claims were found and how many had a
probe behind them, and a unit test pins the real doc lines from the audit
above, so an extractor that stops recognising a known-true claim fails
`cargo test`.

`--fix` rewrites the digits it is certain about, in place, preserving how the
number was written — `~126k` becomes `~166k`, and a hedged figure is re-rounded
so it stays inside its own five per cent band instead of going stale the next
afternoon. It cannot rewrite the sentence around the number, so it prints every
edit and the diff has to be read: "**132** — Elecbyte's 93 and 39 of its own"
needs its arithmetic re-done by a human.

It also reports two structural claims a number cannot express: source and
document paths named in `docs/` that are not there, and the subcommands
`TOOLS.md` never mentions.

## `oxtool eval behave`

    oxtool eval behave <DIR> <completions.jsonl> [--show N]

Scores completions by **what they do** rather than by whether they read the
same.

    $ oxtool eval behave data/bench model.jsonl
      kind        tasks    scorable        behaviour matched
      body         108          41        19 of 174    10.9%
      guard        110          38        14 of 151     9.3%
      params       121          38        14 of 171     8.2%
      ------------------------------------------------------------
      all          339         117        47 of 496     9.5%

### Why a second scorer

`oxtool eval score` measures `correct` as **exact match**: character for
character what the original author wrote. That is fair, strict, and has one
structural problem as the *only* measure — it rewards copying over writing. The
`retrieve` baseline pastes the nearest neighbour out of the training half, and
on an archive where characters copy each other wholesale, pasting is *sometimes
literally right*.

Measured: the model's non-empty answers were **39% similar to the author's text
at the median and 67% at the top quartile**, and scored **0.9% exact**. Those
numbers describe different things, and for "would this help somebody writing a
character", exact match is the wrong instrument.

So this asks a different question. Splice the candidate in, compile it, read the
facts back out of the state it landed in — does it attack, for how much, does it
knock down, what does it cost, how many controllers does it run, what does it
change the animation to — and compare with the facts of what the author wrote.

### Only the fields the hole is responsible for

A hole is a few lines inside a state that may be a hundred lines long, and the
facts the *prompt* already establishes are free to every candidate. Deleting a
controller's parameter list does not stop the state attacking, because the rest
of the state is still there.

So a field is scored only when the reference **moves it away from blank** — the
same document with the hole left empty. A hole that changes nothing observable
is scored out of nothing and excluded, exactly as a task whose own reference
will not compile is dropped.

That is not a refinement, it is the difference between a scorer and a rubber
stamp. Without it, an empty answer scored **95%**.

### The calibration, which is the point

A score you invent is a score you can shape to flatter, so this one is held to
the same two tests as everything else here and both are re-run on demand:

| Answer | behaviour matched |
|---|---:|
| the author's own (**oracle**) | **100.0%** |
| copy the block above | 37.3% |
| nearest neighbour (`retrieve`) | 29.6% |
| **answering nothing** | **0.0%** |

The answer key must score 100% or the scorer is broken; a blank page must score
zero or the metric is satisfied by silence, exactly as `valid` is. Both hold.

Getting there took two bugs, both found by running those baselines rather than
by reading the code:

* A state compiled from **FUSE** keeps its controllers in a structured `body`
  and leaves the flat `controllers` list empty; a state from CNS does the
  opposite. Reading only the flat list reported every FUSE state as doing
  nothing — for the answer key as well as the answer, so the two agreed
  perfectly and **everything scored 100%**.
* Scoring whole-state facts rather than the hole's contribution gave an empty
  answer **95%**.

Neither is visible in the output of a single run. Both are obvious the moment
the baselines are on the same page.

## `oxtool reference`

The complete state-controller, trigger and common-state reference, **generated
from the engine** rather than written beside it.

```
oxtool reference <game-root> --out docs/CONTROLLERS.md
oxtool reference --lookup 120
oxtool reference --lookup hitdef
```

It writes three documents: [CONTROLLERS.md](CONTROLLERS.md),
[TRIGGERS.md](TRIGGERS.md) and [STATES.md](STATES.md).

### Why generated

A hand-written reference is out of date the moment a parameter is added and
nobody notices, because nothing checks a document against the code it
describes. Every structural fact here is read out of the compiler at build
time — the controller list, each controller's accepted parameters, every
trigger and the number of arguments it takes. Those cannot drift, because they
are the same tables the compiler accepts input with.

### What no other reference has

**Usage.** Every controller carries how many of the archive's characters
actually use it, and the list is ordered by it. `ChangeState` is one call in
five; `MoveHitReset` is in eight characters. No manual can tell you that,
because no manual has a thousand characters to count.

**Real examples.** The example beside a controller is lifted from a character
that ships in the archive and compiles. Nothing is invented.

**A coverage number.** Meaning cannot be generated — what a controller is *for*
is prose, and this project will not paste Elecbyte's manual, which is theirs.
So descriptions are written here in original words and the command prints how
many exist. A gap is visible rather than silent, which is the difference
between an incomplete reference and a misleading one. It also prints the
most-used controllers that still lack one, which is the work queue.

### `--lookup`

A reference is a table, not prose, and `--lookup` answers the
question a table is for — exactly, by name, with no ranking involved.

```
$ oxtool reference --lookup 120
state 120 — `GuardStart`

Guarding has begun. The engine sends a fighter here when it decides the
incoming attack is being blocked, and this state chooses which guard
stance follows.
```

## `oxtool trials`

    oxtool trials <game-root> <char.def> [--vs <char.def>] [--demo] [--why]
                  [--trace N]
    oxtool trials <game-root> --roster [--every N] [--limit N] [--tsv FILE]
    oxtool trials <game-root> --combos [--every N]

The move trials a character gets, and how long generating them took — which is
a number worth knowing, because the combo half of a trial set is *proven by
simulation* before it is offered and somebody pays for that when the page is
opened. (In the game it is paid on another thread, started when the practice
session begins.)

    $ oxtool trials . chars/kfm/kfm.def --demo
    Kung Fu Man - 26 trials against Kung Fu Man (311 ms to generate)
       0  MOVE   STANDING LIGHT PUNCH (X)  ->  STANDING MEDIUM PUNCH (Y)  ->  STANDING LIGHT KICK (A)  ->  STANDING MEDIUM KICK (B)  [clears 4/4 moves, 1 hits]
       6  MOVE   FORWARD LIGHT PUNCH SPECIAL (D, DF, F, X)  ->  FORWARD MEDIUM PUNCH SPECIAL (D, DF, F, Y)  [clears 2/2 moves, 1 hits]
      12  MOVE   STANDING LIGHT PUNCH (X)  ->  SMASHKFUPPER (D, DB, B, D, DB, B, X, AFTER A HIT)  [clears 2/2 moves, 2 hits]
      16  COMBO  STANDING LIGHT PUNCH (X)  ->  DASHING 2-KICK SPECIAL (F, F, A+B)  [clears 2/2 moves, 2 hits]
      20  COMBO  JUMPING MEDIUM KICK (UF, B)  ->  STANDING LIGHT PUNCH (X)  [clears 2/2 moves, 2 hits]
      ...
    12 of them are combos, every one proven to connect before it was offered.
    26 of 26 demonstrations were credited by the trial judge.

"Connect" means as one combo: each move lands before the next begins and the
opponent's hit counter never goes back down in between. `--why` says which of
those a rejected route failed — `the opponent got out of the combo` is by far
the most common, and is what a normal that cannot be cancelled into anything
looks like.

`--vs` is who the combos are proven against, and it matters: a route that links
on a tall character can whiff entirely on a small one, which is why the game
proves them against whoever is actually standing opposite.

`--demo` replays each trial's demonstration — what **Select** plays in Training
— and judges it with the same `Attempt` a player is judged by: `clears` is the
engine performing its own trial and being credited for it, `performs, NOT
CREDITED` is every move coming out and the judge still saying no — which is the
symptom a player reports as "I did it and it didn't count". It is the same
driver that proved the route, so a disagreement between the two halves of this
command is a bug in one of them. Moves on the list that got no trial are listed
at the end, each with the reason.

`--roster` asks the whole roster at once: for every special, super and normal
on every character's derived move list, whether a single-move trial covers it
and whether its demonstration clears it, as a table by kind (and a TSV with
`--tsv`, whose last column `via` says how a covered move is reached when it is
more than its command: `charge`, or the setup route in front of it —
`follow-up`, `spawn`, `mode`). The summary counts those under *covered only
with a setup or a charge*, and the moves still without a trial by the reason
their guard gives. `--combos` performs every offered combo the way a quick player does —
each motion straight after the last, one to sixteen ticks apart, without
waiting to see the hit — and counts how often the combo counter said it
connected, how often the judge credited it, and how often an earlier judge
would have.

`--why` also prints every **setup route** tried for a move that comes out from
nowhere on its own — `route BARIBARI X: GATRINGA X (follow-up) - PROVEN,
Cancel(1)`, `route RDP X: BACK DASH (follow-up) - did not bring it out (1
joins, 349 ticks)`, `route BOOM: nothing in its guard a setup could provide`,
`... - a setup never comes out itself` — which is how to tell a move nothing
can reach (a groove picked at the select screen, an entry the author set to
`null`) from a search that ran out of budget. `OXYDE_TRIALS_TIME=1` prints
where generating a set's time went, the route search's ticks included.

An empty combo list is an answer rather than a failure: a great many characters
in this archive genuinely cannot cancel or link anything into anything. `--why`
is how to tell that from a broken search — it prints what became of every
candidate route, and "starter never came out or touched nobody" against all of
them usually means the character's normals are gated behind its own system,
which `oxtool moves --try` will confirm. `--trace N` follows one trial's
demonstration tick by tick: what state the fighter is in, whether it has
control, how far apart they are standing and what is being pressed. That is what
tells "the input never arrived" from "the move never came out" from "it came out
and missed" — and it is what caught the first version of this calling the fight
on while both fighters were still playing their entrances, which made every
trial in the list report that the move never came out.

### `[P2 LEFT AS A COPY OF P1]`

One fault the harness looks for on its own. A throw or a cinematic super puts
the opponent into one of the *attacker's* states and, with `ChangeAnim2`,
into one of the attacker's animations — on purpose, for as long as the custom
state lasts. Still animating out of the attacker's file once everything has
finished is a bug: the opponent keeps the attacker's body for the rest of the
round, which from the sofa is "a clone of the character performing it was also
the victim".

The question is asked of a *settled* match rather than of the tick the watch
window closes. The longest cinematic super in this archive holds both fighters
for the better part of ten seconds, so the harness lets the match run itself
out with nobody pressing anything and asks at the end of that. Asking earlier
called a hundred and sixty perfectly ordinary supers a fault.

`OXYDE_TRACE_CLONE=1` prints what each side was left in.

## sprites

    oxtool sprites <game-root> [--limit N] [--show N] [--only TEXT]
    oxtool sprites <game-root> --roundtrip [--codec NAME] [--limit N] [--show N]
                   [--only TEXT]
    oxtool sprites <game-root> --quantise [--limit N] [--only TEXT]
    oxtool sprites export <char.sff-or-.def> <out_dir> [--pal N]
    oxtool sprites pack <png_dir> <out.sff> --scale N [--png8 [--colors N]]

Decodes **every** sprite of every character, stage and screenpack the archive
can reach, and reports the ones that did not come out whole:

    $ oxtool sprites .
    sprite files  1247
    sprites       765712
      by format   pcx (v1) 765552 raw 3 rle8 157
    failed        158  (the decoder could not read them at all)
    short         0  (decoder ran out before the frame was full)
    size mismatch 0  (the index and the image disagree)

      chars/Seiya3/Seiya.sff  66 unreadable
        sprite 5 (2,0): pcx: unsupported PCX: 8bpp x 3 planes
        ...

Written for a report nobody can act on by reading code: "some of the sprites
don't render properly for some characters — they might look like smeared
pixels, or distorted". A sprite that decodes *wrongly* and one that decodes
*short* look the same on screen, and both look like half a dozen other things
— a bad palette, a bad axis, a scale the character asked for.

What separates them is a number the decoder already knows and used to throw
away: how many of `width * height` pixels it actually wrote. A payload that
ends early leaves the rest of the frame transparent; one that *desynchronises*
keeps writing, from the wrong place, and every row after the fault slides
sideways. That second one is the smear.

The run above is the one that found the archive's 158 24-bit PCXs. It exits
non-zero when anything came out short or mis-sized.

### --roundtrip: proving the SFF *writer*

`oxyde-format` can write an SFF as well as read one — SFF v1.01 with 8bpp RLE
PCX subfiles and shared or per-sprite palettes, and SFF v2.01 with raw, RLE8,
RLE5, LZ5 and PNG-in-SFF payloads. None of that is worth believing on the
strength of synthetic fixtures. The sprites that matter were written between
2001 and last week by a dozen tools nobody has the source to, so the proof is a
round trip over the archive itself: decode a sprite, encode it, decode it
again, and compare.

    $ oxtool sprites .. --roundtrip --show 0
    round trip  decode -> encode -> decode, codec native
    files        16784
      SFF v1      16738 files, 8126562 sprites
      SFF v2      46 files, 4539 sprites
    sprites      8131101 in the index
      tried      8130910
      unreadable 98  (the reader could not decode the source)
              98  sprite N has no payload and links to N, which is not an earlier sprite

    sprites the reader could not decode
      chars/kikyo/kikyo2.sff  sprite 242 (5032,50): sprite 242 has no payload and ...
      ... 97 more, each named with its file, index and group,image

    by format      tried     exact  renumbered
    pcx (v1)     7530411   7530411           0
    rle8            1102      1102           0
    lz5              992       992           0
    png             2149      2149           0
    link          596256    596256           0
    total        8130910   8130910           0

    exact 100.0000%   colour-exact 0.0000%   failed 0
    bytes  source 39340057849  rewritten 38310105665  (-2.6%)
    took 135.1s

    every sprite tried came back exactly as it went in.

Byte-identical output is not the bar and could not be: the original bytes carry
whichever tool's run-splitting and filter choices. What must survive is what
the engine can see, and that is graded in two tiers:

* **exact** — the same size, the same axis, the same palette *indices*, and the
  same colours behind them. An index is not cosmetic: `.act` palettes,
  `RemapPal` and `PalFX` all address a sprite by index.
* **colour-exact** — every pixel the same colour on renumbered indices. Only a
  truecolour sprite can land here, because it has none of its own;
  `spng::index_rgba` assigns them on the way in and does so again coming back.
  Nothing lands there on `native` any more. 330 sprites used to: a 32-bit PNG
  was quantised through a 256-entry table on the way back out, even though the
  format it was going into has no such limit. `SpriteEntry::rgba` carries a
  truecolour sprite's colours alongside its indices, so those 330 are exact
  too. The tier is kept because it is still what `--codec png32` does to
  *indexed* art, which genuinely has indices to lose.

`--roundtrip` walks every `.sff` on disk rather than every `.def`, which is the
opposite of what the decode report above wants: it needs the widest sample of
*files*, including the ones under `Ikemen-GO-Screenpack/` that hold this
archive's only SFF v2.01 sprites. Measured here, the `.def` walk reaches 5,071
files and the tree walk reaches 16,786.

`--codec` forces one storage format on every sprite instead of keeping the
source's — `native`, `pcx`, `raw`, `rle8`, `rle5`, `lz5`, `png8`, `png24` or
`png32`. That is how a codec with no presence in the archive gets tested
against real art: **nothing** in twenty-two years of this corpus uses RLE5, and
forcing it puts all 8,130,894 sprites through it. Measured over the whole
archive:

| `--codec` | exact | colour-exact | failed | rebuilt bytes |
| --------- | ------- | ------- | ---- | ------- |
| `native`  | 8130910 | 0       | 0    | -2.6%   |
| `rle8`    | 8129678 | 0       | 1232 | -11.3%  |
| `rle5`    | 8129678 | 0       | 1232 | +37.5%  |
| `lz5`     | 8129678 | 0       | 1232 | -13.3%  |
| `raw`     | 8129678 | 0       | 1232 | +230.6% |
| `png8`    | 8129677 | 0       | 1233 | -40.4%  |

8,130,910 sprites were tried in every row. `png32` is the row that shows what
the two tiers mean: storing an *indexed* sprite as truecolour throws its
indices away, so almost everything lands in colour-exact — every pixel the
right colour, on a palette the character's `.act` files no longer address.
Nothing fails, because 32-bit PNG is the one codec that can hold anything an
SFF sprite can be.

The 1,232 are one cause, and it is a property of the format rather than a
coding fault: an SFF v2 palette table is RGB and the reader gives every entry alpha
255, so the partly transparent colours in Ikemen GO's 32-bit PNG sprites cannot
survive being stored on an **indexed** codec. `native` keeps them as 32-bit PNG
and loses nothing, which is why it fails none.

The two truecolour codecs take about twenty minutes a sweep, and they behave
differently enough to be worth their own rows:

| `--codec` | exact | colour-exact | failed | substituted | rebuilt bytes |
| --------- | ----- | ------------ | ------ | ----------- | ------------- |
| `png24`   | 5599  | 8125310      | 1      | 7267458     | -38.2%        |
| `png32`   | 5599  | 8125310      | 1      | 0           | -37.6%        |

Storing *indexed* art as truecolour throws its indices away, which is why
almost everything lands in colour-exact: every pixel the right colour, on a
palette the character's `.act` files no longer address. `png24` substitutes
7,267,458 sprites onto `png32` because 24-bit has nowhere to put transparency
and those sprites use index 0.

The **1** is the same sprite in both rows, and it is a disagreement between two
decoders in this crate rather than anything the writer got wrong:

    $ oxtool sprites .. --roundtrip --codec png32 --only jumstage
      sprite 1 (0,1) second decode failed: an embedded 32-bit PNG sprite could
      not be decoded

`stages/jumstage.sff` sprite (0,1) is **420x18600**. `pcx.rs` used to refuse it
under a per-axis `MAX_DIM = 8192` and no longer does — the cap was dropped
precisely because this sprite disproved "8192 is far beyond any real MUGEN
sprite", leaving the pixel-count budget as the only guard. `spng.rs` still
carries a per-axis `MAX_DIM = 16384`, so the sprite now decodes as PCX, encodes
as a 420x18600 PNG, and is then refused on the way back in. Under `native` it
stays a PCX and round-trips exactly, which is why the headline run fails none.

The same argument that retired the PCX cap applies to the PNG one: both PNG
dimension fields are `u32`, and the pixel-count budget already refuses anything
that would provoke a large allocation. Until that is settled, a sprite taller
than 16,384 cannot be stored as PNG-in-SFF and read back by this crate.

LZ5 is the other place the format, not the encoder, sets the limit.
`sprmake2`'s own documentation offers `lz5` and `rle5` under
`sprite.compress.5`, "for 5-bit sprites (32 color)", separately from `rle8`
under `sprite.compress.8` — and LZ5's literal packets really do carry a 5-bit
value, so no LZ5 stream can contain an index above 31. The encoder returns
`None` rather than truncating: of 8,130,910 sprites, 1,930,681 fitted in LZ5
and the other 6,200,229 were written as RLE8 and counted under `substituted`.

### The 117 sprites the reader could not decode

The first full round trip could not test the writer on 117 sprites, because
decoding the **source** failed: those are sprites in real content that this
engine could not draw. They came in four classes and they were four different
things. Three were reader faults and are now read; the fourth is damage, and
the requirement there is that it be *reported* rather than skipped in silence.

| class | count | verdict | now |
| ----- | ----: | ------- | --- |
| `implausible PCX dimensions 65536x65536` | 15 | reader bug | decodes |
| `not a PCX (magic 0x02)` | 3 | reader bug | no longer exists |
| `implausible PCX dimensions 420x18600` | 1 | reader bug | decodes |
| `sprite payload is out of bounds` | 98 | damaged content | reported precisely |

**`65536x65536` is an empty sprite.** The headers are not damaged: magic 0x0A,
version 5, encoding 1, 8bpp, one plane, `xmin = ymin = 0`,
`xmax = ymax = 0xFFFF`, `bytesPerLine = 0`, and a subfile of exactly 897 bytes
— 128 of header plus the `0x0C` marker plus 768 of VGA palette, and **no pixel
data at all**. PCX has no other way to say "no pixels": the width is
`xmax - xmin + 1` over `u16` fields, so a zero-width image must write
`xmax = xmin - 1`, which wraps to `0xFFFF` at the origin. MUGEN computes that in
16 bits and gets 0; Oxyde widened to 32 first, got 65536, and refused the sprite
for being enormous when what it said was "nothing here". The files are
`chars/CRONO/CRONO.SFF` sprites 154 and 156-159, `chars/Andy/ANDY.SFF` 418,
`chars/FF4TERRY/FF4TERRY.SFF` 701, `chars/MAURU/MAURU.SFF` 133 and 147, and
`chars/nesmegaman/nesmegaman.sff` 22. The writer now says `0xFFFF` back, so an
empty sprite round-trips as empty rather than as one pixel.

**`magic 0x02` was not a sprite.** `chars/nicotine/nicotine.sff` declares
`nimages = 582` and its 582nd sprite's `next` points at 1,914 bytes of appended
non-sprite data — pairs of small signed 16-bit integers, whatever the author's
tool left there. The walk read 32 of them as a subfile header (`next` =
0xFFEFF02, `length` = 65539, `palletSame` = 254) and reported sprite 583 as
"not a PCX". The header's count is authoritative in one direction and that is a
measurement, not a reading of the spec: over all **16,738** SFF v1 files here,
walk length minus `nimages` is **0 for 16,725 files, negative for 10 and +1 for
exactly three** — the three copies of nicotine. Not one file in the archive
gains a sprite by walking past the count, and the ten that stop early keep what
they found (`chars/GeorgeWBush/sprite.sff` declares 80 and has 6). So the walk
now stops at the count and says how many trailing bytes it left.

**`420x18600` is a real image.** `stages/jumstage.sff` sprite (0,1) is a
420x18600 stage strip. Decoded by hand its RLE consumes 865,502 of its 865,503
payload bytes and fills all 18,600 rows with 254 distinct palette indices. It
was refused by a `MAX_DIM = 8192` guard sitting in front of the pixel-count
budget, on the reasoning that 8192 is far beyond any real MUGEN sprite. The
budget is the guard that matters and does the job on its own: both PCX
dimension fields are `u16`, so the worst a header can claim is 65535x65535,
which is 4.29 billion pixels against a 64M budget. `MAX_DIM` is gone.

**The 98 are damaged content, and the message said the wrong thing.** They are
zero-length "linked" subfiles whose link field does not name an earlier sprite.
Counting every sprite that fails because of one, including the ones that link
back to it, there are 191: **106 name themselves** and **85 name a later
sprite**, by 1, 5, 10, 11, 12, 31 and once 65,305 places. No sequential loader
can resolve either — MUGEN copies from an array slot it has not filled yet —
and there is no reading of the field that rescues them. That the field is a
plain 0-based index and these files are simply wrong was measured, because the
round trip cannot show it: over the archive's 596,151 zero-length subfiles, the
0-based reading finds a *real* sprite where the 1-based reading finds another
link **162,433** times, and the reverse **2,923** times. `chars/bloo/kfm.sff`
has 45 of them, `chars/Majin Vegeta SSJ6/majinssj6.sff` 20, and
`chars/Rayquaza/Rayquaza.sff` is 544 bytes: a header and one empty subfile.

So they stay unreadable, and what changed is the report. The error used to be
`sprite payload is out of bounds`, which reads as a truncated file and is a
different fault with a different fix; it is now `sprite N has no payload and
links to M, which is not an earlier sprite`, naming the sprite that is actually
broken rather than the one that asked for it. The round trip lists every one
with its file, its index and its `group,image`, unconditionally — a count and
four reason strings is how 117 undecodable sprites sat in this archive
unattributed. None of it costs a character its other sprites: a decode failure
marks one `group,image` and the rest of the file loads.

### --quantise: choosing a quantiser by measuring it

A sprite with more than 255 colours cannot be stored as one: an SFF sprite's
pixels are palette indices. Something has to throw colours away, and for years
that was a fixed 3-3-2 cube — 3 bits of red, 3 of green, 2 of blue — which
spends its 255 slots on a grid of the whole colour space whether or not the
sprite has any colours near each point. Sprite art is a handful of hues in many
shades, which is the worst possible case for it.

`--quantise` is how the replacement was chosen. It walks every truecolour
sprite inside an `.sff` and every loose `.png`/`.pcx`, keeps the ones with more
than 255 opaque colours, and scores each candidate on all of them:

    $ oxtool sprites .. --quantise
    quantiser comparison over images with more than 255 colours
    candidates   16786 .sff files, 10091 loose .png/.pcx files
    images       2470  (1030 inside .sff, 1440 loose)
    opaque pixels 282935165

    quantiser        mean error  worst pixel   exact pixels
    3-3-2 cube          44.9621        95.64         10.36%
    median, box          3.5095        95.66         54.86%
    median, near         3.0235        81.52         54.91%
    median+grid          3.3461        67.39         52.99%

    median cut is 14.87x better on mean error
    took 44.7s

Error is the Euclidean distance between a pixel's RGB and the colour it ends up
on; transparent pixels are excluded, because they are index 0 under every
candidate and counting them would dilute every number with agreement that was
never in question. `median, near` is what ships: **14.87 times** less mean
error than the cube, five and a third times as many pixels reproduced exactly,
and a better worst case as well.

The fourth row is the one worth keeping in view. It spends 64 of the 255 slots
on a uniform 4x4x4 grid so that no colour in the cube can be far from *some*
entry, and it does win the worst case (67.39 against 81.52) at the cost of the
mean and of 1.9% of the exactly-reproduced pixels. It is still there as
`spng::index_rgba_median_gridded` so the comparison can be rerun rather than
believed.

And one fault this command found that no fixture would have. The first
median-cut implementation treated alpha as a fourth colour axis and scored a
mean of 3.1370 with a worst pixel of **178.27** — nearly twice the cube's
worst. Adding the grid, whose whole purpose is to bound the worst case, did not
move it by a thousandth. That is the signature of a measurement answering a
different question: the worst pixels were *partially transparent* ones, and a
4-D nearest search was giving them an entry that matched their opacity over one
that matched their colour, while every grid entry was opaque and so unreachable.
Alpha does not belong in the clustering and the format says so — an SFF's
palette records are RGB and `sffw::encode_v2` writes 255 for every entry, so the
only opacity a sprite carries through an indexed codec is index 0's. Dropping
alpha from the axes and from the search took the worst pixel from 178.27 to
81.52 and the mean from 3.1370 to 3.0235 at the same time.

Four reader faults were found by this command and fixed:

* **238 sprites were read from the wrong place.** An SFF v2 header's word at 56
  is the literal block's *length* and the word at 60 is the translate block's
  offset; the reader took its translate base from 56. Measured across all 46
  SFF v2 files here, `word(52) + word(56) == word(60)` and
  `word(60) + word(64) == the file size`, in every one. Seven PNG sprites in
  `stages/kfm.sff` failed outright and 227 RLE8 sprites in five font files read
  garbage and drew it.
* **24-bit PCX sprites decoded differently on each load.** The background
  colour of a 3-plane PCX is the commonest colour along its border, and where
  two tied the winner came out of `HashMap` iteration order — which
  `RandomState` reseeds per map, so the same bytes decoded twice in one process
  could pick two different transparent colours. 27 sprites in six files did
  exactly that. A sprite whose transparency changes from load to load is a
  rendering fault, not a round-trip one.
* **An empty sprite was refused and then rewritten as one pixel.** Fifteen of
  them; see the four classes above.
* **A stage strip was refused for being large, and a phantom sprite was read out
  of trailing junk.** One and three; also above.

### export / pack: building an HD sprite pack

The two ends of the HD/UHD pipeline (the middle step is a super-resolution model
of your choosing — see [HD-SPRITES.md](HD-SPRITES.md) for the full workflow and
the size trade-offs):

    oxtool sprites export <char.sff-or-.def> <out_dir> [--pal N]
    oxtool sprites pack   <png_dir> <out.sff> --scale N [--png8 [--colors N]]

`export` decodes every sprite to PNG, baking the character's real palette when
you give it the `.def` (a bare `.sff` uses the file's own, often placeholder,
palette); `--pal N` bakes a different one. `pack` reads the (upscaled) PNGs back,
**checks every sprite is exactly N× its base size**, and writes a sidecar SFF
v2.01 — `ky.sff` → `ky.hd2.sff` (`--scale 2`) or `ky.hd4.sff` (`--scale 4`). It
writes Png32 (RGBA, lossless, large) by default; `--png8` quantises each sprite
to an indexed palette (`--colors N`, default 256) for a far smaller pack. The
engine keeps the base sprite's geometry and only swaps in the higher-resolution
texture, so the match checksum is byte-identical whether HD is on or off.

## sprmake

    oxtool sprmake <def-file> [-o OUT.sff] [--v1] [--dry-run] [--force]
                   [--against REF.sff] [--show N]

Builds a sprite file from a `sprmake2` definition file and the loose PNG or PCX
images it names. Every other tool in this workspace reads sprites; this is the
only one that makes one.

That gap was not cosmetic. `oxyde-format::sffw` could write an SFF from palette
indices and nothing in the workspace could get indices out of a PNG on disk, so
a character generated by this project needed Python
(`MugenOxyde_Chars/build_sff.py`) to become a sprite file, and a character whose
art was wrong could be diagnosed and not mended.

The script format is MUGEN's own, from
`mugen_docs/elecbyte.com/mugendocs-11b1/sprmake2.html`:

    [Output]
    filename = chars/kfm/kfm.sff

    [Option]
    sprite.compress.8 = rle8
    sprite.autocrop = 1

    [Pal]
    1,1, kfm.act, 0,255

    [Option]
    sprite.usepal = 1,1

    [Sprite]
    9000, 0, f-face.png,   0,  0
       0, 0, stand00.png, 18,105

`[Option]` blocks may appear anywhere and change what follows — "The definition
file is parsed sequentially" — and all of the manual's options are read:
`input.dir`, `sprite.compress.5/.8/.24`, `sprite.decompressonload`,
`sprite.detectduplicates`, `sprite.autocrop`, `pal.detectduplicates`,
`pal.discardduplicates`, `pal.reverseact`, `pal.reversepng`, `sprite.usepal` and
`sprite.removecolors`. So are the per-sprite `?` extras the manual shows once
and never names:

    0, 33, Menu2.pcx, 0, 12 ? crop=0,0,15,59 ; !

That line is from `Ikemen-GO-Screenpack/work/font/Menu2/Menu2-sff.def`, which
`sprmake2` itself was run on, and whose 224 sprite lines all carry a `crop=`
cutting one glyph out of one `.pcx`. The one-key-per-line block form that this
workspace's own five generated characters use (`chars/Spark/Spark-sff.def` and
siblings) is read too.

### --against: the only check that can tell right from self-consistent

Building a file and reading it back proves that this crate's writer and this
crate's reader agree — which they would go on doing if both were wrong in the
same way. `--against` compares the result, colour for colour, with a sprite file
somebody else built from the same script:

    $ oxtool sprmake Ikemen-GO-Screenpack/work/font/Menu2/Menu2-sff.def \
        -o /tmp/Menu2.sff --against Ikemen-GO-Screenpack/data/ikemen1/fonts/Menu2.sff
    sprmake  Ikemen-GO-Screenpack/work/font/Menu2/Menu2-sff.def
      sprites      143
        linked     0  (identical to an earlier sprite)
        cropped    0
        axis derived 0
      palettes     1
      images read  1  (99797 bytes)
      output       108003 bytes, SFF v2

    read back: every sprite decodes, at the size and axis it went in at.

    against Ikemen-GO-Screenpack/data/ikemen1/fonts/Menu2.sff  (143 sprites there, 143 here)
      byte for byte         identical (108003 bytes)
      identical in colour  143
      differ               0
      not in the other file 0

143 of 143, against a file Elecbyte's own tool produced — and now all 108,003
bytes of it. What the comparison *decides* on is still what the engine can see —
which `group,image` pairs exist, how big each is, where its axis is, and the
colour behind every pixel — and not the bytes, because `sprmake2` was free to
order a palette differently and to split a run elsewhere and neither is visible
in the picture. The byte count is reported because it is the strongest thing
this comparison can say when it happens to be true.

Three bytes stood between "the same picture at the same size" and "the same
file", and each was a claim in a comment that measurement did not support: the
palette node carried group 1 item 1 rather than the `0,0` the script declared
(`[Pal] 0,0, Menu2.pcx`), the fourth byte of palette entry 0 was 255 rather than
0, and the compatibility version repeated the file's own 2.01 rather than the
2.00 that a file with no PNG sprite in it can claim.

The first run of that comparison said **1 identical and 142 differing**, every
one of them an axis, and that is the whole reason the flag exists. The script's
glyph lines read `0, 34, Menu2.pcx, 16, 12 ? crop=16,0,43,59` and every glyph in
Elecbyte's file has axis `(0, 12)`: a script's axis is a point on the **source**
image, so `crop=` takes its origin off the axis exactly as `sprite.autocrop`
does. The one glyph that matched was the one cropped from x=0. Nothing in
`sprmake2.html` says so; only the file it wrote does.

### Where this deliberately differs from sprmake2, and why

* **`sprite.compress.24`.** The manual offers `none`, `rle16` and `rle24` and
  marks the last two "(NOT YET AVAILABLE)". They never became available and no
  file in this archive uses either, so an image with more than 255 colours has
  one home in an SFF: an embedded PNG, format 11 or 12, which MUGEN 1.1 reads.
* **`sprite.decompressonload`.** Parsed, reported, and nothing is written for
  it. `sprmake2.html` says what the option does to the program — "0 - sprites
  are to be decompressed when needed (default). 1 - sprites are to be
  decompressed when loaded from disk" — and never says which byte of the file
  carries it. An SFF v2 sprite node's flags word is 16 bits of which only bit 0
  has a known meaning, and re-measured across all 4,539 sprite nodes in this
  archive's 46 v2 files that word is still only ever 0 (4,301) or 1 (238); the
  header's unassigned words at 16, 20, 28, 32, 68 and 72 are zero in all 46.
  Neither the manual nor the corpus says where this option lives, so the writer
  does not guess. A wrong bit in a file format is worse than an unimplemented
  option.
* **A derived axis.** `sprmake2` requires one on every sprite line. Here a
  sprite may say `? axis=auto`, or leave the axis out of the block form, and
  gets the bottom centre of its cropped pixels — where a standing character's
  feet are, which `mugen_docs/.../spr.html` calls for on the required frames.

### --txt2def: the SFF v1 transcript sprmake2 could convert

`sprmake2`'s usage line offers one more mode than the manual ever describes:

    txt2def - convert in_file (sff1 .txt) to out_file (sff2 .def)

There is no "SFF v1 script format" to describe, which is why `sprmake2.html`
says no more. `sprmaker`, the v1 tool, was interactive, and Elecbyte's own
documentation for it — `tools/mtools.txt`, still in this archive beside
`sprmaker.exe` — tells authors to drive it by piping their answers in:

> Just make a plain text file and put exactly what you would type at the command
> line into it. Then you can pipe this text file into sprmaker everytime you
> need to make your sprite. To pipe a text file named "sprite.txt" into
> sprmaker, you would type: `./sprmaker < sprite.txt`

So the input is a keystroke transcript, one answer per line: the output `.sff`
once, then five lines per sprite — image file, group, image, X axis, Y axis —
with an optional three-line `#` options menu in front of either, and `;`
starting a comment only at the beginning of a line.

    $ oxtool sprmake chars/sonson/SonSon.txt --txt2def -o /tmp/sonson-sff.def
    txt2def  chars/sonson/SonSon.txt
      sprite entries 989
      palettes kept  2  (individual setting)
        [Pal] lines  1  (the rest are sprite.usepal = -1)
      output         sonson.sff

    read back: the .def asks for all 989 sprites, at the group, image and axis
    the transcript gave them.

That last line is the conversion proving itself, and it is not behind a flag:
the `.def` is read back through `sffdef::build` — the same parser `oxtool
sprmake` uses — with a one-pixel stand-in answering for every image the script
names, and every entry's `group,image` and axis is compared with the
transcript's. The art does not have to be on disk, because what is being checked
is the conversion and not the pictures.

Without `-o` the `.def` goes to stdout and the report to stderr, which is both
what `sprmake2` does (`Usage: sprmake2 [options] [-o <out_file>] <in_file>`) and
what keeps a conversion from writing a file next to a transcript nobody asked to
have touched.

**The palettes are the part that does not translate one for one.** SFF v1 has no
palette table: a sprite either stores a palette or carries `palletSame`, meaning
the last one stored. `mtools.txt` offers "Individual palette", "Shared palette"
— "all sprites will use the palette data of the first sprite in the .sff file" —
and a per-sprite override, "2. Use previous sprite's palette". The first and
third readings disagree exactly once in this archive:
`chars/rinfa/rinfa_SFF.txt` asks for a shared palette and then overrides
(9000,0) and (9000,1) back to individual, so "the first sprite's" and "the last
one stored" are different palettes for the 408 sprites after them. The container
settles it — SFF v1 cannot say "sprite 0's palette", only "the previous one" —
so the conversion follows the last palette kept.

A kept palette becomes a `[Pal]` line only where some other sprite draws through
it; one nobody shares from is `sprite.usepal = -1`, "add and use self's pal
(autopal)", which is what "all sprites will keep their own palette data" is in
`sprmake2`'s vocabulary. It is the difference between one line and 1,039 for
`CLARENS/PCX_DEF.TXT`.

**The corpus.** 28 files in this archive match the shape of a transcript, of
which **18 are real ones** — 11 distinct, the rest byte-identical copies — and
ten are documentation that matches because it *quotes* a transcript, eight of
them copies of `mtools.txt` itself. The 18 hold 9,245 sprite entries between
them, **2,801** once the copies are counted once, and all 18 convert with no
read-back problems. The ten come out with warnings naming the lines that are not
numbers, and two sprites between them, which is the answer for a file that is
not a transcript. Outside the archive there are none.

| transcript | entries | palettes kept | `[Pal]` lines |
|---|---:|---:|---:|
| `CLARENS/PCX_DEF.TXT` | 1,039 | 1,039 | 0 |
| `chars/sonson/SonSon.txt` | 989 | 2 | 1 |
| `chars/rinfa/rinfa_SFF.txt` | 410 | 110 | 1 |
| `chars/neoseph/work/sprite.txt` | 179 | 179 | 0 |
| `Utilidades/.../staticfx.txt` | 83 | 83 | 0 |
| `chars/ken/ken.txt` | 64 | 64 | 0 |
| five `Utilidades/CUSTOM/WORK` scripts | 37 | 37 | 0 |

The image names are carried across untouched: `sprmaker` read 256-colour `.pcx`
and `sprmake2` reads 8-bit `.png`, and neither tool converts one into the other.
Nor does this one — but `sffdef` reads a source image by its signature and not
its extension, so a converted `.def` builds from the `.pcx` files the transcript
named.

**And six of them build.** The `Mugen 1000/Utilidades/CUSTOM` tree is the only
place in this archive where a transcript still sits beside the art it names, so
its six scripts go the whole way — `.txt` to `.def` to `.sff`, on 2001-vintage
`.pcx` files — and all 120 sprites come back at the size and axis the transcript
gave them:

| transcript | sprites | images read | `.sff` |
|---|---:|---:|---:|
| `WORK/SYSTEM/select.txt` | 5 | 5 | 5,671 |
| `WORK/FIGHT/fight.txt` | 13 | 12 | 10,562 |
| `WORK/STATICFX/staticfx.txt` | 83 | 83 | 144,340 |
| `WORK/SYSTEM/selectbg.txt` | 14 | 14 | 61,607 |
| `WORK/SYSTEM/system.txt` | 3 | 3 | 29,808 |
| `WORK/STAGES/STAGE0/stage0.txt` | 2 | 2 | 4,202 |

`fight.txt` reads twelve files for thirteen sprites because two of its entries
name the same `.pcx`, and the second is stored as a link — which is
`sprmaker -f`, "eliminate duplicate files", arriving by a different road.

### What a build can lose, and what it says about it

An SFF v2.01 sprite stored as format 11 or 12 is a whole PNG, and a PNG has no
palette ceiling. A build that writes one now keeps every colour the artist's
file had:

    truecolour   28  (more than 255 colours, kept whole in an embedded PNG)
    colours kept 1182897 pixels checked against the source, all of them

The second line is a check, not a boast: the size and axis checks this command
already made compare *indices*, and a truecolour sprite's indices are ones the
reader invents from whatever colours it finds — so they agree whether or not
the colours in between survived. That is exactly how every build here used to
quantise every sprite it stored and still verify clean. The five generated
characters together are 12,076,385 pixels, all of them the colour they went in
as.

Until `sffw::SpriteEntry` could carry RGBA, those five reported this instead:

    quantised    28  (more than 255 colours; mean error 3.045 per pixel, and
                      28 kept as an embedded PNG)

— 3.045, 5.848, 7.030, 7.544 and 6.460 mean error per pixel for Spark, Ferrum,
Sabi, Elara and Arroyo, because the only route into the encoder went through a
256-entry table. Keeping the colours costs bytes and the report says so: Spark
599,538 bytes became 1,435,770, Arroyo 2,711,162 became 7,038,850. A full-colour
PNG is bigger than a 255-colour one, which is what those colours weigh.

`quantised` and its mean error are still printed, for a build that really is
quantised — which now means an SFF **v1** build, since that container holds an
8bpp PCX and no other storage format. `oxtool sprites --quantise` above is where
the quantiser doing that work was chosen; its corpus-wide figure is 3.0235, and
that is the number to compare a future quantiser against.

`--v1` writes WinMUGEN's container instead of 2.01, which is what 16,738 of this
archive's 16,784 sprite files are. `--dry-run` builds and reports without
writing. Writing refuses to overwrite an existing file without `--force`: a
sprite file is a character's whole appearance and this is not a repair tool, so
`oxtool revert` does not cover it.

## sprlinks

    oxtool sprlinks <game-root> [--apply] [--only TEXT] [--show N]

Finds sprites stored as a link to a sprite that cannot be copied, and repairs
the ones whose target the manual names.

An SFF stores a repeated sprite as a *link*: a header with a zero-length payload
and the index of the sprite to copy. 596,256 of this archive's 8,131,101 sprites
are one, and **98 name a sprite that cannot be copied** — 50 name themselves and
48 name a later index. MUGEN fills its sprite array in order, so neither
resolves. Counting the sprites that link *into* one of those 98 as well, **154
sprites in this archive will not decode**; `oxtool sprites --roundtrip` reports
98 of them, because it copies a resolvable link across as a link without ever
decoding it.

### What could not be proved, and what could

Nothing recovers the integer the author's tool meant to write. Two readings were
tried and rejected:

* **"a self-link means the sprite before it"** — it fits `chars/bloo/kfm.sff`
  exactly and nothing else, because `chars/Majin Vegeta SSJ6/majinssj6.sff`
  links *forward* by thirteen places.
* **"the link field is off by one"** — measured false over the archive's 596,151
  zero-length subfiles: the 0-based reading finds a real sprite where the
  1-based reading finds another link 162,433 times, against 2,923 the other way.

What *can* be recovered is which picture the sprite has to hold, and for 65 of
the 98 the manual states it.
`mugen_docs/elecbyte.com/mugendocs-11b1/spr.html` lists the required sprites, and
forty of its rows give a **frame** where the others give a description: sprite
`5011,0`'s row reads "Frame 5010,0", axis "Midsection", and `5012,0`'s reads
"Frame 5010,0", axis "Head". One drawing, three axes — which is what a link is
for. `sprlinks` points a broken link on one of those forty rows at the nearest
earlier sprite in its own file holding that frame.

The roster's vote on the same table, over every link whose `group,image` is one
of the forty rows and whose frame is somewhere earlier in its own file:

| where the link lands | links |
|---|---:|
| the nearest earlier copy of the manual's frame | 215,747 |
| a chain that resolves to that same sprite | 67,936 |
| a different sprite holding the same payload bytes | 1,899 |
| a chain that does not resolve at all | 79 |
| **a genuinely different picture** | **14,419** |
| total | 300,080 |

95.2% of a thousand authors link these sprites where the manual says they are,
and **4.8% do not**. That is real counter-evidence and it is printed here rather
than buried: it does not make the repair a guess — the manual defines what
`5031,20` is, a sprite that draws nothing is not that — but the 14,419 are why
nothing outside those forty rows is touched.

### The guard that earns itself

One more thing has to agree. If a file's links are wrong because its list
shifted — sprites deleted and the links never renumbered — every broken link in
it is wrong by the *same* amount, so `link - target` is one number for the whole
file. It is checked, and it holds:

| file | repairable links | `link - target` |
|---|---:|---:|
| `chars/bloo/kfm.sff` | 15 | 1, all fifteen |
| `chars/Majin Vegeta SSJ6/majinssj6.sff` | 16 | 13, all sixteen |
| `chars/kikyo/kikyo2.sff` | 1 | 2 — one link, so nothing corroborates it |

Two independent derivations agreeing sixteen times out of sixteen is the
difference between this and a hopeful rule. A file whose offsets disagree is
refused **whole**, including the links that looked fine: a disagreement means at
least one target is wrong and nothing says which.

### What it comes to

```
$ oxtool sprlinks .
files        16786 scanned, 22 with a broken sprite link
broken links 98
  repairable 65  (the manual names the frame, the file holds it, and the
                  patched file decodes)
  refused    33  (nothing to point them at)
          25  the manual does not say what this sprite is
           8  the manual's frame is not in this file
sprites that will not decode  154  (98 broken links and 56 sprites that link
                                    into one), and 41 after this repair
```

The 33 stay broken and say why. `chars/bloo/kfm.sff` 73 is `(5000,0)` — a base
frame, which the manual *describes* rather than equates to anything.
`chars/kurihan/Kurihan.sff` 161 is `(225,2)`, a group the manual does not
mention. `chars/Rayquaza/Rayquaza.sff` is 544 bytes, a header and one empty
subfile with no earlier sprite of any kind. Only one of the 22 files is on the
live roster: `chars/kikyo/kikyo2.sff`, whose one broken link costs it five
sprites and is repairable.

Repairing writes **two bytes per link**, in place, at that sprite's own link
field — `node + 16` in an SFF v1's subfile header, `node + 12` in a v2's sprite
node. Re-encoding the file through `sffw` would have been less code and would
have rewritten every PCX in somebody's character to move two bytes. Before
anything reaches the disk the patched bytes are opened again: every sprite that
failed must decode and none that decoded may have stopped, or the file is
refused. `--apply` keeps the original beside it as `*.sprlinks-backup`, written
once and never overwritten, and `oxtool revert` puts it back.

## netcheck

Runs two rollback peers over a simulated lossy link using real characters and
compares their final state. See [NETPLAY.md](NETPLAY.md).

## netudp

The same convergence check as `netcheck`, but over a real UDP socket between two
processes rather than a simulated in-process link — the proof that the rollback
transport survives an actual network stack, not only a modelled one. One side
runs `--host`, the other `--join <addr>`; both replay the same inputs and must
end on an identical checksum. See [NETPLAY.md](NETPLAY.md).

## byoc-netudp

The bring-your-own-characters data path over a real UDP socket. One side runs
`--host --host-pick <char>`, the other `--join <addr> --join-pick <char>`; the
joiner starts without the host's pick, fetches it over the connection, verifies it
by content hash, mounts it and reaches an agreed setup — the proof that a missing
fighter is delivered and played across two separate processes (and, in testing,
two separate machines of different CPU architectures). Prints whether the sides
agreed and what the joiner mounted. See [BYOC.md](BYOC.md).

## balance

Measures the roster's damage and life spread and writes a balance table. See
[BALANCE.md](BALANCE.md).

## frame, select, dump

Rendering, for verification and for screenshots.

```bash
# One simulated frame of a real match, with collision boxes
oxtool frame . chars/ryu/ryu.def --vs chars/kfm/kfm.def --tick 60 --boxes --out fight.png

# The select screen, filtered
oxtool select . --filter ryu --scale 2 --out select.png

# One sprite, straight out of an SFF
oxtool dump . chars/kfm/kfm.def 0 0 stand.png
oxtool dump . stages/2002china3.sff 1 0 bg.png
```

`dump` accepts a character `.def` or an `.sff` directly; the latter is how the
sprite pipeline was verified byte-for-byte against an independent decoder.

## splash

Renders the splash screen without launching the game, which is how to check a
candidate background before shipping it.

```bash
oxtool splash --image art/cover.jpg --width 1920 --height 1080 --out preview.png
```

With no `--image` it draws the built-in backdrop.

## Verifying the window itself

`oxyde --selftest <n>` opens a real window, presents `n` frames and exits,
reporting how many frames were presented and how many were skipped. Paired with
`--shot` it captures what was on screen. This is how the windowed path is
checked on a machine with no display:

```bash
Xvfb :99 -screen 0 1280x720x24 &
DISPLAY=:99 oxyde --root . --selftest 600 --shot window.png
```

Combined with `xdotool`, it drives the whole game — title, character select,
and a match — with synthetic keyboard events that are indistinguishable from a
physical keyboard.

## Looking at one stage

`oxyde --stage <name>` pins every match to the stage whose filename or `[Info]
name` contains that text, so a fault that only shows on one venue out of a
hundred and seventy-nine can be reproduced on purpose rather than waited for:

```bash
oxyde --root . --headless --width 1920 --height 1080 \
      --p1 chars/ryu/ryu.def --p2 chars/kfm/kfm.def \
      --stage venezula --frames 400 --shot venezula.png
```

Four hundred frames is about where the entrance and the round call have
finished and the fight is under way. Nothing matching leaves the rotation
alone and says so.

## Checking a controller

`oxyde --pads` needs no game data at all: it lists what is attached and prints
which engine input each press drove. See **When a pad misbehaves** in
[CONFIGURATION.md](CONFIGURATION.md).

## compat

Which MUGEN release every piece of content belongs to, and whether it loads.

```
$ oxtool compat . --stages
  era         years       characters  loaded  examples
  DOS MUGEN   1999-2001       844     844  chars/!Ilu/!ilu.def, ...
  WinMUGEN    2002-2004       198     198  chars/0Marvin/0Marvin.def, ...
  MUGEN 1.0   2009              9       9  chars/Arroyo/Arroyo.def, ...
  MUGEN 1.1   2011              0       -  none in this archive - untested, not "supported"

  classified by
  DOS MUGEN   169 SFF v1, no version declared; 675 dated before WinMUGEN
  WinMUGEN    198 dated 2002 or later
  MUGEN 1.0   1 SFF v2; 2 declares localcoord; 6 declares 1.0
```

"Compatible with four releases" is easy to write and hard to mean: they share
most of their formats, so a feature table says very little. This classifies by
what the files actually *use* — declared version first, then SFF version,
embedded PNG and `localcoord`, later wins — loads each one, and prints the two
numbers together. An era with no content in it is reported as **untested**
rather than as supported, because a claim nobody has exercised is not evidence.

The `classified by` block is there so a number nobody expected can be traced to
the signal that produced it instead of argued about.

---

## mods

Loads every Lua mod and calls every hook it defines, with the same payloads the
engine sends.

```
$ oxtool mods . --verbose
mods
  ironman
  scoreboard
  turtle

modes declared  2
  ironman        base survival     SURVIVAL WITH NO RECOVERY BETWEEN BOUTS
  tower          its own screens   CLIMB IT WITH WHOEVER YOU ARE GIVEN

screens  declared by mode "tower", over three bouts
   1. (the engine deals a fighter)
   2. interlude "THE TOWER" (4s)
   3. interlude "FLOOR {bout}" (2s)
   4. vs
   5. fight
   6. (the next opponent is chosen)
   ...

ai  exercising 120 frames
  answered 120/120 frames

flow  answered Map({"next": Str("gameover")})
hud   484 overlay item(s) over 180 frames  (frame, rect, text)

no problems
```

Every hook is asked about **every mode a mod declared**, not only the first:
a hook that answers for one mode and declines for another is the ordinary
shape of a mod, and probing one of them reports the others as silent.

A declared screen sequence is *walked* rather than described, and the walk is
built from the same two functions the engine queues from — so a sequence that
reads one way here cannot play another way in the game.

A mod that fails inside the engine is a line in a log the player may never look
at, and the failure latches the mod off for the session. That is right at run
time and a terrible way to *write* a mod. Loads mods whether or not
`[Options] mods = 1` is set: checking one you have not switched on yet is the
normal case.

---

## gpu

What hardware is here, and what each post-processing shader does to a frame.

```
$ oxtool gpu . --out shots/
adapters
  fastest   NVIDIA A2 (DiscreteGpu, Vulkan, NVIDIA)
  software  llvmpipe (LLVM 20.1.2, 128 bits) (Cpu, Vulkan, llvmpipe)

source     320x240  ->  800x600 (2.50x)
shaders
  nearest     86.7% painted   88.22 ms  shots/nearest.png
  sharp       88.6% painted   27.83 ms  shots/sharp.png
  crt         81.6% painted   34.66 ms  shots/crt.png
```

Two jobs. A player whose `renderer = gpu` quietly did nothing needs to know
whether an adapter was found and why it was declined; and a shader is not a
thing you can assert about in words — the only honest way to show what
sharp-bilinear does is a picture of the same frame with and without it. The
scale is deliberately fractional: at a whole multiple every filter agrees.

`--model x.glb` loads a glTF backdrop instead and photographs that.
`--software` forces Mesa's `llvmpipe`, so a result depends on Mesa rather than
on whichever driver the machine happens to have.

---

## shot

Any of the game's own screens, rendered headlessly through the real `Game`.

```
$ oxtool shot . fight --scale 2 --out fight.png
wrote fight.png (640x480)
  screen      fight
  painted     300934/307200 pixels (98.0%)
```

`title`, `team`, `select`, `versus`, `fight`, `interlude`, `movelist`,
`options`, `replays`. `movelist` opens the page and **waits for the frame data
to be measured** before it photographs it, and `--cpu` puts the computer on
both sides so that readouts which need something to have happened — the frame
meter, the combo counter — have something to show. `--mode` takes a mode a mod declared as well as a built-in one, so
`shot . interlude --mode tower` plays a declared run far enough to photograph
the screen it puts on first.

`frame` renders a *fight* and `select` builds the grid by hand; neither can show the
title, the team menu or the versus screen — which are the screens a screenpack
is mostly made of, and "the pack lays this out and the engine ignores it" is
exactly the fault nobody notices without a picture.

The painted-pixel count is the point: a screen that "renders" and is empty is
what this exists to catch, and a byte count on a PNG does not distinguish it
from a dark background.

`--stage NAME` picks a stage, `--gpu` turns on the hardware path so a 3D
backdrop draws, `--side 1` photographs player two's half of the team menu.

---

## video

What is inside a `.webm`, and what a given tick would show.

```
$ oxtool video video/ik_logo.webm --tick 45 --out frame.png
  codec      V_VP9
  size       1280x720
  blocks     240
  duration   4.00s at 60.0 fps

  into 320x240:
    fit         320.0x180.0  at    0.0,30.0
    zoomfill    426.7x240.0  at  -53.3,0.0
```

A video background's failure mode is silent: the stage draws, the fight plays,
and the backdrop is black. This opens the file the engine would open and writes
the frame the engine would be showing.

## replay video

A replay played headlessly into a video file — the command-line half of
converting a `.oxr` replay to MP4; and
the REPLAYS screen's **EXPORT VIDEO** and the result screen's **SAVE VIDEO** are
the same exporter on a background thread (see [MODES.md](MODES.md#replays)).

```
$ oxtool replay video replays/2026-10-13_1357_versus_kfm-vs-kfm.oxr --root . --size 1280x720
replay   replays/2026-10-13_1357_versus_kfm-vs-kfm.oxr
  Kung Fu Man vs Kung Fu Man  -  VERSUS  -  3:14  (11640 frames)
video    videos/2026-10-13_1357_versus_kung-fu-man-vs-kung-fu-man.webm  1280x720  AV1 + Opus / WebM, quality medium
wrote    ...  (92.9 MB)
  frames   11880 written of 11880 played (from frame 0), 198.0 s of video
  streams  video 88.75 MB (3586 kb/s), audio 4.04 MB (163 kb/s)
  speed    36.8 frames/s (0.61x real time) - 322.6 s wall: simulate 2.2 s, draw 123.1 s, waiting on the encoder 177.6 s
  replay   reproduced exactly (end checksum matches)
  check    frame      0 decoded back: PSNR 34.7 dB (4:2:0 alone 38.2) - matches the render
  check    frame   5818 decoded back: PSNR 31.2 dB (4:2:0 alone 36.6) - matches the render
  check    frame  11636 decoded back: PSNR 31.3 dB (4:2:0 alone 36.7) - matches the render
```

**How it works.** The configuration is the one the game would load from that
root (`mugen.cfg`, then `oxyde.cfg`, Knuckle Up's file, the balance table); the
tape is handed over exactly as the REPLAYS screen hands it over; then every
tick the game advances one frame, its sound requests and music go through the
same `SoundPump` the window loop uses into an offline mixer that renders exactly
one tick of 48 kHz audio (800 samples), and the frame is drawn by the software
renderer at the export size. Nothing reads a clock, so picture and sound cannot
drift. The playback line ("REPLAY - 1:23 LEFT") is not drawn into the video;
`--no-hud` leaves the life bars out too.

**Proving it matches.** Two checks, both printed:

* the tape's **end checksum**. Playback runs to the end of the tape even when
  only a slice is written, so the game's own verdict is reached. A tape that no
  longer reproduces on this build still exports — the video is what this build
  plays — and says `WARNING: the tape does not reproduce on this build`. A tape
  recorded against an earlier roster can do exactly that; a tape recorded on
  this build reproduces. `--quick` stops at `--to` and skips the verdict.
* **frames decoded back** out of the finished file (AV1 by `oxyde-video`, GIF by
  the `gif` crate, H.264 by the ffmpeg that wrote it) and compared with the frame
  as rendered. Each line gives the PSNR and, beside it, the PSNR of the same
  frame put through 4:2:0 and back with no codec at all — the best any 4:2:0
  file can do, and on busy pixel art only 33–38 dB. A wrong frame, wrong colours
  or a garbled picture land far under the 25 dB floor and fail the command.
  `--check-dir D` writes each checked frame twice, `<n>_game.png` and
  `<n>_video.png`.

**Range.** `--from 12:30 --to 13:10`, `--last 60` (seconds, `m:ss` or
`h:mm:ss`, counted from the first frame of playback). Everything before the
range is still simulated — it has to be, the match is deterministic from frame
0 — but not drawn or encoded, which is why a minute from the end of a 43-minute
run costs three minutes rather than an hour and a half.

**Codecs, and why.**

| `--codec` | file | needs | |
|---|---|---|---|
| `av1` | `.webm`: AV1 + Opus | nothing — built in, pure Rust | rav1e and opus-pure, muxed by a small built-in Matroska writer. Royalty-free; plays in every browser, VLC, mpv, and on Windows with the free AV1 extension. The default without ffmpeg, and the only video codec in the public engine-only release. |
| `h264` | `.mp4`: H.264 + AAC | an `ffmpeg` beside the game, in the game root or on `PATH` | Frames are piped to ffmpeg's `libx264` (`veryfast`), the mixed audio written to a temporary `.wav` and muxed as AAC at the end. Plays everywhere. **H.264 and AAC are patent-licensed**, which is why the engine never contains an encoder for either: you get them only through an ffmpeg you installed yourself. The default when one is found. |
| `gif` | `.gif` | nothing | No sound, every second frame (delays 3,3,4 hundredths: exactly 30 fps), its own palette per frame. 640x360 unless `--size` says otherwise. For a few seconds to paste into a chat. |

The extension of `--out` picks the codec when `--codec` does not. Colour is
BT.601 limited range and is signalled as such in the file, so every player that
honours the signal (all of the above) shows the right colours, and Oxyde's own
video decoder — which plays stage backdrops with the 601 matrix — decodes an
exported clip back to what was rendered.

**AV1 settings.** rav1e is the only pure-Rust AV1 encoder and it is not fast:
3.9 frames/s at 720p on one thread, and its own tile threading only reached
7.0 frames/s on eight (`examples/ebench.rs`). So the exporter cuts the video
into one-second segments, each opening on a key frame, and encodes them in
parallel on single-threaded encoders — that scales with cores, and the bitstream
is identical whatever the thread count. Speed preset 10, low-latency coding, one
frame of lookahead, no scene detection and no CDEF: together twice the
throughput of the preset alone. `--quality` sets a constant quantizer: `high` 80,
`medium` 120 (default), `small` 170 (`--quantizer`, `--speed`, `--tiles` and
`--threads` override). `--features video-asm` builds rav1e's assembly, about
twice as fast again (4.5 against 2.1 frames/s on one thread, 22 against 12 on
eight, on a loaded machine); it needs `nasm`, so it is off by default like
`oxyde-video`'s `av1-asm`.

**Measured** (AV1, quality `medium`, `video-asm` build; this machine is a
shared 12-core box and the load average while these ran was 10–25, so an idle
machine does better — the sample below ran at load 0.6):

| tape | size | frames | speed | video bitrate | file |
|---|---|---|---|---|---|
| Versus, kfm vs kfm, 3:14, recorded on this build | 1280x720 | 11,880 | 36.8 fps (0.61x real time) | 3.6 Mb/s | 92.9 MB |
| the same | 1920x1080 | 11,880 | 13.7 fps (0.23x) | 6.2 Mb/s | 156.9 MB |
| the same, 0:20–0:26 as `gif` | 640x360 | 360 | 40.5 fps | — | 31.5 MB |
| Knuckle Up `last-run.oxr`, first 2:00 (rain, crowds) | 1280x720 | 7,200 | 16.0 fps | 9.8 Mb/s | 149 MB |
| the same | 960x720 | 7,200 | 24.8 fps | 7.6 Mb/s | 117 MB |
| the same, before the 1080p tile fix | 1920x1080 | 7,200 | 4.1 fps | 16.2 Mb/s | 246 MB |
| `last-run.oxr`, last 60 s of 42:50, load 0.6 | 1280x720 | 154,243 played, 3,600 written | 182 s in all: 47 s simulating the whole run, 26.7 fps drawing and encoding | 4.1 Mb/s | 32.3 MB |

The tape holds 11,640 frames and playback 11,880: the versus screen and the
round call come first, and they are in the video. A GIF is big — 5 MB a second
at 640x360 — because every frame is a whole new picture; keep it to a few
seconds, or give `--size 480x270`.

Simulation alone runs at about 3,300 frames/s, so a 43-minute tape is under a
minute of simulating; the drawing (11–40 ms a frame at 720p–1080p, single
threaded) and the encoder are the cost. Exporting all 42:50 of `last-run.oxr`
at 720p is therefore 154,243 frames at 16–37 fps: **about 70 minutes to 2.7
hours** on this machine depending on its load and the content, and roughly
4–6 GB at 3.6–9.8 Mb/s — `--last`, `--from`/`--to` or `--quality small` are
the practical choices for a run that long. With ffmpeg, x264 `veryfast` is far
faster than rav1e and the drawing becomes the limit.

---

## corrode

A corrosion client with no window and no content.

```
$ oxtool corrode 127.0.0.1:7411 --frames 180 --hold 400 --out shot.png
  128 frame(s) painted in 3.8s, 0 repair(s)
  picture    640x480
  painted    90.6% of the frame
```

The real client needs a display, which makes the one thing worth testing — does
a machine with none of the content see the game? — the one thing that cannot be
tested headlessly. `--hold 400` is START; held against a host on the title
screen it produces a picture of the select grid.

---

## info and simulate

`info` summarises one character — sprite, animation, state and command counts,
constants, palettes, load time, and every warning and diagnostic.

`simulate` runs one character (optionally against another) headless and reports
which states were entered and how often, plus any controllers it reached that
are not implemented. Useful for working out why a specific character misbehaves.

`--corner` stands the opponent with their back to the end of the stage, where
the camera has nowhere left to scroll, and puts the fighter `--gap` away from
them. A whole class of fault only exists there — an attack that pushes its own
caster out of its own range is the one this was added for — and none of it
reproduces in the middle of the stage, where the defender simply travels:

```
# A super on a cornered opponent: does it keep connecting?
oxtool simulate . chars/kfm/kfm.def --vs chars/kfm/kfm.def --corner --gap 45 \
  --power 3000 --inputs "150:-,1:D,1:DF,1:F,1:D,1:DF,1:F,1:x,200:-"
```

---

## fuse

Checks a state script, and converts one to [FUSE](FUSE.md).

```
oxtool fuse <file.zss|file.cns|file.fuse> [--out FILE] [--verify]
oxtool fuse <game-root> --roster [--out DIR] [--limit N] [--verify]
```

Checking prints every diagnostic with a line, a column and a caret — the same
ones the engine will give, from the same compiler — followed by anything that
compiles and is still probably wrong:

```
$ oxtool fuse chars/kfm_zss/command.zss
command.zss: zss, 1 states, 37 controllers, 1 functions, 0 errors

$ oxtool fuse chars/kfm_zss/AI.zss
AI.zss: zss, 2 states, 58 controllers, 0 functions, 0 errors

AI.zss: 2 lint(s), 0 of them likely mistakes
  AI.zss:41:6: hint[unused-local]: `inrange` is assigned and never read
  AI.zss:69:6: hint[unused-local]: `jugpt` is assigned and never read
```

Lints are never counted with the errors: everything they flag loads and runs.
`oxtool eval rules` lists all ten and what each means.

A `.cns` or `.zss` file is also converted, to stdout or to `--out`. Consecutive
controllers with identical triggers are collected into one `if`, which is what
the engine already does with them and how a person would have written them:

```fuse
state 200 (type: S, movetype: A, physics: S, anim: 200, ctrl: 0) {
    if AnimElem == 2 {
        HitDef(
            attr: S, NA,
            damage: 23, 0,
            animtype: Light,
        )
    }
    if AnimTime == 0 {
        ChangeState(value: 0, ctrl: 1)
    }
}
```

### --verify

Parses the conversion back and compares it against the original, controller for
controller and parameter for parameter. This is also how FUSE itself is tested:

```
$ oxtool fuse chars/kfm_zss/command.zss --verify
  verified: the conversion compiles to the same controllers
```

### --roster

Converts every character in the archive, which is both a migration and a
regression test over two million controllers:

```
$ oxtool fuse . --roster --out /tmp/corpus
characters converted  1051
states                276563
controllers           2094037
FUSE source           337.5 MB
with errors           80
  of those, the original did not compile either  80
with warnings only    654
```

The second line under *with errors* is the one that matters. A character whose
CNS already had broken triggers produces the same complaint in any language;
what would be a bug is an error the original did not have, and there are none.

---

## The language server

`oxyde-lsp` is a separate binary, not an `oxtool` subcommand, because it speaks
LSP over stdin and stdout rather than printing anything.

```
oxyde-lsp            # an editor runs this; there is nothing to configure
oxyde-lsp --help
```

It serves `.fuse` and `.zss`: diagnostics as you type, completion (controllers
at a statement, that controller's parameters inside its argument list, triggers
and your own names inside an expression), hover, go to definition, a document
outline, and a quick fix for a misspelled name.

Everything it answers comes from the compiler's own tables, so an editor and
the engine cannot disagree. The per-controller parameter lists are counted from
the archive rather than written by hand — no manual lists them all, and the
ones that try disagree with each other. Regenerate them after adding a
controller:

```
cargo run -p oxyde-tool --example params
```

---

## eval

Turns the archive into a graded benchmark for anything that writes
[FUSE](FUSE.md) — a person, a script, or a model.

```
oxtool eval build <game-root> --out DIR [--limit N] [--tasks N] [--seed N]
oxtool eval baseline <DIR> --kind empty|copy|retrieve [--out FILE]
oxtool eval score <DIR> <completions.jsonl> [--show N] [--csv FILE]
oxtool eval rules
```

### build

```
$ oxtool eval build . --out bench
train characters      946   (182.2 MB)
test characters       105   (18.6 MB)
duplicate files dropped     (136.8 MB — mostly `stcommon`)
tasks                 2000
  (dropped 10 whose own reference does not compile)
  body                666
  guard               667
  params              667
```

The split is by **character**, hashed rather than shuffled, so it is identical
on every machine. `stcommon` is written once rather than a thousand times and
is never cut into tasks — it is the engine's shared file, it is in both halves,
and grading a model on it would be grading it on what it was trained on.

Each task is a window of whole states around a cut, so one line of
`tasks.jsonl` is self-contained and compiles on its own:

```json
{"id":"…#3#207","kind":"body","source":"chars/kfm/kfm.def",
 "prompt":"state 200 (type: S, movetype: A, anim: 200) {\n",
 "reference":"    if AnimElem == 2 {\n        HitDef(…)\n    }\n",
 "suffix":"}\n"}
```

### score

```
$ oxtool eval score bench answers.jsonl
2000 tasks, 2000 answered

  kind        tasks            valid            clean          correct
  body          666      664   99.7%      620   93.1%        9    1.4%
  guard         667      667  100.0%      663   99.4%       45    6.7%
  params        667      542   81.3%      510   76.5%       11    1.6%
  ------------------------------------------------------------------
  all          2000     1873   93.7%     1793   89.7%       65    3.2%

  lints introduced        150
```

**valid** compiles. **clean** introduces no lint the original did not have.
**correct** compiles to the same bytecode as the original — every controller,
guard, loop bound and parameter.

Answering the original file's own text scores exactly 100%, which is the
benchmark's sanity check on itself.

### baseline

Three trivial answers, so a real score has a floor under it:

| | valid | clean | correct |
|---|---:|---:|---:|
| `empty` — answer nothing | 100.0% | 96.5% | 1.4% |
| `copy` — repeat the block above | 33.5% | 24.4% | 0.3% |
| `retrieve` — nearest neighbour in `train/` | 93.8% | 89.8% | **3.2%** |

`retrieve` is the one to beat. Note that `empty` scores 100% valid — an empty
state body compiles — which is why `valid` is a floor and not a bar.

---

## What `troubleshoot` can and cannot explain

`oxtool troubleshoot` turns a *symptom* the gate reported into a *cause* read
out of the character's own files. It is worth knowing how often it can, because
the honest answer is "about a third of the time", and the reason is more
interesting than the number.

### How the measurement was made

Four gate sweeps of the roster were unioned, every non-`ACCEPT` verdict taken,
and its `why` text fed back as `--symptom`. That is 178 real (character,
symptom) pairs across 164 characters — not invented cases.

Two things had to be got right before the numbers meant anything, both of which
this project has been burned by before:

- **The root.** 136 of the 178 characters live under a separate roster root
  (`<game-root>/`), not `chars/`. Run against the wrong root, the engine cannot find the files at
  all, and *"cannot load"* is indistinguishable from *"completely broken"*
  unless you look. An earlier sweep reported `REFUSE` at 0% for an entire
  collection this way.
- **The case.** MUGEN authors ship `.def`, `.DEF` and `.Def` interchangeably.
  A case-sensitive lookup dropped 6 more characters here, and 244 in an
  earlier pass.

### The result

| symptom | cases | cause named |
|---|---:|---:|
| it froze — stopped responding mid-match | 8 | 100% |
| it never took damage — unkillable | 34 | 97% |
| it declares no special moves at all | 23 | 83% |
| not one of its attacks connected | 24 | 71% |
| it never dealt damage | 34 | 50% |
| it only ever entered N distinct states | 95 | 26% |
| it cannot block | 18 | 22% |
| it left the playfield and did not come back | 6 | 17% |
| its specials come out but none of them connect | 13 | **0%** |

### Why the 0% row is not a bug to fix

The obvious reading is that `troubleshoot` is missing a check. Two were added
on that assumption — a per-animation `Clsn1` check (the character has attack
boxes, but not on the frames its specials play) and a `hitflag` check (every
HitDef flagged air-only, so a standing opponent is never a legal target). They
are correct and they stay. Together they explained **one** more case.

So the assumption was wrong, and looking at the actual characters says why.
They are Big Bear, Athena, Birdie, Clark2 — well-made, widely used characters.
Big Bear's state 3000 is `attr = S,HP`: a super that spawns a Helper, entered
by `F, D, DB, F, A+Y`. `oxtool moves --try` reports it `NOT REACHED` at 25, 40
and 60 units and reached only at the default ladder, where it then whiffed with
the fighters 100 units apart.

That is not a defect in the character. It is the harness. The gate's
`specials_connect` figure comes from `probe_specials`, which tried each special
from exactly **two** distances, 60 and 150 world units. A command throw is not
a legal hit at 60 units, so a character whose specials are throws whiffs at
both rungs and the verdict describes the probe rather than the character.

A third rung at 30 units was added. The probe keeps the best result across
rungs, so an extra one can only turn a false negative into a hit — it cannot
cost a result that already worked. Re-gating all thirteen characters carrying this
symptom moved **2 of them (Kodachi, shiki tohno) from WARN to ACCEPT**, with
one special now connecting, and changed nothing else.

The other 11 stay. `oxtool moves --try` shows why for Big Bear: state 3000 is
`NOT REACHED` at 25, 40 and 60 units and reached only from further away, where
it then whiffs with the fighters 100 units apart. The motion needs room the
close rung does not give it. **So "specials come out but none connect" still
carries a harness-dependent false-negative rate, and a verdict built on it
should be read with that in mind.**

`troubleshoot` naming no cause here is therefore the correct behaviour, not a
gap: there is no cause in the character's files, because the character is fine.
The module's rule — *a symptom whose cause none of the checks can establish is
reported as exactly that* — is what keeps a confident wrong answer out of the
results.

**The transferable lesson:** a coverage number you are trying to raise will
happily be raised by a check that guesses. Before adding one, look at the
cases it would fire on and ask whether they are actually broken. Here they
were not, and the low number is the truthful one.

## Why specials do not hit: what the roster actually says

"Its specials come out but none of them connect" reads like a geometry
problem. Measured across the 245-character quarantine, it mostly is not.

| cause | characters | repair |
|---|---:|---|
| the `.def` points at a file that is not there | **most of them** | `oxtool defrefs --repair` |
| no `HitDef` in an attacking state | 8 of 49 | `oxtool complete --apply` |
| no `Clsn1` on the attack's animation | 72 offered, **1 verified** | `oxtool normalize --apply` |
| HitDef and boxes both present | 41 of 49 | nothing mechanical |

The order matters. 41 of the 49 characters that could not hit **already had a
HitDef in every attacking state**, and 71 of the 72 generated attack boxes were
reverted because re-fighting showed no improvement — an auto-generated box is a
guess about where a blow lands, and the verifier rejecting guesses is the
system working, not failing.

What was actually wrong was upstream of all of it. `oxtool moves` on jax
printed `0 commands, 0 moves` with `jaxcmd.txt` sitting in the folder, because
the `.def` said `cmd = jaxcmd.txt.fuse` — a file the conversion never wrote.
Repairing the reference took jax to **51 commands, 12 moves**, and across the
quarantine took `ACCEPT` from **5 to 45**.

**Check that the character is loaded before asking why it does not fight.**

## `oxtool defrefs` — the paths that silently drop a character

Two different files can point at a character that is not there, and neither
failure prints anything.

**Inside a `.def`.** `cmd = jaxcmd.txt.fuse` when only `jaxcmd.txt` exists. The
engine loads nothing for that slot, so the character has no commands, no button
does anything, and it reads as *broken* rather than *misconfigured*.

**Inside `select.def`.** A bare roster name `foo` resolves as
`chars/foo/foo.def`. A character unpacked one folder deeper is not at that
path, so the entry resolves to nothing and the character vanishes from the
select screen. chester is the standing example, at
`chars/chester/chester/chester.def`; a rebuild that emitted `chester` removed a
working character from a 1,051-entry roster and looked entirely correct doing
it.

```sh
oxtool defrefs .                 # report both kinds
oxtool defrefs . --repair        # repoint X.fuse at X, where X really exists
```

`--repair` only ever does one thing, and only where it can prove it: a
reference to `X.fuse` that does not resolve is pointed at `X` when `X` is
really there. Nothing is invented, nothing is deleted, and each `.def` is
backed up. A reference with no original beside it is reported and left alone.

`tools_build_select.py` now emits the resolving path whenever the `.def` is not
at `chars/<name>/<name>.def`, and preserves each character's stage and music
across the change of entry form.

## A conversion must not alter the instrument that judges it

`fuseify` converted `chars/kfm/kfm.def` along with everything else — and that
is the character `gate` and `audit` fight everyone against. The before sweep
and the after sweep were therefore measured against two different opponents.

It reported `kim jae hoon` as degraded, *"it stopped taking damage"*, when the
character's folder was byte-identical to the original. Holding the opponent
fixed, the same conversion degraded **0 of 111**.

`fuseify` now excludes `audit::STANDARD_OPPONENT` and says so. The effect is
real but rare — re-measuring twelve characters against the converted and the
unconverted kfm gave identical results — which is exactly what makes it
dangerous: it is invisible until it is not.

## `oxtool inventory` — what a character is made of

`gate` fights a character and says whether it belongs on a roster.
`troubleshoot` takes a symptom and finds its cause. Neither answers the
question an author starts with: **what is in here?**

```sh
oxtool inventory <root> <char.def> [--tsv]
```

It reports the `[Files]` entries and whether each resolves, the files sitting
in the folder that nothing names, the content counts, and the handful of
numbers that decide whether a character can fight — each flagged against
MUGEN's documented defaults.

Working out why Omega Tom Hanks could not be hit meant reading its `.air` by
hand to find seven `Clsn1` attack boxes and **not one `Clsn2`**, then its
`.cns` for `life = 9999, defence = 999`, then its `.def` to find `cns =`
pointing at a states-only `.fuse`. All three are one-line facts, and they now
print together:

```
  attack boxes  7 of 38 animations
  hurt boxes    0 of 38 animations   <-- nothing can ever hit this character
  life         9999   (default 1000) <-- takes many times the usual punishment to drop
  defence       999   (default 100)  <-- divides incoming damage; at 999 a hit lands a tenth
  size       15 back, 60 tall        <-- the standing sprite is far taller than this;
                                         a box built from it would miss
```

It does not fight the character and it does not guess. Where a line is called
into question it says which fact makes it questionable, so the reader can
disagree.

### Two repairs it led to

**Hurt boxes are measured from the sprite, not only the constants.** A great
many authors never change the size values they inherited from Kung Fu Man.
A box from Omega Tom Hanks' declared 15/13/60 changed nothing; a box from its
standing sprite took it from **REFUSE 79% to WARN 92%**, taking damage, at the
roster mean.

**`normalize` now tries its repairs together after trying them apart.** A
repair judged alone is kept only if it removes a refusal, so one that is a
*prerequisite* for another is thrown away before the second is tried. One
repair at a time is right for attribution and cannot find a fault that only
exists in combination.

**`normalize --rebalance`** additionally offers to bring `life` and `defence`
back to a fightable range. It is off by default and should stay that way for
most work: every other repair here supplies something an author left out, and
this one overrides something they meant. Omega Tom Hanks is a joke boss, and
9999/999 is what its authors intended.

## "Unkillable" needed two readings, not one

`gate` refused a character as *"it never took damage — unkillable"* on the
strength of `card.takes`, which comes from the free-for-all test match. The
audit that computes it says in a comment why that cannot settle the question:

> a free-for-all fight is not proof either way about taking damage: a character
> that dominated it was never hit. The knockdown probe stands them in front of
> an attacking opponent on a quarter of their life, **which is**.

That probe was already running, and already contributing to the score — and
the refusal ignored it. `baldhead` reports **takes damage 0%** and **can be
hurt 100%**, with 109 of its 192 animations carrying hurt boxes and `life` and
`defence` both at the defaults. It was being thrown off the roster for winning
the test match too convincingly.

The refusal now requires both readings to disagree, and `gate --tsv` publishes
`hurt_probe` — because a reader without it repeats the same mistake, as the
first analysis of this very set did.

**Effect on 134 quarantined characters: 52 moved out of `REFUSE`.** The
"cannot get hit" population fell from **55 to 3**.

### What this says about adding repairs

The question that led here was whether `normalize` should gain a function to
make unhittable characters hittable. It should not, because they were not
unhittable. Measuring first:

| candidate repair | characters it would fix |
|---|---:|
| hurt boxes missing entirely | 11 of 1,051 |
| attack boxes missing entirely | 11 of 1,051 |
| `life` above 2,000 | 14 of 1,051 |
| `defence` above 200 | 9 of 1,051 |
| **a verdict reading the wrong measurement** | **52 of 134** |

A repair is worth building when the fault is in the character. Here it was in
the ruler.

## `oxtool revert` — taking a repair back

Every repair in this toolset writes a backup before it writes anything else,
and none of them ever overwrites one: `normalize`, `complete`, `defrefs`,
`fusediff` and `fuseify` all check `backup.exists()` first, so the file beside
a repaired character is that character as it was the first time anybody
touched it. That was always the safety net. What was missing was the thing
that uses it.

There are **3,490 of these files in this archive**, in seven flavours, and
until now the only way back was `find` and a shell loop. That is a reasonable
thing to ask of somebody un-doing one character and an unreasonable one when a
sweep has written states across hundreds.

```
oxtool revert <root> [--kind NAME] [--apply] [--tsv]
```

| kind | written by | reverting gives back |
|---|---|---|
| `complete` | `oxtool complete` | generated HitDefs and generated states |
| `normalize` | `oxtool normalize` | supplied collision boxes, rebalanced life/defence |
| `defrefs` | `oxtool defrefs --repair` | `.def` keys pointed back at files that exist |
| `fusediff` | `oxtool fusediff --repair` | constants restored after a lossy conversion |
| `constants` | `oxtool fusediff` | a `.def` pointed back at its original constants file |
| `sprlinks` | `oxtool sprlinks --apply` | broken sprite links pointed back at the frame the manual names |
| `cns` | `oxtool fuseify` | the CNS original, from before the FUSE conversion |

Over this archive today: 850 files would be put back, 45 already match their
backup, and 2,595 conversion backups are held out of the sweep.

### The conversion backup is not a repair

Five of the six kinds add something to a character. `.cns-backup` does not —
it is the character from before the CNS-to-FUSE conversion, and **three other
tools read its presence in a folder as the fingerprint of a converted
character**: `fuseverify` restores from it, and `inventory` and `dashboard`
both count it. Restoring it changes what those three say about the roster.

That is a legitimate thing to want and a terrible default, so it must be asked
for by name with `--kind cns`. It is the same line `doctor` already draws when
it refuses to run `complete` and `normalize` as part of `--fix`: **a tool may
undo its own work without being asked twice, and may never undo a decision
somebody else made.**

### Three things it is careful about

* **A restore is read back.** The bytes are written, then read again and
  compared to the backup. A short write or a full disk is the one failure that
  would otherwise be reported as a success.
* **The backup is deleted afterwards.** Once the original bytes are back the
  repair is gone, and a backup left beside the file would be a lie in two
  directions — a second `revert` would report work it is not doing, and
  `inventory` and `dashboard` would go on reading the folder as repaired. A
  later repair writes a fresh one, because every writer checks `exists()`
  first and there is now nothing there.
* **A file already identical to its backup is not a restore.** 45 of the 210
  `defrefs` backups are in this state: `--repair` run a second time backs up a
  file it then leaves alone. Counting those as reverts would inflate every
  number the command prints, so they are cleared and reported separately.

A backup no command here writes — this archive has one
`select.def.pre-import-backup` — is counted and named rather than silently
skipped. The point of the command is that nothing is hiding.

## Characters must not be degraded by conversion — the root cause

They were not. The tool measuring them was.

`oxtool migrate` held a single `Vfs` across its whole run: sweep the roster,
convert it, sweep it again. `Vfs` caches one directory listing per directory
and never invalidates on its own — correct for the engine, which indexes its
archive at start-up and never writes to the tree it reads, and a trap for a
tool that does. **Every `.fuse` file the conversion had just written was
invisible through that handle**, and the read failed as `NotFound` rather than
loudly. The characters loaded with no states at all, dealt no damage, and were
reported as *"it stopped dealing damage"*.

| | before the fix | after |
|---|---:|---:|
| characters the conversion touched | 17 | 17 |
| reported degraded | **17** | **0** |

Reproduced down to a single character: `guile` degrades with the stale handle
and is byte-for-byte identical without it — same states, same constants, same
box counts.

**The rule, now in the `Vfs::invalidate` doc and pinned by a test: a tool that
writes into the tree must not read it again through the handle it wrote
behind.**

Why it hid: every symptom pointed at the converter. It was deterministic, it
hit *only* the characters the conversion touched — because only their
directories changed — and each one was healthy when re-measured alone, which
reads as flakiness rather than as the clue it was. The clue was that a fresh
process always disagreed with the batch.

The 17 are now converted and verified in the test roster, ACCEPTing at 88–94%.

## Repeating state cycles — the glitch nothing was looking for

A player reports it as *"it kept crouching over and over, then snapped out of
it"*. Every check passed the character, because the checks were looking for the
wrong shape:

* **`frozen`** counts ticks in **one** state with no control. A fighter
  rotating through two or three states is never still for a moment.
* **the tick-by-tick state list** says nothing, because a state lasts many
  ticks. What shows a circle is the sequence of *transitions*.

`audit` now records the transitions, with consecutive repeats collapsed, and
`longest_cycle` finds the shortest period whose block repeats at least four
times. Single-state periods are excluded — that is `frozen`, already reported,
and counting it twice would call every knocked-down fighter glitched. Three
repeats is a coincidence; four is a pattern.

`gate` reports it as a warning rather than a refusal, because the fighter is
responding and usually does break out:

```
it went round the same 4 states 4 times (0 -> 10 -> 12 -> 1010)
```

`troubleshoot` then names the controller that closes the circle — the
`ChangeState` in the cycle's last state targeting its first:

```
cause  state 1010 sends the character straight back to state 0,
       which closes the loop [0, 10, 12, 1010]
fix    look at [State 1010, 8] in state 1010
```

**On fixing these automatically: it does not, and should not.** A loop is not a
fault by itself — a walk cycle is one — and the edge that closes it is the
author's own logic. What the tools can do honestly is find it, prove it
reproduces, and point at the line. Where the closing edge is computed rather
than a constant, or comes from `[Statedef -1]`, the report says so instead of
guessing.

### How common

15 of the first 240 characters (6.3%) carry a reproducible cycle; Kung Fu Man
carries none, so it is not an artefact of the computer playing both sides.
`0 -> 10 -> 12` is the crouch chain, which is exactly the d-pad-down repeat a
player notices.

## `oxtool simulate --why` — the decisions, not the effects

`--trace` prints the engine's *state* each tick: position, animation, life.
That is the effect. What nobody could see was the **decision** — which
controller the engine looked at, whether its triggers held, and when they did
not, why it was passed over.

Every diagnosis in this project was reconstructed from the outside, and more
than one was reconstructed wrongly.

```sh
oxtool simulate . chars/kfm/kfm.def --ticks 60 --why --why-state -1 \
  --inputs "20:-,1:D,1:DF,1:F,1:x,30:-"
```

```
why: 1920 decision(s) about player one in state -1
       61  fired
     1859  triggers false

  tick   state   controller             kind           outcome
  1      -1      State -1, Smash Kung F ChangeState    triggers false
  1      -1      State -1, Combo condit VarSet         fired
  1      -1      State -1, Fast Kung Fu ChangeState    triggers false
```

`[Statedef -1]` is where a command becomes a move, so that listing is the
direct answer to "why didn't my special come out": every launcher, by its own
label, and whether its trigger held.

Five outcomes are reported — `fired`, `triggers false`, `paused`,
`already fired (persistent = 0)` and `not this tick (persistent = n)` — because
"it didn't run" has five different meanings and they need different fixes.
Consecutive identical decisions are collapsed: a controller skipped for the
same reason on a thousand ticks is one fact.

### Why the buffer is not on the match

A rollback snapshot clones the match several times a frame. A growing `Vec`
inside it would be copied every time, and re-simulating a rolled-back frame
would append the same decisions twice. An observation of a run is not part of
the run's state, so the buffer is thread-local and only a `bool` sits on the
match. A test pins the thing that matters: **recording must not change the
outcome**, RNG included.

## `oxtool complete --absent` — writing the states a character asks for

**943 `ChangeState` references across 338 characters name a state with no
`[Statedef]`** — a third of the roster, and nothing reported one. The author's
own files are stating what is missing.

**265 of them have the animation of the same number already drawn.** That is
the generatable set, and three independent sources describe the state:

* the **animation** gives its length and the frame the attack box sits on;
* the **character's own other attacks** give the damage, timing and spark —
  the same `House` style `complete` already derives;
* a `ChangeState` on `AnimTime = 0` gives it a way out.

```sh
oxtool complete <root> <char.def> --absent            # report
oxtool complete <root> <char.def> --absent --apply    # write, then prove
```

Artwork carrying no attack box becomes a **pose** with `movetype = I`, not an
invented blow — writing a `HitDef` onto artwork the author never drew as a
strike is exactly the kind of guess this project does not make. Rambo's state
7000 is reported as *"no attack box — a pose, not a blow"*.

Every generated state is written with a comment saying it was generated, and
**always has a way out**: a state that could not end would be the very loop
fault the cycle detector exists to find.

### Measured

Applied across 148 candidates: **2 verified** (PhoenixNoir, 4 states; taz, 6),
57 generated and reverted, 89 with nothing rebuildable.

A low pass rate is the expected outcome and not a disappointment. A generated
super that needs meter and a motion will never be exercised by a test fight,
so **"no measurable gain" is not the same as "wrong"** — it is the verifier
declining to certify what it cannot see. The strict rule is kept anyway: a
repair this project cannot prove is a repair it does not keep.

## `oxtool regress` — every character as a regression test

The simulation is deterministic: the same characters, the same seed and the
same inputs produce the same match, tick for tick. That is already relied on
for rollback netplay, replays and spectating. This spends it on a third thing —
**proving an engine change did not quietly alter how 2,400 characters behave.**

```sh
oxtool regress . --record metrics/regression-baseline.tsv   # before
oxtool regress . --check  metrics/regression-baseline.tsv   # after
```

Each character plays two short scenarios from fixed seeds and the runs are
reduced to a single hash. `--check` names everything that moved and exits
non-zero, so a build can use it. A change that was intended is approved by
re-recording. `--threads N` (default 4) fights that many characters at once;
every character is its own match, so the result does not depend on it.

### The fighters have to do something

The first version fought every character against the dummy with nobody
pressing anything and no computer on either side. Both stood still, and **550
of the 1,051** base-archive characters (768 of the 1,438 imports) came out as
the same hash, `6ee7b12208b7b611`: for half the roster the gate proved only
that the character could stand. Now both scenarios are driven by the engine's
own computer player at level 8, seeded like everything else in the
simulation:

* **`cpu-vs-dummy`** — the character, driven, against `kfm` standing still: it
  walks in and lands its attacks.
* **`mirror`** — the character against itself, both sides driven: guarding,
  trading, throws, being hit into its own states, and its own CNS AI where it
  reads `AILevel`.

Each runs the round start properly (`5900`, the entrance, `begin_fight` on the
sweep's rule) and then 600 fight ticks. Every live player is hashed each tick,
helpers and the opponent included.

| | first scheme | now |
|---|---|---|
| base 1,051: distinct fingerprints | 288 | 1,020 |
| base 1,051: largest group sharing one | 550 | 2 |
| imports 1,438: distinct fingerprints | 297 | 1,370 |
| imports 1,438: largest group sharing one | 768 | 4 |
| moved by `damage + 1` on every hit (base / imports) | 1 / 0 | 1,031 / 1,433 |
| moved by gravity 1% stronger (base / imports) | 5 / 1 | 800 / 1,102 |
| wall time, both rosters | ~4 min, one thread | ~2 min, 4 threads |

The characters still sharing a hash are the same code twice — renamed copies
and sprite swaps whose `.cns`/`.cmd` agree, or differ only in sounds, hit
sparks and comments, which the hash leaves out on purpose. The run prints the
distinct count and the largest group every time, so a return of the "stood
idle" cluster is seen the day it happens.

A baseline's first line names its scheme. A file recorded under another one —
including every file the first scheme wrote, which has no such line — is
refused with that said, instead of reporting the whole roster as moved.
Re-record it with `--record NEW --subset OLD`.

### A roster that grows keeps its baseline

Characters the baseline does not know are counted as `new` and never fail a
check, so adding characters is not a regression. But fighting them costs time,
and a baseline should keep meaning what it meant. Two flags keep the two apart:

```sh
oxtool regress .. --check metrics/regression-baseline.tsv --listed
oxtool regress .. --check metrics/regression-baseline-originals.tsv --listed
oxtool regress .. --record metrics/regression-baseline-originals.tsv --subset list.txt
```

`--listed` fingerprints only the baseline's own characters; `--subset FILE`
only the ones a file names (one `.def` per line, or a baseline). The archive's
original 1,051 keep their own file and the original-format imports have a
second one, so "1051 unchanged" still means the same 1,051.

### What is in the hash, and what must not be

Only what the **simulation** decides: state number, animation, position,
velocity, facing, life, power — for every live player, tagged with its id. Position is rounded to whole units and velocity
to hundredths, because a float that differs in its last bit is not a regression
anybody can see, and a suite that cries wolf on a compiler upgrade is a suite
that gets turned off.

Nothing the **renderer** decides is in it — no sprite, no palette, no camera,
no sound. Those change for reasons nobody cares about.

FNV-1a rather than the standard library's hasher, which is explicitly not
stable across versions. A stored baseline needs exactly that property.

### Why a hash rather than a trace

A trace of 2,400 characters is gigabytes; a hash is sixteen characters. The
hash says *that* something moved, and `oxtool simulate --why` says what.
Noticing a difference and finding it are different jobs.

### Proven both ways

A suite that cannot fail is worthless, so both directions were checked:

* run twice with no change — **20 unchanged, exit 0**, twice;
* halve one character's `life` — **19 unchanged, 1 moved**, and it named
  `chars/!falcon/!falcon.def`;
* restore it — **20 unchanged** again.

## `oxtool balance` — how unusual is this character?

MUGEN specifies almost nothing about balance. `life = 1000` is Kung Fu Man's,
not a rule, and an author is free to write 9999. There is no authority to check
a character against — **except the other 2,400 characters**, written by a
thousand people, whose agreement is the closest thing to a convention this
archive has.

```sh
oxtool balance . [--limit N] [--tsv]
```

Measured across the roster of 1,051:

| | 5% | 25% | median | 75% | 95% |
|---|---:|---:|---:|---:|---:|
| life | 1000 | 1000 | **1000** | 1000 | 1600 |
| attack | 85 | 100 | **100** | 100 | 145 |
| defence | 90 | 100 | **100** | 100 | 150 |
| hit damage | 20 | 35 | **45** | 60 | 156 |
| reach | 76 | 124 | **205** | 423 | 1193 |

Percentiles are nearest-rank, so every figure reported is a number some
character really has rather than one nobody wrote.

### What it finds

Omega Tom Hanks took an afternoon to find by reading its `.cns` by hand. This
names it in one run, alongside everything like it:

```
  Broli SSJ5      life 5000 (99th 2200); defence 500 (99th 200); attack 300
  Saga            defence 225; attack 225; reach 30752 (99th 9999)
  Omega Tom Hanks life 9999 (99th 2200); defence 999 (99th 200)
  Akuma           hit damage 390 (99th 200)
  K'              reach 10000 (99th 9999)
```

`Saga`'s reach of **30,752 units** is ninety-six screens. That is not a design
choice; it is a `Clsn1` box somebody typed wrong, and nothing had ever looked.

### What it deliberately does not say

It does not say a character is wrong. **A boss is supposed to be a boss**, and
a prop with 5000 life is a punching bag doing its job. The report says how
unusual a character is against its peers and leaves the judgement where it
belongs — which is also why the bar is the roster's own 99th percentile rather
than a number chosen here.

## `oxtool rewind` — the frames before it went wrong

`simulate --why` says what the engine decided, frame by frame. That is the
right tool **when you know which frame to look at**. Usually you do not: you
know the character ended up somewhere it should not be, and the interesting
frames are the twenty before that, which have already scrolled past.

```sh
oxtool rewind . chars/Daffy/daffy.def --until-state 12 --back 8
```

```
entering state 12 at tick 58

  tick   state    anim           x    vel x   life ctrl controllers that fired
  51     5001     5017       -73.1    -0.27    875 no   State 5001, 3 (VelMul)
  53     0        0          -73.2     0.00    875 yes  State -1, Combo condition Reset
  54     20       21         -75.1    -1.87    875 yes  State -1, Combo condition Reset
  56     10       10         -78.1    -1.15    875 yes  State -1, Combo condition Reset
  58     12       12         -79.9    -0.80    875 yes  State -1, Combo condition Reset
```

Read upwards: it was being hit (5001), recovered to standing, walked, then
crouched. That is the `0 → 10 → 12` chain the cycle detector reports as a loop
— now visible frame by frame, with the controller that moved it each time.

Three moments can be watched for: `--until-state N`, `--until-frozen` and
`--until-offscreen`. Freezing triggers at two seconds rather than the engine's
own seven-second deadlock bar, because the interesting frames are the ones
where it *became* stuck.

### Why it records rather than reverses

Rollback can restore a past frame, and a true reverse step would use it. But
restoring only helps if you mean to **re-simulate** — to ask what would have
happened with a different input. For reading what did happen a recording is
exact, costs one line a frame rather than a whole `Match` clone, and cannot
perturb the run it is observing.

Snapshots are still kept every half-second, because re-simulating from one is
the next thing this wants to do and discarding them would make that a rewrite
rather than an addition.

### It has to be driven

`--ai` defaults to on. A fighter nobody is playing simply stands there, and
none of the faults worth rewinding to — a stuck state, a loop, a walk off the
screen — happen to a character at rest.

## `oxtool find` — which characters do this, and where

This searches the *content*, which is
the half of the question a document cannot answer.

```
oxtool find .. ReversalDef --limit 250 --show 6
71 of 250 character(s) have reversaldef
  Dragon Claw                reversaldef ×66 in states 200, 205, 206, 207, 210, 211
                             chars/DragonClaw/DragonClaw.def
  JAGI                       reversaldef ×43 in states 200, 210, 220, 230, 240, 410
                             chars/JAGI/JAGI.def
```

A term is a state-controller or parameter name — `Helper`, `Projectile`,
`ReversalDef`, `TargetBind` — or a word from a character's name or author.
Several terms narrow: a character must have all of them. `--json` prints the
same thing for a program to read.

### Why this exists

"How do I write a parry" has a documented answer. **"Show me somebody who
wrote one"** does not: it is a fact about two thousand folders, and the only
honest way to answer it is to go and look.

That distinction is the whole argument. A model asked the second question will
answer the first one, fluently, and the reader cannot tell the difference. A
search index answers it with a character that exists and a state number that
can be opened — so its worst failure is *"that example was not what I meant"*
rather than a confident description of a technique nobody uses.

### Results are ranked by how much there is to learn from

Most uses first. Somebody who wrote sixty-six of something is a better example
than somebody who wrote one, because the question behind "show me one" is
almost always "show me one that works".

### Two bugs it found in its own first run

**A flag's value became a search term.** The idiom every other subcommand here
uses — `args.filter(|a| !a.starts_with("--"))` — drops `--limit` and leaves
`400` behind as a word to search for. The first run printed *"0 of 0
characters have reversaldef and 400 and 8"*. It fails silently: an extra term
matches nothing, and the empty result reads as "nobody does this" rather than
as a bug. `positional()` now skips the value of any flag that takes one.

**The verification grep was the thing that was wrong.** Checking the tool's
claim of 423 `TargetBind` uses in Andore Jr, `grep ../chars/Andore Jr/*.cns`
found none — the states are in a `cns/` *subfolder*. Grepping the folder gives
exactly 423. The tool was right both times it was doubted; the check was
written more carelessly than the thing it was checking, which is the ordinary
way a spot-check misleads.

## `oxtool migrate --check` — is every character actually in FUSE?

A roster assembled from several sources drifts back to CNS **silently**:
characters can end up with no `.fuse` anywhere, and nothing in the pipeline is
in a position to notice. `CONVERSION-LOG.tsv` records what conversion
*attempted*, which says nothing about characters it never saw, and the log can
predate the folders it is supposed to describe.

```
oxtool migrate <root> --check          report, with a reason for each
oxtool migrate <root> --check --tsv    the same, for a program
oxtool migrate <root> --only-cns       re-run conversion over just those
oxtool migrate <root> --only-list F    over a named set, one folder per line
```

`--check` exits non-zero when anything is unconverted or shadowed, so it works
as a gate after a merge.

### The five causes, and only one of them was the converter

| cause | characters |
|---|---:|
| merged in from quarantine *after* the sweep ran, never converted | 71 |
| the folder is shadowed by another differing only in case | 48 |
| a storyboard `.def` was chosen over the character's own | 3 |
| state files in a subfolder the converter did not follow | 1 |
| the folder is empty — the files are gone | 1 |
| **a converter error** (`unknown trigger Var1`) | **1** |

Re-running conversion over the affected set: **90 converted, 0 degraded**, then
**4 converted, 0 degraded** after the `.def`-selection fix. All 2,363
enumerable characters are now in FUSE.

### Shadowed folders are reported, not renamed

48 pairs, and **none of them are duplicates** — `AKARI` has 43 files, `akari`
has 17 different ones; they are alternate versions of the same fighter by
different hands. The VFS resolves case-insensitively, which it must, so that a
`.def` written on Windows saying `Data\Common1.cns` opens on Linux. The cost is
that both folders are one folder to every tool and to the engine.

Which of the two to keep is a decision about the roster, not a bug with a
correct fix, so the tool reports and stops. Detection reads with `std::fs`
rather than through the VFS: asking a case-insensitive layer about case
collisions cannot work.

### Choosing a character's `.def`

`iori_imported/` holds `ending.def`, `intro.def` and `iori.def`. The rule was
"prefer `<dirname>.def`, else the first alphabetically" — and the folder had
been renamed on import, so the preference missed and the fallback took the
endings. The tool loaded a storyboard, found no states, and moved on without
an error.

It now falls back to the first `.def` that **declares a state file** — a `cmd`,
`cns`, `st`, `stN` or `stcommon` line — read as text rather than parsed,
because a storyboard `.def` is often malformed in ways a full parse would
reject for the wrong reason.

### Two ways the measurement was wrong before the answer was

Both produced a confident count that had to be withdrawn.

* **The `.fuse` search must walk three levels, not one.** `neoakuma` keeps its
  converted files at `data/cns/*.fuse`, two directories below its `.def`. A
  one-level check called it unconverted, and that false positive was in the
  reported number until a full `find` contradicted it.
* **`migrate`'s filter narrows the sweep but not the conversion.**
  `fuseify::run` still takes the whole root, so `--only-cns` measures 90
  characters and converts 2,363. Harmless — conversion skips a file that
  already exists — but it turns a two-minute job into an hour, and the log
  fills with characters that were never in scope.

## `oxtool unshadow` — giving a hidden character its own name back

48 characters on this roster were unreachable because another folder differed
from them only in case. `oxtool unshadow <root> --apply` renames the hidden one
after its own display name; `select.def` is then rebuilt with
`tools_build_select.py` and the newly visible characters converted with
`oxtool migrate <root> --only-cns`.

```
chars/akari       -> chars/Akari Ichijo        (hidden by chars/AKARI)
chars/ash         -> chars/ASH CRIMSON         (hidden by chars/ASH)
chars/ChibiGoku   -> chars/Goku Pequeno        (hidden by chars/chibigoku)
```

### The roster was already asking for them

`select.def` listed each of these **twice, with the same spelling** — `AKARI`
on two lines. So the roster wanted two characters in those slots and the engine
handed it the same one twice. Renaming did not add 48 slots; it filled 48 that
were already there and had been quietly serving duplicates.

### The new name is the character, not a counter

`akari` becomes `Akari Ichijo`, not `akari-2`. The display name is the thing
that actually distinguishes the two fighters — `AKARI` is M@PPY's, `akari` is
Roque's *Akari Ichijo* — so it is what should distinguish their folders. A
numbered suffix would leave the next person with exactly the puzzle the command
exists to solve. 46 of the 48 pairs had different display names; the two that
did not fall back to `<name> alt`.

### Which one moves

The one the roster does **not** currently spell. `select.def` says `AKARI`, so
`AKARI` keeps its name and `akari` moves — the existing entry keeps working and
the stage, music and order attached to it are not disturbed.

### Result

| | before | after |
|---|---:|---:|
| character folders | 2,413 | 2,413 |
| characters the tools can see | 2,363 | 2,411 |
| `select.def` entries | 2,250 | 2,413 |
| duplicate entries | 47 pairs | 0 |
| characters lost | — | **0** |

Rebuilding `select.def` added **210** entries, not 48: the other 162 were
characters sitting in `chars/` that had never been listed at all. All 48
unshadowed characters convert to FUSE with **0 degraded**, and audit at a
median of **93.5%**, minimum 75.0%, none below 70%.

### Detection cannot use the VFS

Asking a case-insensitive layer to report case collisions cannot work, so both
`unshadow` and `migrate --check` read the directory with `std::fs`.

### The rename is recorded

`model/data/unshadow-log.tsv` maps every `was` → `now` → `was_hidden_by`. It
exists because the fault is now gone from the roster, and the `integrity`
training rows that describe it would otherwise stop being re-derivable — a
corpus row whose answer can no longer be checked against the world is the drift
this project refuses everywhere else.

## `oxtool fusediff` — did the conversion keep everything?

A player reported that some characters would not walk. The cause was that
conversion had dropped their constants: the `.def` pointed at a `.fuse` with no
`constants { … }` block, so `const(velocity.walk.fwd.x)` read **zero**. The
fighter entered the walk state with the right animation and stood still.
`Rare Akuma`'s converted constants file was **0 bytes**.

```
oxtool fusediff <root>            what every conversion lost
oxtool fusediff <root> --repair   point the .def key back at the original
```

**691 of 10,259 converted files had lost something** — constants, states or
commands. After `--repair`: 9,568 compared, nothing lost.

### Why neither existing check could see it

| check | what it compares | why it missed this |
|---|---|---|
| `fuseify`'s shape check | state counts | every state survived |
| `oxtool fuse-verify` | a before/after sweep | needs a *before*; damage from a converter run that no longer exists has none |
| **`fusediff`** | **the original file against the converted one** | **needs no opponent, no sweep, no baseline — both files are on disk** |

That third row is the whole point. The expensive checks answer "is this
character worse than it was", which cannot be asked once the baseline is gone.
The cheap one answers "is anything in the original missing from the
conversion", which stays answerable forever.

### What it compares

The constant sections (`[Data]`, `[Size]`, `[Velocity]`, `[Movement]` — and an
empty section promises nothing), every `[Statedef N]`, and every `[Command]`
name. Deliberately *not* behaviour: this is the static half, and it is cheap
enough to run on every build.

### The repair points back rather than re-converting

The original is still on disk and is by definition complete, so the safe move
is to restore a file the engine already knows how to read. Re-converting would
be the other option and is not what a repair should do. The `.def` is backed up
to `.def.fusediff-backup` first.

### Measured

19 characters that could not walk now can, 17 that could not jump now can, and
**none regressed**. The command losses turned out to be mostly AI and assist
commands, so the special-move counts barely moved — stated because it is the
honest result rather than the one that was expected.

### `--programs`: the files on disk, as programs

```
oxtool fusediff <root> --programs [--only-list F] [--detail FILE] [--jobs N]
oxtool fusediff <root> --programs --regen DIR      what a refresh would write
oxtool fusediff <root> --programs --apply          refresh those files in place
```

Every converted file the `.def` points at, compiled and compared state by state
against the original beside it with `oxyde_cns::compare` — the comparison
`oxtool fuse --verify` makes of a *fresh* conversion, made of what an older
converter left in the tree. It names the characters whose files read a guard
once for several controllers that were separate in the CNS, when something
between the readings can change the answer (homer's two explods on
`NumExplod(1006) = 0`). `--apply` goes through `fuseify`'s refresh — one
`.fuse.refresh-backup` per file, undone by `oxtool revert <folder> --kind refresh
--apply` — and only for a file whose fresh conversion reads no guard once and
differs from the original in no state the file on disk did not. On the test roster:
1,311 characters, 2,055 files.

## Directed jumps are measured now

`oxtool audit`'s movement probe held **up** and nothing else, so a character
that jumped straight up but could not jump forward or backward scored full
marks on movement. Two of the three directions were never tried, which is why
the fault reached a player before it reached a test.

`jump_fwd` and `jump_back` are reported and deliberately **not scored**: every
conversion, repair and quarantine decision here is a before/after comparison of
that number, and adding a term would move all of them at once — a fault that
has existed for months would read as a regression introduced today.

## A trial is only offered if it can be demonstrated

Proving a combo route and playing it back are two different runs, and it is
possible for only the first to succeed. When that happens a trial can list
more moves than the Show Me performs — which is exactly what that gap
produces: the route was proven, the demonstration gave up partway through
`LINK_WINDOW`, and the trial stayed on the list claiming it was possible.

`TrialSet::generate` now replays each trial's demonstration and drops any that
cannot perform every step, restoring the rule the rest of this project already
follows: **the verifier and the demonstrator are the same driver.**

It asks whether every motion produced its state, not whether the route
*connects* — a single-move trial is allowed to whiff, because the move coming
out is what that trial teaches.

## Transcription is one command

`oxtool migrate <root>` is the whole pipeline, and every check it runs was once
a separate tool somebody had to remember:

```
sweeping before ...                      measure what works now
converting ...                           write the FUSE
repaired N dangling reference(s)         defrefs, folded in
comparing each conversion with its original ...   fusediff, folded in, and it repairs
checking constants survived ...          the loader's own answer, folded in
sweeping after ...                       measure again
reverted N of M to CNS                   anything that got worse goes back
```

### Why the checks live inside it

The conversion that dropped constants from 691 files was invisible to the shape
check and to the before/after sweep, and the check that *would* have caught it
did not exist. Adding it as a separate command would have left the same hole:
**a check that has to be remembered is a check that gets skipped.**

So `fusediff` and the constants check now run as stages of the conversion, they
**repair rather than advise**, and the pipeline ends by re-fighting everything
and reverting whatever got worse.

### Scoped to what it touched

Both checks take the same character list the conversion did. Before that, a
two-character migration compared 9,513 files and loaded 2,412 characters to
ask about two of them:

| stage | whole root | scoped |
|---|---:|---:|
| conversion diff | 9,513 files | 6 files |
| constants check | 94.8s | **0.2s** |
| whole pipeline, 2 characters | — | **7.9s** |

`oxtool fusediff <root> --only-list FILE` takes the same list, for checking a
subset without converting anything.

## `oxtool dashboard` — the whole roster on one page

```sh
oxtool dashboard . [--out FILE] [--limit N]
```

One self-contained HTML file in which **every character is one row**, carrying
its gate verdict, its balance outliers, what its own files are missing and what
state its conversion is in — sortable and filterable by fault class in the
browser. Every row, every threshold and all of the behaviour are in the one
file — no server, no data fetch, no dependency — and the only outbound request
it can make is the web-font stylesheet, which it renders completely without.
That is the reason it is a file: a roster's health can be attached to a
message, opened next year, or read on a machine with no toolchain.

The whole roster of 1,051 takes **two and a half minutes** — 22 minutes of CPU
across twelve cores, because the sweep is the fight. `--limit N` is for
iterating on the page itself.

### Nothing on it is derived twice

A page that computes its own answer becomes a second opinion, and the first
time it disagrees with the command a reader runs next, the page is what gets
distrusted — or worse, believed. So every column names a tool, and the binary
calls that tool:

| on the page | comes from |
|---|---|
| verdict, score, specials, why | `audit`'s card, read by `gate`'s own rules and thresholds |
| life, attack, defence, hit damage, reach | `balance::profile` |
| every percentile, and the `unusual` tag | `balance::pct`, computed by the binary and handed to the page — the page has no percentile code of its own |
| hurt boxes, attack boxes, the size constants | the same reads `inventory` prints |
| absent states | `complete::find_absent` |
| missing declared files | `defrefs::scan_def`, whose `repair` field is also what tells a conversion's dangling reference from an author's own |
| conversion state | `script_dialect` per declared state file — the loader's own answer — plus `ch.constants`, which is the question `fusediff --constants` asks |
| the repeating cycle | the card's `loop_cycle` |

Two tests hold the join together: the row order against the page's `K` map, and
the page's thresholds against the source of the tools they came from, so a
change to `inventory`'s bar for cheap constants or to `gate`'s score cut-offs
fails this command's tests rather than silently leaving the page behind.

### The fault classes

Measured across the 1,051 of this installation. A character can be in several
at once, and 661 are in none:

| class | n | what it means |
|---|---:|---|
| broken | 23 | the gate would refuse it: froze, NaN, off the playfield, unkillable, or landed nothing |
| boxes | 2 | no animation carries a hurt box, or none carries an attack box |
| conversion | 0 | a conversion unfinished, lost its constants, or rolled back |
| files | 4 | a file named in `[Files]` is not on disk |
| cheap | 19 | `life` above 2000 or `defence` above 200 |
| loop | 58 | it went round the same states over and over |
| absent | 149 | it asks for states nobody wrote, and the artwork for them is drawn |
| incomplete | 236 | the gate would warn: no specials, no block, or very few states |
| unusual | 29 | above this roster's own 99th percentile on some measure |
| **clean** | **661** | none of the above |

Two runs of this command disagree by **one character**: `oxtool audit`'s
free-for-all fight is not reproducible between processes, even with its seed
fixed at `0xA0D1`. Run the same four characters through `oxtool audit --out`
three times and `distinct_states`, `end_state` and even the function score
move — the pattern is stable within a run and different between runs, which
points at hash iteration order reaching the simulation. The dashboard inherits
it because it reuses the card rather than re-deriving one, which is the right
trade: the page agrees with the tool, including where the tool is noisy.

`conversion` is **0** here because this installation contains no `.fuse` file
at all — it is the CNS tree. On a large roster, where 8,874 of them live, the
same column reports each character as `fuse`, `mixed` or `cns` and names the
unfinished ones: `Marvin` is still pointed at its CNS with two converted files
sitting beside it unreferenced.

**Being CNS is not a fault.** Most of this archive is CNS and works. What the
class reports is a conversion that was *started* and not finished: a `.def`
repointed at a `.fuse` nobody wrote, a conversion that left the character with
no constants, or converted files abandoned beside a backup — the fingerprint of
a conversion measured as worse and rolled back, which for 78 characters was the
stale directory index rather than the conversion.

### Sorting and filtering

The table is sorted by **fault severity, worst first**, on load — sorting by
fault class was the point of the page, so it is what the page opens on. Ties
are broken by function score, so the worst of a class comes first rather than
whichever happened to load first.

Every other column sorts on a click and reverses on a second. The fault
classes double as the filter: one button per class showing its count, so the
number and the thing it selects cannot become two different ideas. Three
further filters cut across the classes rather than replacing them — `Some
FUSE`, `All CNS`, and `Kung Fu Man's size` — because "the broken characters
that are also still CNS" is the question worth asking. The class buttons, their
counts and their descriptions are all emitted from the binary's own table;
there is no second list in the template to drift.

### What it deliberately does not judge

`size.height` is reported beside the height the standing sprite is actually
drawn at, and **never judged against it**. It is jump clearance, not body
height; flagging a sprite taller than it fires on 755 of 1,051 characters, Kung
Fu Man included. What the page does show is the narrower fact — 248 characters
have left the `15 / 16 / 60` trio exactly as they inherited it — with the drawn
height beside it, so a reader can sort the column and decide.

The table lists 400 rows at a time. A page holding a thousand rows of fourteen
columns is a page nobody scrolls; the filters are how the rest is reached.

---

## `oxtool assert` — the claims a source read cannot settle

    oxtool assert <root> <char.def> [--ticks N] [--seed N] [--imply CLAIM]
    oxtool assert <root> --roster [--limit N] [--imply CLAIM]

FUSE's `assert` comes in seven forms. Four of them are questions about the
text — does this state set a `type`, does it end — and the linter answers those
by reading. The other three are questions about a *run*:

| Claim | What only a fight can say |
|---|---|
| `exits within N ticks` | whether the state ever hands control back |
| `no self loop` | whether it changes to itself forever |
| `reachable` | whether anything ever enters it |

This command performs the character and watches. `--imply CLAIM` treats every
state as though it carried the claim, which is the only way to run the check
over the archive's original 1,051 characters, none of which wrote one down:

```
$ oxtool assert .. --roster --limit 12 --imply reachable
12 characters, 900 ticks each
every state treated as though it carried `assert reachable`

0 of 12 characters had a claim fail; 3183 claims checked in 1.1 s
  0 failed, 252 held (7.9% of the claims were actually exercised), 2931 unproven
```

### `unproven` is not `held`, and the distinction is the whole point

Three numbers, not two. A claim **holds** when the fight entered the state and
the claim survived it; it **fails** when the fight contradicted it; it is
**unproven** when 900 ticks of play never got there. 92% of the claims in that
run are unproven, and reporting them as passes would turn this command into a
generator of reassurance — the failure mode that looks like success, which this
project has now paid for three times. The percentage is printed next to the
number precisely so nobody can quote one without the other.

The last two columns of the summary cross the claim result with the audit
result, because the interesting cell is the disagreement: a character whose
claims all hold while the audit froze is a character the probe never drove.

## `oxtool mojibake` — putting back the bytes a lossy decode destroyed

    oxtool mojibake <root> [--sources DIR] [--apply] [--tsv] [--show N]

14.8% of this archive is Shift-JIS. A conversion that read those files as UTF-8
wrote U+FFFD over every byte it could not interpret, and a replacement
character is not recoverable from the file holding it: the original bytes are
gone. They are, however, usually still somewhere else — in the `.def.cns-backup`
beside the file, or in another copy of the same character elsewhere in the
archive.

**The repair is proved, never guessed.** A candidate replacement is accepted
only when decoding *it* lossily reproduces the damaged file exactly, byte for
byte. That test is cheap and it is total: a candidate that differs anywhere,
including in a part of the file that was never damaged, is refused. Guessing
what a mangled name "probably" was is how a repair tool starts inventing
content.

### It reports on its own search first

```
$ oxtool mojibake ..
searching 1 root for clean copies: 0 .def file(s) under /games/oxyde

  nothing to compare against. Every character will read as
  unrecoverable, which is a fact about the search and not about
  the archive. Point --sources at the tree the originals are in.

110 damaged file(s) across 37 character(s) under /games/oxyde
  recoverable      0 character(s), 0 file(s)
  unrecoverable   37 character(s):
         5  no .def.cns-backup, so nothing can prove a candidate
        32  no clean copy of this .def anywhere else in the archive
```

`--sources` defaults to the parent of `<root>` minus `<root>` itself, and in
this installation that parent holds nothing — so the default finds no
candidates and every character reads as unrecoverable. The tool says so, in
those words, before the number. A count of 37 unrecoverable characters is a
true sentence about a search that looked nowhere, and a reader who took it for
a statement about the archive would conclude the damage was permanent. Check
the tool before the roster.

Nothing is written without `--apply`. Every file written is backed up once as
`*.mojibake-backup`, and `oxtool revert <root> --kind mojibake` takes the whole
sweep back.

## `oxtool reproduce` — does the same command twice give the same answer?

    oxtool reproduce <game-root> [--char <char.def>] [--only NAME]

Runs each fact-producing command **twice, as two separate processes**, and
fails on any line whose value moved.

Two processes, not two calls in one. A test that calls a function twice in the
same process shares everything that makes a result unstable — a lazily built
cache, a static, an allocator address that leaks into a hash order, a
directory listing already warm. Twelve commands are checked: nine that take a
root (`audit`, `gate`, `inventory`, `balance`, `coverage`, `defrefs`, `soak`,
`stress`, `troubleshoot`) and three that take a character (`frames`, `moves`,
`trials`), each with a small `--limit` so the whole sweep is minutes rather
than hours.

```
$ oxtool reproduce .. --only coverage
running 1 command(s) twice, as separate processes

  same      coverage

every command repeated itself; 0 duration(s) moved, which is what a duration does
```

A **duration** is allowed to move and is reported without failing — a timing is
not a fact about the content. A **value** is not allowed to move, and one that
does fails the run. That line exists because the first version of this command
failed on its own elapsed-time output, which is the kind of false positive that
gets a checker switched off within a day.

## `oxtool rules` — every ruleset, and what the engine would actually play

    oxtool rules <installation-root> [--stack NAME,NAME] [--list]

A ruleset is a sparse delta over a base mode: a file in `rules/` that sets only
the knobs it cares about. This command loads every one of them and reports
everything wrong with all of them at once, rather than stopping at the first.

`--list` prints the two dozen knobs a modifier may set, each with its range — from
`rounds_to_win 1..99` through `chip_damage 0..0.5` to `difficulty 1..8`. Every
one is a value the engine already reads; a ruleset cannot invent a setting,
which is what keeps the feature from becoming a second configuration language.

`--stack a,b,c` composes those rulesets in order and prints the result. That
output is the thing worth checking: with a stack, no single file says what the
match will play, and a reader reconstructing the composition by hand is a
reader who will get it wrong.

**A clamped value is reported and is not an error.** `life_scale = 12` comes
back as 4 with a line saying so, and the command still exits 0, because the
game will run — the exit code is reserved for a ruleset that genuinely failed
to load. Failing the run on a clamp would mean a player could not start a match
because a mod author typed an ambitious number.

## `oxtool index` — the character index, queried from outside the game

    oxtool index <game-root> [--build] [--query "..."] [--check]
                 [--limit N] [--show N] [--tsv]

One file of facts this engine derived about every character
(`data/oxyde-index.tsv`), so the select screen can filter by what a character
*is*, a mod can declare a ladder as a **query** rather than a list of names. See
[CUSTOMISATION.md](CUSTOMISATION.md) for how a mod uses it.

With no flags it summarises what is in the index. `--build` derives it again
from the characters on disk and writes it; `--check` reports the rows whose
files have changed since it was built; `--query "..."` resolves a query and
prints the ordered list it answers — the same question the game asks, asked
outside it, because a filter that quietly matches nobody looks exactly like a
roster that contains nobody, and running the query here is the only way to tell
them apart before a mod ships. Query terms are and-ed; a bare word matches name
or author, as the select screen's search box always has.

## `oxtool wallbreak`, `breakshow`, `cornerbreak` — proving the stage break

These three render and prove the [stage `[Break]`](EXTENSIONS.md#the-camera)
wall-break transition in-engine. They differ in *which* part of it they drive,
from the lowest-level prototype to the real combat trigger:

    oxtool wallbreak  <char-root> <stage.def> [--p1 REL] [--p2 REL] [--logic PATH]
                      [--out DIR] [--scale N] [--punch TICK] [--shots "t:name,..."]
    oxtool breakshow  <root> --stage <src> --to <dest.def> [--out DIR] [--scale N] [--ku]
    oxtool cornerbreak <root> --stage <src> --to <dest.def> --out <dir> [--scale N]

- **`wallbreak`** drives the Tier-2 prototype: a real `Match` with two fighters
  on a local stage `.def`, its `logic.fuse` machine attached, stepped and
  photographed at chosen ticks. The whole effect — the break decision, the
  `ModifyStageBG` that swaps the wall animation, the `BgPalFx` flash — happens
  inside `Match::step`, so it is a pure function of the fight. `--punch` is the
  tick player one attacks; `--shots` names the frames to save (`f+N` after the
  fight begins, `+N` after the break fires, a bare number an absolute tick).
- **`breakshow`** proves the hard-swap transition (C) through the real
  `Game::update`/`render` loop: it forces the simulation's `stage_break` state,
  the wall-break animation plays, the destination stage is swapped in behind the
  dust at the midpoint, and the fighters arrive on the far side. `--ku` instead
  proves the Knuckle Up stage-change *overlay* (presentation only, no swap).
- **`cornerbreak`** drives the **real trigger** end to end: it backs the
  defender into the corner and lands an actual hit through the ordinary combat
  path, so the wall breaks because `Match::resolve_hits` decided it did — the
  same code a live versus match runs (gated by the `corner_break` ruleset knob,
  on for versus; see [RULESETS.md](RULESETS.md)). It then plays the transition,
  arrives on the destination stage, and runs a control pass (the same hit at mid
  stage) to show the wall stays up when nobody is cornered. `OXYDE_CB_TRACE`
  dumps the per-tick state.
