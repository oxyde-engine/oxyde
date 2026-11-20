# Multi-peer online co-op (3+ separate machines) — the design, and why it is not landed yet

Online co-op today is **two peers**: one point-to-point link, one of which may
be a couch of controllers (the Phase-4 hybrid). This document is the design for
**three or more separate machines** on side zero — four players, each on their
own box, against the same waves — and an honest account of why it is written
down here rather than written into the engine in this change.

The short version: a correct N-peer path cannot be added without either
changing the proven two-peer wire or risking the determinism guardrails, and it
cannot be *confirmed* without a second physical machine. So the two-peer path
stays byte-identical, the run-choice push (Part 1) lands on top of it, and
N-peer is specified against the real code here.

## What already generalises, and what does not

A lot of the hard, determinism-critical machinery is **already N-ready**,
because it was built as a property of the *match*, not of the *machine*:

- **The seat model.** `net_layout` maps a `Human(j)` at any position to peer
  *j*'s seat, and the `owners: Vec<Option<usize>>` map on `Rollback`
  (`declare_couch_ownership`) already says *which peer drives which slot* for an
  arbitrary number of slots. Nothing in the owners map assumes two peers.
- **The multi-stream input packet.** `Packet::MultiInputs` (net kind 11) carries
  one tagged `(slot, window)` per owned seat. A machine that owns slots `{0,1}`
  already announces both in one datagram; a machine owning `{0,1,2}` would too.
- **The run identity in the handshake.** `room_setup_hash` /
  `fold_knuckle_run_identity` fold the campaign and every enemy's content hash,
  so peers on different runs are *refused*, not desynced — and Part 1 now pushes
  the host's run so the joiner adopts it. Both are N-agnostic: the same hash and
  the same push work for any number of peers.
- **Rollback-safe PvE.** The wave director lives in `step()`
  (`Match::advance_wave_director` / `spawn_knuckle_wave`, proven by
  `wave_director_is_rollback_deterministic`) and the round clock is simulated
  (`coop_online`). The enemy side is deterministic sim state on every box,
  whatever the peer count.

What does **not** generalise, and is the whole of the work, is the **peer
transport and the confirm/predict/settle loop**, which are scalar-remote today:

1. **`Transport` is a single pipe.** `trait Transport { fn send; fn recv; }`
   (`packet.rs`) is one stream to one peer. `send` broadcasts to the one remote;
   `recv` drains the one remote. There is no addressing, so three machines have
   no way to say "this datagram is for peer 2 but not peer 1".
2. **`Rollback` predicts exactly one remote.** `side = local_slot.min(1)`,
   `remote_slot() = seats[1 - side]`, and a frame is *confirmed* when the one
   remote stream has reached it. `confirmed`, `settled` and the throttle are all
   "have I heard from **the** other peer up to frame N". With three peers a
   frame is confirmed only when **all** remotes have reached it, prediction is
   per-peer, and a rollback rewinds to the earliest mispredicted peer-frame
   across the set.
3. **The handshake is two-sided.** `Packet::Sync` agrees one `setup_hash` and
   one seed between two peers; "the host decides" (`Room::Begin`, the seed, the
   start frame) is a single asymmetry between a pair. N peers need the host's
   decision to reach *all* joiners and every joiner's readiness to reach the
   host — a lobby, not a pair of messages.
4. **The throttle is pairwise.** Flow control slows the fast peer to the one
   slow peer. With N peers it must slow to the *slowest*, and a single stalled
   peer must not be able to freeze the mesh indefinitely (a drop/replace policy
   the pair does not need, because when a pair loses a peer the session is over).

Items 1–4 are exactly the fields and functions the two-peer guardrail protects.
Generalising `confirmed`/`settled`/`remote_slot` in place — rather than behind a
separate path — is what would risk the byte-identical two-peer case, which is
why it is not done speculatively.

## Topologies, and the one this engine should take

- **Full mesh.** Every peer sends its own input stream to every other peer.
  N·(N−1) streams, each the existing single/multi-stream format. Lowest latency,
  no relay single-point-of-failure, hardest NAT story (every pair must traverse).
- **Host relay (star).** Every joiner sends to the host; the host forwards each
  stream to the others (and is itself a player). N−1 links, one NAT target, one
  extra hop of latency on joiner↔joiner. This is the topology
  `crate::tournament::Control` already uses for its bracket relay, and it is the
  right one here: co-op is **already host-authoritative** for the things that
  must be (the seed, the start frame, the run identity via Part 1), and reusing
  the relay means one socket to forward through and one place that assigns peer
  ids — exactly what the pair deliberately avoids, but exactly what N needs.

The relay is **control-plane only for the handshake**; once the bout starts,
input datagrams are forwarded verbatim and the simulation is still a pure
function of (inputs, state) on every box. The host does not arbitrate the fight
— it relays bytes. Determinism is unchanged: a relayed `MultiInputs` is the same
`MultiInputs` the recipient would roll back on from a direct link.

## The change, grounded in the code

1. **A fan-out transport.** Introduce an N-peer transport alongside `Transport`
   (not a change to it): `send_to(peer, &Packet)` / `recv_from() -> Vec<(peer,
   Packet)>`, backed by the host relay. The existing `Transport` is the N==2
   degenerate case and keeps its exact bytes; the two-peer `Rollback` keeps
   calling `send`/`recv` unchanged.
2. **A peer-indexed confirm/predict loop, behind a flag.** `Rollback` gains an
   `MeshRollback` sibling (or an internal `peers: usize` with the scalar path as
   the `peers == 2` special case, chosen so the N==2 codegen and wire are
   provably identical — a determinism test, not a code read, decides which).
   `confirmed(f)` becomes "min over peers of each peer's confirmed frame";
   prediction and rollback are per-peer; `owners` already says who drives what.
3. **An N-way lobby.** Extend the room/handshake to a host-assigned peer id and a
   seat-occupancy list broadcast to all (the run push from Part 1 already fits:
   the host names the run once and the relay forwards it to every joiner). The
   setup-hash refusal stays the safety net, now checked by every peer against
   the host's declaration.
4. **Slowest-peer throttle + a disconnect policy.** The throttle slows to the
   slowest confirmed peer; a peer that stalls past a bound is dropped and its
   seat either continues under the CPU (the rollback-safe `CpuSeats` path co-op
   already uses for the enemy side) or ends the run, by lobby rule.
5. **Difficulty by hero count.** Enemy count/health already scale with seats
   (KNUCKLE-UP-FLOW.md); N peers just means more seats, no new mechanic.

## How it is proven — on one box, and what still needs a second

The determinism half is provable here, the way the two-peer path was: **N
loopback processes** (3–4 `oxtool netudp`-style processes over localhost), each
rolling back under induced loss, all ending on the **same per-tick checksum** as
a clean single-process oracle. That is the same bar `online_coop_seats_two_
players_and_converges` and the two-process loopback run clear for the pair, and
it is where the mesh confirm/predict loop and the relay forwarding are shown
correct. A convergence claim is only ever backed by an equal-checksum assertion
across the processes — never asserted from a design.

What **cannot** be done without a second machine is the same thing that is still
open for the pair (COOP-ONLINE.md §d): real WAN latency, NAT traversal from more
than one independent install, and the relay's forwarding under genuinely
independent clocks. The mesh peers on this network are pingable but not
SSH-reachable from this session, so the engine cannot be launched on them
autonomously.

## Why it is not landed in this change

- **It cannot be added without a new transport and a peer-indexed rollback
  loop**, and doing that *in place* on the scalar-remote confirm/predict/settle
  code is precisely what would endanger the byte-identical two-peer path the
  guardrails protect. The safe shape (a sibling path with the pair as a proven
  special case) is real work with its own convergence suite, not a small diff.
- **It cannot be confirmed end-to-end here**: the loopback proof is necessary but
  the WAN/NAT/relay-under-independent-clocks run needs a second box this session
  does not have.
- **The pieces that are determinism-critical are already in place** (owners,
  MultiInputs, run identity + run push, rollback-safe waves/clock), so when the
  second machine and the transport land, the mesh is confirm/predict/relay plus
  a lobby — not a rebuild. Landing a shaky mesh now would risk the one thing that
  must not move; landing the design now keeps the two-peer path sacred and the
  N-peer path honest.
