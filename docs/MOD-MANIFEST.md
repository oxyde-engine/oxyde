# The mod manifest — `mod.toml`

A mod is a `.lua` file, or a folder with one in it, and nothing in
[SCRIPTING.md](SCRIPTING.md) requires anything more. A `.lua` dropped in
`mods/` loads, runs and ships without a line of metadata. `mod.toml` does not
change that — the engine still discovers mods by scanning, still gates them on
`mods = 1`, and a mod without a manifest is exactly as valid as it was.

What a manifest adds is **identity**: a name that is not the filename, a
version a user can read before installing, the author to credit, the hooks the
mod actually uses so a packager and a user can see its shape without opening
the Lua, and the engine version it was written against so an install that
cannot run it says so instead of latching it off mid-bout. It is the file a
*distributed* mod carries — the one you download, the one a manager lists, the
one a store page is built from — and it is optional precisely because the mod
you wrote this afternoon and dropped in `mods/` is not any of those things yet.

This document is the whole of the format. The running engine does not yet read
`mod.toml` — it discovers mods by filename (a bare `.lua`, or a folder whose
entry file is `init.lua`) — so the loader that consumes the manifest is wired
separately; the spec is fixed here so a mod authored today packages correctly
for when it lands. The behaviour described below is what that loader does.

---

## Where it goes

Beside the mod it describes, named `mod.toml`:

```text
mods/
  escalation.lua            a bare mod — no manifest, still valid
  bossrush/
    bossrush.lua            a folder mod...
    mod.toml                ...with a manifest beside its entry file
```

A manifest describes **one mod**. A folder with two unrelated `.lua` files and
one `mod.toml` is a mistake the loader reports rather than guesses at: the
manifest's `entry` says which file is the mod, and the rest are either data it
reads or a packaging error.

A bare `mods/foo.lua` with no folder has nowhere to put a `mod.toml`, and that
is fine — it is the unpackaged shape, and `name` falls back to the filename.
To carry a manifest, give the mod a folder.

---

## The format

One table, `[mod]`. TOML because a flat table of strings and lists is all a
manifest is, because it is a format a packager and a store page already
understand, and because a human has to be able to read and fix one by hand.
(The engine's own config and rulesets are an INI dialect, not TOML; the
manifest is packaging metadata, read by a manager rather than the simulation.)

```toml
[mod]
name               = "Boss Rush"
version            = "1.2.0"
author             = "joe"
description         = "The four hardest characters installed, best of one."
engine-min-version = "0.36.0"
hooks-used         = ["modes", "matchup"]
entry              = "bossrush.lua"
homepage           = "https://example.invalid/mods/bossrush"   # optional
```

That is a complete, valid manifest. Everything below is the field-by-field
meaning and the rules a loader checks it against.

---

## The fields

### `name` — required

What the mod is called, for a human. Free text, not an identifier: `"Boss
Rush"`, not `bossrush`. It is what a mod manager lists and what the diagnostics
screen prints when something goes wrong, so it is worth it being the name you
would say out loud.

It is **not** the mod's identity to the engine. A scripted mode's `slug` (see
[SCRIPTING.md](SCRIPTING.md#modes--new-game-modes)) is still the id the engine
and a screenpack share, and a mod's remembered-state key is still its filename.
`name` renames neither; it is the label, not the handle, and two installed mods
sharing a `name` is a cosmetic clash the loader notes, not a conflict it
refuses.

If the manifest is absent, `name` is the entry file's stem — `escalation.lua`
is "escalation" — which is exactly what the diagnostics printed before
manifests existed.

### `version` — required

The mod's own version, as `MAJOR.MINOR.PATCH`. This is the mod's, not the
engine's — a user reads it to know whether the copy they have is the copy a
bug was fixed in, and a manager reads it to know whether an update is an
update. Semantic versioning is the convention, not a rule the loader enforces
beyond the three-number shape: the engine never decides what a version *means*,
only compares `engine-min-version` against its own.

### `author` — required

Who to credit, and who to reach. Free text; an email or a handle is as valid as
a name. Required because an unattributed mod in somebody's `mods/` folder a
year from now is a mod nobody can ask about, and the point of a manifest is the
copy that travels.

### `description` — recommended

One or two sentences: what the mod does, in the words you would use to decide
whether to install it. This is the store-page line and the manager's
one-liner. Keep it to what the mod *is* — the how lives in a `README.md` beside
it, which the manifest does not replace.

Optional, but a mod distributed without one is a mod nobody can tell apart from
the next one in the list.

### `engine-min-version` — recommended

The oldest Oxyde that runs this mod, as `MAJOR.MINOR.PATCH`. The current engine
is **0.36.0**; a mod that uses only what this document and
[SCRIPTING.md](SCRIPTING.md) describe sets `engine-min-version = "0.36.0"`.

This is the one field the engine acts on. A mod whose minimum is **newer** than
the running engine is one that will call hooks or read payload fields this
engine does not have — a `screens` vocabulary word added later, a `view` field
that is not built yet — and the honest failure is to **report it at load and
not run it**, the same way a syntax error is reported at load. The dishonest
failure is to run it until the frame it reaches the missing thing and then
latch it off, which looks to the player like the mod breaking rather than the
mod needing a newer engine.

Omitting it means "I make no promise", and the mod is loaded and left to fail
the ordinary way if it reaches something that is not there. Set it. A mod that
names the version it was written against is a mod whose failures have an
explanation.

There is deliberately no `engine-max-version`. The engine's compatibility
promise runs forward — a mod written against 0.36.0 is meant to keep working —
and a mod declaring a ceiling it was never tested against would turn a future
engine's success into a refusal for no reason.

### `hooks-used` — recommended

The hooks this mod implements, as a list, from the fixed vocabulary:

```toml
hooks-used = ["modes", "rules", "matchup", "ai", "flow", "hud", "layout"]
```

`"screens"` is **not** a hook — it is data a declared mode carries, not a global
function (see [SCRIPTING.md](SCRIPTING.md#screens--the-shape-of-a-run)) — so it
does not belong in this list. A mode with a declared sequence lists `"modes"`.

Every name is one of: `modes`, `rules`, `matchup`, `ai`, `flow`, `hud`,
`layout`. A name outside that set is a typo the loader reports with the nearest
real one, the same way an unknown rules knob is reported.

This field is a **declaration, checked against the code, not a substitute for
it**. The engine still calls the hooks a script actually defines and ignores
the rest; `hooks-used` does not register anything or switch anything on. What
it buys is a packager and a user seeing a mod's shape — "this one drives an AI
and draws a HUD" — without reading the Lua, and a loader warning when the two
disagree: a manifest that claims `ai` for a mod that defines no `ai` is either
a stale manifest or a mod that forgot to define its hook, and both are worth a
line on the diagnostics screen. It never *refuses* over the mismatch; a wrong
manifest is a worse reason to not run a working mod than it is to print a
warning.

### `entry` — required for a folder mod

Which file in the folder is the mod. A string for the common case, a list when
a mod is split across files loaded in order:

```toml
entry = "bossrush.lua"
```

```toml
entry = ["lib.lua", "bossrush.lua"]        # lib first, then the mod
```

Paths are relative to the manifest, and may not climb out of the mod's folder:
`entry = "../other.lua"` is refused, because a mod reaching into a sibling is a
mod that does not package. A listed file that is not there is reported by name.

For a bare `mods/foo.lua` with no manifest there is no `entry` to write and
none is needed — the file is the mod. `entry` exists so a folder mod does not
have to be named `init.lua` to be found, and so a mod with data files beside it
says plainly which of them is the code.

### `homepage` — optional

A URL: where the mod lives, where to report a bug, where the fuller
documentation is. Printed by a manager, never fetched by the engine — the
engine does not touch the network for a mod, and a manifest field is not going
to be the first thing that does.

---

## What a loader checks

In the order a failure matters, and following the same policy every hook does —
*report, do not refuse, unless refusing is the honest answer*:

| Condition | What happens |
|---|---|
| No `mod.toml` at all | Fine. The mod loads unpackaged; `name` is the filename. |
| Malformed TOML | Reported at load; the **manifest** is ignored, and the mod loads as if unpackaged rather than not at all — a broken label is no reason to lose a working mod. |
| Missing `name`, `version`, `author` | Reported; the field falls back (`name` → filename) or is left blank, and the mod still loads. |
| `version` / `engine-min-version` not `MAJOR.MINOR.PATCH` | Reported; treated as absent. |
| `engine-min-version` **newer** than the running engine | Reported at load, and the mod is **not run** — the one case a manifest refuses, because running it would fail worse later. |
| `hooks-used` names an unknown hook | Reported with the nearest real name; the rest of the list stands. |
| `hooks-used` disagrees with the defined functions | Reported as a warning; the mod runs on the functions it actually defines. |
| `entry` missing, or naming a file that is not there | Reported by name; if nothing loadable remains, the mod does not install. |
| `entry` climbing out of the mod's folder | Refused. |

Every one of these shows on the Problems screen and prints from `oxtool mods
<root>` without starting the game — the same place a bad rules knob or a failed
mode already reports. A manifest exists to make a mod's failures legible before
a player ever sees them; a manifest whose own errors were silent would defeat
its own purpose.

---

## The smallest valid manifest

```toml
[mod]
name    = "My Mod"
version = "0.1.0"
author  = "me"
entry   = "mymod.lua"
```

Add `description` and `engine-min-version` before you hand it to anyone else.
`hooks-used` and `homepage` when the mod is worth listing. Everything in
[SCRIPTING.md](SCRIPTING.md) still applies unchanged — the manifest describes
the mod; it does not alter what the mod may do.

See [MODDING.md](MODDING.md) for the end-to-end story, and `docs/../modules/`
for a `mod.toml` beside every template and worked example.
