# Online co-op (Knuckle Up) — the seating design

Two players, each on their own machine, fight **side by side** against the same
endless waves. Everything it needs to be *deterministic* is already built; what
is left is a deliberate extension to the online **seat model**, which is why it
is written down here before it is written in code.

## What is already in place

- **The seating shape.** `Mode::KnuckleUpCoop` fields two heroes on one team
  against the waves (`drives: [row(Human(0), Human(1)), row(Cpu, Cpu)]`), playable
  locally today. Online co-op is this same shape over the wire.
- **Determinism agreement.** `room_setup_hash` folds the run identity — the
  campaign definition plus each resolved enemy's content hash — into the
  handshake whenever the mode `is_knuckle` (`fold_knuckle_run_identity`). So two
  peers on a different run, or a different version of an enemy, are refused, not
  desynced.
- **Rollback-safe CPU.** `OnlineMode::TeamPartner` already seats a *computer*
  player online: its state lives inside `Match` (saved, restored, hashed), and
  the seat is declared in `CpuSeats` and folded into the setup hash. The enemy
  waves reuse exactly this.

## The one architectural thing that is new

The online model assumes **one human peer per side.** It is written into two
places:

1. `NetLayout { seats: [usize; 2] }` — "the match-player index *each side's
   single network seat* drives." One seat, side 0; one seat, side 1.
2. The invariant `every_online_mode_is_driveable`: *the first fighter on each
   side is the peer's; a side with nobody playing is not an online mode.*

Co-op breaks both on purpose: **both peers are on side 0**, and **side 1 is
entirely the computer's** (the waves). This is a player-versus-environment
topology, and the seat model has only ever described player-versus-player.

### The change

1. **Seat topology.** Teach `NetLayout` a co-op shape: the two network seats map
   to side 0's player 0 and player 1 (not side 0 and side 1). Side 1's fighters
   are all `Drive::Cpu`, declared through `CpuSeats` the way `TeamPartner`
   declares its partner — so they are rollback-safe, not the old online-Cpu
   desync. The rollback slot↔player arithmetic is the delicate part (getting it
   wrong is "the joining player driving the host's team mate", per `NetLayout`'s
   own warning), so it is unit-tested against `net_layout` before anything runs.
2. **Generalise the invariant.** `every_online_mode_is_driveable` becomes: side 0
   pos 0 is always a peer; a side may be all-Cpu **only if the mode declares
   itself PvE** (co-op), exactly as the Cpu-seat exception is already spelled out
   for `TeamPartner`. One named exception becomes two.
3. **`OnlineMode::Coop`.** `base() = Mode::KnuckleUpCoop`; `rules()` sets
   `picks = [2, 0]`, `on_screen = [2, 3]`, and the co-op drives, with the enemy
   side declared Cpu via `CpuSeats`. It is point-to-point (not a lobby).
4. **`Game::is_knuckle_match()`.** Online play runs with `self.mode ==
   Mode::Netplay`, so the belt/campaign gates (`self.mode.is_knuckle()`) do not
   fire. A small helper — `is_knuckle()` **or** (`Netplay` and
   `online_mode == Coop`) — replaces those six gate sites so an online co-op
   match turns the belt plane on and resolves the campaign like the local one.
5. **The room picks.** Both players pick a side-0 hero; the handshake's `Pick`
   carries a side, and co-op needs both picks on side 0 rather than one each.

## How it is validated — and why one machine is enough for the hard part

The hard failure in netplay is a **desync**, and a desync is catchable *here*:
`oxtool netcheck` and `oxtool demo` run **two real `Game`s** and compare their
checksums every frame. So the seat model and the CPU-enemy determinism are
proven on one box:

1. `netcheck` a co-op match: both peers **CONVERGED**, under latency, loss and
   input delay — the same bar the versus modes already pass.
2. `demo --flow` a co-op session: the room handshake, both picks on side 0, the
   match, and a rematch, filmed from two `Game`s.

The **second machine** adds only what a simulated link cannot: real WAN latency,
NAT traversal, and two genuinely independent installs. It is where *playing* it
is confirmed, not where *correctness* is.

## Status

- **Determinism fold:** done — the run identity is in the handshake.
- **Local seating:** done — `Mode::KnuckleUpCoop`, playable with two controllers.
- **Seat model (step 1):** done — `net_layout` generalised so a `Human(j)` at any
  position is peer *j*'s seat; co-op's `seats = [0, 1]` (both side 0) falls out,
  versus/team/partner/bye byte-identical. Unit-tested
  (`coop_seats_two_players_on_one_side`, and the bye case that caught a seat
  default regression along the way).
- **Invariant (step 2):** done — `every_online_mode_is_driveable` and
  `online_modes_make_both_sides_human` skip the declared PvE mode; co-op has its
  own invariant.
- **`OnlineMode::Coop` (step 3):** defined and unit-tested (base
  `KnuckleUpCoop`, co-op drives, enemy side CPU), with the `Game::
  is_knuckle_match()` gate so an online co-op match turns the belt plane on and
  resolves the campaign. Correct and green — but **held out of `ONLINE_MODES`**
  until the live path converges (below).
  - *(An earlier "recursion" here was a self-inflicted bug — a broad `sed`
    rewrote `is_knuckle_match`'s own body into a call to itself. A gdb backtrace
    pinned it in one line; fixed. It was never the co-op logic.)*

- **Online run lobby + couch/online hybrid (Phases 3–4):** done and proven on one
  box. `Packet::MultiInputs` (net, kind 11) carries one tagged `(slot, window)`
  per owned seat so a single machine can own more than one side-0 hero (a couch
  of controllers behind one peer); `Rollback` grew an `owners` map and only takes
  the multi-stream path when a side owns >1 slot, so plain co-op/1v1/team keep the
  exact old single-stream wire byte-for-byte. The ONLINE row of the run submenu
  re-offers all four runs online, resolving the campaign through the same
  `knuckle_campaign_pick` as a local run; the run identity already folds into
  `room_setup_hash`, so two peers on different runs are refused at the handshake,
  not desynced. Proven: `a_couch_seat_and_a_remote_peer_converge_and_match_a_clean_run`
  (net — host owns slots 0+1, remote owns 2, all side 0, over a lossy link, both
  peers roll back and all three sims match a clean oracle) and
  `an_online_knuckle_run_with_a_couch_seat_converges` (app — two whole `Game`s,
  three heroes, host drives two + joiner one through real datagram loss, equal
  `checksum_at`). Guardrails intact: plain co-op, 1v1, and solo/2P local KU all
  still reproduce byte-identically.
  - **The host's run is now pushed over the wire (done).** The host's selected
    run is named to the joiner over the room channel — the proven transport — as
    a new `Room::Run` message (net kind 7), and the joiner *adopts* it (the run
    kind, its flags, and the campaign resolved locally from the run's stem, so
    two installs agree on content not on a path) before it builds its match. The
    lobby then shows the agreed run on both machines. The refusal-on-mismatch
    (`room_setup_hash`/`fold_knuckle_run_identity`) is untouched and stays the
    safety net; the push only keeps it off the normal path. `Room::Run` is
    additive — only an online co-op *host that chose a run* ever sends it, so
    plain co-op/1v1/team and the existing two-peer co-op convergence path keep
    their wire byte-for-byte. Proven:
    `the_hosts_run_is_adopted_from_the_room` (the room-state adoption and that a
    run outlives a bout) and
    `the_host_pushes_its_run_to_the_joiner_and_they_converge_on_it` (two whole
    `Game`s: the host picks STORY, the joiner starts on SURVIVAL, the run is
    pushed through a lossy link that drops announcements, the joiner adopts
    STORY, and both then build and **converge** on it — equal `checksum_at` over
    a lossy rollback link; had the run not been communicated the joiner's
    SURVIVAL would have been *refused* at the handshake).
  - **Still not yet, honest:** (i) the point-to-point transport carries exactly
    two peers (one optionally a couch), so a 3-or-more-separate-box lobby needs
    a transport and a peer-indexed rollback loop the two-peer path does not have
    — this is **designed, not landed**: see `docs/COOP-MULTIPEER.md` for the
    full design and exactly why landing it now would risk the byte-identical
    two-peer path; (ii) `oxtool netudp` was not extended to drive a hybrid couch
    over a real socket, so hybrid's real-socket proof remains the in-process
    link.

**The remaining work is the live path, in order:**

- (a) **A co-op-aware test harness — DONE.** `picks` now gives co-op its
  player-versus-environment shape (both heroes on side 0, side 1 unpicked and
  fielded by the campaign); the input routing already feeds each peer's pad 0
  through the seat model, so `play(OnlineMode::Coop, ..)` sets up and runs a real
  co-op match. Running it reproduced the exact desync this refactor targets: the
  peers agree through the handshake and the start of the fight, then diverge at
  the **first KO** (measured: host at Result frame 90, the joiner still
  fighting), because the wave/elimination substitution is still app-side. There
  is no short window that is both actively fighting and pre-KO — the loopback
  handshake runs ~90 frames and the default campaign enemies KO fast — so the
  seat model's convergence is proven as part of the full run once (b) lands,
  not as a separate static test.
- (b) **The wave spawn is driven from `step()` — DONE (sim and app).** The
  decision, the wave contents and the fielding are in `step` and snapshotted
  (steps 1–3 above); the app now constructs `Match.knuckle`/`knuckle_bank` at
  match-deal for online co-op and no longer substitutes that side itself (gated
  to the one mode, so local Knuckle Up is untouched). A companion fix: the
  campaign path resolves against the archive root rather than the process's
  working directory, so a campaign loads wherever the engine is launched from.
- (b′) **A pre-existing co-op desync, found when (b) was wired — now FIXED.**
  With the wave path rollback-safe the run *still* desynced, before any wave
  cleared. Isolated by instrumenting the session's own confirmed-frame checksum
  exchange: the peers' per-fighter state was **byte-identical** at the first
  divergent confirmed frame, and the one field that differed was **`time_left`**
  — the round clock. The cause is the one the `RoundFlow` design already warns
  about: a *continuous-turns* match keeps its clock in the app
  (`round_flow.simulated == false`) and the app writes it into **hashed** sim
  state every frame (`bout.sim.sim.time_left = bout.time_left`), which a rollback
  does not undo — *"none of them is playable online,"* said the comment, and
  co-op is the online continuous-turns match that broke that assumption. **The
  fix:** online co-op now simulates its round flow (`spawn_round` sets
  `simulated = true` for it via `coop_online`), because the sim already owns its
  wave fielding (b) and its round-over, so the clock lives in the simulation like
  every other online match and the fatal per-frame write is skipped. Local
  Knuckle Up (app-fielded waves) keeps its app-side clock, unchanged. A second
  fix fell out: `knuckle_campaign_path` resolves against the archive root, not
  the process's working directory, so the campaign loads in a test and wherever
  the engine is launched.
- (c) **DONE.** `OnlineMode::Coop` is back in `ONLINE_MODES` and
  `online_coop_seats_two_players_and_converges` is un-ignored and **passing** —
  two whole `Game`s, two heroes on side 0 against the campaign's CPU enemies,
  **converged** over a lossy two-frame link with prediction and rollback
  (measured: agreed through ~1,400 rollbacks at 900 frames). The wave
  *transition* itself (a wave clearing, the sim fielding the next, surviving a
  rewind) is proven deterministically by the unit test
  `the_wave_director_fields_the_next_wave_in_step_and_rides_the_snapshot`,
  because the scripted heroes cannot clear three campaign enemies in-window.
- (d) the live two-machine confirmation. The **real UDP transport** is now
  proven to carry a converging, rollback-correcting session — not just the
  simulated in-process link the convergence test uses — by `oxtool netudp`: a
  localhost self-test (two real sockets, one process) and, more tellingly, two
  *separate processes* over loopback where the joining process rolled back 81
  times and still ended on the host's exact checksum. The same command is the
  live two-machine test: `oxtool netudp <root> <p1> <p2> --host` on one box and
  `… --join <host-ip>:7000` on the other, then confirm both end `Running` on the
  same `CHECKSUM`. What remains is running it across two genuinely independent
  installs over a real WAN/NAT link, which needs the second machine (the mesh
  peers are pingable from here but not SSH-accessible from this session, so the
  engine cannot be launched on them autonomously).

(a)–(c) are done and provable here, and (d)'s transport is proven on one box;
only the cross-machine WAN/NAT run needs the second machine. Online co-op
converges today, over both the simulated link and a real UDP socket.

### (b) in full — the wave director, and why it is not a one-line move

The naive plan is "move the Knuckle Up wave director into `step()`", but it does
not fit as stated, and the reason is worth writing down because it is the
**general online continuous-turns problem**, not a Knuckle Up one. The engine's
own comment in `perform_substitution` already flags it: continuous turns online
is unsafe because an app-side field on *predicted* state is not undone by
`restore`. Team Rumble and Roster Rumble have the same gap.

The tension: a wave (or a turns substitute) **spawns a new fighter mid-match**,
and spawning loads a character — `.def`, sprites, animations — which is
`Assets`/VFS work that lives in `oxyde-app` and *cannot* move into `oxyde-core`
(the simulation crate has no asset loading, by design). But rollback needs the
spawn to be re-derivable identically after a rewind, which means the *decision*
must live in snapshotted `step()` state.

So the fix is a split, not a move:

1. **The decision is snapshotted.** *(Done.)* `crates/oxyde-core/src/wave.rs`'s
   `WaveDirector` — the wave cursor, the per-wave sizes, and a latched "spawn
   wave N" request — is a field of `Match` (`Match.knuckle`), advanced inside
   `step()` on the rising edge of `side_down(1)`. Rollback already saves and
   restores `Match`, so a rewind re-derives the same wave at the same frame, and
   `Match::checksum` mixes it so a campaign on a different wave on one peer is a
   reported desync. `None` for every versus bout, so `oxtool regress` is byte
   identical (unit test `the_wave_director_advances_on_a_clear_and_rides_the_snapshot`).
2. **Sources are pre-loaded.** *(Done.)* Every character a campaign can field is
   loaded into the `bank` *before* the match, so fielding one mid-match is a
   `field_fighter` with an already-resident source — no asset I/O on the hot
   path, nothing non-deterministic, nothing that can differ between a first pass
   and its re-simulation.
3. **The spawn itself moves into `step()`.** *(Done — the determinism-critical
   core.)* It is not enough for the app to *read* the director's cursor and
   field the wave, because **a rollback re-simulates `step()` and nothing else**
   (`oxyde-net/src/rollback.rs`): the app's `perform_substitution` does not
   re-run on a rewind, so a wave fielded on a mispredicted frame would be dropped
   by `restore` and never re-added. The fielding therefore happens inside
   `step()`: `Match::advance_wave_director` (`sim.rs`) latches the clear on the
   rising edge of `side_down(1)`, and `Match::spawn_knuckle_wave` (`sim.rs`)
   fields the next wave — `field_fighter`, camera and bounds, all sim-side — from
   the `Arc<Character>` handles pre-loaded into `Match.knuckle_bank`. The only
   app-side part is loading those handles; the app no longer substitutes the
   enemy side for co-op (`game.rs`, `if side == 1 && …knuckle.is_some() { continue }`).
   So the director holds wave *contents* (character handles + boss multipliers),
   not just sizes, and the substitution is pure sim work.

All of (1)–(3) are done and in the simulation. The determinism-critical core is
proven by `wave_director_is_rollback_deterministic` (`oxyde-core/src/sim.rs`): a
co-op-shaped match (heroes on side 0, a sim-director enemy side, three waves with
a 2× boss wave) driven by a fixed event tape is re-simulated twice to byte-identical
per-tick checksums through both wave transitions and the boss gate, and a rollback
(snapshot on the boss wave, run the gate, restore, replay) reproduces the identical
checksum stream and re-fields the identical boss wave inside `step()` — the test
fails if the restored cursor is perturbed, so it is not hollow. The app
convergence test `online_coop_seats_two_players_and_converges` exercises the live
two-`Game` path over a lossy link. The split is what makes **every**
continuous-turns mode online-safe, not only co-op. What remains is item **(d)**
below — a genuine two-machine WAN/NAT run (the transport is already proven on one
box via two-process loopback with real rollbacks); it needs a second independent
install and is the only thing holding the online path from being enabled.
