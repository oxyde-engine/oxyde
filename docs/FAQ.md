# Frequently asked questions

Straight answers. Where a claim is tested, the test is named; where something is
*not* supported, it says so — but the short version is that Oxyde runs the content
you already have and gives it a modern engine around it.

## Compatibility

### Can Oxyde run my M.U.G.E.N characters?

Yes — directly, with no conversion and no import step. A character's `.def`,
`.cns`, `.cmd`, `.air`, `.sff`, `.snd` and `.act` files load exactly as they are.
Point Oxyde at an existing MUGEN installation and it reads your `select.def` and
plays the whole roster. Nothing is copied, rewritten or locked to Oxyde's own
format; the same folder still works in MUGEN afterward.

### Which M.U.G.E.N versions?

All of them that have content: **DOS MUGEN, WinMUGEN, 1.0 and 1.1**. Oxyde reads
SFF v1.01 and SFF v2.00/2.01 (RAW, RLE8, RLE5, LZ5 and embedded PNG), `.act`
palettes including MUGEN's reversed byte order, `.air`, `.snd`, and the
`[Options]`/`[Rules]`/`[Config]` limits and key bindings from `mugen.cfg`. Every
one of WinMUGEN's **93 state controllers** executes — including a couple that
exist in no character in the wild. Each era was tested against real content from
it; an era with no content to test is reported as *untested*, never as
"supported."

### Does it run Ikemen GO content?

Yes. **ZSS is read in full** — every `.zss` file Ikemen ships parses and runs.
Ikemen GO's triggers and state-controllers are recognised, SFF v2 is verified
against Ikemen's own 1.1 characters, and Ikemen's glTF/GLB 3D stage backdrops
draw on the GPU path. The one thing Oxyde does **not** take is Ikemen's
Lua-scripted screenpack *layout* — Oxyde's screens are MUGEN `system.def`, and it
uses Lua for game modes, AI and mods instead. So most Ikemen characters and
stages drop in; an Ikemen *screenpack* built on Lua layout does not.

### Will my characters play the *same* as in MUGEN?

That is the whole point, and Oxyde treats it as something to prove, not promise.
The same files run with no conversion. Where WinMUGEN and the 1.1 beta disagree,
Oxyde's behaviour is pinned to the MUGEN manual, with the original engine (run
under Wine) as the tie-breaker when the manual is silent. A large test library is
the other check: when a rule is ambiguous, Oxyde follows what the **2,500+ real
MUGEN characters it is tested against** actually assume (a test corpus — none of
them ship with the engine; you bring your own). One difference runs in your favour — WinMUGEN silently
drops a mistyped trigger, and Oxyde implements the full controller set rather than
failing quietly, so a move that never worked "right" in MUGEN can start working.

### What happens to my broken or half-finished characters?

They still load, and Oxyde can tell you *why* they misbehave instead of just
crashing. `oxtool audit` scores how much of a character actually works and points
at the faults; `oxtool validate` flags files that aren't what they claim to be;
and `oxtool repair` can fix common breakage — every repair is backed up once and
`oxtool revert` undoes it, so nothing is a one-way change. A character that only
half-ran in MUGEN often runs further here, and you can see the difference measured.

### Do I have to convert anything, or learn a new format?

No. Nothing has to be converted and nothing has to be rewritten to play. FUSE
(below) and the toolkit are there if you want them, but they are always optional —
the default path is "unzip, drop your `chars/` in, play."

## Why Oxyde

### Why bother? What do I actually gain?

A 25-year-old engine, running the content you already love — but with the
limitations that made it feel its age taken away. You keep every character, stage
and screenpack; what you gain is the engine wrapped around them:

- **Online that actually works** — rollback netplay that can't desync, not the
  laggy, delay-based netcode bolted onto older builds.
- **Replays and tournaments you can trust** — a saved match replays bit-for-bit,
  so a result can be re-watched or verified instead of taken on faith.
- **Modern displays** — HD/UHD sprite tiers and a 2.5D depth axis, so classic art
  looks sharp on a modern screen instead of blocky and stretched.
- **A toolkit that works *for* you** — audit, repair, convert, diff, replay and
  render any character from the command line.
- **New ways to play** — bring-your-own-characters online, a content-less join
  mode, universal modern mechanics on every fighter, and built-in brawler modes.

If your content runs in MUGEN today, it runs in Oxyde today — and everything above
comes with it for free.

### What can Oxyde do that M.U.G.E.N and Ikemen can't?

One property underpins all of it: Oxyde's simulation is **deterministic**. Given
the same inputs, two machines produce a bit-for-bit identical match — *even across
different CPUs* (proven x86 vs ARM on real hardware, not emulation). Old engines
can't promise that, and it's the thing everything below is built on:

- **Rollback netplay** that stays in sync frame for frame, with spectating and
  replays that are exact recordings of the real match, not re-simulations that can
  drift.
- **Bring-your-own-characters (BYOC).** Pick a fighter your opponent doesn't own
  and the match *still happens* — their copy pulls the character over the
  connection, verifies it by content hash, and plays. No "you must both have the
  same roster." Validated between two separate machines of different
  architectures.
- **Corrosion.** Join a live match holding *none* of the content: an ~18 MB binary
  in an empty folder plays the host's entire archive, your side sending only
  button presses. A friend can be in your game in the time it takes to download a
  single file.
- **Universal mechanics.** Chip damage, teching, bursts, parry, push-block and a
  tag button, added by the engine to *every* character — whether its author ever
  wrote them or not. A twenty-year-old character gets modern defensive options it
  was never coded with.
- **HD / UHD sprite tiers and a 2.5D depth axis**, so the same art scales cleanly
  to modern resolutions and sits in a sense of space.
- **`oxtool`** — a headless command-line engine that reads the exact same data as
  the game: convert, audit, diff, repair, replay and render any character,
  scriptable and deterministic. Nothing in the MUGEN/Ikemen world has an
  equivalent.
- **Built-in modes** — **Knuckle Up**, a belt-scroll beat-'em-up that turns your
  roster into brawler heroes, **Last Stand** horde survival, and tournament
  rulesets declared as plain data.

### Do I have to learn FUSE?

No. FUSE is Oxyde's own scripting language — clearer than CNS, with real boolean
logic — and `oxtool` can transpile your existing CNS or ZSS into it for you if you
ever want to read or edit a character more easily. But your content runs untouched
either way; FUSE is a convenience for authors, never a requirement for players.

### Can I keep modding and writing AI?

Yes, and with more room than before. Oxyde runs Lua for game modes, character AI
and mods in a sandbox — only plain data crosses the boundary, never engine
internals — so a mod can't desync a match or corrupt the simulation. The
declarative mod surface (screens, shaders, story, an SDK) is being widened to match
Ikemen's reach without giving up determinism.

## Online play

### Does it have online play? Rollback?

Yes — deterministic rollback netplay over UDP, one port to forward. Because the
simulation can't desync, both players always see the same match, and spectators
and replays see it too — exactly, not approximately.

### Can I play online with someone who has a different roster?

Yes — that's **BYOC**. Bring a character the other player lacks and their build
fetches it over the connection, verifies it by content hash, and the bout plays
instead of being refused. It's opt-in on both sides and transfers sandboxed data,
never code — so there's no "we both need the exact same install" anymore.

### Can I play if I have no characters installed at all?

Yes — that's **Corrosion**. A content-less client joins a host over the network
and plays the host's whole archive, receiving the picture and sending input. With
sharing off (the default) it needs nothing on disk and downloads nothing — the
host's game simply runs, two-player, over the wire.

### I run tournaments / I stream. Is there anything here for me?

Yes — this is where determinism pays off most. Every match can be saved as a
replay that plays back bit-for-bit, so results are verifiable and brackets can be
re-watched or audited after the fact. Spectating is exact rather than a separate
re-broadcast, and tournament rulesets (round counts, timers, damage and the rest)
are declared as plain data you can version and share. A disputed round is settled
by replaying it, not by arguing about it.

## Practical

### Is Oxyde free?

Yes — it's **freeware** for non-commercial use. Play, make characters, stages,
screenpacks and mods, run tournaments, stream and record. **Everything you make is
yours** — Oxyde claims no rights over your content. You may redistribute the
complete, unmodified package for free.

### What platforms does it run on?

**Linux and Windows**, each as a single portable binary — it resolves its system
libraries at run time, so one build keeps working across an OS upgrade and there's
nothing to install. It also runs on **ARM** hardware, and because the simulation
is identical across CPUs, an ARM machine and an x86 machine can play each other
online without a hitch.

### How big is the download, and what do I need to run it?

Small. The engine is one binary, and it **boots and plays the moment it unzips** —
the UI, the common states and a reference fighter and stage are built in, so you
can try it with zero author content and drop a MUGEN install in beside it
afterward. No installer, no runtime, no account.

### Does it need a graphics card?

No. Oxyde renders on the CPU by default and runs without a GPU — it'll run on a
laptop or a small ARM board. A GPU path is available for the heaviest extras (HD
shaders, 3D stage backdrops), but the game plays fully without one.

### Is it a drop-in replacement for my MUGEN setup?

Effectively yes — aim it at your game root and it reads your `select.def`,
screenpack, characters and stages, and plays them. It adds its own modes and
online features on top; it doesn't take anything away, and it doesn't change your
files.

### Can Oxyde make my characters 3D?

Not as 3D models — Oxyde is a 2D sprite engine, and the hand-drawn sprite art *is*
the content; there's nothing available that turns a 2D character into a faithful 3D
model. What Oxyde offers instead is HD/UHD sprite tiers and an Ikemen-style 2.5D
depth axis, so 2D characters look sharp and sit in a 3D space. (Ikemen's glTF 3D
stage *backdrops* are supported.)

### Is it still being worked on?

Yes — actively. The current release is v0.37.0, and development is ongoing: online
features, the toolkit and compatibility are all moving forward, with the
determinism guarantee held fixed so nothing that already works can quietly break.

### How do I get started?

Download the release for your platform, unpack it, and run `./oxyde` from the
folder. It boots even with no author content, so you can try it immediately, then
point it at a MUGEN install or drop your characters into `chars/` and go.

---

See also: [COMPATIBILITY.md](COMPATIBILITY.md) for the format-by-format detail,
[VS-MUGEN.md](VS-MUGEN.md) and [VS-ENGINES.md](VS-ENGINES.md) for the head-to-head,
[NETPLAY.md](NETPLAY.md), [BYOC.md](BYOC.md) and [CORROSION.md](CORROSION.md) for
the online features, and [CONFIGURATION.md](CONFIGURATION.md) for every setting.
