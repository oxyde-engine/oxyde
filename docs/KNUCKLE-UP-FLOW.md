# Knuckle Up — the run/seating flow

What happens between picking **Knuckle Up** on the main screen and the fight
starting: which runs there are, how players take their seats, and how the same
run is played solo, on a couch, online, or a mix of the two. This is a
reference for the shipped flow, not a plan — every run type and seating mode
described here is in the engine today.

## The model: two axes, never one list

Everything a player might want is a point on two independent axes:

- **The run** — *what you fight*: **Story**, **Arcade**, **Survival**, **Boss
  Rush**, **Last Stand**.
- **The seating** — *who plays and from where*: **Solo**, **Couch** (friends on
  the same machine), **Online** (friends over the net), or a **Hybrid** of couch
  and online in the same match.

Seating is deliberately *not* a run type. "Arcade with a friend next to you" is
Couch; "Survival with a friend across the country" is Online. Treating seating
as a run would force a combinatorial menu (Arcade-solo, Arcade-couch,
Survival-online…). Instead the **run** is picked from the menu and the
**seating** is resolved by who shows up — a controller pressing Start (couch) or
a peer joining the lobby (online).

## The menu

```
KNUCKLE UP
  ├ STORY          ┐
  ├ ARCADE         │  local runs: solo, or couch co-op by drop-in
  ├ SURVIVAL       │  (Player 2–4 press START at select to take a seat)
  ├ BOSS RUSH      │
  ├ LAST STAND     ┘
  └ ONLINE ▸  STORY · ARCADE · SURVIVAL · BOSS RUSH · LAST STAND
                   the same five runs, hosted/joined over the net;
                   remote peers take seats, and local controllers may
                   ALSO press START to take couch seats → Hybrid
```

- The five top entries start a **local** run. Couch co-op is not a separate
  entry — it is the universal rule that **an unclaimed seat is filled by pressing
  Start** at the character-select screen, and emptied by backing out.
- **Online** is its own door because it needs a host/join lobby and a handshake.
  Inside it the *same* five runs are offered, so Boss Rush, Survival, etc. are
  all playable online — not a reduced set.
- **Hybrid** is not a sixth menu item: it is what happens when, inside an online
  session, a local controller also presses Start. The seat model already treats
  every seat as "peer *j*'s seat", and a couch seat is simply the host peer
  owning more than one seat.

## The runs

The five runs are first-class `KnuckleRunKind` variants (`game.rs`), each with
its own menu label, its built-in campaign, and whether it plays that campaign's
storyboards. None of them is a separate simulation mode: a run is an authored
`.knuckle` campaign plus the menu entry that names it.

| Run | What it is | How it is built |
|---|---|---|
| **Story** | The headline: a campaign with an intro, between-stage beats and an ending. | `campaign_stem = oxyde_story`; the only run with `plays_story = true`, so its storyboards play. |
| **Arcade** | Quick pick-and-go belt run, no narrative. | `campaign_stem = None` — it keeps the campaign picker, so installed and custom campaigns stay reachable, and plays with the storyboards suppressed. |
| **Survival** | Endless roster waves; the score is your **streak**, written to the records board. | `campaign_stem = oxyde_survival`; an endless campaign with the streak wired to `Mode::Records`. |
| **Boss Rush** | Bosses only, chained easiest-to-hardest. | `campaign_stem = oxyde_bossrush`. See [Boss Rush](#boss-rush) below. |
| **Last Stand** | Outlast a dense, continuously-refilled mob against a countdown — fight into the crowd, don't camp. | `campaign_stem = oxyde_laststand`; the one run with its own rule set (`is_last_stand`), driven by a clock/refill/drop/win-check in the sim's wave director. |

Arcade and Story can share one campaign and differ only by whether its
storyboards play (`plays_story`); Survival, Boss Rush and Last Stand are
distinct campaign *shapes*.

### Boss Rush

**BOSS RUSH** — *"BOSSES ONLY, CHAINED HARDEST-LAST."* A shipped run that loads
the built-in campaign `knuckleup/campaigns/oxyde_bossrush.knuckle`
(`campaign_stem = oxyde_bossrush`). It is not a storyboard run: like the other
scored runs it has `plays_story = false`, so it drops you straight into the
fights with no narrative beats.

The campaign is ten stages, `br01`–`br10`, each a single `boss` wave with **no
mook waves** — a stage with a boss and no waves is well-formed, and the boss
opens the stage. The whole difficulty curve is the boss life multiplier, which
climbs down the chain from **1.3** on the first boss to **3.4** on the last:

| | Boss | Life × |
|---|---|---:|
| `br01` | Sodom | 1.3 |
| `br02` | Mr Big | 1.5 |
| `br03` | Violent Yamazaki | 1.7 |
| `br04` | Strong Guy | 1.9 |
| `br05` | Takuma | 2.1 |
| `br06` | Heidern | 2.3 |
| `br07` | Venom | 2.5 |
| `br08` | Thouther | 2.8 |
| `br09` | MB-02 | 3.0 |
| `br10` | Mech Rugal | 3.4 |

The roster gets `lives = 2`, and the boss names, stages and music reuse the
validated set from `oxyde_long_run`. Because the whole thing is an authored
`.knuckle`, editing the chain — bosses, order, multipliers, stages — is a text
edit, and it is reachable from ARCADE through the campaign picker as well. It
can be simulated headlessly with
`oxtool campaign knuckleup/campaigns/oxyde_bossrush.knuckle --root .`.

### Last Stand

**LAST STAND** is the horde-survival run and the only one with its own rule set
rather than a plain campaign shape. *Solo*, reaching the clock alive wins and a
knockout is final; in *co-op* (2–4) a KO'd seat is out and the **healthiest
survivor wins** at the clock. Crowd density scales with hero count, and enemies
drop mini-heals (odds easing as the party's health climbs) plus a richer heal on
a timer at a risky spot — so it rewards fighting into the crowd, not camping.
The clock, refills, drops and win-check all live in the deterministic sim wave
director and fold into the match checksum, so Last Stand is as rollback- and
replay-safe as any campaign.

## Seating — up to four heroes, any mix of couch and online

- **Seats.** `knuckle::Run` holds `seats: Vec<Seat>`, up to four, each carrying
  its own lives and score.
- **Routing.** `net_layout` maps a `Human(j)` to any seat; couch co-op's
  `seats = [0, 1]` (both on side 0) falls out of it, exercised by
  `coop_seats_two_players_on_one_side` and
  `online_coop_seats_two_players_and_converges`. Four seats and a couch/online
  mix are the same mapping: *k* local controllers + *m* remote peers = *k + m*
  heroes on side 0.
- **Belt framing.** Four heroes plus their wave of enemies is a crowd: the belt
  camera's leash and the life-bar HUD handle up to four bars and a wider or
  gently-zoomed view, and difficulty (enemy count and health) scales with hero
  count so four-player is not trivial.

## Character select / lobby (all runs)

- **Per-seat cursors.** Seat 1 is always the starting player. An empty seat shows
  **"PRESS START TO JOIN"**; pressing Start claims it, backing out frees it
  (drop-in / drop-out, any time before the match).
- **Big character name** under each cursor.
- A **Random** slot per seat, plus a "random for everyone" shortcut.
- **Ready** state per seat; the host (seat 1, or the online host) starts when all
  claimed seats are ready.
- In an **online lobby** each seat shows whether it is a controller (couch) or a
  remote peer (online), so a hybrid line-up is legible at a glance.

## Implementation

The mode is built from pieces the engine already had, which is why a run is
configuration rather than a new simulation:

- **Modes.** `Mode::KnuckleUp` / `KnuckleUpCoop` / `Netplay`.
- **Wave director.** The rollback-safe `Match::advance_wave_director` /
  `spawn_knuckle_wave`, proven by `wave_director_is_rollback_deterministic`.
- **Seat model.** `net_layout` and `Run.seats: Vec<Seat>`.
- **Records.** The records/streak screen, `Mode::Records`, carries Survival's
  streak.
- **Content.** Storyboards (`knuckle_home::Kind::Storyboard`,
  `oxyde_render::Storyboard`) and the `.knuckle` format (bosses, waves,
  difficulty, lives, music).
- **Transport.** The UDP transport with real rollbacks.

### Online

The ONLINE door shows the same five runs to be played over the net: choosing one
resolves its campaign and opens the host/join lobby on `OnlineMode::Coop`. The
connecting screen — co-op's lobby — shows the run and a seat-occupancy line (how
many heroes, how many this machine drives and whether that is a couch, how many
the peer drives). Remote peers occupy hero seats on side zero through the seat
model, which converges (`online_coop_seats_two_players_and_converges`).

The run is **mirrored over the wire**: the host names its run to the joiner over
the room channel (`Room::Run`, net kind 7) and the joiner adopts it before
building its match, so a joiner that opened on a different (or no) run ends up on
the host's — the lobby shows the agreed run on both. The run identity also folds
into the handshake, so a genuine mismatch is refused; the push keeps that
refusal off the normal path. Proven by
`the_host_pushes_its_run_to_the_joiner_and_they_converge_on_it` (host picks
STORY, joiner starts on SURVIVAL, adopts STORY over a lossy link, both
converge). `Room::Run` is additive and sent only by an online co-op host that
chose a run, so every other path keeps its wire byte-for-byte.

### Hybrid

A local controller can take a couch seat *inside* an online session: *k* local
seats at the host + *m* remote seats, all on side zero, in one rollback session.
The determinism-critical core is a multi-seat exchange in `oxyde-net`: a machine
owning more than one seat sends `Packet::MultiInputs` (one tagged stream per
owned seat); the `Rollback` learns an `owners` map and derives which slots it
fills from its own `side`; a session owning one seat is byte-identical on the
wire. The app's `Rules::with_hybrid_heroes` + `net_layout.owners` express the
line-up (a match property, identical on both peers), and `game.rs`'s fight loop
feeds each owned seat from its pad. Proven by
`oxyde_net …a_couch_seat_and_a_remote_peer_converge_and_match_a_clean_run` (host
owns two seats, peer one, converges under loss and rollback and matches a clean
oracle) and `oxyde_app …an_online_knuckle_run_with_a_couch_seat_converges`
(three heroes, host drives two, converges through genuine datagram loss with
real characters).

Everything here is two machines (one of them possibly holding a couch of
controllers) over one point-to-point link.

## Still open

- **The run's lives, props and placement over co-op** — online co-op fields its
  waves inside `step()`, so the fight itself seats and converges, but the
  app-side run bookkeeping (lives, props, wave placement) is still local-only; an
  online run does not yet carry it (`knuckle.rs`).
- **Live two-machine WAN/NAT run** (COOP-ONLINE.md §d) — needs a second
  independent install; everything above is proven on one box (localhost +
  two-process loopback with real rollbacks).
- **Multi-peer online lobby** — three or more *separate* machines on side zero,
  which the two-peer point-to-point transport does not carry. It is designed in
  [COOP-MULTIPEER.md](COOP-MULTIPEER.md) (a host-relay topology, a peer-indexed
  rollback loop behind a path that keeps the pair byte-identical, and an
  N-process loopback convergence proof) rather than landed: the
  determinism-critical pieces (the `owners` map, `MultiInputs`, the run identity
  and its push, the rollback-safe waves/clock) are in place, but the
  scalar-remote confirm/predict/settle loop cannot be generalised in place
  without risking the two-peer wire, and it cannot be confirmed without the
  second machine.

## Open questions

- **4-hero belt framing**: a fixed wider view, or a gentle dynamic zoom to keep
  all heroes and the active wave on screen? (Affects the depth/camera tuning.)
- **Difficulty vs. hero count**: the curve for enemy numbers/health as seats
  grow from one to four, and for a hybrid where latency differs per seat.
- **Story vs. Arcade sharing a campaign**: one campaign with a storyboards
  toggle (the shipped answer — `plays_story` is the toggle), or separate curated
  lists?
