# HD sprites (HD / UHD)

Oxyde can draw characters and stages from **AI-upscaled sprites** while leaving
the fight itself untouched. It is a presentational layer: the simulation,
hit/hurt boxes, positions and the match checksum are byte-identical whether HD
is on or off — only the texture density on screen changes. So HD is safe for
netplay, replays and tournaments, and works under both the software and GPU
renderers.

## Turning it on

- **Config:** `[Video] sprite_hd = off | hd | uhd` (default `off`). `hd` is 2×,
  `uhd` is 4×.
- **Options menu:** Presentation → **HD SPRITES** (OFF → HD → UHD). It binds on
  the next match load — no restart.

A character or stage only draws HD if an HD **pack** is present for it (see
below); anything without a pack falls back to its original sprites, per sprite.
So a partial rollout is fine — HD turns on wherever packs exist.

## How a pack works

An HD pack is an ordinary **SFF v2.01** file sitting next to the base sprite
file: `ky.sff` → `ky.hd2.sff` (2×) or `ky.hd4.sff` (4×). It holds the same
`(group, image)` sprites as the base, at exactly N× the size. The engine keeps
the base sprite's geometry (position, axis, scale, localcoord) and only swaps in
the higher-resolution texture, so the on-screen footprint never moves — it just
gains detail.

## Building a pack

Three steps (the middle one is the GPU upscale; the ends are `oxtool`):

1. **Export** the base sprites to PNG, baking the character's real palette:
   ```
   oxtool sprites export chars/ky/ky.def  /tmp/ky_png
   ```
   Give it the `.def` (not the `.sff`) so the character's `.act` palette is
   applied — otherwise the SFF's embedded palette is used, which for many
   characters is a neutral/placeholder set. `--pal N` bakes a different palette.

2. **Upscale** the PNGs 2× (or 4×) with your super-resolution model of choice.
   The reference pipeline uses Real-ESRGAN and handles transparency safely
   (RGB and alpha upscaled separately so silhouettes don't halo).

3. **Pack** the upscaled PNGs back into a sidecar SFF:
   ```
   oxtool sprites pack /tmp/ky_png_2x  chars/ky/ky.hd2.sff  --scale 2
   ```
   `pack` checks every sprite is exactly N× its base size and writes a Png32
   (RGBA) SFF v2.01 by default — no colour quantised away, and large.

   For a much smaller pack, add `--png8` (optionally `--colors N`, default 256):
   ```
   oxtool sprites pack /tmp/ky_png_2x  chars/ky/ky.hd2.sff  --scale 2 --png8
   ```
   This quantises each sprite to an indexed palette (index 0 the transparency
   key) and writes png8 SFF entries, which the engine draws exactly as it does
   any indexed sprite. The quantiser is the one `oxtool sprites --quantise`
   measured best over the archive (median cut, nearest entry — lossless when a
   sprite fits in the palette); **no dithering** is ever applied, because a
   dither drawn in palette indices becomes noise under a PalFX or `.act` change
   and shimmers frame to frame across an animation. Measured on Ky's 2× pack:
   the Png32 SFF is **268 MB**, the png8-256 SFF is **67.8 MB** (**25.3%**,
   ~3.9× smaller), and the two render indistinguishably. `--colors` below 256
   trades a little more fidelity for a little more size. Soft upscaled edges go
   opaque under png8 (indexed sprites carry only the index-0 transparency key),
   so use Png32 when feathered silhouettes matter and png8 when size does.

Stages are identical: export/upscale/pack the stage's `.sff` to
`<stage>.hd2.sff`.

## Cost, and why it ships separately

HD packs are large. AI upscaling turns flat palette fills into truecolour
gradients, which do not compress like the original paletted art — a 2× pack runs
roughly 15–18× the base `.sff` (Ky: 24.7 MB → 441 MB at 2×). Across the whole
roster that is on the order of **~150 GB at 2× with a stock model**, and ~4–5×
that at 4×. For that reason:

- HD packs are **not** in the base download; they are an **optional add-on**
  (per character, or a separate HD pack).
- **UHD (4×)** is intended as a per-character/opt-in tier for large displays and
  close-up cameras, not a roster-wide default.
- A **sprite-specific fine-tuned** upscaler (planned) both looks truer to the
  cel art and compresses far better, because it stops inventing gradient noise
  in flat regions; it will shrink these numbers substantially.

## Limitations

- **Palette / colour-select.** An HD pack bakes one palette. Default-palette
  fighters (e.g. Knuckle Up enemies) look correct; player **colour-select** will
  not recolour HD sprites until per-palette packs or an index-preserving upscale
  are added.
- **Portraits.** `9000`-group portrait sprites can carry padding artefacts from
  a 32-colour `.act`; they are not drawn in the fight and are skipped when
  batching packs.
