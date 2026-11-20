# Corrosion mode

The engine on one machine, the picture on another. A client plays the whole
archive without having any of it.

```
host$   oxyde --root . --corrosion-host 0.0.0.0:7411
client$ oxyde --corrosion-join host.example:7411
```

## Joining from a machine with no content

**The client needs the binary and nothing else.** No `data/`, no `chars/`, no
`oxyde.cfg` — an 18 MB file in an empty directory:

```
$ ls
oxyde
$ ./oxyde --corrosion-join host.example:7411
Oxyde 0.37.0 — corrosion client
  connecting host.example:7411
  connected  seat 0
  no content is loaded on this machine
```

That path is taken *before* the archive is opened, which is what makes it
possible: the client never looks for content, so there is none to be missing.
`--seat 1` takes the second controller; omit it and you get seat 0, or a
spectator's view once both seats are taken. `--width` / `--height` size the
window, and `oxyde.cfg` is read if one happens to be there.

**Hosting needs a display**, because the picture a client receives is the one
the window draws. On a machine without one, give the process a virtual display
rather than `--headless`:

```
xvfb-run -a oxyde --root . --corrosion-host 0.0.0.0:7411
```

`--headless` with `--corrosion-host` is refused with that advice. It used to be
accepted silently and bind nothing, which is the worst way for a flag to fail.

---

## What it is for, and why it is not the other netplay

Every other networked mode here sends **inputs** and re-simulates on both ends —
two `u16`s a frame, which is what makes rollback, replays and spectating the
same three hundred lines. That requires both machines to hold the same content,
byte for byte: the same thousand characters, the same `common1.cns`, the same
`mugen.cfg` limits.

Corrosion mode is the case where they do not.

| | Rollback netplay | Corrosion |
|---|---|---|
| What crosses the wire | inputs | inputs one way, the screen and its sound the other |
| Content needed on the client | all of it | **none** |
| Bandwidth | ~2 kbit/s | ~1–3 Mbit/s, plus ~0.4 for sound |
| Latency added | none (rollback hides it) | one round trip |
| Can the client desync? | it is the whole problem | it is not simulating anything |
| Can the client cheat? | in principle | there is nothing there to cheat with |

What it buys:

* Somebody joins a 40 GB roster from a laptop, and downloads nothing.
* A tournament can *demonstrate* that every entrant is on the same build with
  the same characters, because there is one copy of both.
* A spectator sees and hears exactly what the players do, with no content at
  all.

---

## How the picture is sent

Not as video. The obvious answer is a codec — `oxyde-video` already links one —
and it is the wrong tool here for three reasons that all come from what this
particular picture is:

* **Latency.** A video encoder wants to buffer frames to make good decisions. A
  fighting game is decided in three frames; anything that holds a frame back to
  compress it better has already lost.
* **The content is flat colour.** A 320x240 playfield of palette-indexed sprites
  over a mostly-static backdrop is the case block-based DCT is worst at and
  delta-plus-deflate is best at — no ringing on the hard edges the whole art
  style is made of, and *exact* pixels rather than nearly.
* **It costs nothing to depend on.** Tiles and `flate2` were already here.

So a frame is cut into 16x16 tiles, each tile is hashed, and only the tiles that
changed are deflated and sent. During a round most of the screen is a backdrop
that does not move.

Measured against a synthetic fight — a static backdrop and two figures moving
across it, 120 frames at 320x240:

| | |
|---|---|
| Tiles sent | under 20% of the screen |
| Bytes sent | under 5% of the raw frames |

Sixteen is the tile size because it is the smallest at which the per-tile
overhead stays under a tenth of the payload, and the largest at which a
fighter's arm moving does not dirty half the screen. Eight sends 40% more bytes;
thirty-two sends 60% more.

### Why TCP

Rollback sends the same two bytes every frame and does not care which copies
arrive — a lost input is predicted and a wrong prediction is rolled back.
Losing a *tile* has no such recovery: the picture is wrong in one square until a
full frame is sent, and asking for one costs a round trip and a whole screen.
Ordering matters too — a delta applied out of order is not a late frame, it is a
corrupt one.

The latency argument against TCP is about head-of-line blocking on *stale* data,
and there is none here: every frame is needed, in order, exactly once.

### Recovery

A gap in the sequence is noticed, not papered over. The client asks for a
complete frame and the host obliges — per client, so one late arrival does not
cost every other viewer a full screen. The same happens on a resize, on a
corrupt tile, and on connect.

---

## How the sound is sent

Down the same connection, as a packet queued immediately after the frame it was
captured alongside. One socket means one ordering and one congestion window:
there is no second stream to fall behind the first, which is the usual way a
streamed picture and its sound come apart.

### Not PCM, and not Opus either

The picture is sent as changed tiles because a fighting game's screen is mostly
still. Sound has no such structure — every sample is new, sixty times a second,
and deflating game audio saves almost nothing. So the coder is **IMA ADPCM**,
four bits a sample:

* Exactly 4:1 against 16-bit PCM, always. That is 44.1 kHz stereo at 350 kbit/s
  instead of 1.4 Mbit/s — which matters, because 1.4 Mbit/s is *half again* what
  the picture costs, and the sound would have been the expensive half of a
  corrosion session.
* **No latency at all.** No window, no lookahead, no bit reservoir: sample in,
  nibble out. Anything that buffered audio to compress it better would lose the
  same argument a video encoder loses against the tile stream.
* **Nothing new to depend on.** The whole coder is two tables and a loop, which
  is the same reason the tiles are deflated rather than encoded. Opus would be
  better sound per bit and a C library or a large dependency to carry.
* Each packet is **self-contained** — the predictor and step index travel with
  it — so a packet the client deliberately drops costs that packet and not the
  rest of the round.

What it costs is quality: ADPCM is audibly lossy on music, roughly a 1990s
console's DAC. For a spectator's stream of a fighting game that is the right
trade, and it is the one decision here somebody might reasonably want to change.

### Staying in sync, and what gives way

Three rules, in the order they are enforced:

1. **Audio never delays a frame.** The host drains whatever the mixer produced
   when it sends a frame, compresses it once, and queues the same bytes to
   every client *after* that client's tiles. A client that is behind gets this frame's picture
   before last frame's sound.
2. **The sound card never waits for the network.** The tap the mixer writes into
   is taken with `try_lock`; if the frame loop holds it, that block is dropped
   and counted. A glitch on one machine's speakers is better than a stall in
   everybody's picture. The same rule runs backwards on the client: its audio
   callback plays silence rather than waiting for the socket thread.
3. **Drift is corrected by dropping, never by stretching.** The client holds a
   jitter buffer with a target depth of 33 ms — two frames — and a ceiling of
   120 ms. Below the target it plays silence rather than stalling; above the
   ceiling it throws the *oldest* samples away. Resampling to pull the queue
   back would trade one click for a permanent pitch error.

The consequence, said plainly: **lip-sync is bounded, not zero.** The sound is
between one frame and the queue ceiling behind the picture, and a client whose
network stalls hears silence and then catches up, rather than hearing the last
second of the round half a second late. Two counters say which is happening —
samples *dropped* mean this client is behind the host, samples of *silence* mean
the host went quiet or the client is ahead — and `oxtool corrode` prints both.

### What it costs

At 48 kHz stereo, one frame's sound is 800 sample frames: 1,600 samples, 800
bytes of nibbles, plus six bytes of coder state and thirteen of header. That is
about 49 KB/s, or 390 kbit/s — against the picture's 1–3 Mbit/s.

---

## Seats

```
oxyde --root . --corrosion-host 0.0.0.0:7411
```

Two seats by default, handed out lowest-free-first. A third connection is
accepted as a **spectator**: it receives frames and its buttons are ignored.
A client that disconnects frees its seat.

A client's buttons are *unioned* with the local controller rather than replacing
it, so somebody sitting at the host can still play — and a client that drops
mid-round leaves the seat to whoever is there rather than to nobody.

```
oxyde --corrosion-join host:7411 --seat 1
```

---

## What the client is

A window, a controller, and nothing else. No `Assets`, no `Character`, no
`Stage`, no `SpriteBank`, no `Match` — `oxyde-app/src/corroded.rs` is short
precisely because of what is not in it. The client never opens the archive
because it does not have one.

---

## Checking it without a display

```
$ oxtool corrode 127.0.0.1:7521 --frames 180 --hold 400 --out shot.png --wav sound.wav
corroded   127.0.0.1:7521
  seat       0
  holding    0x0400

  50 frame(s) painted in 3.0s, 0 repair(s)
  audio      none arrived
  picture    960x720
  painted    91.2% of the frame
  wrote      shot.png
  ! no sound to write
```

The real client needs a display, which makes the one thing worth testing — does
a machine with none of the content see and hear the game? — the one thing that
cannot be tested headlessly. `oxtool corrode` is a client with no window: it
connects, sends a scripted controller, and writes out what arrived, as a PNG and
as a WAV. It loads no archive, exactly as the real client does not.

`--hold 400` is START. Held against a host sitting on the title screen, it
produces a picture of the character select grid — every fighter in the archive,
none of which exist on the machine that photographed them. That run was against
a real `oxyde --root . --corrosion-host` under `xvfb-run`, which is the only way
to have a host on a machine with no display.

"None arrived" there is a host that sent no sound. The audio tap is wired now —
the mixer hands every block it renders to `Host::set_audio_tap`
(`oxyde-app/src/main.rs`) — but a host on a machine with no sound device has
nothing to send, which is the case on this machine (`snd_pcm_open failed`); see
the limits below. Against a host that does send sound, the same command with
`--wav` reports it:

```
$ oxtool corrode 127.0.0.1:7511 --frames 300 --hold 400 --out shot.png --wav sound.wav
corroded   127.0.0.1:7511
  seat       0
  holding    0x0400

  295 frame(s) painted in 5.0s, 0 repair(s)
  audio      48000 Hz x2, 299 packet(s), 240 KiB
  buffered   66 ms mean, 50 ms now
  lost       0 sample(s) dropped, 0 of silence played
  picture    320x240
  painted    99.2% of the frame
  wrote      shot.png
  wrote      sound.wav (4.93s, peak 0.60)
```

Those last three lines are the diagnosis. `buffered` should sit between the
33 ms target and the 120 ms ceiling; `dropped` climbing means this client is
behind the host, and `silence` climbing means the host is not producing sound
fast enough or this client is playing it faster than it arrives. Here both are
zero and the recording is 4.93 seconds of unbroken 440.0 Hz, which is the
stream staying in step for five seconds without a correction.

### A host with no engine

```
$ oxtool corrode --serve 127.0.0.1:7511 --frames 420
corrosion  host with no engine
  listening  127.0.0.1:7511
  picture    320x240, a bar on a gradient
  sound      440 Hz tone, 48000 Hz stereo

  420 frame(s) sent to 1 client(s)
  traffic    1675 KiB, 12.2% of tiles
  audio      0 block(s) missed, 0 sample(s) dropped
```

The other end of the same idea: a corrosion host with no archive, no simulation
and no sound device, streaming a moving picture and a tone. Both halves of the
protocol can then be driven from a terminal with no display anywhere in sight,
which is how the sound stream above was measured: 240 KiB over five seconds is
48 KB/s, as predicted.

---

## Limits, stated plainly

* **One round trip of input latency.** Unavoidable: the simulation is somewhere
  else. Fine on a LAN, noticeable across a country, unplayable across an ocean.
  Rollback netplay remains the right answer when both ends have the content.
* **Bandwidth scales with motion, not resolution alone.** A 640x480 host with a
  busy screen costs more than a 320x240 one with a still one.
* **The host's mixer is plugged into the tap, but the live path is unproven on
  this machine.** Everything is wired — the packet, the coder, the host's tap,
  the client's queue, `oxtool corrode`, and the line in `oxyde-app` that hands
  the mixer's output to `Host::set_audio_tap` (`main.rs`). What is not proven
  here is the live engine-host path end to end, because this machine has no
  sound device (`snd_pcm_open failed`), so the mixer never runs and there is
  nothing to tap; `oxtool corrode --serve` drives the whole protocol without it.
  A host also has nothing to stream on any machine whose engine reports `audio
  UNAVAILABLE`: what is sent is what the mixer played, and a machine with no
  sound device plays nothing.
* **The sound is lossy and the lip-sync is bounded, not exact** — see above for
  both numbers.
* **No encryption.** Run it on a LAN or through a tunnel. The frames are
  pictures of a fighting game, but the inputs are a control channel.
