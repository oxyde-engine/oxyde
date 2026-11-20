# Netplay

Two players over the internet, using rollback: your own input is displayed on
the very next frame, and the engine reconciles the other player's input when it
arrives.

## Playing

One side hosts, the other joins. UDP port 7500 by default.

From the title menu, **ONLINE** asks for the sub-mode and then for a role. The
screen shows what it needs you to know rather than assuming you already do:

* the **sub-mode screen** shows this machine's address and port, which is what
  the other player has to type;
* the **HOST** row repeats that address on its hint line;
* **FIND A HOST ON THIS NETWORK** lists the hosts that are announcing
  themselves and connects to the one you pick. Nothing is typed;
* **TYPE AN ADDRESS** opens an address box. A bare IP or host name is enough —
  the configured port is filled in — and what you type is remembered for next
  time;
* the **connecting screen** lists the role, this machine's address, the address
  it is trying to reach, and the input delay, so a failed connection says what
  it was attempting.

## Finding a host on the local network

Two people in the same room do not need to read an IP address out loud. A host
that is waiting broadcasts a small beacon on the game port plus one — 7501 by
default — about once a second, and anybody on **FIND A HOST ON THIS NETWORK**
sees it appear in a list with its name and mode. Choosing a row connects to it.

The address connected to is the one the beacon *arrived from*, not the one the
host believes it has. That is the difference that matters: a machine with a
VPN, a container bridge and two network cards has several addresses and only
one of them works, and the one the datagram came from is by definition the one
that does.

Nothing is discovered across a router, because nothing broadcasts across one.
For a host somewhere else, or on a network where broadcast is blocked, press
**C** on the list to go straight to the address box.

The beacon stops the moment the match starts — there is nothing left to join —
and carries the protocol version, so a host running a different build of Oxyde
is not offered rather than offered and then refused at the handshake.

| `oxyde.cfg` | |
|---|---|
| `[Netplay] port` | The game port. The beacon port is this plus one, so one number still describes the whole of netplay. |
| `[Netplay] name` | What this machine calls itself in the list. Empty uses the host name, then this machine's address. |

## Typing an address with a controller

The address box takes the keyboard *and* the pad. An on-screen keyboard sits
under the box: the d-pad moves, **A** types the key under the cursor, **B**
deletes, **START** or **Enter** connects, **SELECT** or **Escape** goes back.
`DEL`, `CLR`, `CONNECT` and `BACK` are on the keyboard as well, so a pad on its
own can do the whole thing.

While the box is open it owns every key. That is not a detail: a keystroke that
is also a game button would otherwise do two wrong things at once — never
reaching the box, and acting as the button — so on the shipped bindings `s` and
`x` would back out of the box and `a` submit it half-typed, and whether an
address could be typed at all would depend on which characters it happened to
contain.

The same thing can be started from the command line, which skips the menu:

```bash
# Host (needs the port reachable: forward UDP 7500, or use a LAN/VPN address)
oxyde --root /path/to/mugen --host

# Join
oxyde --root /path/to/mugen --join 203.0.113.7:7500
```

The address shown is this machine's address *on its own network*. On a LAN that
is the one to give out; over the internet it is your router's public address
with UDP 7500 forwarded to this machine, or an address from a VPN that puts
both players on one network.

Both sides pick the same characters. The session refuses to start if the two
sides disagree about the matchup (see *Setup hashing* below).

Tune the trade-off in `oxyde.cfg`:

```ini
[Netplay]
port = 7500
; Frames of deliberate input delay. Higher trades a little latency for
; noticeably fewer rollbacks on a poor connection.
inputdelay = 2
; The last host joined, offered again next time.
peer =
```

`F1` in game shows rollback count, worst rollback depth and round-trip time.

## How it works

Both peers simulate every frame immediately, using the local input plus a
*prediction* of the remote one. The prediction is "repeat the last input
received", which is right the overwhelming majority of the time — real inputs
are held for several frames.

When a real remote input arrives and disagrees with what was predicted, the
session restores the snapshot from that frame and re-simulates forward to the
present. Nobody ever waits for the network.

```
frame:        100  101  102  103  104
local  (you): known --------------------->
remote:       known  ?    ?    ?    ?      <- predicted as "same as 100"
                     ^
                     packet arrives saying frame 101 was different
                     -> restore snapshot 101, re-simulate 101..104
```

### Why this is possible at all

Rollback requires that the same state plus the same inputs always produces the
same result, on both machines, every time. `oxyde-core` was built for that
from the start:

* No wall-clock time anywhere in the simulation.
* No float derived from frame duration.
* An explicit RNG (`Rng`, xorshift64*) advanced only by the simulation.
* No I/O inside `Match::step` — sound is a queue the platform drains, so
  playing a sound is not a side effect rollback would have to undo.

The netcode is about 400 lines as a consequence.

### Snapshots

A snapshot is a clone of the whole `Match`. That is a blunt instrument and the
right one: a match is a few tens of kilobytes — sprite and state data live
behind `Arc` and are never copied — and only `max_rollback + 2` snapshots are
retained. Hand-rolled delta encoding would save little and risk exactly the
kind of subtle state omission that produces an unreproducible desync.

### Packet loss

Every packet carries a sliding window of the last 12 inputs, not just the
newest one. A lost datagram therefore costs nothing at all: the next packet
already contains what was missed. This is far cheaper than any retransmission
scheme and is why the engine converges through 20-25% loss.

### Throttling

If the local side gets more than `max_rollback` frames ahead of confirmed
remote input, it stalls rather than continuing — running further would
guarantee a rollback deeper than the retained history can correct.

### Setup hashing

Before the match, both sides exchange a hash of `(p1, p2, stage, bout)` with
the bout's declared settings and its computer seats folded on top. A mismatch
disconnects immediately with "match setup mismatch" instead of starting a game
that would desynchronise a few seconds in.

**The stage is in the hash, by identity.** Bout one is the bout where that
matters, because it is the bout where the two peers resolve the venue
*independently* — from `select.def`'s character-to-stage pairing, or from each
machine's own `stage_index` rotation, and online never offers the stage-select
screen. Two peers put on `stages/oxyde_reactor_core.def` and
`stages/oxyde_rust_cathedral.def` are told `match setup mismatch` before either
simulates a frame; were the stage not in the hash they would both reach
`Running` and share a checksum for frame 150 — two people fighting in two
different places and agreeing about it.

The stage goes in by identity rather than by spelling: the path this machine
loaded, with its separators and its case flattened, and no roster index anywhere
near it. Two installations that spell one stage differently or list their stages
in a different order are fighting in the same place and must not be refused.

**The characters go in the same way.** A roster path is not read off the disk:
`Assets::resolve_character` builds it out of the `select.def` line and checks it
through a VFS that ignores case and takes either separator. Of this archive's
1,051 character entries **451** carry a capital, so two people with the same
roster, typed out by two different people, would be a capital letter away from
being refused a bout they agreed about if the hash did not ignore case as its
own lookup does. A path that finds a stage or a fighter and a path that hashes
to one are the same reading, which is what stops `CHARS\KFM\KFM.DEF` being told
the character is not in its own roster.

### The host decides what the match is played with

Four settings change the *simulation* rather than the picture: the playfield
half-width, `[Game] inputbuffer`, `[Game] introtime` and the rounds it takes to
win. Two people at different values are running two
different games.

Folding **each machine's own** values into the setup hash and refusing a
difference would be a safe answer to a question nobody should be asked, and it
would **refuse legitimate opponents**: two people who had each set `introtime`
to what they like could not fight at all, and a player whose window was 16:9
could not enter a bracket run by a player whose window was 4:3 — because
`Viewport::fit` fills the height, so 1280x720 leaves more width over than
960x720 and the playfield is a different number. Nobody ever chose the shape of
their window as a gameplay setting.

**The playfield is a setting, not a window.** Measured off each machine's live
framebuffer it would be not only different between two people but different on
one machine whenever the window changed: the same seed at 1280x720 and at
640x480 would be two different games, a headless run would depend on `--width`,
and a replay would be reproducible only because it carried the number it was
recorded with. It comes instead from `[Game] playfield`
— `auto`, the default, takes the shape of the window the config file asks for
(`[Video] width` x `height`, or `mugen.cfg`'s), as it stood when the file was
read, and `4:3`, `16:9` or `21:9` fix it — together with the stage, and the
window only decides how the picture is fitted. A window narrower than the
playfield shows more sky rather than hiding a fighter past its edge.

Two installations can still have different
`playfield` settings, and a stage whose art is narrower than the playfield
still narrows it, so it remains a property of the bout that the host names and
the joiner adopts. It does not move under anybody: a peer who resizes their
window, goes fullscreen, or plays at a different size from the host is playing
the same game, fitted to their screen.

**The host declares them and everybody else adopts them.** That is not a new
idea here, it is the idea the rest of the bout already runs on: the host names
the characters and the stage in `Tour::Begin` and `Room::Begin`, and settings
are the same kind of thing — a property of the bout, not of each machine. They
travel beside the characters and the stage, and on the first point-to-point
bout they travel in the `Packet::Sync` that already carries the seed, for
exactly the reason the seed travels there: the seed has always been the host's
to name and the joiner's to take, and nobody ever thought a coin flip on two
machines should have to agree by luck.

A peer adopts for the length of the bout. **Nothing is written to anybody's
config**: the declaration is an overlay the round is built from, so "restore
the player's settings afterwards" is not a step that exists and therefore not
a step that can be skipped on one of the six paths out of a match. A player's
own settings are exactly what they were when the match ends, whether it ended
on a win, a disconnection or a closed window.

**What is adopted is what `Match::step` reads, and nothing else.** Key
bindings, audio, the renderer, the window size itself, the screenpack and the
difficulty preference are the player's own and no peer touches them. The line
is not "is it in the config file" — half of the four are — it is "does a step
read it".

**And the hash is still computed, over the adopted values.** Declaration takes
away the disagreements that should never have existed; it cannot take away the
one that means something is broken. A peer that is handed the declaration and
fails to apply it is about to simulate a different fight, and this engine's
rule is that such a disagreement is a **refusal** and never two simulations.

What is folded in is read back out of the `Match` that was actually built —
`MatchSettings::of`, not the declaration that arrived. Hashing the declaration
would have made the comparison "did we both receive the same datagram", which
every peer passes by construction: the exact fault a tournament bout's hash can
fall into, where both fighters hand shake on a number the host has
sent them and neither can disagree about it. Reading it back means a peer
that applied three of the four fields hashes the fourth as it really is, and is
refused.

Measured, two machines at `[Game] inputbuffer` 4 against 9, `introtime` 1
against 300, first-to-2 against first-to-4, and 960x720 against 1280x720:

```text
                  before                       after
each alone        playfield 160.000 buffer 4 intro 1 rounds 2
                  playfield 213.333 buffer 9 intro 300 rounds 4
handshake         match setup mismatch         Running / Running
frames driven     [0, 0]                       400 of 400, agreed
joiner simulates  its own                      playfield 160.000 buffer 4 intro 1 rounds 2
joiner's config   9, 300, 4, 1280              9, 300, 4, 1280  (untouched)
```

A peer that does **not** adopt is measured too, by handing it the declaration
and throwing it away: both sides end on `match setup mismatch` with zero frames
simulated. It costs one extra round trip when the two machines really were set
up differently — the peer does not answer the `Sync` that carried a declaration
until it has been applied, because a reply carrying a hash that is one frame
from changing would have the host drop it for a disagreement it is in the
middle of fixing. Measured at 31 polls to `Running` against 2 when nothing
needed adopting, and capped: after three handovers the comparison runs anyway,
so a peer that genuinely cannot adopt gets `match setup mismatch` rather than
five seconds of silence and "the other player never answered".

The connecting screen says whose settings are in force, in one row beside the
role and the input delay. Silently rewriting somebody's settings is its own
kind of dishonesty.


**Which seats the computer drives is in the hash too**, as a `CpuSeats`
declaration: a level per match-player slot, folded in at round start and again
whenever a seat is installed. This is the one thing two peers cannot catch any
other way — a computer seat's presses are on neither wire, so a machine that
fields a fighter nobody drives and a machine that fields one the computer drives
send precisely the same input stream. Measured before it was hashed, two peers
declaring level 8 and level 4 on the same seat: both ran, disagreed about every
settled frame, and were eventually dropped as "DESYNCHRONISED". Now they are
refused before the first frame. A declaration with nobody in it folds to the
identity, so an ordinary match hashes exactly as it did.

A mismatch is **answered** rather than only noticed: the peer that spots it
replies with its own hash before dropping, so the other side is told too instead
of waiting for a `Sync` answer that is never coming.

### And the other seventy-odd settings, the same way

Four settings changed the *simulation* and were declared. They were not the
only ones. `Game::spawn_round` writes seven config structs into the `Match`
before a round — `mugen_rules`, `mugen_limits`, `meters`, `parry`, `absorb`,
`tag` and the balance settings — plus `camera_keep_visible` and the round
clock. An audit walked all of them and asked the one question the four were
chosen by: **does `Match::step` read it** (per frame, or at construction where
it shapes the checksummed initial `Match` that `step` then evolves — life and
power scaling are read in `add_player`, but a difference in them diverges the
first checksum just the same). The answer, field by field:

* **Read, and now declared:** all of `mugen_limits` (6), `meters` (20),
  `absorb` (8) and `tag` (4); twelve of `parry`'s fourteen; five of
  `mugen_rules`' fifteen plus its four `burst` sub-fields; five of the six
  balance fields; `camera_keep_visible`; and the round clock. The difficulty
  that resolved `parry.ai` needs no field of its own — its whole effect is that
  resolved `ai`, which is declared, so a joiner adopts the number the host
  arrived at.
* **Not read by any step, and deliberately left local:** `rules.draw_shadows`
  (the renderer's, not the simulation's), `rules.team_1vs2_life` and
  `rules.team_lose_on_ko` (which — see below — nothing in the engine reads at
  all today), and the parry/absorb `effect` and `sound` fields (they set a
  palette flash and queue a sound, and neither the palette-fx nor the sound
  queue is in `Match::checksum`).

The read fields travel as a **210-byte config block** on the
same three carriers the four scalars use — `Packet::Sync`, `Room::Begin` and
the side-zero fighter's `Sync` — declared by the host, adopted as an overlay,
and folded into the setup hash by reading it back out of the built `Match`
(`MatchSettings::of` → `write_sim_config`), never off the datagram. A peer that
receives the block and fails to apply one field of it hashes what it is really
simulating with and is refused, exactly as one that dropped a scalar is.

**One field is refused rather than adopted, on purpose.**
`balance.per_character_damage` is a name-to-multiplier map with no bound, so it
cannot ride a fixed block. What travels is an 8-byte hash of it, and only when
balancing is switched on (off, the map is dead config and both peers hash a
zero for it, so a difference cannot refuse a bout it would never affect). Two
peers with balancing on and different maps are refused — the pre-declaration
answer — rather than desynced; the map itself is not adopted.

**The block does not fit every carrier, and that was measured.** A `Packet::Sync`
with the block is 240 bytes against a `MAX_PACKET` of 512. `Room::Begin` is the
tight one: it also carries a stage path of up to 255 bytes, and header + four
scalars + flag + block + a maximal stage comes to **500** — it fits, by twelve.
A uniform four-bytes-a-field block measured 284 and pushed that to 573, past
`MAX_PACKET`, where the socket drops the datagram and a rematch is silently
refused. The twelve-byte margin is bought by packing fourteen bools into a
two-byte word and encoding the six `Limits` and the tag button as `u16`; the
`f32` fields cannot be shrunk without losing the fraction the hash goes to the
trouble of distinguishing. If a field is ever added, the honest move is to take
the block off `Room::Begin` and lean on the roomier `Sync`.
`room::tests::a_begin_with_a_full_config_block_and_a_maximal_stage_fits` and
`packet::tests::a_sync_with_a_full_config_block_fits_one_datagram` are the
measurements that hold the sizes there.

### Desync detection

Every 30 frames each side sends a checksum of the simulation state at a frame
both are certain to have confirmed. The checksum covers everything that affects
future simulation — positions, velocities, life, power, state numbers, all 60
int and 40 float variables per player, the RNG, explods and projectiles — and
deliberately excludes presentation-only state such as the sound queue and log,
which would otherwise report a desync where none exists.

If the checksums differ the session disconnects and says so, rather than
letting two players watch different fights.

## Verifying it yourself

`oxtool netcheck` runs both peers in one process over a simulated link with
configurable latency and loss, using real characters, and compares the final
state:

```
$ oxtool netcheck . chars/ryu/ryu.def chars/kfm/kfm.def --frames 1200 \
      --latency 8 --loss 4

netcheck
  p1         Ryu
  p2         Kung Fu Man
  link       8 frame latency, 1-in-4 loss, 2 frame input delay

  frames     1200 / 1200
  rollbacks  A 776 (4895 frames, worst 7) | B 776 (4904 frames, worst 7)
  packets    A sent 1200 recv 901 | B sent 1200 recv 901
  wall time  7.28s (330 frames/s including all re-simulation)

  A: p1 life   910 state 5050   pos  1000.00 | p2 life  1000 state 1000  pos  26.09
  B: p1 life   910 state 5050   pos  1000.00 | p2 life  1000 state 1000  pos  26.09

  CONVERGED: both peers agree (checksum 0x56c5585cb4aec1ff)
```

330 frames per second *including* all re-simulation, against a 60 fps
requirement — roughly 5x headroom on one core.

The unit tests in `oxyde-net` cover the same ground against a toy
deterministic simulation, including convergence at 3-frame latency with 20%
loss, zero rollbacks on a perfect link, version and setup mismatch handling,
desync detection, and throttling.

## The connection outlives the match

The result screen offers **REMATCH**, **CHARACTER SELECT** and **QUIT**, and
online all three keep the connection. Without a room a match would be one match
per connection: the host dropping its bout for the title screen while the joiner
reconnects into a fresh one. Measured, the same 1,600 frames of a two-round
match with the room and without it:

| | with a room | without |
|---|---|---|
| screens the two peers end on | `Result` and `Result` | `Fight` and `Connecting` |
| joiner's session | running | re-handshaking |
| rounds won, as each peer sees it | `[0,2]` and `[0,2]` | `[1,0]` and `[0,0]` |
| checksums agree | yes | **no** |

In the "without" column the host had already started a *fresh round one* while
the joiner was still handshaking, and the two machines disagreed about the score
of the match that had just finished.

### Both players choose, and the wider choice wins

Each of you is looking at that menu on your own machine, so a press is a **vote**
rather than a decision, and the menu says what the other player picked and who it
is waiting for. When the two of you disagree the outcome is the wider choice:

    REMATCH  <  CHARACTER SELECT  <  QUIT

The order is not arbitrary. CHARACTER SELECT satisfies somebody who asked for a
rematch — the roster still has the fighter they just used, and picking it again
*is* a rematch — while REMATCH denies somebody who wanted to switch the only
thing they asked for. And nobody should be held in a session they have chosen to
leave. Because the rule is a function of both votes and both machines hold both
votes, neither has to ask the other what to do, and there is no second round
trip and no tie-break on who is host.

### What carries, and what does not

The session carries: `Rollback::adopt` keeps the frame counter, the input rings
and the seats, and only the `Match` inside is replaced. A rematch resumes from the
frame the last match ended on — measured, 1401 to 1402 — where a rebuilt session
would start at zero. The match does not carry: round one, no score, full life.

Both peers freeze on the *same* session frame at the end of a match, because the
verdict is decided inside `Match::step`. That is what makes the handover need no
agreed future frame, and it is checked rather than assumed: the host names the
frame it is on, and a mismatch says so and ends the room instead of playing a
match that slowly comes apart.

### Character select, over the wire

Each of you picks for yourself. Your controller works on that screen whichever
end of the connection you are, and it is **pad 0** — your own keys — on both
machines. The seat and the pad are two different questions and are two different
values: the fight uses `local_slot`, the match player this machine drives, which
is not a pad index, so a joining player uses their own keys rather than P2's.
And the press that takes you to the roster does not choose a fighter when it
gets there. Were side two's picks filled in by *copying* side one's, a networked
match would be the host's character against itself — a placeholder that reads as
a feature. Each machine announces what it is
bringing as a **path**, not a roster index, because two installations do not have
the same roster order; a fighter the other player does not have is reported rather
than silently substituted.

### A lost pick

Every loss on the pick channel is now covered, by two different mechanisms, and
which one applies is decided by whether the session is running.

**Before the first bout** there is no session to acknowledge anything with. The
peer that holds both picks builds its match and leaves the roster, which stops the
pre-match pump — and what covers the window is that a peer whose session exists
but has **not yet answered its handshake** keeps repeating its pick, over the
session channel, while the peer still on the roster reads it off the socket.
Measured, with every host-to-joiner `Pick` dropped until the host left the roster:
the bout started on both machines anyway, the host locking on frame 0, leaving on
frame 15 and resending on frame 30, and the joiner locking and following. With that
term taken out of the resend condition the same run measures the deadlock it
prevents — the host on `waiting for the other player...` and the joiner on
`WAITING FOR THE OTHER PLAYER'S FIGHTER...` for all 1200 frames.

**From the second bout on** the session *is* running, so that term is false and the
pick stops the frame the bout starts. That is the one-frame window `Room::Ready`
closes: both peers announce a hash of the two teams they are holding while the
roster is up, and the host sends no `Room::Begin` until the two announcements
agree, so the frame the bout starts is a frame after the other machine has proved
it got this one's pick. Measured on the harness with that datagram dropped: before,
`room_bout` `[2, 0]` and the joiner reading
`CANNOT START THE NEXT BOUT - MATCH SETUP MISMATCH` 150 frames later; after,
`[2, 2]` and no status at all.

A disagreement that a resend cannot fix is still a refusal, and which end says so
is deliberate: the joiner refuses at `HANDOVER_GRACE`, the host only at twice that.
Both ends refusing on one clock is a race between two counters started by two
arrivals a link delay apart, measured as the host naming the fault and the joiner
reading `PEER LEFT`.

## When the other player goes

Three ways a session ends, and all three now say so.

**They chose to leave.** QUIT on the post-match menu sends a goodbye, and the
other side is told who left rather than being shown "connection lost".

**They vanished.** A pulled cable, a killed process, a laptop lid — none of these
send a goodbye. Without a silence timeout nothing would notice: `Bye` is the only
thing that could set `Disconnected`, so the session would stay `Running` for ever
while `Rollback::advance` returns `false` — it refuses to run more than
`max_rollback` frames past unconfirmed input — and the match would simply
**freeze**, stopping at a frame and still calling itself connected. A frozen game
that says it is connected is the worst of the three possible answers.

There is a silence timeout: five seconds without a single packet ends the
session and names it. It is counted in **polls, not wall time**, because a poll
is a frame and a deterministic session must not acquire a clock — a timeout that
read the wall would make how long a match survives depend on how fast the machine
runs it.

A timeout needs something to time. A session *between* bouts sends nothing at
all — input is what a running match sends, and a menu has none — so without a
keep-alive both players would time each other out on the roster screen. There is
a keep-alive every half second, which also measures the round trip continuously,
since `Ping` is answered with `Pong`.

Five seconds rather than one, because the failure that gets a timeout switched
off is dropping somebody whose connection hiccuped. `INPUT_REDUNDANCY` puts
twelve frames of input in every datagram, so a link has to lose a great deal
before anything is actually missing — and a pinned test runs a link losing every
third packet for fifteen seconds and expects both peers to survive it.

**Whatever the reason**, the room ends and you go back to the title with a line
saying who is gone and why. Staying on the result screen was the other option and
is worse than it sounds: without a room that screen falls back to its *offline*
menu, so REMATCH would quietly start a match against the computer — a different
kind of match than the one you asked for, with nothing but a status line to say
so.

## Chat

Press **Z** on the result, roster, team or connecting screen to open the chat box,
type, and **Enter** or **START** sends. **B** puts it away. A pad types on the same
on-screen keyboard the address box uses.

Composing is deliberately not available during a round — nobody types while
holding a stick, and a box that grabs the keyboard mid-round eats the inputs a
fight is made of — but lines that *arrive* during a round are drawn for four
seconds, because not seeing them is the part that would be rude.

Chat is best-effort and rides the same socket: each line goes out three times with
a sender counter, so a lost datagram costs nothing and a duplicated one does not
read as the other player saying it twice. There is no acknowledgement, because a
reliability layer next to a protocol whose whole design is that it does not need
one is a reliability layer the *match* would end up waiting on. **Nothing here
touches the simulation**: names, chat and votes are never hashed into
`Match::checksum`, never filed as inputs and never written to a replay, so two
peers with different chat logs are not desynchronised.

Everything arriving from the network is cleaned before it is kept — length capped
on a character boundary, and control characters stripped. A name is drawn next to a
life bar and printed into the status line; a newline in one is two rows of HUD, and
a carriage return rewrites the line.

## Your name

One name, in one place. `[Netplay] name` in `oxyde.cfg` was already what this
machine calls itself in the LAN host list, and it is now also what the other
player sees in the room, the chat log, the post-match menu and a tournament
lobby. A second key for "the name in a match" would have been two settings nobody
keeps in sync — whoever changed one would expect the other to follow.

**The file is the store; the engine is the editor.** *CHANGE YOUR NAME* on the
online screen opens the same box and on-screen keyboard the address uses, and
submitting it writes `oxyde.cfg` immediately rather than leaving it for the options
screen to save: a name you have to go and save somewhere else is a name that is
lost the first time you forget. It is on that screen rather than in the options
because that is where you are when you are about to play somebody, and with a
connection that outlives the match you will want to change it between bouts — a
name changed mid-session reaches the other player without a reconnect.

Leave it empty and the machine's own host name is used. An opponent who has set
nothing shows as `PLAYER 1` or `PLAYER 2`, because a blank where a name should be
reads as a bug.

## Tournaments

The other three modes under **ONLINE** are two people playing each other.
**TOURNAMENT** is up to thirty-two, with a bracket, and with everybody who is
not fighting watching the fight that is.

Neither M.U.G.E.N nor Ikemen GO has anything like it, and the reason is not that
a bracket is hard. A tournament needs spectators, and watching a match you are
not in means either a video stream or a deterministic simulation. This engine has
the second one: a whole match is a seed plus one number per player per frame —
which is what makes a replay two kilobytes — so **a spectator is a peer that
receives both fighters' inputs and runs the same simulation**. Two `u16`s a frame
is 240 bytes a second of *payload* — but the relay sends one datagram a frame,
and 28 of every 39 bytes on the wire are IPv4 and UDP header, so a spectator
really costs **18.7 kbit/s**. Six frames to a datagram brings it to 4.7, at a
tenth of a second of lag a spectator cannot perceive because they are watching
a recording rather than reacting to it. The *listing* is the expensive message in a
full room, not the relay: a thirty-two-entrant lobby republished every second is
322 kbit/s, seventeen times one spectator's stream.

### Running one

The host picks a character, chooses **ONLINE → TOURNAMENT → HOST A MATCH**, and
reads out the address the lobby shows. Everybody else picks a character and
joins it, by address or off the LAN list. The lobby shows who is in and whether
they have brought somebody.

When everyone is there the host picks **DRAW THE BRACKET**. The draw is seeded
from one `u64` the host announced when the lobby opened, so every machine builds
the same bracket from the same entrant list *without it being sent* — and every
machine can therefore show it, live, as results come in. **SHOW THE BRACKET**
flips the screen between the entrant list and the tree.

Then **START THE NEXT BOUT**, once per fight. Two people play; everybody else
watches. When the fight ends the host announces the result, the bracket advances,
and the next bout is one button away.

### How it is wired

```
  fighter A ──inputs──►  HOST  ──inputs A+B──► spectator
  fighter B ──inputs──►   │    ──inputs A+B──► spectator
                          └──── the other fighter's inputs back
```

**Everything goes through the host.** A mesh would be one hop faster and needs
every entrant reachable from every other; in a group of eight, exactly one person
will forward a port. So the host relays — and in exchange it is the **authority**:
it runs the same simulation everybody else does and its copy decides who won.

That matters for the two failure modes an online tournament actually has. A
fighter cannot claim a win: a `Result` sent *to* the host is ignored, and only
the host's own simulation moves the bracket. And a fighter who disappears
mid-bout forfeits rather than stalling the evening — ten seconds of silence and
they are dropped, their remaining matches walked over.

The two fighters still get the ordinary rollback session with each other; the
host is simply the wire between them. One socket carries both channels, told
apart by a kind byte, because a second port is a second thing to forward.

### The bracket

Single elimination, up to 32 entrants, byes to the top seeds — which is what
every real bracket does and what makes a five-player tournament three matches'
worth of structure rather than an argument. Rounds are named back from the final:
FINAL, SEMI-FINAL, QUARTER-FINAL, then ROUND *n*.

It is a pure data structure in `oxyde-net/src/bracket.rs` with no networking
anywhere near it, and it is tested exhaustively: **every field size from one to
thirty-three, against four seeds, played out to exactly one champion**, plus
withdrawals, double withdrawals, replayed results and results for bouts that are
not ready.

### What the two fighters hand shake on

A bout's setup hash is in **two halves**, and only one of them travels.

The host composes the bracket's shape and the bout number and sends it in
`Control::Begin`. That half binds a session to the bout it was opened for, and it
is the only half a host is entitled to decide. Were it the whole thing —
`bouts.len() * 0x9E37_79B9_7F4A_7C15 ^ rounds`, no characters, no stage, none of
the per-installation settings — the handshake would be a comparison between one
machine's arithmetic and a copy of itself: every entrant reading the identical
number out of the identical datagram, so **nothing about the bout could
disagree**. Two entrants who resolved it differently would not be refused; they
would simulate two different fights and the bracket would record whichever
verdict the host's copy produced.

The other half is computed on each machine, out of what that machine actually
resolved and loaded: the two fighters by identity, the venue, and the settings
the bout is simulated with. `begin_tour_bout` mixes the two, so a bout between
two people is refused for every reason an ordinary online match is.

Measured, two entrants whose `select.def` pairs the same fighter with different
stages while the host names none: with only the host's half, both hand shake on
`15755400384260043837` — the host's announcement to the bit — and both reach
`Running`, with their simulations already disagreeing at frame 0. With the second
half, `12670293389261454162` against `4650672922625411067` and `match setup
mismatch` before either simulates a frame.

**A settings difference is not one of the reasons, and that is the point.**
Were the four simulated settings — playfield half-width, `[Game] inputbuffer`,
`introtime`, rounds-to-win — each machine's own half of the hash, a bracket
would turn away anybody whose options screen did not match their
opponent's. They are declared instead, by the fighter on **side zero**: a bout has
no host of its own, since the lobby host may be watching it or fighting in it,
so "who declares" has to be a rule both machines can read off the bout itself —
and the side number is already that rule, because it is the side that repeats
the `Sync`. Measured at `[Game] inputbuffer` 4 against 5: the two hand shake on
`4727910641485741865` against `1850217743265801112` before the declaration
lands, and both reach `Running` after it, with side one simulating side zero's
buffer of 4 and its own config still saying 5. An entrant that is handed the
declaration and ignores it is still refused, with nothing simulated.

The lobby host is not in that decision and deliberately so. It composes the
bout, but it may not be in it, and the playfield depends on the stage's own art
as well as on the window — `Viewport::fit_stage` zooms into a stage with no
scenery past its camera bounds — so a machine that has only *named* a stage
does not yet know the number. A declaration nobody can compute is a declaration
nobody can make.

A stage this machine does not have is a separate answer and a better one: it is
refused on the spot with `THIS BOUT'S STAGE IS NOT IN YOUR STAGE LIST`, the way a
missing fighter always was. The hash answers the question that is left — two
machines that both have a stage and did not load the same one.

### Limits, said plainly

* One bout at a time. That is the format, not a shortcut: everybody watching the
  same fight is the thing a tournament has that a queue of private matches does
  not.
* The host must be reachable. Forward the port, or use a VPN mesh.
* A spectator whose roster is missing one of the two characters is told so and
  sits the bout out; the bracket goes on without them watching.
* No ranking, no seeding by skill, no double elimination. All three are worth
  having and none is worth guessing at before anybody has run a tournament on
  this.

## The computer in a networked match

A computer-driven fighter is decided inside `Match::step`, out of state every
rollback snapshot carries and every checksum covers. That is what makes one
playable over a link at all, and it leaves exactly one thing outside the
simulation: *which seats, at what level*. That sentence is a `CpuSeats` — a level
per match-player slot — and it is handled two ways, depending on who knows.

**Point to point, it is derived.** `ONLINE > TAG WITH A PARTNER` is two a side
with each side's second fighter driven by the computer. Both peers compute the
same declaration from the same rules and the same fielded fighters, so there is
nothing to send; the level comes from each machine's own difficulty setting and
is refused on mismatch rather than declared — and it is the **only** thing
on this channel that is. The playfield width, `[Game] inputbuffer`, `introtime`
and the rounds it takes to win were refused the same way and are declared by the
host instead; the computer's level is left alone because it
already has a declaration channel of its own for the flow that needs one (a
lobby sends it in `Tour::Begin`) and a derivation both peers share for the flow
that does not. Folding it into the match settings as well would be two
declarations of one fact. It is named here rather than quietly left out: two
people at different **difficulty** settings still cannot play online Tag, and
under declaration they should be able to.
Nothing about the partner is on the wire, and a mirrored team mate's ring is not
used for it either: `Simulation::advance` drops the ring's input for a computer
seat and the step fills it instead.

**In a lobby, it is sent.** A bye, or an entrant who never arrived, is filled by
`ADD A COMPUTER` / `FILL THE BYES WITH COMPUTERS` in the tournament lobby. Such an
entrant has an id, a name and a character like anybody else — the bracket, the
standings, the results and the relay need no notion of it — and what it has
instead of a socket is a level. The host composes the bout, so it is the only
machine that knows, and the declaration travels in the `Begin` that already
carries the two characters and the stage (`TOUR_VERSION` 3). It is folded into
the same setup hash on arrival, so a peer that ignored it is refused rather than
watching a different fight.

A bout against a computer entrant has **one input source**, so it is a local
match that is broadcast rather than a networked one: the fighter's session is
`Rollback::local` — there is nobody to hand shake with and nothing to be
corrected by — and it streams its own input ring to the host as ordinary
`Packet::Inputs`, which the host absorbs exactly as it absorbs a rollback peer's.
The host referees from that stream and relays it.

### A spectator re-derives the computer, and receives nothing extra

The relay publishes the two fighters' input rings, and a computer seat's presses
are in neither. A watcher therefore **installs the same seat** — the declaration
arrived with the bout — and decides it inside its own step. That costs nothing on
the wire and leaves the relay a pair of `u16`s.

Relaying the presses instead was rejected on two counts. It would widen
`Control::Relay` for every onlooker, and it would be *wrong*: the relay publishes
the run of frames both fighters have agreed on, while the computer's presses for
a frame are known only once that frame has been simulated, and a re-simulation
after a correction can change them — the host would be publishing values it might
have to take back, on a channel with no way to take anything back.

The seat's slot in the relay is published as **zero** and read by nobody; what it
buys is the run not stopping. Before that, a bout with the house in it published
no frames at all, for ever, because one side would never agree to anything. A
missing *human* still stops the run.

Measured, a watched bout against the fight it was watching: with no declaration
the computer's fighter was driven on 0 frames and the two agreed about 60 of 199
(the entrance); with it, 25 frames and 199 of 199.

## Limitations

* **A spectator's config is its own.** The two fighters agree theirs in the
  handshake, but a watcher does not hand shake with anybody and nothing
  compares its simulation with the bout it is watching. A watcher whose window
  is a different shape has fighters bounded differently from the fight it is
  showing — and the same is true of the whole config block
  below: a watcher runs on its *own* `mugen_rules`, `parry`, `meters` and the
  rest, because the block rides the fighters' `Packet::Sync` and a spectator
  receives only the relayed inputs. It is the same limitation the playfield
  has, spanning the config; closing it means carrying the block, or
  a hash of it, on the relay, which no watcher today verifies against anything.
* **A tournament bout and a room rematch say nothing on screen** about whose
  settings are in force: both go straight to the fight, and the engine draws no
  status line there. The connecting screen — the point-to-point path — has a
  row for it, and the lobby and roster screens show the status line.
* Ordinary online play is two players, direct connection. No matchmaking and no
  NAT punch-through — the tournament's host relay is the nearest thing, and it
  still needs the host reachable.
* `begin_fight()` is still written by the app at the intro-to-fight handover.
  Safe today only because control is withheld until then, so every prediction is
  of empty input — a property of the flow rather than of the code.
* A tournament bout **between two people** hand shakes inside the fight, under
  the round intro, with the fighter on **side 0** repeating the `Sync` twice a
  second — a bout has no host of its own, so which of the two says it has to be a
  rule both can read off the bout. A bout against a computer entrant runs on a
  local session with nobody to hand shake with.
* **Any networked bout reads pad 0**, not input seat 1, because the person at a
  networked machine is one person at one keyboard whichever side of the match the
  link put them on. Offline local versus is untouched — there pad 1 really is a
  second player, and it comes from the `Drive::Human` table rather than from the
  seat.
