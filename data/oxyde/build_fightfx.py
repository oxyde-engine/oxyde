#!/usr/bin/env python3
"""
Builds the Oxyde fight effects: fightfx.sff and fightfx.air.

    python3 data/oxyde/build_fightfx.py

Writes  data/oxyde/fightfx.sff
        data/oxyde/fightfx.air

These are the effects the *engine* makes: the spark when an attack lands, the
flash when one is blocked, the dust when somebody hits the floor or a wall, and
the charge a `SuperPause` puts over the fighter who called it. A character asks
for one by number — `HitDef sparkno = 2`, `guard.sparkno = 40` — and the number
indexes this file unless the author prefixed it with `S`, in which case it
indexes their own. So replacing this pack changes the hits of every character
in the archive that uses the defaults, and changes nothing at all for one that
brought its own art.

**What was here before.** `data/fightfx.sff` is Elecbyte's, dated 28 June 2000:
sixteen-colour sparks drawn on a 320x240 canvas for a 640x480 display, most of
them four or five frames long. On a 1080p panel they are eight-pixel blobs with
visible banding, and the four hit sparks are the same yellow starburst at four
sizes. They are also the only thing left in the picture that still looks like
2000, now that the stages are drawn at full size and the HUD is the pack's own.

**What replaced it.** The same nineteen actions, the same numbers, the same
meanings — a light hit is still `0` and a guard is still `40`, because a
thousand characters wrote those numbers down — drawn four times the size, in
the pack's own palette, with the shapes a modern fighting game uses:

    a white-hot core          every impact starts at white, not at its colour
    hard radial shards        the thing that reads as *force* at 60fps
    one thin expanding ring   what separates a hit from a sparkle
    a short, sharp decay      six to nine frames, never a slow fade

Colour carries weight, which is the one thing Elecbyte's set does not do: a
light hit is cold (cyan-white), a heavy one is hot (ember), and the strongest
is white through gold into rust. A blocked hit is the only cyan hexagon in the
game, so a block never looks like a hit that did nothing.

Everything is drawn additively (`A` in the `.air`), which is why the cores are
white: additive art has to be lit, not coloured.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_screenpack import (  # noqa: E402
    CYAN,
    EMBER,
    RUST_HI,
    RUST_LO,
    quantise,
    ramp,
    write_sff,
)

# Sprites are drawn at this multiple and downsampled, so every edge is
# antialiased before it is quantised.
SS = 3


# ----------------------------------------------------------------- palette
#
# Its own table rather than the screenpack's: these are all additive, so what
# the file needs is long ramps from white down through each accent into black,
# and almost nothing else. The screenpack's palette spends most of itself on
# steel and board greys, which an explosion has no use for.

def fx_palette():
    pal = [(0, 0, 0)]
    pal += ramp((255, 255, 255), (0, 24, 40), 46)          # cold impact
    pal += ramp((255, 255, 255), (60, 16, 0), 46)          # hot impact
    pal += ramp((255, 250, 230), EMBER, 26)                # ember core
    pal += ramp(EMBER, RUST_LO, 24)                        # ember falloff
    pal += ramp((236, 253, 255), CYAN, 20)                 # guard
    pal += ramp(CYAN, (4, 28, 44), 20)
    pal += ramp((255, 236, 236), (150, 16, 24), 24)        # blood
    pal += ramp((214, 206, 192), (28, 24, 20), 24)         # dust
    pal += [RUST_HI, RUST_LO, (255, 255, 255), (0, 0, 0)]
    seen, out = set(), []
    for c in pal:
        c = tuple(c)
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    out += [(0, 0, 0)] * (256 - len(out))
    return out[:256]


PAL = fx_palette()


def canvas(n):
    return Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))


def finish(img, n):
    return img.resize((n, n), Image.LANCZOS)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


# -------------------------------------------------------------- primitives


def glow(d, cx, cy, r, colour, steps=14, alpha=210):
    """A soft round core, drawn as nested discs rather than blurred.

    Blurring costs a Gaussian pass per frame and, once quantised to 256
    colours, bands anyway. Nested discs on a fixed ramp band the same amount
    and land exactly on palette entries.
    """
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        a = int(alpha * (1.0 - t) ** 2)
        if a <= 0 or rr < 0.4:
            continue
        c = mix((255, 255, 255), colour, t * 0.9)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c + (min(255, a + 45),))


def shards(d, cx, cy, inner, outer, n, colour, width, phase=0.0, taper=True):
    """Hard radial spikes: the thing that reads as force.

    Drawn as triangles rather than lines so they taper to a point at the far
    end, which is what stops a burst looking like a bicycle wheel.
    """
    for k in range(n):
        a = phase + k * math.tau / n
        ca, sa = math.cos(a), math.sin(a)
        px, py = -sa, ca
        w0 = width
        w1 = 0.0 if taper else width * 0.35
        pts = [
            (cx + ca * inner + px * w0, cy + sa * inner + py * w0),
            (cx + ca * outer + px * w1, cy + sa * outer + py * w1),
            (cx + ca * outer - px * w1, cy + sa * outer - py * w1),
            (cx + ca * inner - px * w0, cy + sa * inner - py * w0),
        ]
        d.polygon(pts, fill=colour + (255,))


def ring(d, cx, cy, r, thickness, colour, alpha=235):
    if r <= 0 or thickness <= 0:
        return
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=colour + (alpha,), width=max(1, int(thickness)))


def cross(d, cx, cy, reach, thick, colour):
    """The four-point lens flare every impact in a modern fighter has."""
    d.polygon([(cx - reach, cy), (cx, cy - thick), (cx + reach, cy),
               (cx, cy + thick)], fill=colour + (255,))
    d.polygon([(cx, cy - reach), (cx + thick, cy), (cx, cy + reach),
               (cx - thick, cy)], fill=colour + (255,))


# --------------------------------------------------------------- the hits
#
# One function for all four weights; they differ in size, colour, spike count
# and how long they live. Making them one shape at four temperatures is the
# point: a player learns the vocabulary once.

HIT_SPEC = {
    # group: (canvas, frames, spikes, hot, seed_angle)
    0: (48, 6, 6, False, 0.0),
    1: (68, 7, 8, False, 0.26),
    2: (92, 8, 10, True, 0.13),
    3: (128, 9, 12, True, 0.40),
}


def hit_frame(n, f, frames, spikes, hot, phase):
    img = canvas(n)
    d = ImageDraw.Draw(img)
    c = n * SS / 2.0
    t = f / max(1, frames - 1)
    # An impact is at its biggest almost immediately and then decays: the
    # curve is a fast open and a long tail, not a symmetric bloom.
    open_t = min(1.0, (f + 1) / 2.0)
    decay = (1.0 - t) ** 1.6

    tip = (255, 255, 255)
    if hot:
        body = mix((255, 244, 214), EMBER, t)
        rim = mix(EMBER, RUST_LO, t)
    else:
        body = mix((255, 255, 255), (150, 232, 255), t)
        rim = mix((120, 208, 250), (10, 48, 78), t)

    # The ring: out fast, thin, gone by two thirds.
    if t < 0.75:
        rr = c * (0.22 + 1.05 * (t / 0.75))
        th = max(1, int(c * 0.10 * (1.0 - t / 0.75) * SS / SS))
        ring(d, c, c, rr, th * SS * 0.5, rim, alpha=int(210 * (1.0 - t / 0.75)))

    # Shards.
    inner = c * 0.06
    outer = c * (0.42 + 0.58 * open_t) * (0.55 + 0.45 * decay)
    shards(d, c, c, inner, outer, spikes, body,
           width=c * 0.085 * (0.5 + 0.5 * decay), phase=phase + t * 0.5)
    # A second, shorter set offset between the first, which is what gives the
    # star its depth instead of looking like a snowflake.
    shards(d, c, c, inner, outer * 0.52, spikes, rim,
           width=c * 0.055 * (0.5 + 0.5 * decay),
           phase=phase + math.pi / spikes + t * 0.5)

    # The core, and the flare through it.
    glow(d, c, c, c * (0.34 * decay + 0.06), body, alpha=int(235 * decay))
    if t < 0.45:
        k = 1.0 - t / 0.45
        cross(d, c, c, c * (0.55 + 0.55 * k), c * 0.035 * k, tip)
        glow(d, c, c, c * 0.16 * k, tip, steps=8, alpha=255)
    return finish(img, n)


# --------------------------------------------------------------- the guard
#
# A blocked hit is the one thing in the set that is not a starburst: a
# hexagonal plate that flashes and breaks up. It is the only cyan hexagon in
# the game, so a block can never be mistaken for a hit that did no damage.


def guard_frame(n, f, frames):
    img = canvas(n)
    d = ImageDraw.Draw(img)
    c = n * SS / 2.0
    t = f / max(1, frames - 1)
    decay = (1.0 - t) ** 1.4
    r = c * (0.52 + 0.44 * min(1.0, (f + 1) / 2.5))

    def hexpts(rad, rot=0.0):
        return [(c + rad * math.cos(rot + k * math.tau / 6),
                 c + rad * math.sin(rot + k * math.tau / 6)) for k in range(6)]

    face = mix((236, 253, 255), CYAN, t)
    edge = mix(CYAN, (4, 28, 44), t)
    d.polygon(hexpts(r), fill=face + (int(120 * decay),))
    d.line(hexpts(r) + [hexpts(r)[0]], fill=face + (int(245 * decay),),
           width=max(1, int(c * 0.10 * SS / SS)))
    d.line(hexpts(r * 0.66, 0.5) + [hexpts(r * 0.66, 0.5)[0]],
           fill=edge + (int(190 * decay),), width=max(1, int(c * 0.05)))
    # It cracks outward in the back half rather than fading.
    if t > 0.3:
        k = (t - 0.3) / 0.7
        shards(d, c, c, r * (0.9 + 0.5 * k), r * (1.1 + 1.0 * k), 6, edge,
               width=c * 0.05 * (1.0 - k), phase=0.26)
    glow(d, c, c, c * 0.22 * decay, (236, 253, 255), alpha=int(220 * decay))
    return finish(img, n)


# --------------------------------------------------------------- the blood
#
# The same silhouette as a hit, in crimson, with the shards thrown to one side
# instead of radiating evenly. Kept abstract: this is an impact mark, not gore.


def blood_frame(n, f, frames, spread):
    img = canvas(n)
    d = ImageDraw.Draw(img)
    c = n * SS / 2.0
    t = f / max(1, frames - 1)
    decay = (1.0 - t) ** 1.5
    hot = mix((255, 236, 236), (214, 40, 48), t)
    low = mix((214, 40, 48), (86, 8, 12), t)
    for k in range(spread):
        a = -0.9 + k * (1.8 / max(1, spread - 1))
        d0 = c * (0.16 + 0.72 * t)
        d1 = d0 + c * 0.46 * decay
        w = c * 0.11 * decay * (0.45 + 0.55 * math.cos(a))
        ca, sa = math.cos(a), math.sin(a)
        d.polygon([(c + ca * d0 - sa * w, c + sa * d0 + ca * w),
                   (c + ca * d1, c + sa * d1),
                   (c + ca * d0 + sa * w, c + sa * d0 - ca * w)],
                  fill=(hot if k % 2 else low) + (255,))
    glow(d, c, c, c * 0.34 * decay, hot, alpha=int(245 * decay))
    return finish(img, n)


# ------------------------------------------------------------- the ground
#
# Dust rather than light: a low, wide ring that flattens as it spreads, with a
# few chips thrown up out of it. Drawn on a canvas twice as wide as it is tall
# and anchored at the bottom, because it happens on the floor.


def dust_frame(w, h, f, frames, chips):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w * SS / 2.0, h * SS * 0.86
    t = f / max(1, frames - 1)
    decay = (1.0 - t) ** 1.3
    r = w * SS * (0.10 + 0.42 * t)
    ry = r * 0.36
    pale = mix((214, 206, 192), (60, 54, 48), t)
    for k in range(4):
        rr = r * (1.0 - k * 0.16)
        d.ellipse([cx - rr, cy - rr * 0.36, cx + rr, cy + rr * 0.36],
                  outline=pale + (int(235 * decay * (1.0 - k * 0.15)),),
                  width=max(2, int(h * SS * 0.13 * decay) + 1))
    # A lit smear where the body actually landed, or the ring reads as a
    # smoke signal rather than as an impact.
    glow(d, cx, cy, h * SS * 0.42 * decay, (255, 246, 226),
         steps=10, alpha=int(215 * decay))
    for k in range(chips):
        a = -0.35 - k * (2.4 / max(1, chips))
        rise = h * SS * 0.5 * t * (0.6 + 0.4 * ((k * 7) % 5) / 5.0)
        px = cx + math.cos(a) * r * 1.05
        py = cy - rise - ry * 0.2
        s = max(1.5, h * SS * 0.085 * decay)
        d.rectangle([px - s, py - s, px + s, py + s], fill=pale + (230,))
    return img.resize((w, h), Image.LANCZOS)


# --------------------------------------------------------------- the wall
#
# A fan against a vertical surface, opening away from it.


def wall_frame(w, h, f, frames):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w * SS * 0.12, h * SS / 2.0
    t = f / max(1, frames - 1)
    decay = (1.0 - t) ** 1.4
    pale = mix((255, 244, 220), EMBER, t)
    for k in range(9):
        a = -1.15 + k * (2.30 / 8)
        d0 = w * SS * (0.04 + 0.30 * t)
        d1 = d0 + w * SS * 0.42 * decay
        wd = h * SS * 0.045 * decay
        ca, sa = math.cos(a), math.sin(a)
        d.polygon([(cx + ca * d0 - sa * wd, cy + sa * d0 + ca * wd),
                   (cx + ca * d1, cy + sa * d1),
                   (cx + ca * d0 + sa * wd, cy + sa * d0 - ca * wd)],
                  fill=pale + (255,))
    glow(d, cx, cy, w * SS * 0.13 * decay, (255, 250, 235),
         alpha=int(230 * decay))
    return img.resize((w, h), Image.LANCZOS)


# --------------------------------------------------------------- the super
#
# `SuperPause`'s own charge animation — actions 100, 101 and 102 — is the one
# effect in this file that has to be *big*. MUGEN draws it as an `ontop`
# explod over the fighter who called the super, which means it is the only
# part of a hyper flash the engine itself is allowed to draw over the darkened
# screen, and Elecbyte's is eighty pixels tall.
#
# These are 320 units tall on a 240-unit screen: a column of fire from below
# the fighter's feet to above the top of the picture, with a rising sheet of
# embers inside it and a ground flare at the bottom. Anchored at the feet.
#
# The engine also paints its own full-screen burst behind all of this
# (`oxyde-render/src/superfx.rs`); the two are meant to be seen together, the
# column reading as the source of the rays.

SUPER_SPEC = {100: (200, 320, 3), 101: (240, 360, 4), 102: (300, 420, 5)}


def super_frame(w, h, f, frames, level):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * SS / 2.0
    floor = h * SS * 0.97
    t = f / max(1, frames - 1)
    grow = min(1.0, (f + 1) / 3.0)
    height = h * SS * (0.40 + 0.58 * grow)

    hot = (255, 250, 232)
    mid = EMBER

    # Tongues of flame rather than a stack of filled ellipses: a column drawn
    # as nested discs comes out as a solid lampshade with a hard flat top,
    # which is what the first pass at this looked like. What reads as fire is
    # a handful of tapering blades of different heights, leaning, overlapping
    # and additive, with nothing solid anywhere in it.
    blades = 9 + level
    for k in range(blades):
        u = (k + 0.5) / blades
        # Spread out from the middle, tallest in the centre.
        side = (u - 0.5) * 2.0
        base = cx + side * w * SS * 0.34
        tall = height * (1.0 - abs(side) ** 1.6 * 0.62)
        tall *= 0.78 + 0.22 * math.sin(k * 2.3 + f * 0.85)
        wob = math.sin(k * 1.7 + f * 0.7) * w * SS * 0.06
        wide = w * SS * (0.085 + 0.05 * (1.0 - abs(side)))
        # Each blade is a quad that pinches to a point, drawn a few times at
        # shrinking width so it has a lit core.
        for pass_i, (shrink, colour, alpha) in enumerate(
            ((1.0, mix(mid, RUST_LO, 0.45), 120),
             (0.58, mid, 170),
             (0.26, mix(hot, mid, 0.35), 225))
        ):
            ww = wide * shrink
            d.polygon(
                [
                    (base - ww, floor),
                    (base - ww * 0.25 + wob * 0.5, floor - tall * 0.55),
                    (base + wob, floor - tall),
                    (base + ww * 0.25 + wob * 0.5, floor - tall * 0.55),
                    (base + ww, floor),
                ],
                fill=colour + (alpha,),
            )

    # Embers rising out of it, beyond the tips.
    rise = (f * 0.9) % 1.0
    for k in range(16 + level * 5):
        u = (k * 0.137 + rise) % 1.0
        y = floor - height * (0.15 + 0.95 * u)
        off = math.sin(k * 2.1 + u * 5.0) * w * SS * 0.30 * (0.25 + u)
        sz = max(1.0, w * SS * 0.016 * (1.0 - u * 0.7))
        d.rectangle([cx + off - sz, y - sz, cx + off + sz, y + sz],
                    fill=mix(hot, mid, u) + (235,))

    # The ground flare, the shards standing out of it, and a hard core at the
    # fighter's chest — which is what the engine's full-screen rays behind all
    # of this appear to come out of.
    glow(d, cx, floor, w * SS * 0.40 * (0.7 + 0.3 * math.sin(f * 0.8)), mid,
         steps=16, alpha=225)
    shards(d, cx, floor, w * SS * 0.10,
           w * SS * (0.46 + 0.10 * math.sin(f * 0.7)), 8,
           mix(hot, mid, 0.4), width=w * SS * 0.026, phase=f * 0.18)
    chest = floor - h * SS * 0.20
    glow(d, cx, chest, w * SS * 0.15 * (0.8 + 0.2 * math.sin(f * 1.1)), hot,
         steps=10, alpha=245)
    if t < 0.2:
        cross(d, cx, chest, w * SS * 0.7 * (1.0 - t / 0.2), w * SS * 0.02, hot)
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------- 120 and 130
#
# 120 is the hit-spark a *throw* makes and 130 is the small power-up flash a
# character gets for banking a level. Both are one-offs in Elecbyte's set and
# both are kept.


def throw_frame(n, f, frames):
    img = canvas(n)
    d = ImageDraw.Draw(img)
    c = n * SS / 2.0
    t = f / max(1, frames - 1)
    decay = (1.0 - t) ** 1.5
    body = mix((255, 250, 240), EMBER, t)
    shards(d, c, c, c * 0.05, c * (0.55 + 0.45 * min(1.0, (f + 1) / 2.0)) * (0.5 + 0.5 * decay),
           4, body, width=c * 0.13 * decay, phase=math.pi / 4 + t)
    glow(d, c, c, c * 0.38 * decay, body, alpha=int(240 * decay))
    return finish(img, n)


def powerup_frame(n, f, frames):
    img = canvas(n)
    d = ImageDraw.Draw(img)
    c = n * SS / 2.0
    t = f / max(1, frames - 1)
    r = c * (0.20 + 0.78 * t)
    a = int(235 * (1.0 - t) ** 1.2)
    ring(d, c, c, r, max(1, c * 0.09 * (1.0 - t)), mix((255, 250, 235), EMBER, t), a)
    ring(d, c, c, r * 0.62, max(1, c * 0.05 * (1.0 - t)), mix(EMBER, RUST_LO, t), a)
    glow(d, c, c, c * 0.22 * (1.0 - t), (255, 250, 235), alpha=a)
    return finish(img, n)


# ------------------------------------------------------------------- build


def build():
    sprites = []
    actions = []

    def add(group, image, img, axis):
        w, h, idx = quantise(img, palette=PAL)
        sprites.append((group, image, axis, w, h, idx))

    def centred(group, image, img):
        add(group, image, img, (img.size[0] // 2, img.size[1] // 2))

    # --- hit sparks 0-3
    for g, (n, frames, spikes, hot, phase) in HIT_SPEC.items():
        for f in range(frames):
            centred(g, f, hit_frame(n, f, frames, spikes, hot, phase))
        # Two ticks a frame at the front where the shape is changing fastest,
        # one at the back: an impact is not evenly paced.
        steps = [(g, f, 1 if f < 3 else 2) for f in range(frames)]
        actions.append((g, steps, "A"))

    # --- blood 10-12
    for g, (n, frames, spread) in {10: (44, 6, 5), 11: (62, 7, 7),
                                   12: (84, 8, 9)}.items():
        for f in range(frames):
            centred(g, f, blood_frame(n, f, frames, spread))
        actions.append((g, [(g, f, 2) for f in range(frames)], "A"))

    # --- guard 40
    gframes = 7
    for f in range(gframes):
        centred(40, f, guard_frame(64, f, gframes))
    actions.append((40, [(40, f, 1 if f < 3 else 2) for f in range(gframes)], "A"))

    # --- ground shockwaves 60-62
    for g, (w, h, frames, chips) in {60: (96, 40, 6, 5), 61: (140, 56, 7, 8),
                                     62: (200, 76, 9, 12)}.items():
        for f in range(frames):
            img = dust_frame(w, h, f, frames, chips)
            # Anchored at the bottom centre: it happens on the floor.
            add(g, f, img, (img.size[0] // 2, img.size[1] - 1))
        actions.append((g, [(g, f, 2) for f in range(frames)], "A"))

    # --- wall hits 70-72
    for g, (w, h, frames) in {70: (72, 60, 5), 71: (104, 84, 6),
                              72: (150, 120, 7)}.items():
        for f in range(frames):
            img = wall_frame(w, h, f, frames)
            add(g, f, img, (int(img.size[0] * 0.12), img.size[1] // 2))
        actions.append((g, [(g, f, 2) for f in range(frames)], "A"))

    # --- super charge 100-102
    for g, (w, h, level) in SUPER_SPEC.items():
        frames = 8
        for f in range(frames):
            img = super_frame(w, h, f, frames, level)
            add(g, f, img, (img.size[0] // 2, img.size[1] - 1))
        # Looped: a SuperPause runs for as long as the character asked, and
        # the charge has to still be burning when it ends.
        actions.append((g, [(g, f, 2) for f in range(frames)], "A", True))

    # --- throw spark 120, power-up 130
    for f in range(6):
        centred(120, f, throw_frame(72, f, 6))
    actions.append((120, [(120, f, 2) for f in range(6)], "A"))
    for f in range(7):
        centred(130, f, powerup_frame(96, f, 7))
    actions.append((130, [(130, f, 2) for f in range(7)], "A"))

    size = write_sff(os.path.join(HERE, "fightfx.sff"), sprites, PAL)
    print("fightfx.sff  %d sprites, %d KiB" % (len(sprites), size // 1024))

    lines = [
        "; Oxyde fight effects - GENERATED by build_fightfx.py.",
        "; Edit the script, not this file.",
        ";",
        "; Action numbers are Elecbyte's, because a thousand characters wrote",
        "; them down: 0-3 hit sparks by weight, 10-12 blood, 40 guard, 60-62",
        "; ground shockwaves, 70-72 wall hits, 100-102 the SuperPause charge",
        "; by level, 120 a throw, 130 a banked power level.",
        "",
    ]
    for entry in actions:
        loop = len(entry) > 3 and entry[3]
        g, steps, mode = entry[0], entry[1], entry[2]
        lines.append("[Begin Action %d]" % g)
        if loop:
            lines.append("Loopstart")
        for sg, si, dur in steps:
            lines.append("%d,%d, 0,0, %d, ,%s" % (sg, si, dur, mode))
        lines.append("")
    path = os.path.join(HERE, "fightfx.air")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print("fightfx.air  %d actions" % len(actions))


if __name__ == "__main__":
    build()
