# FUSE

**F**lexible **U**nified **S**tate **E**xpression — Oxyde's own state language.

FUSE is a front-end, not a second engine. A `.fuse` file, a `.zss` file and a
`.cns` file all compile to the same `Controller`, the same bytecode and the
same `execute`, and a character may mix them freely. What changes is the
front.

---

## 1. Why a third language

MUGEN's CNS is an INI file pretending to be a program. A state is a flat list
of controllers, each carrying its own copy of a guard that is usually the same
as the one above it, and there is no `if`, no loop, no local variable and no
way to name anything. Every character in this archive works around that in the
same three ways: repeated triggers, sixty shared `var()` slots, and magic
numbers.

Ikemen GO's ZSS fixes the first of those — it has real control flow — and
Oxyde reads it (see [§9](#9-zss)). It keeps CNS's punctuation, though, and
CNS's punctuation is where the ambiguity lives.

FUSE keeps everything a MUGEN author already knows — every trigger, every
controller, every parameter name, the state machine, `[Statedef -1]`, hit
pause, `persistent` — and changes only the places where the older languages are
ambiguous, silent, or ask the author to carry something the compiler could
carry for them.

| | CNS | ZSS | FUSE |
|---|---|---|---|
| Redirection | `p2, time` | `p2, time` | `p2.time` |
| Compare | `=` | `=` | `==` |
| Assign | `value = …` in a parameter | `var(0) := 1` | `var(0) = 1` |
| Range | `x = [1, 5]` | `x = [1, 5]` | `x in [1, 5]` |
| Local | — | `let $x = 1` | `let x = 1`, then `x = 2` |
| Array | — | — | `let buf[8]` |
| Named constant | — | — | `const Fireball = 1000` |
| Call | — | `call F(a);` | `F(a)` |
| Controller | `[State 0, 1]` + `type = …` | `posAdd{x: 1;}` | `PosAdd(x: 1)` |
| Comment | `;` | `#` | `#`, `//`, `/* */` |

### The one that matters most

**Redirection with a dot.** In CNS a comma separates a tuple, an argument list
*and* a redirect, and telling them apart takes lookahead a reader does not
have. Every parser bug found while bringing ZSS up in this engine was that
comma — a `HitDef` cut in half at its own closing parenthesis, a condition that
swallowed the rest of the file, `jugglePoints(p2, ID)` read as two arguments.

A dot has one meaning. `p2.time` cannot be misread, and a parameter can never
be silently truncated by a comma the author thought was a separator.

---

## 2. A file

```fuse
# Three comment styles. This one, and:
// this one,
/* and this one, which nests. */

const Fireball = 1000

fn Combo() -> ret {
    return stateType != A && ctrl
}

state 200 (type: S, movetype: A, physics: S, anim: 200, ctrl: false) {
    if animElem == 2 {
        HitDef(
            attr: S, NA
            damage: 23, 0
            animType: light
            hitSound: S 0, 0
            guardSound: S 1, 0
            ground.type: high
            ground.hitTime: 12
        )
    }
    if animTime == 0 {
        ChangeState(value: 0, ctrl: true)
    }
}
```

Top level holds `state`, `fn` and `const`, in any order. A `fn` may be used
before it is defined, and so may a named state.

### Statements

Statements end at a line break, or at a `;` if you prefer one. A line that ends
on an operator continues:

```fuse
if command == "SmashKFUpper" && power >= 1000 &&
   (ctrl || (hitDefAttr == SC, NA && moveContact)) {
    ChangeState(value: 3050)
}
```

### Controllers

`Name(param: value, param: value)`. Every parameter is named. A comma ends the
parameter when a parameter *name* follows it, and separates tuple elements
otherwise — which is how a reader parses it too, and means `damage: 40, 0` and
`sparkno: S 2` need no extra punctuation. One parameter to a line, with no
commas at all, also works.

---

## 3. Control flow

```fuse
if cond { … } else if cond { … } else { … }

while cond { … }
loop { … }                       # while 1

for i in 0 .. 8 { … }            # 0 to 7
for i in 0 ..= 8 { … }           # 0 to 8
for i in 8 .. 0 step -1 { … }

switch stateNo {
    case 100 { … }
    case 105, 106 { … }
    case in [200, 299] { … }     # a range arm
    else { … }
}

break
continue
stop                             # run no more of this state's body this tick
```

`stop` has no equivalent in CNS or ZSS. There, "stop here" has to be written as
a `ChangeState` to the state you are already in, which resets `time`, reloads
the animation, and is not what the author meant.

Every loop is capped at **2,500 iterations**, as Ikemen GO's are, and for one
more reason: a state body runs inside `Match::step`, which every rollback
re-runs. `oxtool` reports how often a loop hit the cap.

---

## 4. Variables

### Locals

```fuse
let x = 1        # declare
x = x + 1        # assign; `let` is not repeated
x += 1           # and -=, *=, /=
```

A local is a name, with no sigil. The compiler refuses to let one be named
after a trigger — `let time = 1` is an error, not a shadow — which is what
makes the sigil unnecessary.

Locals are **compile-time slots**. They are allocated when a structured state
starts and cleared when it ends, so they cost a rollback snapshot nothing: the
frame is always empty at the moment a snapshot is taken.

### Arrays

```fuse
let hist[8]
for i in 0 .. 8 {
    hist[i] = p2BodyDist x
}
VarSet(v: 0, value: hist[3])
```

Fixed length, decided when the character loads. An index outside the array
reads zero and writes nothing — never a neighbouring variable.

ZSS has scalars and nothing else, so anything with a shape competes for the
same sixty `var()` slots as everything else the character does.

### MUGEN's variable banks

```fuse
var(5) = 1
fvar(2) = 0.5
sysvar(0) = 1
map(combo) = 3
p2.var(1) = 7          # through a redirect
map(hits) += 1
```

These lower to `VarSet` and `MapSet` — the controllers that already do it —
with a `redirectid` when a redirect is written. There is one variable-writing
path in the engine, not two.

An assignment may also appear inside an expression, as CNS and ZSS allow:

```fuse
if sysVar(0) = (pos y >= 0 && vel y > 0) { … }
```

FUSE can afford this because `==` has taken over comparison, so an assignment
inside a condition is *visible* rather than hidden. That is the whole problem
with CNS's single `=`.

---

## 5. Constants and named states

```fuse
const Fireball = 1000
const FireballEx = Fireball + 50

state Fireball = 1000 (type: S, anim: 1000) { … }

state 200 {
    ChangeState(value: Fireball)
}
```

`state Name = n` declares the state and the constant together.

A constant is worked out when the character loads and emitted in place of its
name, so naming one costs nothing at run time. A constant that reads anything
about the match is an error, not a zero. A constant may not be named after a
trigger.

The character's own `[Data]`, `[Size]`, `[Velocity]`, `[Movement]` and
`[Constants]` sections are visible through `const(...)` as usual, including
Ikemen GO's `common.const` when the archive has one — which is how
`state const(StateDizzy)` works.

---

## 6. Functions

```fuse
fn Bump(by) {
    PosAdd(x: by)
}

fn Doubled(n) -> out {
    return n * 2
}

state 0 {
    Bump(4)
    let d = Doubled(21)
}
```

Functions are **inlined**, not called: no stack, no frame pointer, no return
address. A state body is one flat frame whose size is known when it is
compiled.

That is why `return` must be the last statement of a function — it is sugar for
assigning the named result, not a jump, and FUSE says so rather than letting
you find out. Recursion is refused for the same reason.

### Calling one inside an expression

A call is a sequence of statements, so strictly it cannot sit inside a
condition. Write it there anyway:

```fuse
if CanAct() && power >= 1000 {
    ChangeState(value: Fireball)
}
```

The compiler hoists it ahead of the statement, which is what you would have
typed by hand:

```fuse
let _fuse_call_0 = CanAct()
if _fuse_call_0 && power >= 1000 { … }
```

Nested calls are hoisted innermost first, and a call inside a string is left
alone.

The one place this needs care is a `while` condition, which is evaluated before
every iteration — hoisting out of the loop would evaluate it once. So the loop
is turned inside out instead:

```fuse
while !Done(i) { i += 1 }
```

becomes

```fuse
while 1 {
    let _fuse_call_0 = Done(i)
    if !(!_fuse_call_0) { break }
    i += 1
}
```

which is the same program. The iteration cap applies either way.

A function may not be named after a controller or a trigger, which is what lets
`Foo(…)` be decided without a `call` keyword.

Functions are shared across a character's files, so one defined in `st` may be
used from `st2` — the same rule Ikemen GO's `kfm_zss` relies on.

---

## 7. Modifiers

```fuse
@ignoreHitPause
PosAdd(x: 4)

@persistent(0) {
    VarAdd(v: 0, value: 1)
}

@ignoreHitPause @persistent(3) if time == 0 { … }
```

The `@` is what keeps these from reading as controllers. They change how a
controller is *scheduled* rather than doing anything themselves, and in ZSS
they are spelled like statements, which hides that.

`@persistent(n)` takes a plain number: it is read when the character loads.

---

## 8. Errors

Every diagnostic carries a line, a column and a caret, and an unknown name is
answered with the nearest one that exists — including transposed letters, which
is the commonest typo anyone makes:

```
kfm.fuse:12:15: error: unknown trigger `tiem`; did you mean `time`?
    PosAdd(x: tiem)
              ^
```

A file with errors in it still yields every state that parsed. A character
whose eighth state has a typo should still be able to stand up, and the author
should be told about the typo rather than handed a black screen.

What FUSE refuses that CNS accepts, and why:

| Refused | Reason |
|---|---|
| `let time = 1` | a local named after a trigger is unreadable without a sigil |
| `fn PosAdd(x)` | a function named after a controller makes `PosAdd(…)` ambiguous |
| `stateNo = 200` | `=` assigns; write `==` |
| `stateNo == [1, 5]` | write `in [1, 5]` |
| `$x` | FUSE locals have no sigil |
| `var(0) := 1` | FUSE assigns with `=` |
| `x = 1` with no `let` | a typo in a name would otherwise make a second variable |
| a `const` that reads the match | it is worked out when the character loads |
| `return` other than last | a function is inlined, so nothing jumps |
| recursion | the same reason: there is no stack to recurse on |

### Lints

Beyond what the compiler refuses, seventeen rules catch things that *compile*
and are still probably wrong. `oxtool fuse <file>` prints them, `oxyde-lsp`
shows them as you type, and `oxtool eval rules` explains each one.

| Code | Level | What it catches |
|---|---|---|
| `dead-after-state-change` | warn | statements after an unconditional `ChangeState` |
| `one-tick-controller` | warn | `Width`/`PlayerPush`/`ScreenBound`/`AngleDraw`/`AngleSet` under a `time == n` guard, which sets them for one tick |
| `parameter-misspelled` | warn | a parameter no controller of that kind takes, with a near neighbour that does |
| `loop-cannot-end` | warn | a `while` whose body changes nothing its condition reads |
| `hitdef-not-attacking` | warn | a `HitDef` in a state that declares `movetype: I` |
| `hitflag-air-only` | warn | a `hitflag` naming none of `M`, `H` or `L`, which passes through anybody standing |
| `state-not-defined` | warn | a state change to a number nothing in the character defines |
| `hitdef-without-attack-box` | warn | a `HitDef` in a state whose animation carries no `Clsn1` |
| `def-file-missing` | warn | a `.def` line naming a file that is not there |
| `assert-failed` | warn | the state does not do what its `assert` claims |
| `assert-not-understood` | warn | an `assert` the checker cannot settle, which would otherwise never fail |
| `re-enter-self` | hint | `ChangeState` to the state you are already in — usually `stop` was meant |
| `var-beyond-mugen` | hint | `var(60)` and up: Oxyde allows it, nothing else does |
| `unused-local` | hint | a `let` nothing reads |
| `helper-without-id` | hint | a helper `helper(n)` cannot single out |
| `parameter-unknown` | hint | a parameter name that appears nowhere in the archive |
| `constant-far-above-the-archive` | hint | `life`, `attack` or `defence` above the archive's 99th percentile |

A `warn` is a mistake — every instance found in the archive was one. A `hint`
has a reading where it is deliberate.

#### What counts as unknown

The two parameter rules read `params.rs`, which is **counted from the archive**
— what a thousand authors write. That is the right evidence for *offering* a
name and the wrong evidence for *rejecting* one: the filters that keep
misspellings out of a counted table cannot tell a typo from a real parameter
that happens to be short. `fv` is one edit from `v` and far rarer, so `VarSet`'s
float-variable parameter was being reported as a typo for its integer one —
and the hint's own words were "the engine will ignore it" about a parameter
`exec.rs` implements.

So a second list, from the other side: `engine_params.rs` holds every name
`oxyde-core` passes to `param…("…")`, and a name on it is never reported. It is
flat rather than per-controller, because the engine reads them inside match
arms a scanner cannot attribute, so it is used only to **stop** a claim and
never to make one. A test scans the engine's own source and fails if the list
drifts.

Measured over the 1,051-character roster, that took `parameter-unknown` from
**946 characters (90.1%) and 57,477 hints to 317 (30.2%) and 1,997**, and
`parameter-misspelled` from 558 characters to 496. What is left reads like
`Explod takes no persisent` and `no Varadd takes a triggeall`, which is what
the rule is for.

#### The three that need the whole character

`state-not-defined`, `hitdef-without-attack-box` and `def-file-missing` cannot
be decided from the file on the screen. Whether a state exists is a fact about
the `.cns`, the six `st` files and the `.cmd` together; whether an attack has a
box to hit with is a fact about the `.air`; a `.def` line is a promise about a
file somewhere else entirely.

So `oxyde_cns::lint` grows a view of the character — every state number, every
animation and whether it carries a `Clsn1`, and the states this character puts
*somebody else* into — built once from the `.def` through a `Files` trait, so
the engine can hand it a VFS and the language server a directory. The server
reads it when a document opens and not on every keystroke; the buffer's own
states are added on top, so a state written a moment ago counts as defined.

Two things the view has to get right or the rules are worse than useless. The
common states come from the game's `data/`, not from the character — 734 of the
1,051 characters name a `common1.cns` that is not in their folder, and a view
that stopped at the folder would report every `ChangeState 5000` in all of them
as going nowhere. And a state the character puts the opponent into names the
*opponent's* state numbers, which nothing here can see; the targets of
`p2stateno`, `p2getp1state` and `TargetState` are collected for exactly that
reason.

`cargo run --release --example lintroster` re-measures the whole archive. On
the archive's original 1,051 characters: `state-not-defined` fires on 330 characters
(31%), `hitdef-without-attack-box` on 208 (20%), and `def-file-missing` on 4.

The bar for adding a rule is deliberately high, because a rule that fires on
correct code gets the whole linter switched off. Across all fourteen of
Ikemen GO's own `.zss` files, exactly **two** lints fire, and both are genuine:
`inrange` and `jugpt` in its Kung Fu Man's AI are assigned and never read.

`ReversalDef` is deliberately absent from `hitdef-not-attacking`: a parry waits
to be attacked rather than attacking, and Ikemen's own character declares three
such states `movetype: I`, correctly. The rule fired on all three before that
exception existed, which is how it was found.

---

## 8b. Commands

A character's input motions — quarter-circles, charges, double taps — have
always lived in a `.cmd` file in MUGEN's 2001 INI format. **Neither CNS nor ZSS
can declare one.** Ikemen GO's own `data/common.cmd` is `[Command]` sections
and its compiler reads them exactly as MUGEN's does. FUSE can:

```fuse
commands (time: 15, buffer: 1) {
    QCF_x                   = ~D, DF, F, x
    QCF_y                   = ~D, DF, F, y
    Hadouken (time: 20)     = ~D, DF, F, x | y | z
    Charge   (time: 60)     = /60B, F, x
    Taunt                   = start
    Recovery                =
}
```

Against the same thing in a `.cmd`, which spends five lines and a quoted string
on each command and keeps its defaults in a separate section:

| | `.cmd` | FUSE |
|---|---|---|
| a command | 4–6 lines | one line |
| the name | a quoted string | **an identifier** |
| defaults | `[Defaults]`, elsewhere in the file | the `commands (…)` header |
| buffer time | `command.buffer.time` *and* `buffer.time` | `buffer`, both places |
| a mistyped option | silently ignored | `` `tiem` is not a command option; did you mean `time`? `` |

The motion is unchanged — `~D, DF, F, x` is the same text, read by the same
parser the input system runs. FUSE supplies the *declaration*; re-implementing
the motion grammar in a second place would be two grammars to keep in step.

Every extension this engine adds to the command file works here unchanged:
`|` alternatives, `L`/`R` absolute directions, `/60B` held charges, `steptime`,
`buffer.hitpause`, `buffer.pauseend` — see
[EXTENSIONS.md](EXTENSIONS.md#command-file).

### The reason this is worth having

The name is an **identifier**, not a string.

`command == "Hadouken"` against a command declared as `hadoken` is not an error
in MUGEN, in Ikemen GO, or in this engine when the command came from a `.cmd`.
The move simply never comes out, and the author reads the state machine forty
times looking for the reason. Declared in the same file the compiler can check
it, which is the difference between a typo and an afternoon.

### One extension, and why there is not a second

There is no `.fused` for commands or `.fuses` for states. Role-specific
extensions would rebuild exactly the split FUSE exists to remove: CNS and CMD
need different extensions because they are different *formats*, and FUSE is one
format that holds both.

Three separate things decide what happens to a file, and only one of them is
the name:

| question | answered by |
|---|---|
| which parser reads it | the extension — `.fuse`, `.zss`, anything else is CNS INI |
| where it comes from | the `.def`'s `[Files]` section, which has always been the manifest |
| what it provides | **the file's own contents** |

A file called `attck1.fuse` that contains a `commands { … }` block provides
commands, whatever it is called and whichever `[Files]` key names it. That is
why a character can now be a *single* file:

```ini
[Files]
cns = kfm.fuse        ; commands and states together
```

with no `cmd` key at all.

### When two files declare the same command

The file the `.def` lists **later** wins — MUGEN's existing rule within a file,
extended across files, so it is deterministic and replays are unaffected. It is
also almost always a mistake, so the engine says so:

```
command `Hadouken` is declared more than once; cmd2.fuse wins
```

A `.zss` file in the `cmd` slot warns too, rather than loading an empty command
set in silence: ZSS has no syntax for commands and never has.

---

## 9. ZSS

Oxyde reads Ikemen GO's ZSS too, in full. All fourteen `.zss` files Ikemen
ships — `common1.cns.zss`, `action.zss`, `dizzy.zss`, `guardbreak.zss`,
`score.zss`, `system.zss`, `tag.zss`, `training.zss`, `demo.zss`,
`functions.zss`, and `kfm_zss`'s four — parse and lower with no errors: 140
states and 1,081 controllers.

One rule of ZSS is worth stating because it is not MUGEN's. **A negative state
appends across files rather than replacing.** Six of Ikemen's own `data/*.zss`
files each declare `[StateDef -4]` and three declare `[StateDef -2]`;
`kfm_zss` puts its moves in `command.zss` and its AI in `AI.zss`, both under
`[StateDef -1]`. Replacing rather than appending leaves that character able to
walk and unable to punch. The same rule applies to `.fuse`. CNS keeps MUGEN's
replace semantics untouched.

---

## 10. Converting

```
oxtool fuse <file.cns|file.zss|file.fuse> [--out FILE] [--verify]
oxtool fuse <game-root> --roster [--out DIR] [--verify]
```

`--verify` parses the converted text back and checks it against the original,
controller for controller and parameter for parameter. That is also how FUSE
is tested: Ikemen's fourteen ZSS files transpile to FUSE and lower to
**byte-identical bytecode**, 1,081 controllers, zero mismatches. "A FUSE
character and a CNS character are the same character written twice" is the sort
of thing a language's documentation always says; here it is checked.

Across the whole archive, `--roster` converts **1,051 of 1,051 characters** —
276,563 states and 2,094,037 controllers, about 338 MB of FUSE. Every error
that remains is one the original CNS already had.

**What conversion cannot do.** It produces *correct* FUSE, not *idiomatic*
FUSE. Every guarded controller gets an `if` of its own, even when the one above
has the same triggers: two CNS controllers each read their triggers, so a
`Random` in them is drawn twice and a guard the first controller falsifies stops
the second, and one shared `if` would read it once. Nothing can infer that three
variables were really a loop, or name a magic number: nothing in the file says
which 1000 is the fireball.

**`cns("…")`.** A few released triggers are not well-formed CNS, and the CNS
loader *recovers* them into a real program rather than refusing them:
`AnimElem > = 1 = 1` is read as `AnimElemNo(0) > 0` and fires. FUSE cannot
spell that, so the converter keeps the author's text inside `cns("…")`, which the
FUSE compiler hands to the CNS front-end unchanged. The converted controller runs
the very bytecode the original does. Only a trigger that folds to a constant is
written as the constant (`if false /* was: … */`); `cns("…")` is for the ones that
do not, and it is a converter's tool rather than something to write by hand.

A parameter the engine ignores — a controller neutralised by changing only its
`type` to `Null`, leaving a full `HitDef` behind it — is kept as a comment
rather than converted or dropped.

---

## 11. The editor

`oxyde-lsp` is a language server for FUSE and ZSS. It speaks LSP over stdin and
stdout; point any editor at the binary and there is nothing to configure.

* diagnostics as you type, the same ones the engine will give
* completion — controllers at a statement, that controller's parameters inside
  its argument list, triggers and your own names inside an expression
* hover — what a controller is and which parameters it takes
* go to definition, for a function, a constant or a local
* document outline
* lints as warnings and hints, never as errors — everything they flag compiles
* a quick fix for a misspelled name

Everything it says is derived from the compiler's own tables, so the editor and
the engine cannot disagree. The parameter lists are counted from the archive —
if four hundred characters put `sparkno` on a `HitDef`, a `HitDef` takes
`sparkno` — because no manual lists them all and the ones that try disagree
with each other. Regenerate with `cargo run -p oxyde-tool --example params`.

---

## 12. Where FUSE fits

```
   .cns ──► Def ──────► Vec<Controller>  ─┐
                                          │
   .zss ──► Node ──► Block ───────────────┼──► Controller, Program, execute
                                          │
  .fuse ──► Node ──► Block ───────────────┘
```

CNS produces a flat controller list, because that is all its format can
express, and all 2,527 characters here
are written that way. ZSS and FUSE
produce a `Block`, which has control flow in it. Below that line everything is
shared, and a fix to one lands for all three.

A `.def` picks the language by extension:

```
[Files]
cns      = kfm.const
st       = kfm.fuse
st2      = hits.zss
st3      = command.cns
stcommon = common1.cns
```

`stcommon = common1.cns` also finds `common1.cns.zss` or `common1.fuse` when
that is what is on disk, which is Ikemen GO's convention.

---

## 13. The benchmark

`oxtool eval` turns the archive into a graded benchmark for anything that
writes FUSE — a person, a script, or a model.

```
oxtool eval build <game-root> --out bench     # corpus, split, and 2,000 tasks
oxtool eval baseline bench --kind retrieve    # a floor to compare against
oxtool eval score bench answers.jsonl         # valid / clean / correct
oxtool eval rules                             # what each lint code means
```

Three tiers, because comparing generated code to a reference by *text* is close
to meaningless — two spellings of a state are the same state:

| Tier | Means |
|---|---|
| **valid** | it compiles: the character loads |
| **clean** | valid, and it introduces no lint the original did not have |
| **correct** | clean, and every controller, guard, loop and parameter compiles to the same bytecode |

`correct` compares the whole `Block`, not the flattened controller list. An
earlier version compared only the controllers, and a baseline that replaced
every condition with `1` scored **100% correct on guards** — of course it did,
since changing a condition does not change which controllers exist. A state
language is mostly control flow; comparing what it *contains* rather than what
it *does* is the one mistake that would make the benchmark say nothing, and say
it confidently.

Answering exactly what the original file said scores exactly 100%, which is the
benchmark's own sanity check: a task whose reference does not compile is
dropped at build time rather than capping every score below it.

## Constants

A character's own measurements — how much life it has, how fast it walks, how
big its push box is. CNS keeps these in `[Data]`, `[Size]`, `[Velocity]` and
`[Movement]` sections of the file named by `cns =`; FUSE keeps them in one
block:

```fuse
constants {
    data {
        life = 1000
        attack = 100
        fall.defence_up = 50
    }
    size {
        ground.back = 15
        ground.front = 16
        height = 60
    }
    velocity {
        walk.fwd = 2.4
        walk.back = -2.2
        air.gethit.groundrecover = -1.5, -3
    }
    movement {
        airjump.num = 1
    }
}
```

Values are written exactly as CNS writes them, tuples included, and are read
back under the same names: `walk.fwd = 2.4` answers to `const(velocity.walk.fwd)`
**and** to `const(velocity.walk.fwd.x)`, which is the form the common states
use. A two-component value answers to `.x` and `.y`.

Entries written bare at the top of the block, outside any section, match
Ikemen GO's `[Constants]` — named rather than measured values, asked for
without a prefix:

```fuse
constants {
    StateDizzy = 6565300
}
```

Until this block existed a character could never be *fully* transcribed: one
`[Files]` slot had to keep pointing at a `.cns` purely to carry numbers, and
renaming that file to `.fuse` dropped every constant in silence, because the
loader then read constants only from non-script files. A walk velocity of zero is
a character that cannot walk, and no state count or move list shows it.

## Button remapping

MUGEN's `[Remap]`: which logical button a physical press is seen as.

```fuse
remap {
    x = a
    y = b
    z = c
}
```

Buttons only — directions are not remappable. Two physical buttons may map to
one logical button, which is how a character offers the same attack on either
punch. 407 characters in this archive declare one; ten of them genuinely swap
their punches and kicks.

## Comments

Three forms, all equivalent:

```fuse
// to end of line
# to end of line, for anyone coming from a .cfg
/* a block, which nests, so commenting out a commented-out block works */
```

A converted file uses the block form inline to preserve something the original
said but the language will not repeat — a trigger the loader folds to zero, for
instance, becomes `if false /* was: … */`. (One it recovers into a real program
is kept as `cns("…")` instead; see [Converting](#10-converting).)

## `assert` — saying what a state is for

A CNS author can only write what a state *does*. What it is *for* lives in
their head, and the moment anyone edits it — including the same author a year
later — nothing notices that the two have come apart. Most of what goes wrong
in this archive is that shape: a state that used to exit and no longer does, an
attack that used to hit.

FUSE lets the intent be written down, next to the thing it is about:

```fuse
state 1010 (type: S, movetype: A, anim: 1010, ctrl: 0) {
    assert exits
    assert no self loop

    if AnimElem == 3 {
        HitDef(attr: S, NA, damage: 40, hitflag: MAF)
    }
    if AnimTime == 0 {
        ChangeState(value: 0, ctrl: 1)
    }
}
```

**An assertion compiles to nothing.** The engine never sees it, it costs a
frame nothing, and it cannot change behaviour — which is the only way a claim
*about* behaviour is safe to write. What reads it is the checker, which
compares the claim against the state and reports where they disagree.

**Six claims, and they are checked in two different places.** `exits`,
`no self loop` (where the destination is a number), `hits` and `harmless` are
settled by *reading the state*, so `oxtool fuse` reports them without running
anything. `exits within N ticks`, `reachable`, and `no self loop` where the
destination is an expression cannot be settled that way at all — a state whose
only exit is gated on a velocity the animation never supplies contains a
`ChangeState` and still never leaves. Those are checked by **`oxtool assert`**,
against a real fight, from outside the simulation: `oxyde-cns` cannot depend on
`oxyde-core`, so the checker structurally cannot reach `step()`.

A claim that was never exercised comes back `unproven` and is never folded into
"held" — the runtime form of the rule that an assertion which cannot fail is
worse than none.

| claim | holds when |
|---|---|
| `exits` | some path leaves the state |
| `no self loop` | nothing changes to this state's own number |
| `hits` | a `HitDef` or `Projectile` is issued |
| `harmless` | none is |

A claim the checker cannot settle is reported as
`assert-not-understood` rather than quietly passed. **An assertion that never
fails is worse than none**, because it reads as a guarantee.

### Why this is the feature FUSE is for

Neither MUGEN nor Ikemen GO has anywhere to put this. Everything else FUSE does
— braces, `if`, `commands`, `constants` — is a better way to write what CNS
already expressed. This expresses something CNS cannot, and it is checkable
without running the game.

`assert exits` in particular catches, before a character is ever fought, the
fault that the runtime cycle detector finds after — and names the state instead
of a symptom.

## `import` — one copy of the common states

Every character in this archive ships its own copy of the common states,
because MUGEN gave authors nowhere else to put them. A thousand copies of the
same walk cycle means a fault in it is a thousand fixes, and this project has
already had to make several of those.

```fuse
import "common/guard.fuse"
import "common/movement.fuse"

// Everything from those files, except state 20, which is mine.
state 20 (type: S, physics: S, anim: 21) {
    assert exits
    if command == "holdfwd" { VelSet(x: 2.4) }
    if command != "holdfwd" { ChangeState(value: 0) }
}
```

**The importing file wins.** A state it defines itself replaces one of the same
number from anything it imports, so a character takes the shared set and
overrides only what it actually needed to change. Between two imports the later
one wins — the same rule, applied consistently rather than as a special case.

That is exactly what authors have been doing by hand with copied files for
twenty years. This makes the copy unnecessary; it does not make the override
harder.

### The two guards

A module system without these is a hang and a stack overflow waiting to be
found by content:

* **Cycles terminate and are named.** `a` importing `b` importing `a` reports
  `import "a.fuse" is circular`, and the states it *could* reach are still
  merged rather than the whole file being thrown away.
* **Nesting is capped at eight.** A chain longer than that is a mistake, and a
  much longer one is hostile.

A missing file is an error naming the path, never a silent empty merge — a
character quietly missing its common states is precisely the fault this project
spent a session chasing.

### Proven end to end

A character whose `.def` says `st = mine.fuse`, where `mine.fuse` is

```fuse
import "lib/common.fuse"
state 20 (type: S, physics: S, anim: 20, ctrl: 1) { … VelSet(x: 4.8) … }
```

loads with the library's full hundred states, and walks at **4.08** where the
stock character walks at **2.04**. The import supplied everything; the local
state 20 replaced one thing.

### What a computed state number does

Nothing. `state (1000 + var(1))` cannot be compared with another state number
at parse time, so it never overrides and is never overridden; both are kept.
Guessing there would be worse than leaving it alone.
