# Content validation

Oxyde checks that your content is what it says it is.

A file's extension is a claim: `kfm.cns` claims to be CNS, `Arroyo.cns.fuse`
claims to be FUSE, `common1.cns.zss` claims to be ZSS. Nothing used to check that
claim, and so a file could quietly be something other than it looked — a `.cns`
renamed to `.fuse` but never converted, a `.def` pointing at a constants file
that is not there, a half-finished hand conversion with two languages in one
file. Each of those loads *wrong* rather than loudly, and the most visible of
them is the one where a character with no size constants is drawn four times too
big.

Validation is the answer to that silence. At load, once per character, Oxyde
reads the content and reports — in a log, and on request — where it does not
match what it claims to be. It is **detection only**: it never converts,
rewrites or repairs anything. Turning CNS into FUSE is a tool's job
(`oxtool fuse`), done on purpose, with a backup; the engine only tells you it
needs doing.

None of this touches the simulation. Validation runs at load, never inside a
frame, so it cannot change how a match plays, what a replay replays, or what two
machines agree on over the net. It also costs nothing you would notice: it is a
single linear scan of files the engine was already reading.

## What it checks

**1. Reference integrity.** Every file a `.def` names in `[Files]` — its
constants/state file, its command file, its state files — is checked to exist.
A declared-but-missing constants file is the cause of the oversized-render
problem: with nothing to set `xscale`/`yscale`, the character falls back to the
engine's default scale. That fallback is no longer silent.

**2. Content coherence.** Each script file is read and matched against the
language its extension claims, by the surface tokens that only one of the three
languages uses:

| Language | Told apart by |
|---|---|
| CNS  | `[State N, M]` controller sections, `;` line comments |
| ZSS  | brace controllers `velSet{x: 4;}`, `let $name` locals |
| FUSE | `==`, `//` and `/* */` comments, `x in [a, b]`, `fn`, `commands {` |

From that it reaches one of a few verdicts:

* **Coherent** — the content is the language the extension claims. The healthy
  case, and it says nothing.
* **Foreign** — the content is coherently *one* language, but not the declared
  one. A `.cns` renamed to `.fuse` without being converted lands here.
* **Mixed** — tokens from more than one language appear in the same file: a
  half-finished hand conversion, or a block pasted in from another engine. The
  engine reads one language per file, so this is named rather than mis-run.

It is deliberately conservative. A language is only believed present once at
least two of its exclusive tokens appear, so a single incidental token never
flips the verdict, and when nothing is certain it says nothing at all. A false
alarm on a working character is worse than silence.

**3. Freshness.** A transpiled `.fuse` whose hand-editable source (`.cns`/`.zss`)
is newer on disk means the engine is running an out-of-date conversion — you
edited the source and forgot to re-run `oxtool fuse`. This is reported only when
both files' timestamps are available (an on-disk working tree), never for
packaged or archived content.

## A mixed roster is fine

Validation flags a file that mixes languages, not a *roster* that does.
CNS characters, ZSS characters and FUSE characters coexisting in one game is the
intended, everyday case — the three languages are front-ends that all compile to
the same internal form before the first frame, so by the time a match runs there
is no "CNS character fighting a FUSE character", only compiled state machines.
Validation has nothing to say about a healthy mixed roster, and says nothing.

## How findings reach you

The governing rule is that **validation is always on, but its loudness is a
policy, not a feature.** You should never be interrupted while you are just
playing.

* **A log file, always.** Findings are written to `oxyde-validate.log` under the
  game root — silently, at full detail, bounded so it never grows without end. A
  player never sees it; it is there when something is wrong and you (or a bug
  report) go looking.
* **The terminal, only if you ask.** Set `OXYDE_VALIDATE` to raise the volume:
  `OXYDE_VALIDATE=fatal` echoes only failures, `OXYDE_VALIDATE=all` echoes every
  finding (developer / debugging mode). Unset — the default — the terminal stays
  quiet. This is the sibling of the engine's other developer dials
  (`OXYDE_AUDIT_TRACE` and the like).
* **On demand, the whole roster.** `oxtool validate <game-root>` is the pull
  report: it sweeps every character and prints what does not match what it
  claims to be, with a summary by severity and kind. `--char <def>` checks one;
  `--strict` exits non-zero if anything is found, for a build gate.

Findings carry a severity, used to decide how far each one travels:

| Severity | Meaning | Default surfacing |
|---|---|---|
| FATAL | the character will not work as authored | log + terminal |
| WARN  | it loads but is degraded or wrong | log only |
| NOTE  | informational | log only |

## What to do about a finding

Validation tells you what is wrong; the fix is always yours to make, with a
tool, on purpose:

* **Foreign** (`content-foreign`) — the file is a different language than its
  name. Convert it with `oxtool fuse <file>`, or rename it to the extension its
  content actually is.
* **Mixed** (`content-mixed`) — finish the conversion, or split the stray block
  out. `oxtool fuse` converts a whole file; it cannot guess which half you meant.
* **Missing reference** (`def-missing-cns`, `def-missing-state`,
  `def-missing-cmd`) — a file the `.def` names is not there. Fix the `[Files]`
  path, or add the file.
* **No size** (`no-size-constants`) — the constants file loaded but declares no
  `[Size]`; add one, or the character renders at default scale.
* **Stale** (`stale-transpile`) — re-run `oxtool fuse` to regenerate the `.fuse`
  from its newer source.

See [FUSE-CONVERSION.md](FUSE-CONVERSION.md) for the conversion itself and
[DIAGNOSTICS.md](DIAGNOSTICS.md) for the in-game problems screen that validation
findings share with the rest of the engine's load-time reporting.
