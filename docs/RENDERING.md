# Rendering

The software rasteriser, the hardware path that sits on top of it, and the four
things the GPU makes possible.

---

## The software path is still the authoritative one

`oxyde-render` fills a `Framebuffer` on the CPU. That path is what every test
asserts against, what `oxtool` renders headlessly, and what runs on a machine
whose GPU driver is a rumour. **Nothing here replaces it.**

`renderer = software` is the default. A GPU is one more thing that can be
missing, out of date or subtly wrong, and an engine whose default path depends
on one is an engine that does not start for somebody.

```ini
[Options]
renderer = software   ; default - CPU rasteriser through softbuffer
; renderer = gpu      ; hardware, and say so if it cannot be had
; renderer = auto     ; hardware if it initialises, software in silence
```

Opening a device never panics and never aborts start-up. On `gpu` a failure is
reported and the software path is used; on `auto` it is used without comment.
A software Vulkan implementation (llvmpipe) is *declined* rather than used:
llvmpipe presenting a scaled frame is slower than the `memcpy` it would replace.

---

## 1. Scaling that is not a choice between blurry and chunky

The playfield is 320x240. A modern screen is not a whole multiple of that, and
both obvious answers are wrong:

* **Nearest** picks one source pixel per destination pixel. At a non-integer
  scale some source pixels land on two destination pixels and some on one, so a
  fighter's outline is one pixel thick here and two there — and which is which
  *changes as the camera moves*. That is the shimmer every emulator front-end
  has a page about.
* **Bilinear** blends everywhere, so a hard pixel edge becomes a two-pixel ramp
  and twenty-year-old pixel art looks like a photograph of itself.

`shader = sharp` is the standard answer and it is four lines: sample at the
texel centre across the whole middle of each texel, and ramp to the boundary
only over the last destination pixel at each edge. Edges stay hard, nothing
shimmers, and it costs one texture fetch.

The ordering matters and is easy to get backwards. Clamping `offset * scale`
ramps through the *centre* of the texel and sits on the boundary — a 50/50 blend
— for most of it, which is blurrier than plain bilinear rather than sharper.
Subtracting the clamp is what makes the flat part flat. The test that caught
this measures the width of the red-to-blue transition at 3.75x and asserts it is
at most two pixels.

```ini
[Options]
shader = sharp          ; nearest | sharp | smooth | scanlines | crt | lcd
shaderstrength = 1.0
```

| | |
|---|---|
| `nearest` | No filtering. Correct at whole multiples, shimmery elsewhere |
| `sharp` | Hard edges without the shimmer. **Recommended** |
| `smooth` | Plain bilinear, for somebody who wants it softened |
| `scanlines` | Darkened alternate rows |
| `crt` | Scanlines, a barrel curve and an RGB grille |
| `lcd` | A flat pixel grid, no curvature, no glow |

One shader module per effect, compiled on first use, rather than one über-shader
taking a uniform branch — the branches are per *pixel* at up to 4K, and a
constant the compiler can fold is free where a uniform read is not.

```
$ oxtool gpu . --out shots/
adapters
  fastest   NVIDIA A2 (DiscreteGpu, Vulkan, NVIDIA)
  software  llvmpipe (LLVM 20.1.2, 128 bits) (Cpu, Vulkan, llvmpipe)

source     320x240  ->  800x600 (2.50x)
shaders
  nearest     86.7% painted   88.22 ms  shots/nearest.png
  sharp       88.6% painted   27.83 ms  shots/sharp.png
  ...
```

Deliberately a fractional scale: at a whole multiple every filter agrees and the
comparison shows nothing.

---

## 2. Perspective

MUGEN has no third axis. Ikemen GO added `xangle`, `yangle`, `projection` and
`focallength` to `AngleDraw` and to background elements, and Oxyde now draws
them honestly rather than approximating.

It used to squash the axis being turned about by `cos(angle)`. That is exactly
right at 0 and 180 degrees and a lie in between, because it happens in *sprite*
space and so disagrees with any in-plane `angle` applied after it.

The rasteriser now places the sprite's four corners in space, rotates them about
X and Y, projects them, and builds the **homography** that maps the sprite's
rectangle onto the resulting quadrilateral. Inverting it once, before the loop,
turns the inner loop back into "read a destination pixel, ask which source pixel
it came from" — the same shape as every other path here, and equally exact. One
function then covers rotation, shear and perspective alike, because when the
quad is a parallelogram the projective terms vanish and it reduces to an affine
map.

```ini
; on a character, through AngleDraw
[State 0]
type = AngleDraw
trigger1 = 1
xangle = 30
projection = perspective2
focallength = 512

; on a stage background
[BG floor]
type  = normal
angle = 0
xangle = 60
projection = perspective
```

`orthographic` (the default, and Ikemen's) gives exactly `cos(angle)`;
`perspective` measures depth from the centre of the *screen*, so a row of tilted
panels all lean the same way; `perspective2` measures it from each sprite's own
axis, so each is upright in its own right.

Stage backgrounds also gained `angle` and `xshear`, which MUGEN never had at all.

**Nothing in this archive sets any of them** — the whole group is an Ikemen
extension — so replacing the approximation cannot change a stage or a character
that already works.

---

## 3. glTF stage backdrops

```ini
[BGdef]
model = stage3d.glb
spr   = stage3d.sff     ; still required: the software path and the portrait

[Model]
offset = 0,-0.2,-0.9
scale  = 0.05, 0.05, 0.05
rotate = 0,0,0

[Camera]
fov  = 30              ; where Ikemen GO puts it, and where its own stage does
near = 0.1
far  = 10000
```

Indexed or non-indexed triangle lists with `POSITION`, `TEXCOORD_0` and an
optional `NORMAL`, one base-colour texture per material, node transforms,
`KHR_materials_unlit`, `KHR_lights_punctual`, and glTF animation of a node's
translation, rotation and scale.

`fov`, `near` and `far` are read from `[Camera]` first and `[StageInfo]`
second. Ikemen GO reads them from `[Camera]` only, which is where its own
`stage3d.def` writes `fov = 30` — with a comment above it explaining what it is
for. Reading `[StageInfo]` alone meant Ikemen's own reference stage was drawn at
the default 40 degrees, a visibly wider shot than the one it asks for.

Skinning and morph targets are absent, and that is a boundary rather than a
gap: both of them are for a character, which is the other half of Ikemen's 3D
layer and the half that would have to become part of the simulation.

Verified against Ikemen GO's own `stages/stage3d.glb` — 9 meshes, 7,352
triangles, six animations — and against `stage3d_outline.glb`, which this
engine used to **refuse**: it carries Ikemen's own `_OUTLINE_ATTRIBUTE` vertex
attribute, and the glTF reader only recognises an underscore-prefixed semantic
with its `extras` feature on. Twelve megabytes of stage were being thrown away
over an attribute nothing here reads.

At 640x480 on an NVIDIA A2, including the readback: 12 ms on the first frame
while the pipelines compile, then 1.4 ms. Animating costs nothing measurable.
Lighting the whole set and casting a shadow from it — which no real stage does,
because they are all unlit — takes it to 1.6 ms.

### Lighting

A directional light and an ambient term, and no more than that. The art a
MUGEN-era stage ships is a hand-painted diffuse texture, so the only thing
lighting can usefully add is which way a surface faces; anything more arrives
as a shine on a texture that already has one drawn in.

**`KHR_materials_unlit` is obeyed.** A material that asks not to be lit is not
lit, which is what Ikemen does and what matters most here, because Ikemen GO's
own `stage3d.glb` marks *every* material unlit. Turning lighting on therefore
changes not one pixel of the only 3D stage that exists — there is a test that
renders it with the light on and off and compares the readbacks byte for byte,
and a second one that flips the override to prove the first was testing
something.

**The light comes from the file where the file has one.** `KHR_lights_punctual`
is Ikemen's own place for this and the only place its `.def` format has, so a
set authored for Ikemen lights the same way here with its `.def` untouched. The
first directional light in the scene is taken; a second would have to be either
averaged in, which is not what the author asked for, or dropped in silence.
Point and spot lights are not read.

For a file that declares no light, the `.def` can:

```ini
[Model]
environmentintensity = 1.0     ; Ikemen's own key: how hard the surroundings light it
light        = -0.4, 0.85, 0.5 ; direction *towards* the light, in model space
lightcolor   = 179,179,179     ; 0-255, the way [Shadow] color is written
ambientcolor = 102,102,107
castshadow   = 1
lightunlit   = 0               ; light a material that asked not to be
```

Only `environmentintensity` is Ikemen's; the rest are Oxyde's, because Ikemen
has no def-level light at all — it has `environment`, an image-based light,
which is a different renderer. Every default is the fallback light rather than
darkness: a model with no lights anywhere would be faithful to the format and
invisible.

`lightunlit` should stay off on a finished stage. It exists because every 3D
stage that exists today marks its whole set unlit, so there is otherwise no way
to look at what the light does to one.

### Animation

Node translation, rotation and scale, with `LINEAR` and `STEP` interpolation
and `CUBICSPLINE` read as linear through the same keys — which differs from a
spline in the middle of a segment and not at the keys, and nobody will see it
on a backdrop. Rotation is slerped the short way round, because a quaternion
and its negation are the same rotation and interpolating towards the wrong one
makes a gong swing 350 degrees to get to -10. Ikemen's `loopCount` and
`enabled` node extras are read.

**The clock is the stage's tick, not the wall's.** This is the same argument as
[§4](#4-video-backgrounds) and it lands the same way: `Model::set_tick` takes
`Stage::tick`, the counter the `[BG]` layers and the `[BGCtrl]` controllers
already run on. It stops when the fight stops, goes back to zero on `resetBG`,
and gives the same pose for the same tick — so a replay of a fight on a 3D
stage shows the same backdrop, down to where the gong was when the round ended.
The default is tick 0, a still model, rather than anything derived from a clock.

**Wired into the game loop.** `Game::draw_stage_model` now calls both before it
draws, from the `stage` that function already has in hand:

```rust
sm.model.set_tick(stage.tick);
sm.model.set_lighting((&stage.model_light).into());
```

So in a match a 3D backdrop animates on the fight's tick (`stage.tick`, the
same counter the `[BG]` layers run on, so a replay reproduces the same pose) and
is lit by the stage's own `model_light`. Both setters compare before they store,
so a still model on a fixed light costs two comparisons a frame. `oxtool gpu`
drives the same two setters headlessly.

### Shadow mapping

One depth-only pass from the light into a 1024-square `Depth32Float` map, and a
nine-tap comparison in the fragment shader. The pass is skipped entirely when
nothing in the set is lit, and the map is only redrawn when the pose or the
light changes, so a static stage pays for it once.

Two details are worth stating because they are where a shadow map usually goes
wrong:

* **The frustum is fitted to the model.** Ikemen GO asks the stage author for
  six numbers — `shadowMapNear`, `Far`, `Left`, `Right`, `Top`, `Bottom` — and
  its own wiki warns that "the frustum should cover all the visible objects in
  order to produce correct result". Deriving it from the model's own bounds for
  the current pose means it always does, and there is nothing to get wrong.
* **The shadow pass has a fragment shader**, whose only job is to discard below
  the alpha cutoff. Without it a foliage card casts a rectangle.

Bias is in two places on purpose: a small constant in normalised depth, plus
the pipeline's own slope-scaled bias, which is the half that keeps working when
the fitted frustum turns out deeper or shallower than usual.

### Looking at any of it

```
$ oxtool gpu --def Ikemen-GO-Screenpack/stages/stage3d.def \
      --out-model shot.png --scale 2 --tick 0,60,120
stage      Third Heights by SuperFromND
  9 primitive(s), 2 material(s) (0 lit), 7352 triangles, 6 animation(s)
  anim     GongAction          4.15s  2 channel(s)
  ...
  !        every material is KHR_materials_unlit, so nothing here takes a light
           pass --force-lit to light it anyway
  camera   fov 30, near 0.1, far 10000, offset [0.0, -0.2, -0.9]
  tick 0     640x480 in   1.42 ms, 100.0% painted  shot-0.png
  tick 60    640x480 in   1.47 ms, 100.0% painted  shot-60.png
```

`--def` takes the camera, the placement and the light from a stage's own
`.def`, and loads the model it names, so the picture is a test of the parser as
well as of the renderer. `--model` names a `.glb` directly. `--tick` writes one
PNG per tick, named after it; `--force-lit`, `--no-shadows`, `--light X,Y,Z`
and `--ambient F` override the light. Everything runs headlessly, and
`--software` forces Mesa so the answer depends on lavapipe rather than on
whichever driver the machine has — the two agree on the synthetic shadow
fixture to within four pixels along one shadow edge.

### How it reaches the screen

Rendered to an offscreen texture and **read back** into the software
rasteriser's framebuffer as the stage background, rather than composited on the
GPU. Compositing would be faster and would mean two rendering paths for the rest
of the frame: shadows, the `EnvColor` wash, the super darkening, reflections,
the gutter fill and the HUD all read and write that framebuffer, and every one
would need a second implementation.

The readback costs one texture copy a frame — about a megabyte at 640x480 — and
keeps all of them working unchanged. That is the right trade for a feature no
stage in this archive uses. If a 4K 3D stage ever makes it hurt, the answer is a
second compositing path, not a second engine.

A 3D stage on `renderer = software` draws its `[BG]` layers instead, which is
what the stage ships them for.

### Presentation only, and what that rules out

Nothing in this section is part of the simulation. The lighting, the shadow map
and the animation clock are all read off state the fight already computed, and
none of them writes anything back: the software rasteriser draws the same
fight, the replay reproduces the same fight, and a netplay peer with no GPU
sees the same fight. That is the whole reason a GPU-only 3D layer is allowed to
exist at all.

**A Z axis for characters is the one that cannot be.** Ikemen GO has it; it
changes where a fighter is, and therefore what hits, and therefore what a
replay and a netplay peer compute. It is not a presentation feature dressed up
as one, and it is left out rather than taken on quietly.

### What the per-primitive uniforms used to do

Worth writing down because the picture was wrong for a long time and looked
fine. Each primitive's transform, tint and normal matrix went into one uniform
buffer, rewritten inside the draw loop with `Queue::write_buffer`.

That call does not happen where it is written. It is staged and performed at
`submit`, *before* any command in that submission runs — so every draw read
whatever the *last* primitive had written: one transform for the whole model.
A set whose node transforms are mostly the identity looks very nearly right
that way, which is why nobody noticed; Ikemen's `stage3d.glb`, whose gong,
stand and four islands each sit on their own node, did not. It drew as a
handful of flat shapes scattered near the horizon.

It is now one slot per primitive in a single buffer, selected by a dynamic
offset, all of it written before the pass is encoded. The gong is a gong. An
animated node could not have moved at all under the old scheme, which is how
it came to light.

---

## 4. Video backgrounds

Ikemen GO added `[BG] type = video`. Oxyde reads the same files with the same
parameters and differs in two deliberate ways: the clock, and which codecs are
in the box.

**The clock is the simulation's, not the wall's.** Ikemen advances a video by
elapsed real time. That is the obvious choice and the wrong one for this engine:
`Match::step` is a pure function of state and inputs, the netcode re-runs it on
a mispredict, and a replay is two `u16`s a frame. A backdrop driven by
`Instant::now` shows something different every time the same fight is played
back, and something different on each side of a netplay session.

So a video is addressed by **frame number**, and the frame number comes from the
tick count. A replay of a fight on a video stage is then the same fight, down to
which frame of the backdrop was on screen when the round ended. Two smaller
things follow: seeking backwards is cheap (a replay rewind is a number going
down, and the decode restarts at the nearest key frame — or at the frame itself,
for MJPEG), and a machine that drops frames drops them from the backdrop too, in
step with everything else, instead of the video sliding ahead of the fight.

WebM and Matroska containers, and Ikemen's six `scalemode` values spelled the
same way.

### A video is a **layer**, and that is where the flexibility comes from

```
[BG arena screen]
type    = video
path    = video/crowd.webm
start   = -120, -80
scalestart = 0.25, 0.25
window  = 0, 0, 160, 120
layerno = 0
```

`type = video` is a `BgKind` beside `normal`, `parallax` and `anim`, matched on
its leading letter like the others — this archive is full of layers spelled
`norm`, `ani` and `nomal`, and a video layer spelled `vid` is read the same
way. Declaring it a *kind* rather than a special case is the whole design, and
it is what buys every one of these, at no cost in new code:

| parameter | what it does to a video |
|---|---|
| `start` | where it sits. Its **top-left corner**, since a frame has no axis of its own |
| `delta` | it scrolls with the camera at its own rate — a video *parallaxes* |
| `scalestart`, `scaledelta` | how big, and how that changes as the camera rises |
| `window`, `windowdelta` | clips it to **an area of the screen** |
| `tile`, `tilespacing` | repeats it across or down |
| `layerno` | `0` behind the fighters, `1` in front |
| `trans`, `alpha` | fades it, or adds it over what is behind |
| `velocity`, `sin.x`, `sin.y` | it drifts and it oscillates |
| `enabled`, `id`, the `BG*` controllers | switched on and off mid-round like any layer |
| `loop` | whether it repeats. **Defaults to `0`**, which is Ikemen's documented default — a stage backdrop usually wants `loop = 1` written explicitly |
| `scalemode` | `none` (the default), `fit`, `fitwidth`, `fitheight`, `zoomfill`, `stretch`. Applied *before* `scalestart`, which multiplies it |
| `volume` | the soundtrack's level, out of 100 |

So **a stage may declare as many videos as it likes, each in its own place, at
its own size, clipped to its own area, mixed freely with still layers in any
order.** One playing on a screen above the ring at quarter size behind the
fighters, another tiling across the crowd in front of them, and a painted
`type = normal` backdrop between the two, is four lines of `.def` each and
nothing else.

And because `parse_layers` is one function shared by three readers, the same
`[BG]` block works in a **stage**, in a **screenpack** — a title screen or a
select grid with a moving backdrop — and in a **storyboard**, which is where
Ikemen GO's own `logo.def` and `credits.def` put theirs.

Three limits, stated rather than discovered, and the first two are places
Ikemen GO is ahead:

* **Rotation and shear.** Ikemen's own documentation lists `angle`, `xangle`,
  `yangle`, `projection`, `focallength` and `xshear` as working on a video
  element. Here they are **ignored rather than approximated**, because silently
  drawing an unrotated layer where a rotated one was asked for is the sort of
  quiet wrongness this engine is written against.
* **`scalefilter`.** Ikemen takes eleven values and defaults to
  `fastbilinear`; this engine samples nearest-neighbour and reads the key not
  at all.
* **`PalFx`**, which does not apply — there is no palette to transform, the
  same reason eleven of the sixteen built-in shaders are palette transforms.
  Ikemen lists `trans`, `alpha` and `palfx` on a video as *untested*; the first
  two work here.

### The decoder may economise; the `.def` still means what it says

A 720p file drawn a quarter size is decoded at 320x180, because converting
921,600 pixels so the rasteriser can sample 57,600 of them is most of the cost
of playing one — **12.42 ms a frame against 3.06**. But the layer is still 1280
units wide as far as its `.def` is concerned. So a `VideoFrame` carries the
size it should *measure* as alongside the size of its buffer: geometry is
computed from the first and sampling steps across the second, and nothing
rewrites the author's numbers to make the arithmetic come out.

The first version did rewrite them, and it was a real bug rather than an
inelegance: an arcade ladder hands the same `Stage` back for a second match,
the compensated scale was read as though it were the authored one, and the
backdrop drew four times too big.

### Why the frame is handed to the renderer rather than fetched by it

`oxyde-render` does not depend on `oxyde-video` and should not: a renderer that
opens files has to care about the VFS, about codecs and about a clock. So a
layer holds a `VideoFrame` — `0x00RRGGBB`, the framebuffer's own packing — and
whoever owns the decoder calls `Stage::set_video_frame` once a tick. A layer
that has been handed nothing draws nothing, which is exactly what a missing
file, an unbuilt codec, or a file still opening should do. One silent layer
does not break a stage.

Drawing is a second blit, `raster::blit_rgba`, rather than a branch inside
`blit`. `blit`'s inner loop is the hottest code in the engine and every
pixel-difference guarantee in the crate rests on it — that a 3D stage draws a
flat fight identically, that six post-processing shaders change nothing. A
branch there puts all of it back in question to serve a handful of files; a
separate function cannot regress sprite drawing, because sprite drawing did not
change. The cost is that the two must agree on *where* art lands, so
`a_video_frame_lands_where_a_sprite_of_the_same_size_lands` draws the same
picture both ways over 64 combinations of position, scale and flip and requires
**0 differing pixels**. Introducing a one-pixel drift in either makes it fail.

### Which codecs, and why those

| Track | Decoder | Licence | In a default build |
|---|---|---|---|
| `V_AV1` | `rav1d` — a Rust transliteration of dav1d | BSD-2-Clause | **yes** |
| `V_MJPEG`, and `V_MS/VFW/FOURCC` with `MJPG` | `zune-jpeg`, already here for SFF v2 sprites | MIT OR Apache-2.0 OR Zlib | **yes** |
| `V_VP8`, `V_VP9` | the system libvpx | BSD-3-Clause | **yes, when libvpx is installed** (loaded at run time by soname) |

Ikemen GO links FFmpeg, which is usually summarised as "it takes whatever FFmpeg
takes". Its own `build/build.sh` says otherwise: the FFmpeg it builds is
configured `--enable-demuxer=matroska,webm` and
`--enable-decoder=libvpx_vp8,libvpx_vp9,opus,vorbis`, and `BUILDING.md` names
the feature as "background video: VP8/VP9/Opus/Vorbis in WebM/Matroska". What
Ikemen *ships* is VP8/VP9 in WebM; anything more is what a user gets by opting
into a system FFmpeg with `BUILD_FFMPEG=no`.

Linking FFmpeg here to match that would trade one self-contained binary for a C
toolchain, six shared libraries and an LGPL relinking obligation, to gain
nothing over what this engine already reads. So the question became which
*royalty-free* codec has a decoder that needs no C — and the answer is AV1.
`rav1d` is Rust, BSD-2-Clause, and with `default-features = false` it does not
even want an assembler; AV1 itself is covered by the Alliance for Open Media's
patent licence, which is the same reason VP8 and VP9 were acceptable. MJPEG came
free: `zune-jpeg` is already in the tree for SFF v2's JPEG sprites, and JPEG's
patents expired last century.

What is deliberately **not** here is H.264, HEVC and the rest of the MPEG
family. Those are patent-encumbered whatever a decoder's copyright licence says,
which is why no royalty-free engine ships them, and no video content in this
archive or in Ikemen GO's own is in one.

MJPEG earns its place twice over: every frame is a whole JPEG, so it is the one
format where a *backwards* seek costs one decode rather than a run from the last
key frame. For the other two, each block carries Matroska's key-frame flag and a
rewind starts from the nearest one — `oxtool video` prints how many a file has,
and a file that flags none (some writers use block groups, which do not say)
rewinds from the start.

### Building it

A default build needs nothing but `rustc`: AV1 and MJPEG are pure Rust, and so
is the demuxer. VP8/VP9 need no feature either — the system libvpx is loaded at
run time, not linked (below). The one optional feature is AV1's assembler:

```toml
oxyde-video = { features = ["av1-asm"] }  # AV1's assembly, needs nasm to build
```

VP8/VP9 need no feature because `oxyde-video` loads the system libvpx **at run
time** with `dlopen`, trying `libvpx.so.10` down to `libvpx.so.6` and the
unversioned `libvpx.so`. One binary therefore plays VP8/VP9 on any distro that
has libvpx — Ubuntu 22.04's `.so.7` through 26.04's `.so.10` alike — and still
starts where it has none, detecting a VP8 or VP9 file, reporting it by name, and
falling back to the stage's `[BG]` art. The decoder ABI has been stable since
2010, so the soname is the only thing that varies; `vpx_codec_dec_init_ver` is
still handed `VPX_DECODER_ABI_VERSION`, which libvpx rejects on a real mismatch.

The libvpx bindings are hand-written rather than generated. Two published `-sys`
crates wrap this API: one uses a 2015 `bindgen` that cannot parse a 2024
`vpx_codec.h` at all, and the other vendors its own libvpx from 2015 and emits
future-incompatibility warnings. Neither is worth carrying for seven entry
points, and writing them out is smaller than the build script that would
generate them.

`av1-asm` turns on `rav1d`'s hand-written assembly, which is built by `nasm-rs`
and therefore needs `nasm` on the build machine — exactly the kind of dependency
the default build exists without. It changes nothing about behaviour and roughly
halves the decode time; it is there for a packager who has an assembler.

### Cost

One synthetic 720p clip — a bar sliding over a textured gradient — encoded three
ways and played back in order, at three output sizes. Medians of five runs on a
*shared* machine, so read them as "about this much" rather than to two decimal
places:

| ms/frame | native 1280x720 | 640x480 | 320x240 |
|---|---|---|---|
| VP9, libvpx | 10.6 | 6.6 | 2.5 |
| AV1, `rav1d` as built here | 22.5 | 15.6 | 10.3 |
| AV1, `rav1d` with `av1-asm` | 10.0 | 8.6 | 4.9 |
| MJPEG, `zune-jpeg` | 20.0 | 10.7 | 9.9 |

The engine has 16.6 ms a frame for everything, so the honest reading is: a 720p
AV1 backdrop does not hold 60 Hz in a default build, the same file at playfield
size costs most of a frame's budget, and `av1-asm` or a VP9 encode is the answer
for anyone who minds. That is the price of not linking a C decoder, stated
rather than hidden. The same clip is 93 KB as VP9, 226 KB as AV1 at a comparable
quantiser, and 7.5 MB as MJPEG — which is the other reason MJPEG is a
convenience rather than a recommendation.

Converting the frame is a large part of all three numbers, and it used to be
*more* than the decode — 6 ms against 3.7 on the 720p VP9 logo, which is not
where anyone looks first. Two things fixed it: converting two pixels at a time
(4:2:0 chroma is shared by each horizontal pair, so the arithmetic that turns
`u` and `v` into colour offsets is done once per pair), and taking each
destination row as one slice instead of four bounds checks per pixel. Then
converting at the *destination* size rather than the source's, since the frame
was going to be scaled anyway — which is most of the difference across each row
of the table.

```
$ oxtool video video/ik_logo.webm --tick 45 --out frame.png
video      video/ik_logo.webm
  codec      V_VP9 (libvpx)
  size       1280x720
  blocks     240 (none flagged as key)
  duration   4.00s at 60.0 fps

  into 320x240:
    fit         320.0x180.0  at    0.0,30.0
    zoomfill    426.7x240.0  at  -53.3,0.0
    ...
```

The test clips for AV1 and MJPEG are generated rather than found — neither codec
has any content in this archive to be tested against — by
`crates/oxyde-video/tests/assets/make.sh`, which needs `rav1e` and GStreamer and
is not a dependency of anything the engine builds.

### What is still missing

A video's **own soundtrack**. Ikemen GO decodes the Opus or Vorbis track of a
WebM background and mixes it; this reads the video track and ignores the rest.
Of the two videos Ikemen ships, `ik_logo.webm` has no audio track at all and
`ik_credits.webm` has an `A_OPUS` one.

The container half is already parsed, so for Vorbis the gap is only wiring —
`symphonia`, which the engine already uses for music, decodes it. Opus is the
harder half: `symphonia` has no Opus decoder, and every other option is either a
C library or a dependency whose licence has not been checked. It is not done
because it would have meant taking exactly the kind of dependency the rest of
this section is about refusing.

---

## 5. Stage transitions (the corner break)

A stage can name another stage to **break into**: corner an opponent, land a
hard enough unblocked hit against the wall, and the fight carries on in a
different arena — one match, no loading screen. It is wired from the stage's
`.def`, with `next` (where it breaks to) and `damage` (how hard the wall-hit
must be); see [EXTENSIONS.md](EXTENSIONS.md) for the full authoring detail and
the versus ruleset that gates it.

The transition itself is **presentation only** — a deterministic function of the
checksummed break timer, captured when the break starts, so it changes nothing
the simulation, a replay or a netplay peer can see. The default is a seamless,
MK-style swap: a short flash on the breaking hit, and a second flash across the
few ticks the backdrop changes on, so the new arena arrives *inside* a hit-flash
rather than behind an opaque cover. An author styles it from the same `[Break]`
section:

```ini
[Break]
next        = stages/rooftop.def
damage      = 60
flash       = 1             ; draw the flash at all (0 = bare swap, your own fx)
flashcolor  = 255, 40, 20   ; its tint (default warm white)
flashtime   = 6             ; half-width in ticks of the swap flash
flashbright = 180           ; peak alpha 0..255
impactflash = 1             ; the short pop on the breaking hit
```

Every key defaults to the built-in flash, so a stage that names only
`next`/`damage` is unchanged. `oxtool cornerbreak` renders the styled result
headlessly for previewing.

---

## Testing all of it without a screen

Every pipeline can draw to an offscreen texture and read it back, so the same
assertions the software rasteriser gets — this many pixels, this colour, in this
place — apply to the GPU path. Forcing the `llvmpipe` adapter gives an answer
that depends on Mesa rather than on whichever driver the machine has, which is
what makes a comparison between the two paths mean anything.

The row-padding dance in the readback is required rather than incidental: a
buffer copy must have rows that are a multiple of 256 bytes, so a 320-pixel
readback is 1280 bytes in a 1280-byte row and a 300-pixel one is 1200 in 1280.
Getting it wrong shifts every row by a few pixels, which reads as a shear rather
than as an error — so there is a test at 300 pixels wide.

## Supplied post-processing shaders

A player may drop their own shader into the installation and have the finished
frame presented through it. WGSL is read natively; GLSL is read when the engine
is built with the `glsl` feature, so a look written for another engine ports by
being copied in rather than rewritten.

```wgsl
// data/shaders/swap.wgsl — the whole thing
@group(0) @binding(0) var frame: texture_2d<f32>;
@group(0) @binding(1) var samp: sampler;

@fragment
fn fs(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let uv = pos.xy / vec2<f32>(64.0, 48.0);
    let c = textureSample(frame, samp, uv);
    return vec4<f32>(c.b, c.g, c.r, c.a);
}
```

The author writes a fragment shader and nothing else. The vertex stage is the
engine's own — one full-screen triangle, with nothing to customise about it.

### This does not make a GPU necessary

**The software rasteriser remains the default and the authoritative path.** A
supplied shader is a look applied to the finished frame on the optional
hardware path; with no GPU, the game runs exactly as before with the built-in
effects, which the rasteriser draws itself. Nothing about the match, the
replay, or a netplay peer depends on a shader compiling — or on there being a
GPU at all.

That is also why **per-sprite `ShaderSet` effects are deliberately not done
this way**. Those are part of the deterministic simulation: a character that
dissolves must dissolve identically on every machine, including one whose GPU
is a software driver. They stay a table of built-ins the rasteriser can draw.
See [the rationale in `oxyde_core::shader`](../crates/oxyde-core/src/shader.rs).

The division is worth stating once, plainly:

| | runs on | part of the simulation | may be supplied by a player |
|---|---|---|---|
| `ShaderSet` per-sprite effects | CPU **and** GPU | yes | no — named built-ins only |
| present-time post-processing | GPU path only | no | **yes, WGSL or GLSL** |

### A broken shader cannot take the game down

Nothing trusts the file. The name is refused if it carries a path, the source
is size-limited, a file of only comments is rejected, and WGSL without an `fs`
entry point is caught before the GPU ever sees it — so the common mistakes are
reported identically on a machine with no GPU.

The compile itself runs inside a wgpu error scope, because an uncaptured
validation error aborts the process rather than returning a `Result`. A shader
that will not compile comes back as a message, the frame is presented with the
built-in default, and the device stays usable — there is a test that compiles a
deliberately broken shader and then compiles a good one on the same device to
prove it.

Editing a shader rebuilds its pipeline: the cache is keyed by a hash of the
source, not by the file name, so saving a change does not leave the old version
on screen.
