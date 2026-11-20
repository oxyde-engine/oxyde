# Bring-your-own-characters (BYOC)

Two people play online, each bringing a character the other may not have. The
one who lacks it receives it over the connection and the bout happens — instead
of being refused because the rosters differ.

**Status:** built end to end and tested in-process; the one remaining gate is a
run on two real machines. The data path (bundle → chunks → reassembly → verify →
confined mount) is loopback-tested, manual BYOC via `oxtool pack`/`unpack` works
today, the negotiation engine is in place (the `Room::Need` and `Room::Declare`
messages, the two-sided sharing policy with HD/UHD-sized caps in
`oxyde_net::byoc`, and the single verified-and-confined mount every received
character passes through, `oxyde_app::bundle::receive`), **and the game loop now
drives it**: both the first bout's pre-match pump and the in-session pump (a
rematch where a peer reselects a fighter the other lacks) declare each side's
picks by content id, answer a gap with a `Need`, answer a `Need` by packing and
streaming `Content`, and mount a finished transfer into a VFS overlay
(`oxyde_vfs::Vfs::add_overlay`) so the fighter resolves at the path the setup
hash expects — turning the old "fighter not in your roster" refusal (and the
between-bouts "match setup mismatch" refusal) into a fetch. A two-`Game` harness test
(`a_missing_fighter_is_fetched_over_the_room_and_the_bout_starts`) runs the whole
negotiation over a simulated link and asserts the received fighter's content hash
equals the sender's.

**The two-machine run is done.** `oxtool byoc-netudp --host` / `--join` drives
the real `Game` BYOC flow over a **real UDP socket** between two independent
processes — and two independent machines. It has been run three ways: two
processes on one host (localhost UDP); and **x86 host ↔ ARM joiner on a real
network** (a different-CPU second machine, the cross-architecture case), where
the joiner fetched a fighter it lacked, verified and mounted it over the wire,
and the setup hashes agreed. A localhost version is a regression test
(`byoc_transfers_over_a_real_udp_socket`). Separately, the content identity
(`source_hash` — what every `Need` names and the setup hash folds) was shown to
compute **bit-identically on x86 and ARM**, so a host and joiner on different
architectures agree on what a fighter *is*. BYOC is validated end to end.

Security note: `Bundle::unpack_into` confines every path to its target
directory (an absolute path, a drive/UNC root, or any `..` is refused and the
whole unpack fails), and `receive` additionally checks the content hash of what
*landed* equals the id that was asked for — so a received character can neither
escape its directory nor be a different fighter than the one requested.

This is a thing a *deterministic* engine can do safely and a non-deterministic
one cannot, for two reasons that are the whole design:

1. **Determinism.** Once both machines hold the same bytes, the fight is
   provably identical — so transferring the character is enough; nothing else
   has to be kept in sync. See [DETERMINISM in NETPLAY.md](NETPLAY.md).
2. **A character is *data*, not code.** FUSE/CNS/SFF is interpreted, sandboxed
   content — `oxyde-script` is absent from `oxyde-core`'s manifest, so nothing a
   received character brings can run code or read the disk. Accepting a
   stranger's character is safe in a way "download and run this mod" never is.

---

## What is built (and tested on one machine)

The data path is complete and loopback-tested end to end. Four pieces:

| Piece | Where | What it does |
|---|---|---|
| **Content identity** | `oxyde_app::index::source_hash` | One hash of a character — its `.def` and the text files it names (sprites by size, since they do not change the fight). The thing two installs must agree on. |
| **In the handshake** | `Game::room_setup_hash` | Folds each picked character's content hash into the setup hash, so a *version* mismatch is refused, not desynced. |
| **In replays** | `oxyde_app::replay` (format 3) | Records the same hash per fighter, so a replay reports "present but a different version". |
| **The bundle** | `oxyde_app::bundle` + `oxtool pack`/`unpack` | A character as one portable, digest-verified `.oxc` file. Manual BYOC works today. |
| **The transfer** | `oxyde_net::transfer` + `Room::Content` | Splits a bundle into datagram-sized chunks, carries them as room messages, reassembles with loss recovery. |

Every arrow in the path has a test:

```
Bundle::pack(vfs, def)            # collect the character  (oxyde-app)
  → Bundle::encode                # → bytes, with an integrity digest
  → transfer::Send::new(id,bytes) # → chunks (≤448B, fit a datagram)  (oxyde-net)
  → Room::Content(chunk)          # → room messages over the wire
  … [ lost chunks: Reassembly::missing() → Send::resend() ] …
  → Reassembly::finish            # → the bytes back
  → Bundle::decode                # digest verified (intact)
  → source_hash == bundle.root    # content verified (the right character)
  → write into the VFS            # now both peers hold the same bytes
```

---

## The trigger flow (the remaining piece — not yet wired; to be validated on two machines)

The handshake already **detects** the case: `Room::Ready` carries the setup
hash, and the content fold makes it differ when a peer lacks a character or
holds another version. Today that is a refusal. BYOC turns the refusal into a
transfer:

1. **Detect.** A peer's `Ready` hash disagrees, and the disagreement is a
   character neither the stage nor the settings. (The host knows which fighters
   it named; the joiner knows which it is missing or hashes differently.)
2. **Offer / request.** *Which* characters a peer must ask for is decided by
   `transfer::requests(declared, mine)` (built and tested): over the opponent's
   declared `(path, content id)` picks, it returns the ones this peer is missing
   or holds at a different id. Each peer runs it; the two lists say who sends
   what. The ask itself is a new room message (`Room::Need { id }` — one line to
   add when wiring live), and the peer that **has** it begins a `transfer::Send`
   for that content id.
3. **Transfer.** The sender emits `Room::Content` chunks. The receiver feeds
   them into a `Reassembly`; on a lull it replies with `Reassembly::missing()`
   and the sender `resend()`s exactly those. Loss-tolerant by construction.
4. **Verify.** On `finish()`, the receiver runs `Bundle::decode` (the digest
   proves the bytes arrived intact) and checks `source_hash == bundle.root` (the
   content is the character that was promised). A mismatch aborts the transfer,
   not the engine.
5. **Load.** The bundle is written into a transient mount the VFS resolves — the
   received character is now present, byte-for-byte, at the path the hash
   expects.
6. **Proceed.** `Ready` is recomputed; the hashes now agree; the bout starts.

The message (`Room::Need`), the policy gate and transfer sessions
(`oxyde_net::byoc::{may_share, may_accept, Incoming, Outgoing}`), and the
verified confined mount (`oxyde_app::bundle::receive`) are now **built and
loopback-tested** — including a full pack → session → reassemble → verify →
mount → re-hash round trip. What is left is to *drive* them from the game's
online loop: send a `Need` when `needed()` returns a gap, answer an incoming
`Need` by packing and `offer`ing over the socket, feed arriving `Content` into
`Incoming`, call `receive` into the running VFS, `invalidate` it, and recompute
`Ready`. The reason that last step is the two-machine piece: a mount into a live
VFS and a real lossy link between two independent installs are exactly what a
single-process loopback cannot stand in for.

### Caps and safety when wiring it live
- **Size cap.** Refuse a transfer whose declared size is implausible (the bundle
  already caps files at 256 MB and the transfer at `MAX_CHUNKS`); add a
  per-match ceiling and a per-peer rate so a transfer cannot be a denial of
  service.
- **Opt-in.** BYOC is a room setting, off by default: a host may want "my roster
  only". When off, a mismatch stays a refusal.
- **Audit on arrival.** Run the existing health audit on a received character
  before it plays, and apply resource caps — it cannot run code, but it can be
  broken or oversized.

---

## Sharing policy & scopes (design spec — not yet implemented)

The trigger flow above says *how* a character moves. This section says *whether*
and *what* — the opt-in surface a person actually touches. It is a **policy
layer** on top of the machinery already built; it never bypasses the
verification in step 4. All of it is design, not code (status at the end).

### Consent is two-sided

There are two parties opting into two different things, and **both default to a
safe posture**: you never silently upload your roster to a stranger, and you
never silently ingest a stranger's files.

- The **sender/host** opts into *giving* (`share`).
- The **receiver** opts into *taking* (`accept`).

A transfer happens only where both sides' policies permit it. Surfaced three
consistent ways — a `[Sharing]` config block, CLI flags (for headless and for
Corrosion), and an **Online → Content sharing** Options pane with a per-peer
"always accept from this peer" memory.

```ini
[Sharing]
; what THIS install will GIVE a peer
share           = off | on-request | roster     ; default off
share-allow     = *                             ; glob allowlist of char folders
; what THIS install will TAKE from a peer
accept          = off | ask | single | roster   ; default ask
accept-dir      = chars/.incoming               ; where received bundles land
keep            = session | always              ; discard after the bout, or keep
; ceilings (belt-and-braces with the hard caps in step 4 / Caps and safety)
max-per-char-mb = 256
max-match-mb    = 1024
```

CLI equivalents: `--share off|on-request|roster`, `--accept off|ask|single|roster`,
and `--share-content` (the Corrosion host switch, below).

### The scopes (what moves, when)

| Scope | Trigger | What moves | Default posture |
|---|---|---|---|
| **Manual** | `oxtool pack` / `unpack` | one `.oxc` you move by hand | shipped today |
| **Single @ match** | matchup locks and one side lacks the picked fighter | just that character | `accept = ask` prompts the receiver |
| **Selective request** | receiver browses the peer's roster and picks one | just the chosen character(s) | receiver asks; sender's `share` gates |
| **Roster sync** | explicit, in the lobby | the hash-diff of the whole shareable roster | loud opt-in, both sides |
| **Corrosion pull** | content-less client asks the host mid-session | any/all content the host flagged shareable | separate mode; host `--share-content` |

### Selective request — the "ask to get" flow

This inverts the offer. Instead of waiting for a matchup to expose a gap, the
receiver asks to *browse* a peer's shareable set and pull a specific character on
demand. The **ask is symmetric**: the receiver asks to get, and the sender is
asked to give — either side's policy can be the gate.

1. **List.** Receiver sends `Room::Catalog?`; the peer replies
   `Room::Catalog { entries: [(path, content-id, name, size)…] }`, filtered by
   its `share-allow`. Only *metadata* crosses here — names, hashes, sizes — never
   content.
2. **Pick.** Receiver chooses one or several — a "get from peer" list in the UI,
   or `oxtool request <peer> <name>` on the CLI.
3. **Ask.** Each pick becomes a `Room::Need { id }`. The **sender's** `share`
   policy gates it: `on-request` → prompt the host ("Peer wants *X* — send it?
   [once / always / no]"); `roster` → auto-approve within `share-allow`; `off`
   → declined, with a reason. The receiver's own `accept` must also permit it.
4. **Transfer → Verify → Load.** Reuses the trigger flow's steps 3–5 unchanged.

### Roster sync — a manifest diff, not a firehose

Bulk sync is cheap because the content hash already lets peers move only the
delta:

1. Each side sends a manifest of `(path, content-id)` for its shareable roster.
2. `transfer::requests(theirs, mine)` (built and tested) returns exactly what
   this peer lacks or holds at a different id — identical ids are skipped, so
   dedup is free.
3. Pull the delta, hash-verified per character, resumable over the existing
   `missing()`/`resend()` loop, with a progress bar and the `max-match-mb`
   ceiling. `keep = session` evaporates the synced set after the bout;
   `keep = always` persists it to `accept-dir`.

### Corrosion content-pull — a separate, deliberate mode

Corrosion streams **pixels, not files** — so this is an *added* side channel, not
a change to Corrosion itself. It reuses the bundle/transfer machinery over the
Corrosion TCP link rather than the netplay room:

- The content-less client keeps spectating/playing on streamed frames (unchanged)
  and *separately* may request a catalog and pull characters into `accept-dir`,
  "graduating" from thin client to a populated install it can later run offline.
- Gated by the host running **`--share-content`**; absent that flag the channel
  does not exist.
- **Invariant preserved:** with `--share-content` **off (the default), Corrosion
  still needs nothing on disk and sends no files** — only the picture. The promo
  claim stays literally true; content-pull is always an explicit extra, never
  implicit. (This is also why "pull the host's whole roster" is a deliberate
  switch, not a default: that button is a mass-redistribution button, and the
  host must choose to expose it.)

### What the policy layer may *not* do

It decides *whether* and *what*, never *how safely*. Every transfer, in every
scope, still: happens outside `Match::step` (lobby/handshake or the Corrosion
side channel); carries only sandboxed data, never code; is digest- and
`source_hash`-verified on arrival (step 4); is health-audited and resource-capped
before it plays; and obeys the per-char / per-match / per-peer ceilings. The
switches gate the door — they do not unlock the verification.

### Status & build order

**Built and loopback-tested:** manual `pack`/`unpack`; the content-identity
hash and the setup-hash refusal; the chunk/reassembly transfer + `requests`
delta; the `Room::Need` message; the two-sided policy with safe defaults and
size caps (`oxyde_net::byoc`) and its `[Sharing]` config; the pull-only transfer
sessions (`Incoming`/`Outgoing`); and the one verified, path-confined mount every
received character passes through (`oxyde_app::bundle::receive`). A full
pack → session → reassemble → verify → confined-mount → re-hash round trip is a
test, as are the traversal and wrong-character refusals.

**Built since:** the trigger flow is driven from the game's online loop — the
pre-match pump sends `Declare`/`Need`/`Content`, mounts a finished transfer into
a VFS overlay so the fighter resolves at its pick path, and the first bout waits
for the transfer instead of refusing a missing fighter (bounded, so a declined
or stalled share cannot hang the match). Harness-tested; see the Status note.

**Pending, in order:** (1) the two-machine run below — the only thing in-process
testing cannot stand in for; (2) the Options → Content sharing pane and the
`accept = ask` prompt (today `ask` surfaces the request but the pump acts only on
the automatic `single`/`roster` policies); (3) the `Room::Catalog` browse message
for selective requests beyond the match-time picks, and roster sync on top of it;
(4) the Corrosion `--share-content` side channel last, as its own mode.

---

## The two-machine test plan

On a second host reachable over SSH (specs: a mid-range Linux box, 8+ cores,
16–32 GB, 150 GB SSD, ideally a *different* CPU than the first so determinism is
cross-checked):

1. Install the engine on both; give each a character the other lacks.
2. Start a match. Confirm the pre-BYOC build **refuses** (the content fold
   working), then the BYOC build **transfers** and plays.
3. Confirm the received character's `source_hash` matches and the match's
   checksums stay identical on both peers for the whole bout (no desync).
4. Pull the link during a transfer; confirm `missing()`/`resend()` recovers it.
5. Repeat with a *different version* of the same character to confirm the
   version mismatch, not just absence, triggers the transfer.

Until then, `oxtool pack`/`unpack` is BYOC you can drive by hand: export your
character, send the file, and the other install verifies it by content hash.
