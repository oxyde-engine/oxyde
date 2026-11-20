# Importing a large download

*How a pile of archives becomes a roster you would actually play.*

This page describes the import pipeline: the stages a large collection of
downloaded content passes through before any of it reaches a playable roster,
what each tool reports, and how to read the results. The counts shown in the
worked examples are illustrative — run the tools on your own content and read
your own.

## The shape of the problem

A big download is not a big roster. It is the same Ryu nineteen times, at
nineteen levels of quality, mixed in with characters that freeze, characters
that cannot be hit, and characters that were never finished. Adding it
wholesale gives you a roster nobody can navigate.

So nothing is added until it has earned a place. Five stages, in order, and
**nothing touches the live roster until the last one**.

```
extract → inventory → deduplicate → fight → decide
staging   count the    collapse     gate     keep only the new,
tree      real defs    copies       verdict  working, unique
```

## 1. Extract, to a staging tree

Into `staging/`, never into your game folder. The point of the gate is that
things can fail it; they cannot fail it from inside the roster.

Note that a single download often unpacks to several *complete MUGEN installs*,
each with its own `chars/`, `data/`, common states and standard opponent. The
later stages treat all of them as one corpus, because the duplication worth
finding is between collections, not inside them.

## 2. Inventory — `oxtool dedupe <root>`

`find_roots` locates every install under the staging tree and walks them as one
corpus. The inventory distinguishes three things that are easy to conflate:

| | |
|---|---|
| `.def` files on disk | every `.def`, including stages, effects and fragments |
| actual character definitions | the `.def` files that define a playable character |
| distinct characters | after collapsing copies (stage 3) |

The first number is always much larger than the second — a character folder
holds many `.def` files — and the third is smaller again.

## 3. Deduplicate — three tiers, not one

Telling "the same character" from "a similar one" uses three signals, in
decreasing strength:

1. **The same sprites.** A character *is* its `.sff`. Fingerprinted by size
   plus a hash of the first and last 64 KB — hashing thousands of sprite files
   end to end is hours of disk for a question the edges already answer.
2. **The same normalised name and author.** Normalising strips the release
   debris authors add — `v2`, `final`, `(2008)` — but **keeps digits**, because
   `Android 16`, `17`, `18` and `20` differ in the number alone. Dropping them
   collapses those four characters into one.
3. **A near-identical name**, which is never used on its own: `Ryu` and
   `Evil Ryu` are not the same character.

The tiers matter, and the tool reports them separately:

| tier | meaning |
|---|---|
| byte-identical sprites | certainly redundant |
| same character, same author | redundant; keep the best |
| same character, **rival authors** | a *choice*, not redundancy |

Nineteen authors' Ryus are nineteen takes on Ryu, not eighteen mistakes.
Collapsing those needs `--strict` and is a judgement about the roster, not
about duplication.

## 4. Fight everything — `oxtool gate --tsv`

Every copy is fought against the standard opponent, because **which release is
better cannot be read off its metadata**. A v2 that freezes is worse than the
v1 that does not, and only running both finds that out.

`gate --tsv` writes one line per character with a verdict — `ACCEPT`, `WARN` or
`REFUSE` — and the raw measurements behind it. On a large staging tree a large
fraction of the download is typically refused: that is the "roster of useless
characters" the gate exists to prevent, now measured rather than guessed.

### Two harness bugs this stage can produce, and what they teach

Both look like results. Neither is.

- **Every character refused at 0%.** This happens when the sweep is pointed at
  `staging/`, which is not a MUGEN root — the `data/` folder, the common states
  and the standard opponent live inside each collection. The same character can
  score `REFUSE 0%` one way and `ACCEPT 88%` the other. A systematic zero looks
  exactly like a broken collection. **Each collection is its own root.**
- **A run vanishes silently.** Multiple workers appending to one inherited file
  descriptor lose rows and leave a block of NUL bytes at the head of the file,
  with empty `stderr` and perfectly valid surviving rows. Each worker writes
  its own file.

A third is pure luck to catch: `grep '\.def'` is case-sensitive, and a fair
number of characters ship their definition as `.DEF`.

> The standing lesson, again: **check the tool before the roster.**

## 5. Decide — `oxtool dedupe --compare`

Copies are ranked by a strict order, not a weighted sum:

1. verdict — **a working character beats a broken one at any score**
2. fewer refusals, then fewer warnings
3. more specials that connect, then more attacks that land
4. function score, then distinct states
5. path, so the run is reproducible

Step 1 is the whole point. A naive "keep the newer version" or "keep the
bigger file" gets exactly this case wrong.

The output is `dedupe-plan.tsv`. **It moves nothing.** It is a proposal — the
set of characters that are new, working and unique, with the copy to keep for
each. A large download typically yields far fewer keepers than its raw character
count, which is the honest result of the gate.

## Cost

Fighting is the expensive stage: on the order of a few seconds per character
per pass, parallel across cores, and characters are fought twice when the
second pass adds measurement columns. A full download is minutes to an hour of
wall clock, not days.

## Reproducing the pipeline

```sh
oxtool dedupe  staging --out inventory.tsv      # inventory + duplicate tiers
oxtool gate    <collection> <char.def> --tsv    # one line per character
oxtool dedupe  staging --compare results.tsv    # writes dedupe-plan.tsv
oxtool troubleshoot <collection> <char.def> --symptom "..."
```

Each collection is its own root.

---

# Applying the import

Once `dedupe-plan.tsv` is approved, the keepers are copied into the game folder.
The whole roster is then **re-fought in its new home**, because a character's
score is measured against `chars/kfm/kfm.def` inside *that* installation and
does not travel with the character.

## Rejecting

The reject scope is: **broken** (froze, NaN, left the playfield), **cannot be
hit**, **cannot hit**, **no special that comes out**. Characters that fail are
first offered to `oxtool normalize` (below); those that still fail are **moved
to `rejected-characters/`, not deleted**, with a manifest recording where each
came from. A folder is only moved when *every* character def inside it failed.

## Repairing: what `normalize` is worth

`oxtool normalize` derives a missing `Clsn2` hurt box (or `Clsn1` attack box)
from the character's own `size.ground.back/front` and `size.height`, writes it
into the `.air`, **re-fights the character, and keeps the change only if a
refusal disappeared and the score did not fall**. Otherwise the file is
restored byte for byte and the backup deleted.

The mechanism is proven: a healthy character stripped of every `Clsn2` drops
to `REFUSE 85%`, unkillable, and `normalize` returns it to `ACCEPT 98%`.

In practice it repairs almost none of the real candidates, and that is the
useful finding: characters that fail the gate are rarely failing from a missing
collision box. They are missing a `HitDef` in every state, or declare no
specials at all — structural incompleteness, which no geometry fixes.

## Transcribing to FUSE, and the regression to watch for

`fuseify` converts a character's state files to FUSE. Re-fighting the roster
after a bulk conversion is **not optional**: conversion has historically left
characters newly refused or several points down even while their *shape* —
state count and move count — matched exactly, so `fuseify`'s shape-based
safeguard could not see it. Diffed on a single character, the loss is precise:

```
CNS   walks yes  jumps yes   ACCEPT 92%
FUSE  walks NO   jumps NO     ACCEPT 81%   (32 warnings)
```

Everything else — attacks, specials, blocking, damage — identical, and the
held-direction commands survive conversion looking correct (`/$F`, `/$U`), so
the loss is downstream of them. **Transcription is verified by fighting**,
exactly as `normalize` is. See `docs/FUSE-CONVERSION.md` for the converter
bugs, their fixes, and the `oxtool fuse-verify` gate that enforces "no character
does worse after conversion".

`fuseify` rewrites the `.def` to point at the `.fuse` files and keeps
`<name>.def.cns-backup`; restoring that backup is the revert, and it recovers
the score exactly. Two things to know when scripting the revert:

* the backup's extension is lowercased, so `AOSHI.DEF` has `AOSHI.def.cns-backup`;
* revert on a **verdict** change too, not only on score — a character can fall a
  few points and flip `ACCEPT` to `REFUSE`.

## Re-running the whole pipeline rather than patching forward

Several conversion faults surface only when the *whole* roster is put through
again — non-ASCII command names mangled byte-wise, `.def` files that disagree
with the filesystem about case, and prose inside constants sections. None
produces a diagnostic; all are found by counting what came out the other end
and asking why it is smaller than what went in.

That is the argument for re-running the whole pipeline: **the count is the
test.** Run it with the same tool and the same roster, compare the input and
output counts, and investigate any shortfall.

## Archives

`.zip` and `.rar` both mount as folders and need no unpacking. A character
zipped as `chars/CaptZip.zip` scores `ACCEPT 98%`, identical to the same
character unpacked, and a genuine `.rar` loads and fights. `default = ["rar"]`
is on in `oxyde-vfs`.

## Stages

Stages are not written in FUSE and cannot be. A stage `.def` is declarative
data — `[BGdef]`, `[BG bg0]`, `[Camera]`, `[Bound]`, `[Music]`, plus
`[Begin action N]` blocks in `.air` syntax. There are no statedefs, no
controllers and no triggers, so there is nothing for a *state* language to
express. `fuseify` correctly leaves `stages/` alone.

---

# Keeping the originals beside the FUSE form

A converted character can end up existing only as FUSE. Because the CNS loader
is itself under test, it is worth keeping the **original** author files beside
each converted character — the base archive (the one with `Winmugen.exe`) is a
natural home for them. WinMUGEN does not have to be able to play them; they are
the reference, and Oxyde's CNS loader is what is being tested.

## Which copy is the original

If no per-character provenance survived the first import, it can be rebuilt from
content. Every converted character still has the sprite file it was converted
from, and a sprite file is the one thing no repair ever rewrites, so each is
matched back to `staging/` by the hash of its `.sff`. The copy taken is the
character folder that sprite sits in — found by the sprite's own path inside the
converted folder, **not** by searching upward for a `.def`. Searching upward
copies the wrong folder: a character's `ETC/` or `files/` subfolder instead of
the character (so `GGX_Ky & Sol` arrives without its `.def`). Where one sprite
appears in several collections, the copy whose other files match best wins.

| how the original was found | share |
|---|---|
| a `staging/` copy whose files all match the kept FUSE form | most |
| a `staging/` copy differing only in the `.def` the import edited | some |
| a `staging/` copy differing in one `.cns` | a few |
| a `staging/` copy missing a file the converted folder gained | a few |
| reconstructed from the converted folder with its repairs reverted | none, ideally |

The copies that differ from the matched original — a `.def` path or storyboard
line, occasionally a state file — show how much the first import edited before
converting, which is itself worth recording.

## Does Oxyde load them

`oxtool verify` on the grown archive reports loaded / playable / refused;
`oxtool doctor` reports perfect / playable / repaired-at-load / unplayable.
A healthy archive loads and plays every character, with some loading with
findings and a handful repaired at load time.

## Original against FUSE, by fighting

`oxtool audit` fights each original against its FUSE form with the same battery
and the same opponent; `oxtool ab` compares the two forms tick by tick. On a
faithful conversion the two agree: nothing in the converted set plays worse than
its author's files, mean scores match, and any character that scores higher does
so for a legible reason (one more special lands).

Beware a comparison that changes when the input is fixed. An early pass reported
a handful of characters better or worse; all were misplaced copies — a character
missing its `.def` or part of its art compared against one that had everything —
and re-running on the corrected copies removed them. **A result that changes
when the input is fixed was measuring the input.**

## What WinMUGEN makes of them

Each original can be started in the real `Winmugen.exe` under wine, in a quick
VS against Kung Fu Man, several private WinMUGEN roots in parallel. The verdicts
land in `metrics/winmugen-originals.jsonl` in three buckets:

| WinMUGEN | meaning |
|---|---|
| loaded | the opponent's loader was reached |
| refused with an error | an error dialog, or `Exit with an error.` |
| neither, within the timeout | a hang — no dialog, loader never reached |

Hangs are not refusals, and Oxyde may load a character WinMUGEN hangs on.

The static predictor `oxtool ab --winmugen-check` reads the same characters'
files and is scored against these runs. It agrees with WinMUGEN on the large
majority, calls every refusal it makes correctly, and misses some refusals it
cannot yet see from the files alone — and its misses are the predictor's next
rules, which is what a sweep like this is for.

## Two baselines

`oxtool regress` treats characters its baseline does not know as `new`, so
adding imports does not fail a check — but a baseline should keep meaning the
exact set it was built from. Keep the base roster in
`metrics/regression-baseline.tsv` and the imports in
`metrics/regression-baseline-originals.tsv`, and check each against only its own
characters with `--listed`:

```sh
oxtool regress .. --check ../metrics/regression-baseline.tsv --listed
oxtool regress .. --check ../metrics/regression-baseline-originals.tsv --listed
```

Record the newcomers' fingerprints twice — once in a scratch copy of the grown
archive and once in the archive itself — and confirm the two runs agree to the
bit before trusting the baseline.
